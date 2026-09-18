"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { BUDGET_TIER_LABELS, CATEGORY_LABELS, USAGE_PURPOSE_LABELS } from "@/lib/types";
import { createPoll, PollCreateError, type NewProductInput } from "@/lib/poll-client";

const MIN_PRODUCTS = 2;
const MAX_PRODUCTS = 5;

function emptyProduct(): NewProductInput {
  return {
    name: "",
    price: "",
    features: "",
    productUrl: "",
    imageUrl: "",
    attributes: "",
    imageFile: null,
  };
}

export function PollCreateForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("");
  const [description, setDescription] = useState("");
  const [usagePurpose, setUsagePurpose] = useState("");
  const [budgetTier, setBudgetTier] = useState("");
  const [hideResults, setHideResults] = useState(false);
  const [expiresAt, setExpiresAt] = useState("");
  const [products, setProducts] = useState<NewProductInput[]>([emptyProduct(), emptyProduct()]);

  const [pollErrors, setPollErrors] = useState<Record<string, string[]>>({});
  const [productErrors, setProductErrors] = useState<Record<string, string[]>[]>([]);
  const [nonFormErrors, setNonFormErrors] = useState<string[]>([]);
  const [pending, setPending] = useState(false);

  function updateProduct(index: number, patch: Partial<NewProductInput>) {
    setProducts((current) => current.map((p, i) => (i === index ? { ...p, ...patch } : p)));
  }

  function addProduct() {
    if (products.length >= MAX_PRODUCTS) return;
    setProducts((current) => [...current, emptyProduct()]);
  }

  function removeProduct(index: number) {
    if (products.length <= MIN_PRODUCTS) return;
    setProducts((current) => current.filter((_, i) => i !== index));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setPollErrors({});
    setProductErrors([]);
    setNonFormErrors([]);
    try {
      const { id } = await createPoll({
        title,
        category,
        description,
        usagePurpose,
        budgetTier,
        hideResultsUntilVote: hideResults,
        expiresAt,
        products,
      });
      router.push(`/anket/${id}`);
    } catch (err) {
      if (err instanceof PollCreateError) {
        setPollErrors(err.errors.pollErrors);
        setProductErrors(err.errors.productErrors);
        const uploadErrors = Object.values(err.errors.productUploadErrors);
        setNonFormErrors([...err.errors.nonFormErrors, ...uploadErrors]);
      } else {
        setNonFormErrors(["Anket oluşturulamadı."]);
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
          <option value="">Kategori seç</option>
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
      <p className="text-xs text-text-muted">
        Önyargıyı azaltmak için: bir ürüne oy verene kadar o ürünün oy sayıları gizli kalır.
      </p>

      <div className="flex flex-col gap-4">
        <h2 className="font-heading text-lg font-semibold">Ürünler ({products.length}/{MAX_PRODUCTS})</h2>
        {products.map((product, index) => (
          <ProductFields
            key={index}
            index={index}
            product={product}
            errors={productErrors[index]}
            canRemove={products.length > MIN_PRODUCTS}
            onChange={(patch) => updateProduct(index, patch)}
            onRemove={() => removeProduct(index)}
          />
        ))}
        {products.length < MAX_PRODUCTS && (
          <button
            type="button"
            onClick={addProduct}
            className="w-fit rounded-full border border-border px-4 py-2 text-sm transition hover:border-primary hover:text-primary"
          >
            + Ürün ekle
          </button>
        )}
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
        {pending ? "Oluşturuluyor..." : "Anketi Yayınla"}
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
  canRemove,
  onChange,
  onRemove,
}: {
  index: number;
  product: NewProductInput;
  errors?: Record<string, string[]>;
  canRemove: boolean;
  onChange: (patch: Partial<NewProductInput>) => void;
  onRemove: () => void;
}) {
  return (
    <div className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium">Ürün {index + 1}</h3>
        {canRemove && (
          <button
            type="button"
            onClick={onRemove}
            className="text-sm text-not-worth hover:underline"
          >
            Kaldır
          </button>
        )}
      </div>

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
          placeholder="0,00"
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
          placeholder={"8 GB RAM\n120 Hz ekran"}
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
          placeholder={"RAM: 8 GB\nDepolama: 128 GB"}
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
