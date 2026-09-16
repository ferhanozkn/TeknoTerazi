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
