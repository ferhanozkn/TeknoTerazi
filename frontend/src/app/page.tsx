import Link from "next/link";
import { FilterBar } from "@/components/filter-bar";
import { PollCard } from "@/components/poll-card";
import { mockPolls } from "@/lib/mock-data";

const CATEGORY_CHIPS = [
  { value: "", label: "Tümü" },
  { value: "telefon", label: "📱 Telefon" },
  { value: "laptop", label: "💻 Laptop" },
  { value: "kulaklik", label: "🎧 Kulaklık" },
  { value: "beyaz_esya", label: "🧺 Beyaz Eşya" },
];

export default function Home() {
  const trending = mockPolls.filter((poll) => poll.todayVotes > 0);

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-10 px-4 py-10">
      <section
        className="rounded-3xl px-8 py-14 text-white"
        style={{ background: "var(--gradient-brand)" }}
      >
        <h1 className="font-heading max-w-xl text-4xl font-semibold leading-tight sm:text-5xl">
          Almadan önce topluluğa sor. ⚖️
        </h1>
        <p className="mt-4 max-w-lg text-white/90">
          Aday ürünleri topluluğa sor, oylarla en değerlisini bul.
        </p>
        <Link
          href="/anket-olustur"
          className="mt-6 inline-block rounded-full bg-white px-6 py-3 font-medium text-primary transition hover:bg-white/90"
        >
          Anket Oluştur
        </Link>
      </section>

      {trending.length > 0 && (
        <section className="flex flex-col gap-4">
          <h2 className="font-heading text-xl font-semibold">🔥 Bugün trend olanlar</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {trending.map((poll) => (
              <PollCard key={poll.id} poll={poll} />
            ))}
          </div>
        </section>
      )}

      <div className="flex flex-wrap gap-2">
        {CATEGORY_CHIPS.map((chip) => (
          <button
            key={chip.value}
            type="button"
            className="rounded-full border border-border px-4 py-1.5 text-sm text-text-muted transition hover:border-primary hover:text-primary first:border-primary first:text-primary"
          >
            {chip.label}
          </button>
        ))}
      </div>

      <FilterBar />

      {mockPolls.length > 0 ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {mockPolls.map((poll) => (
            <PollCard key={poll.id} poll={poll} />
          ))}
        </div>
      ) : (
        <p className="text-center text-text-muted">
          Henüz anket yok. İlk anketi sen oluştur! 🚀
        </p>
      )}
    </div>
  );
}
