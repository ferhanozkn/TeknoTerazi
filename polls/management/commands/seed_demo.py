import random
import uuid

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import CustomUser
from polls.models import Category, Poll, Product, Vote, VoteValue

DEMO_USERNAME_PREFIX = "demo_"

DEMO_USERS = [
    {"username": "demo_ahmet", "email": "demo.ahmet@teknoterazi.demo"},
    {"username": "demo_ece", "email": "demo.ece@teknoterazi.demo"},
    {"username": "demo_can", "email": "demo.can@teknoterazi.demo"},
]

SAMPLE_POLLS = [
    {
        "title": "Hangi telefonu almalıyım?",
        "category": Category.PHONE,
        "description": "Bütçem sınırlı, kamera ve pil ömrü benim için önemli.",
        "products": [
            {"name": "iPhone 13", "price": "24999.00", "features": "128 GB\nA15 Bionic\n12 MP çift kamera"},
            {"name": "Samsung Galaxy S22", "price": "21999.00", "features": "128 GB\n50 MP kamera\n120 Hz ekran"},
            {"name": "Xiaomi 12", "price": "16999.00", "features": "256 GB\n108 MP kamera\nHızlı şarj"},
        ],
    },
    {
        "title": "Öğrenci laptopu önerisi var mı?",
        "category": Category.LAPTOP,
        "description": "Ofis işleri ve hafif düzenleme için, taşınabilir olsun istiyorum.",
        "products": [
            {"name": "MacBook Air M2", "price": "42999.00", "features": "8 GB RAM\n256 GB SSD\n18 saat pil"},
            {"name": "Lenovo IdeaPad 5", "price": "24999.00", "features": "16 GB RAM\n512 GB SSD\nRyzen 5"},
        ],
    },
    {
        "title": "Çizim için tablet arıyorum",
        "category": Category.TABLET,
        "description": "Dijital çizim ve not almak için kullanacağım.",
        "products": [
            {"name": "iPad Air", "price": "27999.00", "features": "64 GB\nApple Pencil desteği\nM1 çip"},
            {"name": "Samsung Galaxy Tab S8", "price": "23999.00", "features": "128 GB\nS Pen dahil\n120 Hz ekran"},
            {"name": "Xiaomi Pad 6", "price": "13999.00", "features": "128 GB\n144 Hz ekran"},
        ],
    },
    {
        "title": "Spor için kulaklık önerisi",
        "category": Category.HEADPHONE,
        "description": "Koşarken kullanacağım, ter/su geçirmez olsun.",
        "products": [
            {"name": "AirPods Pro 2", "price": "9999.00", "features": "Aktif gürültü engelleme\nIPX4"},
            {"name": "JBL Endurance Peak 3", "price": "2499.00", "features": "IP68\n10 saat pil"},
        ],
    },
    {
        "title": "İlk akıllı saatim ne olmalı?",
        "category": Category.SMARTWATCH,
        "description": "Uyku takibi ve nabız ölçümü öncelikli.",
        "products": [
            {"name": "Apple Watch SE", "price": "12999.00", "features": "Nabız ölçer\nUyku takibi\nGPS"},
            {"name": "Xiaomi Watch S1", "price": "4499.00", "features": "14 gün pil\nSpO2 ölçer"},
        ],
    },
    {
        "title": "Konsol mu PC mi almalıyım?",
        "category": Category.GAMING,
        "description": "Bütçem sınırlı, öncelik oyun performansı.",
        "products": [
            {"name": "PlayStation 5", "price": "26999.00", "features": "825 GB SSD\n4K 120 Hz destek"},
            {"name": "Xbox Series S", "price": "10999.00", "features": "512 GB SSD\n1440p 120 Hz"},
        ],
    },
    {
        "title": "Vlog için hangi kamera?",
        "category": Category.CAMERA,
        "description": "Youtube videoları çekeceğim, otofokus önemli.",
        "products": [
            {"name": "Sony ZV-E10", "price": "28999.00", "features": "APS-C sensör\nDeğiştirilebilir lens"},
            {"name": "Canon PowerShot G7X III", "price": "24999.00", "features": "1 inç sensör\nDikey video modu"},
        ],
    },
    {
        "title": "Salon için TV önerisi",
        "category": Category.TV,
        "description": "55 inç civarı, oyun konsolu bağlayacağım.",
        "products": [
            {"name": "LG C2 OLED 55\"", "price": "34999.00", "features": "120 Hz\nHDMI 2.1\n4K OLED"},
            {"name": "Samsung QN90B 55\"", "price": "29999.00", "features": "Neo QLED\n120 Hz"},
            {"name": "TCL C735 55\"", "price": "17999.00", "features": "Mini LED\n4K 120 Hz"},
        ],
    },
    {
        "title": "Ekran kartı yükseltmesi mantıklı mı?",
        "category": Category.PC_PART,
        "description": "1080p'de oynuyorum, 1440p'ye geçmeyi düşünüyorum.",
        "products": [
            {"name": "RTX 4070", "price": "32999.00", "features": "12 GB VRAM\nDLSS 3"},
            {"name": "RX 7800 XT", "price": "27999.00", "features": "16 GB VRAM\nFSR 3"},
        ],
    },
]


class Command(BaseCommand):
    help = "Demo kullanıcılar, anketler ve rastgele oylarla veritabanını doldurur."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Yeni veri eklemek yerine yalnızca demo verisini temizle.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()
        else:
            self._seed()

    def _flush(self):
        demo_users = CustomUser.objects.filter(username__startswith=DEMO_USERNAME_PREFIX)
        polls = Poll.objects.filter(author__in=demo_users)
        poll_count = polls.count()
        polls.delete()
        user_count = demo_users.count()
        demo_users.delete()
        self.stdout.write(
            self.style.SUCCESS(f"{poll_count} demo anket ve {user_count} demo kullanıcı silindi.")
        )

    def _seed(self):
        with transaction.atomic():
            users = [self._get_or_create_user(data) for data in DEMO_USERS]

            created_count = 0
            for index, poll_data in enumerate(SAMPLE_POLLS):
                author = users[index % len(users)]
                poll, created = Poll.objects.get_or_create(
                    title=poll_data["title"],
                    author=author,
                    defaults={
                        "category": poll_data["category"],
                        "description": poll_data["description"],
                    },
                )
                if not created:
                    continue
                created_count += 1
                for position, product_data in enumerate(poll_data["products"]):
                    product = Product.objects.create(poll=poll, position=position, **product_data)
                    self._add_random_votes(product)

        self.stdout.write(self.style.SUCCESS(f"{created_count} demo anket oluşturuldu."))

    def _get_or_create_user(self, data):
        user, created = CustomUser.objects.get_or_create(
            username=data["username"], defaults={"email": data["email"]}
        )
        if created:
            user.set_password("demo12345")
            user.save()
        return user

    def _add_random_votes(self, product):
        vote_count = random.randint(3, 40)
        votes = [
            Vote(
                product=product,
                anon_id=uuid.uuid4(),
                value=random.choices([VoteValue.WORTH, VoteValue.NOT_WORTH], weights=[7, 3])[0],
            )
            for _ in range(vote_count)
        ]
        Vote.objects.bulk_create(votes)
