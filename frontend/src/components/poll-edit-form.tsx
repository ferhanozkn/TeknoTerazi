"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import type { PollEditData } from "@/lib/api";
import { BUDGET_TIER_LABELS, CATEGORY_LABELS, USAGE_PURPOSE_LABELS } from "@/lib/types";
import { updatePoll, PollEditError, type EditProductInput } from "@/lib/poll-client";

function toDatetimeLocal(iso: string | null): string {
  if (!iso) return "";
  return iso.slice(0, 16);
}

export function PollEditForm({ poll }: { poll: PollEditData }) {
  const router = useRouter();
  const [title, setTitle] = useState(poll.title);
  const [category, setCategory] = useState<string>(poll.category);
  const [description, setDescription] = useState(poll.description);
  const [usagePurpose, setUsagePurpose] = useState(poll.usagePurpose ?? "");
  const [budgetTier, setBudgetTier] = useState(poll.budgetTier ?? "");
  const [hideResults, setHideResults] = useState(poll.hideResultsUntilVote);
  const [expiresAt, setExpiresAt] = useState(toDatetimeLocal(poll.expiresAt));
  const [products, setProducts] = useState<EditProductInput[]>(
    poll.products.map((p) => ({
      id: p.id,
      name: p.name,
      price: String(p.price),
      features: p.features,
      productUrl: p.productUrl,
      imageUrl: p.imageUrl,
      attributes: p.attributes,
      imageFile: null,
    })),
  );

  const [pollErrors, setPollErrors] = useState<Record<string, string[]>>({});
  const [productErrors, setProductErrors] = useState<Record<number, Record<string, string[]>>>({});
  const [nonFormErrors, setNonFormErrors] = useState<string[]>([]);
  const [pending, setPending] = useState(false);

  function updateProduct(id: number, patch: Partial<EditProductInput>) {
    setProducts((current) => current.map((p) => (p.id === id ? { ...p, ...patch } : p)));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setPollErrors({});
    setProductErrors({});
    setNonFormErrors([]);
    try {
      await updatePoll(poll.id, {
        title,
        category,
        description,
        usagePurpose,
        budgetTier,
        hideResultsUntilVote: hideResults,
        expiresAt,
        products,
      });
      router.push(`/anket/${poll.id}`);
      router.refresh();
    } catch (err) {
      if (err instanceof PollEditError) {
        setPollErrors(err.errors.pollErrors);
        setProductErrors(err.errors.productErrors);
        const uploadErrors = Object.values(err.errors.productUploadErrors);
        setNonFormErrors([...err.errors.nonFormErrors, ...uploadErrors]);
      } else {
        setNonFormErrors(["Anket güncellenemedi."]);
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      <label className="flex flex-col gap-1 text-sm">
        Anket başlığı
        <input
          required
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="rounded-full border border-border bg-surface px-4 py-2 text-sm outline-none focus:border-primary"
        />
        <FieldErrors errors={pollErrors.title} />
      </label>

      <label className="flex flex-col gap-1 text-sm">
        Kategori
        <select
          required
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="rounded-full border border-border bg-surface px-4 py-2 text-sm"
        >
          {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <FieldErrors errors={pollErrors.category} />
      </label>

      <label className="flex flex-col gap-1 text-sm">
        Açıklama (opsiyonel)
        <textarea
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="rounded-2xl border border-border bg-surface px-4 py-2 text-sm outline-none focus:border-primary"
        />
        <FieldErrors errors={pollErrors.description} />
      </label>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm">
          Kullanım amacı (opsiyonel)
          <select
            value={usagePurpose}
            onChange={(e) => setUsagePurpose(e.target.value)}
            className="rounded-full border border-border bg-surface px-4 py-2 text-sm"
          >
            <option value="">Kullanım amacı seç (opsiyonel)</option>
            {Object.entries(USAGE_PURPOSE_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Bütçe (opsiyonel)
          <select
            value={budgetTier}
            onChange={(e) => setBudgetTier(e.target.value)}
            className="rounded-full border border-border bg-surface px-4 py-2 text-sm"
          >
            <option value="">Bütçe seç (opsiyonel)</option>
            {Object.entries(BUDGET_TIER_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <label className="flex flex-col gap-1 text-sm">
        Bitiş tarihi (opsiyonel)
        <input
          type="datetime-local"
          value={expiresAt}
          onChange={(e) => setExpiresAt(e.target.value)}
          className="rounded-full border border-border bg-surface px-4 py-2 text-sm"
        />
        <FieldErrors errors={pollErrors.expires_at} />
      </label>

      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={hideResults}
          onChange={(e) => setHideResults(e.target.checked)}
          className="accent-primary"
        />
        Sonuçları oy vermeden gizle
      </label>

      <div className="flex flex-col gap-4">
        <h2 className="font-heading text-lg font-semibold">Ürünler</h2>
        {products.map((product, index) => (
          <ProductFields
            key={product.id}
            index={index}
            product={product}
            errors={productErrors[product.id]}
            onChange={(patch) => updateProduct(product.id, patch)}
          />
        ))}
      </div>

      {nonFormErrors.length > 0 && (
        <ul className="flex flex-col gap-1 text-sm text-not-worth">
          {nonFormErrors.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
      )}

      <button
        type="submit"
        disabled={pending}
        className="w-fit rounded-full bg-primary px-6 py-3 text-sm font-medium text-white transition hover:bg-primary-600 disabled:opacity-50"
      >
        {pending ? "Kaydediliyor..." : "Kaydet"}
      </button>
    </form>
  );
}

function FieldErrors({ errors }: { errors?: string[] }) {
  if (!errors || errors.length === 0) return null;
  return (
    <ul className="text-xs text-not-worth">
      {errors.map((error) => (
        <li key={error}>{error}</li>
      ))}
    </ul>
  );
}

function ProductFields({
  index,
  product,
  errors,
  onChange,
}: {
  index: number;
  product: EditProductInput;
  errors?: Record<string, string[]>;
  onChange: (patch: Partial<EditProductInput>) => void;
}) {
  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <h3 className="text-sm font-medium">Ürün {index + 1}</h3>

      <label className="flex flex-col gap-1 text-sm">
        Ürün adı
        <input
          required
          value={product.name}
          onChange={(e) => onChange({ name: e.target.value })}
          className="rounded-full border border-border bg-bg px-4 py-2 text-sm outline-none focus:border-primary"
        />
        <FieldErrors errors={errors?.name} />
      </label>

      <label className="flex flex-col gap-1 text-sm">
        Fiyat (TL)
        <input
          required
          inputMode="decimal"
          value={product.price}
          onChange={(e) => onChange({ price: e.target.value })}
          className="rounded-full border border-border bg-bg px-4 py-2 text-sm outline-none focus:border-primary"
        />
        <FieldErrors errors={errors?.price} />
      </label>

      <label className="flex flex-col gap-1 text-sm">
        Özellikler (her satıra bir özellik)
        <textarea
          rows={3}
          value={product.features}
          onChange={(e) => onChange({ features: e.target.value })}
          className="rounded-2xl border border-border bg-bg px-4 py-2 text-sm outline-none focus:border-primary"
        />
        <FieldErrors errors={errors?.features} />
      </label>

      <label className="flex flex-col gap-1 text-sm">
        Karşılaştırma özellikleri (opsiyonel, &quot;Anahtar: Değer&quot;)
        <textarea
          rows={2}
          value={product.attributes}
          onChange={(e) => onChange({ attributes: e.target.value })}
          className="rounded-2xl border border-border bg-bg px-4 py-2 text-sm outline-none focus:border-primary"
        />
        <FieldErrors errors={errors?.attributes} />
      </label>

      <label className="flex flex-col gap-1 text-sm">
        Ürün linki (opsiyonel)
        <input
          type="url"
          value={product.productUrl}
          onChange={(e) => onChange({ productUrl: e.target.value })}
          className="rounded-full border border-border bg-bg px-4 py-2 text-sm outline-none focus:border-primary"
        />
        <FieldErrors errors={errors?.product_url} />
      </label>

      <label className="flex flex-col gap-1 text-sm">
        Görsel linki (opsiyonel)
        <input
          type="url"
          value={product.imageUrl}
          onChange={(e) => onChange({ imageUrl: e.target.value })}
          className="rounded-full border border-border bg-bg px-4 py-2 text-sm outline-none focus:border-primary"
        />
        <FieldErrors errors={errors?.image_url} />
      </label>

      <label className="flex flex-col gap-1 text-sm">
        Görsel yükle (opsiyonel — yüklersen yukarıdaki link yok sayılır)
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp,image/gif"
          onChange={(e) => onChange({ imageFile: e.target.files?.[0] ?? null })}
          className="text-sm"
        />
        <FieldErrors errors={errors?.image} />
      </label>
    </div>
  );
}
