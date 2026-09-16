# TeknoTerazi — Proje Planı ve Teknik Şartname (MVP)

> Bu dosya, Claude Code ile TeknoTerazi uygulamasını geliştirmek için tek kaynak (source of truth) olarak hazırlanmıştır.
> Geliştirme **fazlar halinde** ilerler. Bir fazın **kabul kriterleri** karşılanmadan sonraki faza geçilmez.

---

## 0. Claude Code İçin Çalışma Talimatları

1. Her oturumun başında bu dosyayı oku ve hangi fazda olduğumuzu **"İlerleme Durumu"** bölümünden kontrol et.
2. Bir fazdaki görevleri sırayla yap; tamamlanan maddeleri `- [ ]` → `- [x]` olarak işaretle.
3. Faz bitince: testleri çalıştır (`USE_DIRECT_DB=1 python manage.py test --keepdb` — bkz. Karar Günlüğü #13), kabul kriterlerini tek tek doğrula, ardından anlamlı bir commit at (örn. `feat(faz-3): anket oluşturma formu`).
4. **Dil kuralı:** Kullanıcıya görünen tüm metinler (arayüz, hata mesajları, e-postalar) **Türkçe**; kod, değişken, fonksiyon, model ve dosya adları **İngilizce**.
5. Ayrı bir frontend framework (React, Vue, Tailwind build, HTMX vb.) **kullanma**. Yalnızca Django şablonları + saf HTML, CSS ve JavaScript.
6. Bu dosyada karar verilmemiş bir konuyla karşılaşırsan en basit çözümü uygula ve **"Açık Sorular / Karar Günlüğü"** bölümüne not düş.
7. Gizli bilgileri (SECRET_KEY, veritabanı parolası) asla koda veya commit'e yazma; `.env` kullan.
8. Vercel ve Supabase yapılandırması zamanla değişebilir. Dağıtım adımlarında güncel resmi dokümantasyonu kontrol et.

### İlerleme Durumu

| Faz | Başlık | Durum |
|-----|--------|-------|
| 0 | Kurulum ve ortam | ✅ Tamamlandı |
| 1 | Veri modeli ve admin | ✅ Tamamlandı |
| 2 | Kimlik doğrulama | ✅ Tamamlandı |
| 3 | Anket oluşturma | ✅ Tamamlandı |
| 4 | Listeleme ve detay | ✅ Tamamlandı |
| 5 | Oylama sistemi | ✅ Tamamlandı |
| 6 | Tasarım sistemi ve arayüz cilası | ✅ Tamamlandı |
| 7 | Güvenlik, testler, demo verisi | ✅ Tamamlandı |
| 8 | Vercel'e dağıtım | ⬜ |
| 9 | MVP sonrası (backlog) | — |

---

## 1. Ürün Özeti

**TeknoTerazi**, teknolojik ürün satın alırken kararsız kalan kullanıcıların, aday ürünleri topluluğa sorarak karar vermesini kolaylaştıran bir web uygulamasıdır.

- Kayıtlı kullanıcı bir **anket** oluşturur ve ankete **2–5 ürün** ekler.
- Her ürün için **ad, fiyat ve özellikler zorunludur.**
- Platformu ziyaret eden **herkes** (üye olsun olmasın) tüm anketleri görebilir ve her ürün için **"Buna değer 👍"** veya **"Buna değmez 👎"** oyu verebilir.
- **Takip mekanizması yoktur.** Akış herkese aynıdır.
- Anketlerde yazar olarak yalnızca **kullanıcı adı** görünür (e-posta asla gösterilmez).

### Hedef kitle
Teknolojiye ilgi duyan gençler (16–30 yaş). Arayüz mobil öncelikli, hızlı ve eğlenceli olmalı.

### MVP kapsamı

| Kapsamda ✅ | Kapsam dışı ❌ (Faz 9'a) |
|---|---|
| Kayıt / giriş / çıkış (e-posta + parola + kullanıcı adı) | E-posta doğrulama, şifre sıfırlama |
| Anket oluşturma (2–5 ürün) | Anket düzenleme |
| Anket listeleme, arama, kategori filtresi, sıralama | Yorumlar |
| Anket detay ve sonuç çubukları | Görsel yükleme (Supabase Storage) |
| Üyeli/üyesiz oylama, oy değiştirme ve geri alma | Takip, bildirim |
| Anketi kapatma ve silme (sahibi) | Sosyal giriş, karanlık mod |
| "Anketlerim" sayfası | CAPTCHA, gelişmiş bot koruması |

---

## 2. Teknoloji Yığını

| Katman | Teknoloji | Not |
|---|---|---|
| Dil | Python 3.12 | Vercel Python runtime ile uyumlu sürümü kontrol et |
| Web framework | Django 5.2 (LTS) | |
| Veritabanı | Supabase (PostgreSQL) | Django doğrudan Postgres'e bağlanır |
| DB sürücüsü | `psycopg[binary]` (v3) | |
| Yapılandırma | `django-environ` veya `python-dotenv` + `dj-database-url` | |
| Statik dosyalar | `whitenoise` | |
| Frontend | Django şablonları + HTML + CSS + vanilla JS | Framework yok |
| Barındırma | Vercel (Python serverless) | |
| Test | Django `TestCase` | |

### Mimari kararlar
- **Kimlik doğrulama Django'nun kendi auth sistemiyle yapılır**, kullanıcı tablosu Supabase Postgres'te durur. Supabase Auth MVP'de kullanılmaz (tek bir auth kaynağı, daha az karmaşıklık).
- Supabase'in otomatik REST API'si (PostgREST) üzerinden tablolara dışarıdan erişilmesini engellemek için **tüm tablolarda RLS açılır** (bkz. Faz 8).
- Sunucusuz ortam nedeniyle kalıcı DB bağlantısı tutulmaz (`CONN_MAX_AGE = 0`) ve Supabase **connection pooler (transaction mode, port 6543)** kullanılır.

### `requirements.txt` (başlangıç)
```
Django>=5.2,<5.3
psycopg[binary]>=3.2
dj-database-url>=2.2
python-dotenv>=1.0
whitenoise>=6.7
```

---

## 3. Proje Yapısı

```
teknoterazi/
├── manage.py
├── requirements.txt
├── vercel.json
├── .env.example
├── .gitignore
├── README.md
├── PROJE_PLANI.md
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/
│   ├── models.py          # CustomUser
│   ├── forms.py           # SignUpForm, EmailLoginForm
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── polls/
│   ├── models.py          # Poll, Product, Vote
│   ├── forms.py           # PollForm, ProductFormSet
│   ├── services.py        # oylama ve istatistik iş mantığı
│   ├── voter.py           # anonim oylayıcı kimliği (çerez) yardımcıları
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── templatetags/
│   │   └── tt_filters.py  # fiyat formatı (₺), yüzde vb.
│   ├── management/commands/
│   │   └── seed_demo.py
│   └── tests/
│       ├── test_models.py
│       ├── test_forms.py
│       ├── test_views.py
│       └── test_voting.py
├── templates/
│   ├── base.html
│   ├── partials/
│   │   ├── navbar.html
│   │   ├── footer.html
│   │   ├── messages.html
│   │   ├── poll_card.html
│   │   ├── product_card.html
│   │   └── pagination.html
│   ├── accounts/
│   │   ├── signup.html
│   │   └── login.html
│   ├── polls/
│   │   ├── home.html
│   │   ├── poll_detail.html
│   │   ├── poll_create.html
│   │   ├── poll_confirm_delete.html
│   │   └── my_polls.html
│   ├── 404.html
│   └── 500.html
└── static/
    ├── css/
    │   └── main.css
    ├── js/
    │   ├── poll_form.js   # dinamik ürün ekleme/çıkarma
    │   └── vote.js        # AJAX oylama
    └── img/
        ├── logo.svg
        └── favicon.svg
```

---

## 4. Veri Modeli

### 4.1 `accounts.CustomUser`
> ⚠️ Özel kullanıcı modeli **ilk `migrate` komutundan önce** tanımlanmalıdır.

`AbstractUser`'dan türetilir.

| Alan | Tip | Kural |
|---|---|---|
| `username` | CharField(30) | Zorunlu, benzersiz, `^[a-zA-Z0-9_]{3,30}$`, büyük/küçük harf duyarsız benzersizlik |
| `email` | EmailField | Zorunlu, benzersiz (küçük harfe çevrilerek saklanır) |
| `password` | — | Django parola doğrulayıcıları (min 8 karakter vb.) |
| `date_joined` | DateTime | Otomatik |

- `USERNAME_FIELD = "email"` → giriş e-posta + parola ile yapılır.
- `REQUIRED_FIELDS = ["username"]`
- `first_name` / `last_name` kullanılmaz.
- `AUTH_USER_MODEL = "accounts.CustomUser"`

### 4.2 `polls.Poll` (Anket)

| Alan | Tip | Kural |
|---|---|---|
| `author` | FK → User, `CASCADE`, `related_name="polls"` | Zorunlu |
| `title` | CharField(120) | Zorunlu, min 5 karakter. Örn: "Hangi telefonu almalıyım?" |
| `description` | TextField(max 1000) | Opsiyonel. Kullanım amacı, bütçe vb. |
| `category` | CharField(choices) | Zorunlu |
| `is_active` | BooleanField(default=True) | `False` ise oylama kapalı |
| `created_at` | DateTime(auto_now_add) | İndeksli |
| `updated_at` | DateTime(auto_now) | |

**Kategori seçenekleri:**
`phone` Akıllı Telefon · `laptop` Dizüstü Bilgisayar · `tablet` Tablet · `headphone` Kulaklık · `smartwatch` Akıllı Saat · `gaming` Oyun & Konsol · `camera` Kamera · `tv` TV & Monitör · `pc_part` Bilgisayar Parçası · `other` Diğer

`Meta.ordering = ["-created_at"]`

### 4.3 `polls.Product` (Ankete eklenen ürün)

| Alan | Tip | Kural |
|---|---|---|
| `poll` | FK → Poll, `CASCADE`, `related_name="products"` | |
| `name` | CharField(100) | **Zorunlu** |
| `price` | DecimalField(max_digits=10, decimal_places=2) | **Zorunlu**, `> 0`, `≤ 10.000.000` |
| `currency` | CharField(3, default="TRY") | MVP'de yalnızca TRY |
| `features` | TextField | **Zorunlu.** Her satır bir özellik; 1–15 satır, her satır ≤ 120 karakter |
| `product_url` | URLField | Opsiyonel (yalnızca http/https) |
| `image_url` | URLField | Opsiyonel (yalnızca https) |
| `position` | PositiveSmallIntegerField | Anket içindeki sıra (0–4) |

- `features_list` property: boş satırları atarak listeyi döndürür.
- `Meta.ordering = ["position"]`
- `UniqueConstraint(fields=["poll", "position"])`
- **Ürün sayısı kuralı (2–5):** Veritabanında değil, form/formset ve servis katmanında zorunlu tutulur.

### 4.4 `polls.Vote` (Oy)

| Alan | Tip | Kural |
|---|---|---|
| `product` | FK → Product, `CASCADE`, `related_name="votes"` | |
| `user` | FK → User, `SET_NULL`, null=True | Üye oyları |
| `anon_id` | UUIDField, null=True, indeksli | Üyesiz oylar (çerezden gelir) |
| `value` | SmallIntegerField(choices) | `1` = Buna değer, `-1` = Buna değmez |
| `created_at` / `updated_at` | DateTime | |

**Kısıtlar:**
```python
constraints = [
    models.UniqueConstraint(
        fields=["product", "user"],
        condition=models.Q(user__isnull=False),
        name="unique_vote_per_user",
    ),
    models.UniqueConstraint(
        fields=["product", "anon_id"],
        condition=models.Q(anon_id__isnull=False),
        name="unique_vote_per_anon",
    ),
    models.CheckConstraint(
        condition=(
            models.Q(user__isnull=False, anon_id__isnull=True)
            | models.Q(user__isnull=True, anon_id__isnull=False)
        ),
        name="vote_has_exactly_one_voter",
    ),
]
```
> Django 5.2'de `CheckConstraint` için parametre adı `condition`'dır (eski `check` değil).

---

## 5. İş Kuralları

### 5.1 Anket
- Yalnızca **giriş yapmış** kullanıcılar anket oluşturabilir.
- Bir ankette **en az 2, en fazla 5** ürün bulunur.
- Aynı anketteki ürün adları (büyük/küçük harf duyarsız, baştaki/sondaki boşluklar atılarak) **tekrar edemez**.
- Anket ve ürünleri **tek bir `transaction.atomic()`** içinde kaydedilir.
- Oluşturulduktan sonra anket **düzenlenemez** (oylar yanıltıcı hale gelmesin diye). Sahibi anketi **kapatabilir/yeniden açabilir** veya **silebilir**.

### 5.2 Oylama
- Herkes oy verebilir: üyeler `user` ile, üyesizler `anon_id` ile tanınır.
- Her oylayıcı, **her ürün için** en fazla 1 oy verebilir (yani bir ankette her ürüne ayrı ayrı oy verilir).
- Aynı butona tekrar basmak oyu **geri alır** (toggle). Diğer butona basmak oyu **değiştirir**.
- Anket kapalıysa (`is_active=False`) oy verilemez; sonuçlar görünmeye devam eder.
- **Anket sahibi, giriş yapmışken kendi anketine oy veremez.** (Butonlar pasif görünür, sunucu da reddeder.)
- Sonuçlar oy vermeden de görünür (MVP kararı; bkz. Açık Sorular).

### 5.3 Anonim oylayıcı kimliği
- Çerez adı: `tt_voter`, değer: UUID4, **imzalı** (`set_signed_cookie` / `get_signed_cookie`, salt: `"tt-voter"`).
- Ömür: 365 gün, `HttpOnly`, `SameSite=Lax`, üretimde `Secure`.
- Çerez yalnızca **ilk oy verildiğinde** oluşturulur (gereksiz çerez yazma yok).
- Geçersiz/değiştirilmiş imza → yeni UUID üretilir.
- Bilinen sınırlama: Çerezi silen kişi tekrar oy verebilir. MVP'de kabul edilir; Faz 9'da ek önlemler.
- Footer'da kısa bir çerez bilgilendirme notu bulunur (KVKK farkındalığı).

### 5.4 İstatistikler (her ürün için)
- `worth_count`, `not_worth_count`, `total_votes`
- `worth_ratio = worth_count / total_votes * 100` (oy yoksa `None` → "Henüz oy yok")
- Tek sorguda `annotate(Count("votes", filter=Q(votes__value=1)), ...)` ile hesaplanır; N+1 sorgudan kaçınılır.
- **"Topluluğun Favorisi" rozeti:** En az 3 oy almış ürünler arasında en yüksek `worth_ratio`'ya sahip ürün. Beraberlikte daha çok toplam oy alan; yine eşitse rozet verilmez.

---

## 6. URL Haritası

| URL | View | Yöntem | Erişim | Açıklama |
|---|---|---|---|---|
| `/` | `home` | GET | Herkes | Anket akışı (arama, filtre, sıralama, sayfalama) |
| `/anket/yeni/` | `poll_create` | GET, POST | Üye | Anket oluşturma |
| `/anket/<int:pk>/` | `poll_detail` | GET | Herkes | Anket detayı ve oylama |
| `/anket/<int:pk>/durum/` | `poll_toggle_active` | POST | Sahibi | Anketi kapat/aç |
| `/anket/<int:pk>/sil/` | `poll_delete` | GET, POST | Sahibi | Silme onayı ve silme |
| `/urun/<int:pk>/oy/` | `vote` | POST | Herkes | Oy ver/değiştir/geri al (JSON döner) |
| `/anketlerim/` | `my_polls` | GET | Üye | Kullanıcının kendi anketleri |
| `/hesap/kayit/` | `signup` | GET, POST | Misafir | Kayıt |
| `/hesap/giris/` | `login` | GET, POST | Misafir | Giriş |
| `/hesap/cikis/` | `logout` | POST | Üye | Çıkış (Django 5'te yalnızca POST) |
| `/admin/` | Django admin | — | Staff | Yönetim |

- Giriş gerektiren sayfalarda `LOGIN_URL = "accounts:login"`, girişten sonra `next` parametresine dönülür.
- Sahibi olmayan kullanıcı sahip işlemlerine erişirse **404** döner (varlık bilgisi sızdırılmaz).

### Ana sayfa sorgu parametreleri
- `?q=` → anket başlığı **veya** ürün adında arama (`icontains`, `distinct()`)
- `?kategori=phone`
- `?sirala=yeni` (varsayılan) | `?sirala=populer` (toplam oya göre)
- `?durum=acik` → yalnızca aktif anketler
- `?sayfa=2` → 12'şerli sayfalama

---

## 7. Formlar ve Doğrulama

### 7.1 Kayıt formu (`SignUpForm`)
Alanlar: `username`, `email`, `password1`, `password2`

| Durum | Hata mesajı |
|---|---|
| Kullanıcı adı alınmış | "Bu kullanıcı adı zaten kullanılıyor." |
| Kullanıcı adı formatı hatalı | "Kullanıcı adı 3–30 karakter olmalı ve yalnızca harf, rakam ve alt çizgi içermelidir." |
| E-posta kayıtlı | "Bu e-posta adresiyle zaten bir hesap var." |
| Parolalar eşleşmiyor | "Parolalar eşleşmiyor." |

Kayıt başarılı → otomatik giriş → ana sayfaya yönlendir → "Aramıza hoş geldin, @kullaniciadi! 🎉" mesajı.

### 7.2 Giriş formu
E-posta + parola. Hatalı girişte genel mesaj: "E-posta veya parola hatalı." (Hangisinin yanlış olduğu söylenmez.)

### 7.3 Anket formu (`PollForm`) + ürün formseti
```python
ProductFormSet = inlineformset_factory(
    Poll, Product,
    form=ProductForm,
    fields=["name", "price", "features", "product_url", "image_url"],
    extra=0, min_num=2, max_num=5,
    validate_min=True, validate_max=True,
    can_delete=False,
)
```
- `position` alanı formdan değil, kayıt sırasında form sırasına göre atanır.
- Formset `clean()` içinde tekrar eden ürün adları kontrol edilir.
- `features` için: boş satırlar temizlenir; 1–15 satır; her satır ≤ 120 karakter.
- `price` alanı kullanıcıdan hem `12999,90` hem `12999.90` biçiminde kabul edilmelidir (virgülü noktaya çeviren temizleme).

| Durum | Hata mesajı |
|---|---|
| < 2 ürün | "Bir ankete en az 2 ürün eklemelisin." |
| > 5 ürün | "Bir ankete en fazla 5 ürün ekleyebilirsin." |
| Fiyat boş/≤0 | "Geçerli bir fiyat gir." |
| Özellik boş | "Ürünün en az bir özelliğini yazmalısın." |
| Tekrar eden ad | "Aynı ürünü iki kez ekleyemezsin." |

### 7.4 İstemci tarafı (`poll_form.js`)
- Sayfa 2 boş ürün kartıyla açılır.
- "＋ Ürün Ekle" butonu `empty_form` şablonunu klonlar, `__prefix__` değerini indeksle değiştirir, `TOTAL_FORMS` değerini günceller.
- 5 ürüne ulaşınca ekle butonu pasifleşir ve "Maksimum 5 ürün" etiketi görünür.
- Ürün sayısı 2'deyken "Kaldır" butonları pasiftir.
- Kaldırma sonrası tüm kartların `name`/`id` indeksleri yeniden numaralandırılır.
- Ürün kartları başlığında canlı sayaç: "Ürün 2 / 5".
- İstemci doğrulaması yalnızca kullanıcı deneyimi içindir; **asıl doğrulama sunucudadır.**

---

## 8. Oylama Uç Noktası

`POST /urun/<pk>/oy/` — gövde: `value=worth` veya `value=not_worth` (form-encoded), `X-CSRFToken` başlığı ile.

### İş akışı (`polls/services.py → cast_vote(product, voter, value)`)
1. Ürünü ve anketini getir (`select_related("poll")`). Yoksa 404.
2. Anket kapalıysa → `403`, `{"error": "Bu anket oylamaya kapalı."}`
3. Oylayıcı giriş yapmış anket sahibiyse → `403`, `{"error": "Kendi anketine oy veremezsin."}`
4. Oylayıcıyı belirle: üye ise `user`, değilse `anon_id` (yoksa yeni üret, yanıtta çerezi yaz).
5. `transaction.atomic()` içinde mevcut oyu bul:
   - Yok → oluştur
   - Aynı değer → sil (geri al)
   - Farklı değer → güncelle
   - `IntegrityError` (eşzamanlı istek) → mevcut oyu yeniden okuyup tekrar uygula
6. Güncel istatistikleri hesaplayıp döndür.

### Yanıt (200)
```json
{
  "product_id": 42,
  "user_vote": "worth",
  "worth_count": 18,
  "not_worth_count": 6,
  "total_votes": 24,
  "worth_ratio": 75.0
}
```
`user_vote` değerleri: `"worth"`, `"not_worth"` veya `null`.

### İstemci (`vote.js`)
- Butonlara `data-product-id` ve `data-value` verilir.
- `fetch` ile POST; CSRF token `csrftoken` çerezinden veya şablondaki gizli input'tan okunur.
- İstek sürerken buton pasif + küçük yükleniyor animasyonu.
- Başarılı yanıtta sayılar, yüzde çubuğu ve seçili buton durumu (`aria-pressed`) güncellenir; çubuk genişliği CSS geçişiyle animasyonlu değişir.
- Hata durumunda kartın altında kısa bir uyarı (toast) gösterilir.
- **JS kapalıysa** butonlar normal `<form method="post">` olarak çalışır; view, AJAX olmayan isteklerde anket detayına geri yönlendirir.

---

## 9. Sayfa Tasarımları

### 9.1 Ortak yerleşim (`base.html`)
- **Navbar:** Sol: ⚖️ logo + "TeknoTerazi". Sağ: "Anket Oluştur" (birincil buton), giriş yapmışsa `@kullaniciadi` menüsü (Anketlerim, Çıkış); değilse "Giriş Yap" / "Kayıt Ol".
- Mobilde hamburger menü (saf JS).
- **Mesajlar:** Django messages, sağ üstte kaybolan toast'lar.
- **Footer:** Kısa açıklama, çerez notu, © yıl.
- `<meta name="viewport">`, `lang="tr"`, favicon, Open Graph temel etiketleri.

### 9.2 Ana sayfa (`/`)
```
┌───────────────────────────────────────────────────────┐
│ HERO: "Almadan önce topluluğa sor." ⚖️                  │
│ Alt metin + [Anket Oluştur]                             │
├───────────────────────────────────────────────────────┤
│ [🔍 Ara...............] [Kategori ▾] [Yeni | Popüler]   │
│ Kategori çipleri: Telefon · Laptop · Kulaklık · ...     │
├───────────────────────────────────────────────────────┤
│ ┌───────────┐ ┌───────────┐ ┌───────────┐               │
│ │ 📱 Telefon │ │ 💻 Laptop │ │ 🎧 Kulak. │   (grid)       │
│ │ Başlık     │ │ Başlık    │ │ Başlık    │               │
│ │ 3 ürün     │ │ 2 ürün    │ │ 5 ürün    │               │
│ │ Ürün adları│ │ ...       │ │ ...       │               │
│ │ 124 oy     │ │ 8 oy      │ │ 51 oy     │               │
│ │ @ahmet·2g  │ │ @ece·5s   │ │ @can·1a   │               │
│ └───────────┘ └───────────┘ └───────────┘               │
│               [‹ Önceki]  1 2 3  [Sonraki ›]            │
└───────────────────────────────────────────────────────┘
```
- Anket kartı: kategori etiketi, başlık, ürün sayısı, ilk 3 ürün adı (fazlası "+2"), en düşük–en yüksek fiyat aralığı, toplam oy, yazar ve göreli zaman (`timesince`), kapalıysa "Kapandı" rozeti.
- Boş durum: "Henüz anket yok. İlk anketi sen oluştur! 🚀"
- Sorgu optimizasyonu: `select_related("author")`, `prefetch_related("products")`, `annotate(total_votes=...)`.

### 9.3 Anket detay (`/anket/<pk>/`)
```
┌───────────────────────────────────────────────────────┐
│ ← Tüm anketler                                          │
│ [📱 Telefon]  Hangi telefonu almalıyım?                 │
│ @ahmet · 2 gün önce · 124 oy        [Kapat] [Sil]*      │
│ Açıklama metni...                                       │
├───────────────────────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
│ │ 🏆 Favori     │ │              │ │              │      │
│ │ Ürün A        │ │ Ürün B       │ │ Ürün C       │      │
│ │ ₺42.999,00    │ │ ₺38.499,00   │ │ ₺51.000,00   │      │
│ │ • 256 GB      │ │ • 128 GB     │ │ • 512 GB     │      │
│ │ • 120 Hz      │ │ • ...        │ │ • ...        │      │
│ │ Ürüne git ↗   │ │              │ │              │      │
│ │ ████████░░ 78%│ │ █████░░░ 52% │ │ ███░░░░░ 31% │      │
│ │ 👍 32   👎 9   │ │ 👍 ..  👎 .. │ │ 👍 ..  👎 .. │      │
│ │[Buna değer]   │ │[Buna değer]  │ │[Buna değer]  │      │
│ │[Buna değmez]  │ │[Buna değmez] │ │[Buna değmez] │      │
│ └──────────────┘ └──────────────┘ └──────────────┘      │
└───────────────────────────────────────────────────────┘
 * yalnızca anket sahibine görünür
```
- Masaüstünde ürünler yan yana grid (2–5 sütun, otomatik sığdırma); mobilde alt alta veya yatay kaydırmalı kartlar.
- En ucuz ürün fiyatının yanında küçük "En uygun fiyat" etiketi.
- `image_url` varsa kart üstünde görsel (`loading="lazy"`, `referrerpolicy="no-referrer"`, yüklenemezse gizlenir).
- Dış bağlantılar `rel="noopener noreferrer nofollow" target="_blank"`.
- Kullanıcının mevcut oyu sayfa yüklenirken butonlarda seçili gösterilir.
- Sayfa altında "Bu anketi paylaş" → bağlantıyı panoya kopyalayan buton (`navigator.clipboard`).

### 9.4 Anket oluşturma (`/anket/yeni/`)
- Adım göstergesi görünümü (tek sayfa): **1. Anket bilgileri** → **2. Ürünler** → **Yayınla**.
- Anket bilgileri: başlık, kategori (ikonlu seçim kartları veya select), açıklama.
- Ürün kartları: ad, fiyat (₺ önekli input, `inputmode="decimal"`), özellikler (textarea, placeholder: "Her satıra bir özellik yaz\n8 GB RAM\n120 Hz ekran"), ürün linki, görsel linki.
- Karakter sayaçları (başlık 120, açıklama 1000).
- Hatalar ilgili alanın altında kırmızı ve ikonlu gösterilir; formset genel hataları üstte gösterilir.
- Başarılı kayıt → detay sayfasına yönlendir + "Anketin yayında! 🎉 Linki paylaşarak daha çok oy toplayabilirsin."

### 9.5 Kayıt / Giriş
- Ortalanmış kart, soft gradient arka plan, parola göster/gizle butonu.
- Kayıt ve giriş sayfaları birbirine bağlantı verir.

### 9.6 Anketlerim (`/anketlerim/`)
- Kullanıcının anketleri; her birinde toplam oy, durum, "Görüntüle / Kapat-Aç / Sil" aksiyonları.
- Boş durum: "Henüz anket oluşturmadın."

### 9.7 Hata sayfaları
- 404: "Bu sayfa terazide yok ⚖️" + ana sayfa butonu. 500: sade bir özür mesajı.

---

## 10. Tasarım Sistemi

**Hedef his:** Açık (light), temiz (pure), teknoloji temalı; canlı renkler yüzeylere hafif ton olarak işlenmiş; gençlere hitap eden enerjik ama sade bir arayüz.

### 10.1 Renk paleti (CSS değişkenleri)
```css
:root {
  /* Zemin ve yüzeyler */
  --bg:            #F6F7FB;   /* açık, hafif soğuk beyaz */
  --surface:       #FFFFFF;
  --surface-tint:  #F1EDFF;   /* mor tonlu yüzey */
  --border:        #E4E7F0;

  /* Metin */
  --text:          #0E1330;
  --text-muted:    #5B6384;

  /* Canlı vurgu renkleri */
  --primary:       #6C3BFF;   /* elektrik moru */
  --primary-600:   #5A2BE6;
  --secondary:     #00B8F0;   /* neon camgöbeği */
  --accent:        #FF4FA3;   /* neon pembe (rozet, vurgu) */
  --warning:       #FFB020;

  /* Oy renkleri */
  --worth:         #12C98A;   /* Buna değer */
  --worth-tint:    #E3FAF1;
  --not-worth:     #FF4D6D;   /* Buna değmez */
  --not-worth-tint:#FFE8EC;

  /* Gradyanlar */
  --grad-brand: linear-gradient(135deg, #6C3BFF 0%, #00B8F0 100%);
  --grad-soft:  linear-gradient(135deg, rgba(108,59,255,.10), rgba(0,184,240,.10));

  /* Biçim */
  --radius-sm: 10px;
  --radius:    16px;
  --radius-lg: 24px;
  --shadow:    0 6px 24px rgba(40, 30, 120, .08);
  --shadow-hover: 0 12px 32px rgba(108, 59, 255, .18);

  --font-heading: "Space Grotesk", system-ui, sans-serif;
  --font-body:    "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
}
```

### 10.2 Arka plan dokusu ve tonlama
- `body`: `--bg` üzerine çok hafif **nokta ızgarası** (devre kartı hissi):
  `background-image: radial-gradient(rgba(108,59,255,.08) 1px, transparent 1px); background-size: 22px 22px;`
- Hero ve sayfa üstlerinde düşük opaklıkta (%15–25), bulanık (`filter: blur(80px)`) **mor ve camgöbeği renk lekeleri** (`position: absolute` pseudo-element) → "canlı renklerle üstüne ton" efekti.
- Kartlar beyaz, ince kenarlıklı; hover'da hafif yükselme ve mor tonlu gölge.

### 10.3 Tipografi
- Google Fonts: **Space Grotesk** (başlıklar, 500/700), **Inter** (gövde, 400/500/600).
- Ölçek: `h1 clamp(2rem, 5vw, 3.25rem)`, `h2 1.75rem`, `h3 1.25rem`, gövde `1rem / 1.6`.
- Fiyatlar: Space Grotesk, 700, `font-variant-numeric: tabular-nums`.

### 10.4 Bileşenler
- **Butonlar:** Birincil = `--grad-brand` dolgu, beyaz metin, `border-radius: 999px`; ikincil = beyaz zemin + mor kenarlık; hover'da hafif parlama.
- **Oy butonları:** "👍 Buna değer" (yeşil kenarlık, seçiliyken yeşil dolgu) ve "👎 Buna değmez" (kırmızı kenarlık, seçiliyken kırmızı dolgu). Renk tek başına anlam taşımaz: ikon + metin + `aria-pressed`.
- **Sonuç çubuğu:** Tek çubukta yeşil (değer) ve kırmızı (değmez) segmentler, `transition: width .5s ease`. Altında sayılar ve yüzde.
- **Rozetler:** Kategori (mor tonlu), "🏆 Topluluğun Favorisi" (pembe-mor gradyan), "Kapandı" (gri), "En uygun fiyat" (camgöbeği tonlu).
- **Toast:** Sağ üst, 4 sn sonra kaybolur.
- **İkonlar:** Emoji veya satır içi SVG (harici ikon kütüphanesi yok).

### 10.5 Duyarlılık ve erişilebilirlik
- Mobil öncelikli; kırılım noktaları: 640px, 960px, 1200px. Maksimum içerik genişliği 1200px.
- Tüm etkileşimli öğelerde görünür `:focus-visible` halkası (mor).
- Metin kontrastı WCAG AA.
- `prefers-reduced-motion` durumunda animasyonlar kapatılır.
- Form alanlarında `<label>` zorunlu.

### 10.6 Mikro etkileşimler
- Oy verildiğinde butonda kısa "pop" animasyonu.
- Kartlarda hover yükselmesi, çubuk genişliğinde yumuşak geçiş.
- Abartı yok: sayfa hızlı ve sade kalmalı.

---

## 11. Yapılandırma

### 11.1 `.env.example`
```
SECRET_KEY=degistir-beni
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.vercel.app
CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://*.vercel.app

# Supabase — uygulama çalışırken (transaction pooler, port 6543)
DATABASE_URL=postgresql://postgres.<PROJECT_REF>:<PASSWORD>@aws-0-<REGION>.pooler.supabase.com:6543/postgres

# Supabase — migration için (session pooler 5432 veya direct connection)
DIRECT_DATABASE_URL=postgresql://postgres.<PROJECT_REF>:<PASSWORD>@aws-0-<REGION>.pooler.supabase.com:5432/postgres
```
> Gerçek bağlantı dizelerini Supabase panelindeki **Connect** ekranından al.

### 11.2 `settings.py` önemli noktalar
```python
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")

AUTH_USER_MODEL = "accounts.CustomUser"
LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_TZ = True

# Migration komutları için DIRECT_DATABASE_URL'i tercih et
_db_url = os.getenv("DIRECT_DATABASE_URL") if os.getenv("USE_DIRECT_DB") == "1" else os.getenv("DATABASE_URL")
DATABASES = {
    "default": dj_database_url.parse(_db_url, conn_max_age=0, ssl_require=not DEBUG)
}
# Supabase transaction pooler (PgBouncer) ile uyumluluk
DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"] = True

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # ... Django varsayılanları
]

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "polls:home"
LOGOUT_REDIRECT_URL = "polls:home"

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600  # MVP'de düşük tut, sonra artır
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
```
- Yerel geliştirme için Supabase yerine SQLite'a düşmek **istenmez**; kısmi indeks/kısıt davranışı aynı kalsın diye yerelde de Supabase (veya yerel Postgres) kullanılır.
- Migration: `USE_DIRECT_DB=1 python manage.py migrate`

### 11.3 Şablon filtreleri (`tt_filters.py`)
- `tl`: `Decimal("42999.9")` → `₺42.999,90`
- `percent`: `75.0` → `%75`
- `category_icon`: kategori koduna göre emoji (📱 💻 📟 🎧 ⌚ 🎮 📷 🖥️ 🧩 ✨)

---

## 12. Fazlar

### Faz 0 — Kurulum ve Ortam
**Amaç:** Çalışan boş bir Django projesi, Supabase bağlantısı ve Git deposu.

- [x] Sanal ortam oluştur (`python -m venv .venv`), `requirements.txt` yaz ve kur. (Python 3.12 ile, Vercel uyumluluğu için.)
- [x] `django-admin startproject config .` ile projeyi oluştur.
- [x] `accounts` ve `polls` uygulamalarını oluştur, `INSTALLED_APPS`'e ekle.
- [x] `.env.example`, `.gitignore` (`.venv`, `.env`, `__pycache__`, `*.pyc`) oluştur.
- [x] `settings.py`'yi Bölüm 11.2'ye göre düzenle.
- [x] `templates/` ve `static/` klasörlerini oluştur, ayarlara bağla.
- [x] Supabase projesini oluştur, bağlantı dizelerini `.env`'e yaz. Proje adı: `TeknoTerazi`, bölge: eu-central-1 (Frankfurt). ⚠️ Not: Şifrede `#` karakteri geçtiği için bağlantı dizesinde URL-encode edilmesi gerekti (`#` → `%23`); ilk denemede bu atlanınca "password authentication failed" hatası alındı.
- [x] `README.md`: kurulum ve çalıştırma adımları.
- [x] **Erken Vercel doğrulaması:** Tamamlandı (2026-09-16). Vercel'e deploy edildi (`https://teknoterazi.vercel.app`, proje: `ferhan-oezkan/teknoterazi`), zero-config Django algılandı, `/admin/` 302 (login yönlendirmesi) döndürerek uygulamanın gerçekten çalıştığını doğruladı. Detaylar ve öğrenilenler için bkz. Faz 8 notu.

**Kabul kriterleri:**
- [x] `python manage.py check` hata vermez.
- [x] Uygulama Supabase'e bağlanabiliyor (`DATABASE_URL` ve `DIRECT_DATABASE_URL` gerçek bir sorguyla doğrulandı: `SELECT version()` → PostgreSQL 17.6).
- [x] Boş proje Vercel'de gerçek bir URL üzerinden açılıyor (erken doğrulama başarılı).
- [x] Henüz `migrate` çalıştırılmadı (özel kullanıcı modeli Faz 1'de gelecek).

---

### Faz 1 — Veri Modeli ve Admin
**Amaç:** Tüm modeller, kısıtlar ve yönetim paneli.

- [x] `CustomUser` modelini oluştur (Bölüm 4.1), `AUTH_USER_MODEL` ayarla.
- [x] `Poll`, `Product`, `Vote` modellerini oluştur (Bölüm 4.2–4.4), `Category` ve `VoteValue` için `TextChoices`/`IntegerChoices` kullan.
- [x] `Product.features_list` property'sini yaz.
- [x] `makemigrations` ve `USE_DIRECT_DB=1 python manage.py migrate`. (Supabase'e uygulandı.)
- [x] Admin: `CustomUserAdmin`; `PollAdmin` (Product inline, liste filtreleri: kategori, aktiflik, tarih; arama: başlık, yazar); `VoteAdmin` (salt okunur liste).
- [x] `createsuperuser` ile admin hesabı oluştur. (`admin@gmail.com` / kullanıcı adı `admin` — şifre kullanıcı tarafından belirlendi.)
- [x] Model testleri: kısıtların çalıştığını doğrula (aynı kullanıcı aynı ürüne iki oy veremez; hem user hem anon_id boş olamaz). `polls/tests/test_models.py` + `accounts/tests.py`, 8/8 test yeşil.

**Kabul kriterleri:**
- [x] Admin panelinden anket + ürün eklenebiliyor. (Gerçek giriş + formset submit ile uçtan uca doğrulandı, ardından test verisi silindi.)
- [x] Kısıt testleri geçiyor. (8/8, `USE_DIRECT_DB=1 python manage.py test --keepdb`.)

---

### Faz 2 — Kimlik Doğrulama
**Amaç:** Kayıt, giriş, çıkış.

- [x] `SignUpForm` (Bölüm 7.1) ve e-posta ile giriş formu.
- [x] Kayıt, giriş, çıkış view'ları ve URL'leri (`accounts` namespace).
- [x] `base.html`, navbar, mesaj bileşeni (ham ama işlevsel stil yeterli; tasarım Faz 6'da cilalanır). Navbar'ın referans verdiği `poll_create`/`my_polls` için de küçük stub view+template eklendi (NoReverseMatch olmasın diye); gerçek içerikleri Faz 3/4'te dolacak.
- [x] Giriş yapmış kullanıcı kayıt/giriş sayfasına gelirse ana sayfaya yönlendir.
- [x] Çıkış POST formu ile yapılır (GET → 405).
- [x] Testler: başarılı kayıt, tekrar eden e-posta/kullanıcı adı, hatalı giriş, çıkış. 19/19 yeşil.

**Kabul kriterleri:**
- [x] Kullanıcı kayıt olup otomatik giriş yapıyor; navbar'da `@kullaniciadi` görünüyor.
- [x] E-posta hiçbir sayfada görünmüyor.

---

### Faz 3 — Anket Oluşturma
**Amaç:** Üyelerin 2–5 ürünlü anket oluşturabilmesi.

- [x] `PollForm`, `ProductForm`, `ProductFormSet` (Bölüm 7.3).
- [x] `poll_create` view'ı (`@login_required`, `transaction.atomic`, `position` ataması).
- [x] `poll_create.html` şablonu (Bölüm 9.4), `empty_form` şablonu `<template>` etiketi içinde.
- [x] `poll_form.js` (Bölüm 7.4).
- [x] Başarı mesajı ve detay sayfasına yönlendirme (detay sayfası bu fazda basit bir iskelet).
- [x] Testler: 1 ürünle reddedilir, 6 ürünle reddedilir, fiyatsız/özelliksiz ürün reddedilir, tekrar eden ad reddedilir, 2 ve 5 ürünle başarılı, misafir giriş sayfasına yönlendirilir. 9/9 yeşil.

**Kabul kriterleri:**
- [x] Tarayıcıda ürün ekleme/çıkarma sorunsuz çalışıyor; sınırlar hem istemci hem sunucu tarafında uygulanıyor. (Gerçek HTTP üzerinden virgüllü/noktalı fiyat, opsiyonel link alanları ve `position` ataması uçtan uca doğrulandı.)
- [x] Hatalı gönderimde girilen veriler kaybolmuyor.

---

### Faz 4 — Listeleme ve Detay
**Amaç:** Herkesin anketleri görebilmesi.

- [x] `home` view'ı: arama, kategori filtresi, sıralama, durum filtresi, 12'li sayfalama (Bölüm 6).
- [x] `poll_card.html`, `pagination.html` parçaları.
- [x] `poll_detail` view'ı: ürünler + istatistikler tek sorguda (`services.get_poll_with_stats`), favori ürün hesaplaması (Bölüm 5.4).
- [x] `product_card.html` (oy butonları bu fazda görünür ama pasif).
- [x] `my_polls`, `poll_toggle_active`, `poll_delete` view'ları (sahiplik kontrolü → 404).
- [x] `tt_filters.py` şablon filtreleri.
- [x] 404/500 şablonları. (500.html bilinçli olarak `base.html`'i extend etmiyor — Django'nun 500 handler'ı RequestContext/context processor çalıştırmadığı için tamamen bağımsız/sade tutuldu.)
- [x] Testler: misafir listeyi ve detayı görebiliyor; arama ve filtre doğru sonuç veriyor; başkası silemiyor/kapatamıyor (404); sayfalama çalışıyor. 20 yeni test, toplam 52/52 yeşil.

**Kabul kriterleri:**
- [x] Ana sayfa ve detay sayfası üye olmadan açılıyor.
- [x] Ana sayfa sorgu sayısı, anket sayısından bağımsız ve sabit (`CaptureQueriesContext` ile 3 anket / 15 anket senaryoları karşılaştırılarak doğrulandı — sorgu sayısı birebir aynı).

---

### Faz 5 — Oylama Sistemi
**Amaç:** Üyeli ve üyesiz oylama.

- [x] `polls/voter.py`: `get_voter(request)` → `(user, anon_id, is_new_anon)`; `attach_voter_cookie(response, anon_id)`.
- [x] `services.cast_vote()` (Bölüm 8, toggle ve eşzamanlılık dahil).
- [x] `vote` view'ı: `@require_POST`, JSON ve JSON olmayan istek desteği.
- [x] Detay sayfasında kullanıcının mevcut oylarını tek sorguda getirip butonlara yansıt.
- [x] `vote.js` (Bölüm 8, İstemci).
- [x] Testler:
  - Misafir oy verir → çerez oluşur → aynı çerezle ikinci kez aynı oy → oy silinir.
  - Üye oyunu `worth`'ten `not_worth`'e değiştirir → tek kayıt kalır.
  - Kapalı ankete oy → 403.
  - Anket sahibi kendi anketine oy → 403.
  - Oynanmış/geçersiz imzalı çerez → yeni kimlik atanır, hata oluşmaz.
  - GET isteği → 405.
  - CSRF token olmadan istek reddedilir (`Client(enforce_csrf_checks=True)`).
  - 11 yeni test, toplam 63/63 yeşil.

**Kabul kriterleri:**
- [x] Sayfa yenilenmeden oy verilebiliyor, sayılar ve çubuklar anında güncelleniyor. (Gerçek HTTP üzerinden fetch akışı doğrulandı.)
- [x] JS kapalıyken de oy verilebiliyor. (Plain `<form method="post">` fallback, view AJAX olmayan isteklerde detay sayfasına yönlendiriyor.)
- [x] Sayfa yenilendiğinde verilen oy seçili görünüyor. (`aria-pressed` gerçek sunucu üzerinden doğrulandı.)

---

### Faz 6 — Tasarım Sistemi ve Arayüz Cilası
**Amaç:** Bölüm 10'daki görsel kimliği tüm sayfalara uygulamak.

- [x] `main.css`: değişkenler, reset, tipografi, düzen yardımcıları, bileşenler (buton, kart, rozet, form, toast, çubuk, sayfalama).
- [x] Arka plan nokta ızgarası ve renk lekeleri (Bölüm 10.2).
- [x] Logo (`logo.svg`: terazi ikonu + gradyan) ve favicon (`favicon.svg`).
- [x] Hero bölümü, kategori çipleri, boş durumlar.
- [x] Mobil navbar (hamburger) — `static/js/nav.js`.
- [x] Şifre göster/gizle (`static/js/password_toggle.js`), karakter sayaçları (Faz 3'te vardı), panoya kopyala butonu (Faz 4/5'te vardı).
- [x] Erişilebilirlik kontrolleri (Bölüm 10.5): `:focus-visible` halkası, `prefers-reduced-motion`, tüm alanlarda `<label>` zaten mevcuttu.
- [x] 375px, 768px ve 1280px genişliklerde tüm sayfalar Chrome üzerinden gerçek ekran görüntüleriyle gözden geçirildi (ana sayfa, detay, kayıt, anket oluşturma, anketlerim).

**Kabul kriterleri:**
- [x] Tüm sayfalar tutarlı görünüyor; yatay taşma yok. (375/768/1280px'te gerçek tarayıcıda doğrulandı.)
- [x] Klavye ile tüm akışlar (kayıt, anket oluşturma, oylama) tamamlanabiliyor. (Oylama: Tab ile odaklanıp Enter ile oy verme, sayfa yenilenmeden sonuç güncellendi — izole test anketiyle doğrulandı.)
- [x] Harici CSS/JS kütüphanesi yok (yalnızca Google Fonts).

**Faz 6'da bulunan ve düzeltilen hata:** `CustomUser.username`/`email` alanlarında `verbose_name` yoktu, bu yüzden kayıt formu "Username"/"Email" gibi İngilizce etiketler gösteriyordu (dil kuralına aykırı). Model alanlarına Türkçe `verbose_name` eklenip küçük bir migration (`accounts/migrations/0002_...`) ile düzeltildi. Ayrıca `PollForm`'da kategori seçiminin varsayılan "---------" placeholder'ı "Kategori seç" ile değiştirildi.

---

### Faz 7 — Güvenlik, Testler ve Demo Verisi
**Amaç:** Yayına hazır sağlamlık.

- [x] Tüm POST formlarında `{% csrf_token %}` olduğunu doğrula. (8 form, hepsinde var.)
- [x] Kullanıcı içeriğinde `|safe` kullanılmadığını doğrula (otomatik kaçış açık). (Hiç kullanılmamış.)
- [x] URL alanlarında yalnızca `http/https` şemasına izin ver (`javascript:` engellenir). (Faz 1'den beri `URLValidator(schemes=[...])`.)
- [x] Üretim güvenlik ayarları (Bölüm 11.2), `python manage.py check --deploy` uyarılarını gider. (Yalnızca 2 opsiyonel HSTS subdomain/preload uyarısı kaldı, bilinçli olarak MVP'de açılmadı — bkz. not.)
- [x] Basit kötüye kullanım önlemi: aynı oylayıcı 1 dakikada 60'tan fazla oy isteği atarsa 429 döndür (DB tabanlı sayım; bellek içi önbellek sunucusuzda güvenilir değildir). `VoteAttempt` modeli + `services.enforce_vote_rate_limit`.
- [x] `seed_demo` yönetim komutu: 3 demo kullanıcı, farklı kategorilerde 8–10 anket, rastgele oylar. `--flush` bayrağı ile yalnızca demo verisini temizler. (9 anket, 9 farklı kategori.)
- [x] Test kapsamını gözden geçir; tüm testler yeşil. (68/68.)
- [x] `README.md`'yi güncelle.

**Kabul kriterleri:**
- [x] `USE_DIRECT_DB=1 python manage.py test --keepdb` tamamen geçiyor. (68/68.)
- [x] `check --deploy` kritik uyarı vermiyor. (Yalnızca 2 opsiyonel/isteğe bağlı HSTS uyarısı — preload geri dönüşü zor olduğu için MVP'de bilinçli olarak atlandı.)
- [x] `python manage.py seed_demo` ile uygulama dolu görünüyor. (Gerçek Supabase veritabanında doğrulandı.)

---

### Faz 8 — Vercel'e Dağıtım
**Amaç:** Uygulamanın herkese açık bir URL'de çalışması.

> ✅ **Faz 0'da doğrulandı (2026-09-16):** Vercel, Django'yu **zero-config** olarak otomatik algılıyor (`vercel link` çıktısında "Detected Django" görülüyor, build log'unda "Django 5.2.17 detected" ve otomatik `collectstatic` çalışıyor). Ayrıca **özel bir `vercel.json` `builds`/`routes` yapılandırmasına gerek yok** — hatta `"/(.*)" → "/config/wsgi.py"` gibi elle yazılmış bir `rewrite` eklemek routing'i bozdu (build log'unda "Internal rewrites in backend framework projects now route requests using the rewritten destination path" uyarısı çıktı ve `/admin/` gibi gerçek route'lar bile 404 döndü). **`vercel.json` hiç olmadan** deploy edilince `/admin/` doğru şekilde 302 (login'e yönlendirme) döndürdü. Bu yüzden bu fazda `vercel.json` eklenmeyecek; gerekirse (ör. `maxDuration`) yalnızca ihtiyaç çıktığında, `functions` anahtarıyla `config/wsgi.py` dosyası hedeflenerek eklenir.

`config/wsgi.py` sonuna (bu satır zaten Faz 0'da eklendi):
```python
app = application  # Vercel giriş noktası
```

**Statik dosyalar:** ✅ Faz 0 doğrulamasında Vercel'in kendi build adımı `collectstatic`'i otomatik çalıştırdığı görüldü (build log: "Running collectstatic..."). Bu yüzden yerelde `collectstatic` çalıştırıp commit'lemeye gerek yok; `staticfiles/` `.gitignore`'da kalabilir. WhiteNoise bu dosyaları fonksiyon içinden sunar.

**Görevler:**
- [x] `wsgi.py` düzenlemesi (`app = application` — Faz 0'da yapıldı). `vercel.json` eklenmeyecek (bkz. yukarıdaki not).
- [x] Vercel projesi oluşturuldu (`ferhan-oezkan/teknoterazi`, Faz 0'da erken doğrulama için). GitHub deposu henüz bağlanmadı — bu fazda bağla (otomatik deploy için).
- [ ] Ortam değişkenlerini Vercel paneline **gerçek** değerlerle gir/güncelle: `SECRET_KEY` (yeni ve güçlü), `DEBUG=False`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` (gerçek domain ile), `DATABASE_URL` (6543 pooler). ⚠️ Faz 0'da yalnızca doğrulama amaçlı **placeholder** değerler girildi, bunlar üretime geçmeden önce gerçek değerlerle değiştirilmeli.
- [ ] Migration'ları **yerelden** üretim veritabanına uygula: `USE_DIRECT_DB=1 python manage.py migrate`. (Dağıtım sırasında migration çalıştırılmaz.)
- [ ] **Supabase güvenliği:** `public` şemasındaki tüm tablolarda RLS'i aç. Django, tabloların sahibi olan `postgres` rolüyle bağlandığı için etkilenmez; ancak Supabase REST API'si (anon/authenticated anahtarları) üzerinden erişim kapanır. Supabase SQL Editor'da çalıştır (her yeni migration'dan sonra tekrarla):
  ```sql
  DO $$
  DECLARE r record;
  BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
      EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', r.tablename);
    END LOOP;
  END $$;
  ```
  Ardından Supabase panelindeki **Security Advisor** uyarılarını kontrol et.
- [ ] Üretimde duman testi: kayıt → anket oluştur → gizli pencerede oy ver → sonuçları kontrol et → admin paneline gir.

**Kabul kriterleri:**
- Uygulama `*.vercel.app` adresinde HTTPS ile çalışıyor.
- Statik dosyalar (CSS/JS/logo) yükleniyor.
- Üretimde `DEBUG=False` ve hata sayfaları özel şablonlarla görünüyor.
- Supabase Security Advisor'da RLS kapalı tablo uyarısı yok.

---

### Faz 9 — MVP Sonrası (Backlog — birlikte tartışılacak)
Önceliklendirme için aday fikirler:

**Topluluk ve etkileşim**
- Ürün/anket yorumları, "neden buna değer?" kısa gerekçe notu
- Anket şikayet etme ve moderasyon
- Oy verdikten sonra sonuçları gösterme seçeneği (önyargıyı azaltmak için)
- Trend anketler, "bugün en çok oy alanlar"

**Hesap**
- E-posta doğrulama ve şifre sıfırlama (SMTP / transactional e-posta servisi)
- Google ile giriş
- Profil sayfası ve kullanıcı adı değiştirme
- Girişte, anonim oyları kullanıcı hesabına birleştirme

**Anket**
- Ürün görsellerini Supabase Storage'a yükleme
- Sınırlı süreli anketler (bitiş tarihi)
- Oy gelmeden önce anket düzenleme
- Yapılandırılmış özellik alanları (RAM, depolama, ekran…) ve yan yana karşılaştırma tablosu
- Bütçe ve kullanım amacı etiketleri (oyun, okul, iş)

**Kalite ve güvenlik**
- Cloudflare Turnstile / hCaptcha ile bot koruması
- IP-hash tabanlı ek oy tekrarı kontrolü
- Hata izleme (Sentry vb.), analitik

**Deneyim**
- Karanlık mod
- Paylaşım için dinamik Open Graph görseli
- PWA (ana ekrana ekleme)
- Çoklu dil

---

## 13. Açık Sorular / Karar Günlüğü

| # | Konu | MVP kararı | Alternatif |
|---|---|---|---|
| 1 | Auth kaynağı | Django auth + Supabase Postgres | Supabase Auth |
| 2 | Giriş kimliği | E-posta + parola | Kullanıcı adı veya e-posta |
| 3 | Anket sahibi kendi anketine oy verebilir mi? | Hayır (giriş yapmışken) | Evet |
| 4 | Sonuçlar oy vermeden görünür mü? | Evet | Oy verdikten sonra göster |
| 5 | Anket düzenleme | Yok (kapat/sil var) | Oy gelene kadar düzenlenebilir |
| 6 | Üyesiz oy tekrarını önleme | İmzalı çerez (UUID) | + IP hash, CAPTCHA |
| 7 | Para birimi | Yalnızca TRY | Çoklu para birimi |
| 8 | Ürün özellikleri formatı | Serbest metin, satır başına bir özellik | Yapılandırılmış anahtar–değer |
| 9 | Ürün görseli | Opsiyonel harici URL | Supabase Storage yükleme |
| 10 | Favori rozeti eşiği | En az 3 oy | Ayarlanabilir |
| 11 | Sahibi anonim olarak kendi anketine oy verebilir mi? (çıkış yapıp/farklı oturum) | Evet, engellenmiyor (bilinen MVP sınırlaması — anon_id ile author arasında ilişki kurulmuyor) | Session/IP bazlı ek kontrol (Faz 9) |
| 12 | Barındırma platformu doğrulaması | Vercel doğrulandı (2026-09-16): zero-config Django desteği çalışıyor, `https://teknoterazi.vercel.app` canlı | Sorun çıksaydı Railway/Render'a geçilecekti — gerek kalmadı |
| 13 | Test veritabanı yönetimi | `python manage.py test` her zaman `--keepdb` ile çalıştırılır (bkz. Faz 1, 2026-09-16). Bu projede Supabase yalnızca pooler (Supavisor) bağlantısı sunuyor — gerçek "direct connection" IPv6-only ve bu ağda çözülmüyor. Supavisor arka planda bağlantı tuttuğu için normal `DROP DATABASE` teardown'ı güvenilmez şekilde "being accessed by other users" hatası veriyor ve bir sonraki çalıştırmayı da tıkıyor. `--keepdb` bu adımı tamamen atlar. | IPv6 destekleyen bir ağdan gerçek direct connection kullanmak (mümkün olursa) |
| 14 | "1–15 satır, her satır ≤120 karakter" sınırları aşıldığında hata mesajı | Doküman yalnızca "özellik boş" mesajını tanımlamış; sınır aşımları için "En fazla 15 özellik ekleyebilirsin." ve "Her özellik satırı en fazla 120 karakter olabilir." eklendi (Faz 3, 2026-09-17) | — |

> Yeni kararlar bu tabloya eklenmelidir.

---

## 14. Tanım: "Bitti" (Definition of Done)
Bir özellik ancak şu koşullarda tamamlanmış sayılır:
1. Kabul kriterleri karşılandı.
2. İlgili testler yazıldı ve geçiyor.
3. Arayüz metinleri Türkçe ve tutarlı.
4. Mobil görünüm kontrol edildi.
5. Bu dosyadaki ilgili kutucuklar işaretlendi ve "İlerleme Durumu" tablosu güncellendi.
6. Commit atıldı.
