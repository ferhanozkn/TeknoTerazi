import Link from "next/link";
import { FilterBar } from "@/components/filter-bar";
import { Pagination } from "@/components/pagination";
import { PollCard } from "@/components/poll-card";
import { fetchPollList, fetchTrendingPolls } from "@/lib/api";
import { CATEGORY_LABELS, type PollCategory } from "@/lib/types";

const CATEGORY_CHIPS: { value: PollCategory | ""; label: string }[] = [
  { value: "", label: "Tümü" },
  ...(Object.entries(CATEGORY_LABELS) as [PollCategory, string][]).map(([value, label]) => ({
    value,
    label,
  })),
];

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | undefined>>;
}) {
  const params = await searchParams;
  const filters = {
    q: params.q,
    kategori: params.kategori,
    amac: params.amac,
    butce: params.butce,
    durum: params.durum,
    sirala: params.sirala,
    sayfa: params.sayfa,
  };

  const [pollList, trending] = await Promise.all([fetchPollList(filters), fetchTrendingPolls()]);

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
          <Link
            key={chip.value}
            href={chip.value ? `?kategori=${chip.value}` : "/"}
            className={`rounded-full border px-4 py-1.5 text-sm transition ${
              (params.kategori ?? "") === chip.value
                ? "border-primary text-primary"
                : "border-border text-text-muted hover:border-primary hover:text-primary"
            }`}
          >
            {chip.label}
          </Link>
        ))}
      </div>

      <FilterBar
        query={params.q}
        category={params.kategori}
        usagePurpose={params.amac}
        budgetTier={params.butce}
        sort={params.sirala}
        onlyOpen={params.durum === "acik"}
      />

      {pollList.results.length > 0 ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {pollList.results.map((poll) => (
              <PollCard key={poll.id} poll={poll} />
            ))}
          </div>
          <Pagination
            currentPage={pollList.currentPage}
            numPages={pollList.numPages}
            hasNext={pollList.hasNext}
            hasPrevious={pollList.hasPrevious}
            querystringPrefix={pollList.querystringPrefix}
          />
        </>
      ) : (
        <p className="text-center text-text-muted">
          Henüz anket yok. İlk anketi sen oluştur! 🚀
        </p>
      )}
    </div>
  );
}
