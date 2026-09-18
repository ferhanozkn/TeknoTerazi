import Link from "next/link";
import { notFound } from "next/navigation";
import { ProductCard } from "@/components/product-card";
import { PollOwnerActions } from "@/components/poll-owner-actions";
import { ShareButton } from "@/components/share-button";
import { fetchCurrentUser, fetchPoll } from "@/lib/api";
import {
  BUDGET_TIER_LABELS,
  CATEGORY_LABELS,
  USAGE_PURPOSE_LABELS,
} from "@/lib/types";
import { timeAgo, timeUntil } from "@/lib/format";

export default async function PollDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [poll, user] = await Promise.all([fetchPoll(Number(id)), fetchCurrentUser()]);
  if (!poll) notFound();

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-8 px-4 py-10">
      <Link href="/" className="text-sm text-text-muted hover:text-primary">
        ← Tüm anketler
      </Link>

      <header className="flex flex-col gap-3">
        <div className="flex flex-wrap gap-2 text-xs font-medium">
          <span className="rounded-full bg-surface-tint px-3 py-1 text-primary">
            {CATEGORY_LABELS[poll.category]}
          </span>
          {poll.usagePurpose && (
            <span className="rounded-full bg-surface-tint px-3 py-1 text-text-muted">
              {USAGE_PURPOSE_LABELS[poll.usagePurpose]}
            </span>
          )}
          {poll.budgetTier && (
            <span className="rounded-full bg-surface-tint px-3 py-1 text-text-muted">
              {BUDGET_TIER_LABELS[poll.budgetTier]}
            </span>
          )}
          {(poll.isExpired || !poll.isActive) && (
            <span className="rounded-full bg-not-worth-tint px-3 py-1 text-not-worth">
              {poll.isExpired ? "Süresi doldu" : "Kapandı"}
            </span>
          )}
        </div>

        <h1 className="font-heading text-3xl font-semibold">{poll.title}</h1>
        <p className="text-sm text-text-muted">
          @{poll.authorUsername} · {timeAgo(poll.createdAt)}
        </p>
        {poll.description && <p className="text-text-muted">{poll.description}</p>}
        {poll.expiresAt && (
          <p className="text-sm text-text-muted">
            {poll.isExpired
              ? `⏳ Süresi doldu (${new Date(poll.expiresAt).toLocaleString("tr-TR")})`
              : `⏳ Bitiş: ${new Date(poll.expiresAt).toLocaleString("tr-TR")} (${timeUntil(poll.expiresAt)} kaldı)`}
          </p>
        )}

        {poll.isOwner && (
          <>
            <p className="text-sm text-text-muted">
              📊 {poll.viewCount} görüntülenme · {poll.totalVotes} oy
              <span className="ml-1 text-xs">(yalnızca sana görünür)</span>
            </p>
            <PollOwnerActions
              pollId={poll.id}
              title={poll.title}
              isActive={poll.isActive}
              isExpired={poll.isExpired}
              pollHasVotes={poll.pollHasVotes}
            />
          </>
        )}

        <div className="flex flex-wrap gap-2">
          <ShareButton />
          {user.authenticated && !poll.isOwner && (
            <Link
              href={`/anket/${poll.id}/sikayet`}
              className="w-fit rounded-full border border-border px-4 py-2 text-sm font-medium transition hover:border-not-worth hover:text-not-worth"
            >
              Şikayet et
            </Link>
          )}
        </div>
      </header>

      <div className="grid gap-6 sm:grid-cols-2">
        {poll.products.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            canVote={poll.canVote}
            hideResultsUntilVote={poll.hideResultsUntilVote}
            isAuthenticated={user.authenticated}
          />
        ))}
      </div>

      {poll.attributeKeys.length > 0 && (
        <section className="flex flex-col gap-3">
          <h2 className="font-heading text-xl font-semibold">Karşılaştırma tablosu</h2>
          <div className="overflow-x-auto rounded-2xl border border-border">
            <table className="w-full min-w-max text-sm">
              <thead>
                <tr className="border-b border-border bg-surface-tint text-left">
                  <th className="px-4 py-3 font-medium">Özellik</th>
                  {poll.products.map((product) => (
                    <th key={product.id} className="px-4 py-3 font-medium">
                      {product.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {poll.attributeKeys.map((key) => (
                  <tr key={key} className="border-b border-border last:border-0">
                    <th scope="row" className="px-4 py-3 text-left font-medium text-text-muted">
                      {key}
                    </th>
                    {poll.products.map((product) => (
                      <td key={product.id} className="px-4 py-3">
                        {product.attributes[key] ?? "—"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
