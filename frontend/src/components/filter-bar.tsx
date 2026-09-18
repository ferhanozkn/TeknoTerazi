import { BUDGET_TIER_LABELS, CATEGORY_LABELS, USAGE_PURPOSE_LABELS } from "@/lib/types";

export function FilterBar() {
  return (
    <form className="flex flex-wrap items-center gap-3 rounded-2xl border border-border bg-surface p-4">
      <input
        type="search"
        name="q"
        placeholder="🔍 Ara..."
        className="min-w-40 flex-1 rounded-full border border-border bg-bg px-4 py-2 text-sm outline-none focus:border-primary"
      />
      <select name="kategori" className="rounded-full border border-border bg-bg px-3 py-2 text-sm">
        <option value="">Tüm kategoriler</option>
        {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
      <select name="amac" className="rounded-full border border-border bg-bg px-3 py-2 text-sm">
        <option value="">Tüm kullanım amaçları</option>
        {Object.entries(USAGE_PURPOSE_LABELS).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
      <select name="butce" className="rounded-full border border-border bg-bg px-3 py-2 text-sm">
        <option value="">Tüm bütçeler</option>
        {Object.entries(BUDGET_TIER_LABELS).map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
      <select name="sirala" className="rounded-full border border-border bg-bg px-3 py-2 text-sm">
        <option value="yeni">Yeni</option>
        <option value="populer">Popüler</option>
      </select>
      <label className="flex items-center gap-2 text-sm text-text-muted">
        <input type="checkbox" name="durum" value="acik" className="accent-primary" />
        Yalnızca açık anketler
      </label>
      <button
        type="submit"
        className="rounded-full bg-primary px-4 py-2 text-sm font-medium text-white transition hover:bg-primary-600"
      >
        Filtrele
      </button>
    </form>
  );
}
