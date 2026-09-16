# TeknoTerazi

Teknolojik ürün satın alırken kararsız kalan kullanıcıların, aday ürünleri topluluğa sorarak karar vermesini kolaylaştıran bir web uygulaması.

Teknik şartname ve faz planı için bkz. [`docs/PROJE_PLANI.md`](docs/PROJE_PLANI.md).

## Kurulum

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` dosyasını gerçek `SECRET_KEY` ve Supabase bağlantı dizeleriyle doldur (Supabase panelindeki **Connect** ekranından alınır).

## Çalıştırma

```bash
source .venv/bin/activate
python manage.py check
python manage.py runserver
```

Migration'lar için `DIRECT_DATABASE_URL` (session pooler / direct connection) kullanılır:

```bash
USE_DIRECT_DB=1 python manage.py migrate
```

## Testler

```bash
USE_DIRECT_DB=1 python manage.py test --keepdb
```

`--keepdb` şart: Supabase'in yalnızca pooler bağlantısı erişilebilir olduğu için normal test veritabanı silme adımı güvenilir çalışmıyor (bkz. `CLAUDE.md`).

## Demo veri

Uygulamayı boş görmemek için 3 demo kullanıcı, 9 farklı kategoride anket ve rastgele oylarla doldurabilirsin:

```bash
python manage.py seed_demo
```

Yalnızca demo verisini (gerçek kullanıcı/anketlere dokunmadan) temizlemek için:

```bash
python manage.py seed_demo --flush
```

## Özellikler

- E-posta ile kayıt/giriş, üyeli ve üyesiz (anonim çerezli) oylama
- Anket oluşturma (2–5 ürün), arama/kategori/durum filtreleri, sıralama ve sayfalama
- Anket detayında canlı oy sonuçları, "Topluluğun Favorisi" ve "En uygun fiyat" rozetleri
- Sayfa yenilenmeden oylama (AJAX), JS kapalıyken de çalışan form fallback'i
- Aynı oylayıcıdan dakikada 60'tan fazla oy isteğine karşı basit hız sınırlama

## Üretime dağıtım öncesi

```bash
DEBUG=False python manage.py check --deploy
```

kritik bir uyarı vermemeli (yalnızca HSTS subdomain/preload gibi opsiyonel sertleştirme uyarıları beklenir, bkz. `docs/PROJE_PLANI.md` Bölüm 11.2).
