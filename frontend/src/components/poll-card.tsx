import Link from "next/link";
import {
  BUDGET_TIER_LABELS,
  CATEGORY_LABELS,
  USAGE_PURPOSE_LABELS,
  formatTl,
  type PollSummary,
} from "@/lib/types";
import { timeAgo } from "@/lib/format";

export function PollCard({ poll }: { poll: PollSummary }) {
  const visibleProducts = poll.productNames.slice(0, 3);
  const remaining = poll.productCount - visibleProducts.length;

  return (
    <article className="flex flex-col gap-3 rounded-3xl border border-border bg-surface p-5 shadow-[var(--shadow-card)] transition hover:shadow-[var(--shadow-card-hover)]">
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
        {poll.isExpired ? (
          <span className="rounded-full bg-not-worth-tint px-3 py-1 text-not-worth">
            Süresi doldu
          </span>
        ) : !poll.isActive ? (
          <span className="rounded-full bg-not-worth-tint px-3 py-1 text-not-worth">
            Kapandı
          </span>
        ) : null}
        {poll.todayVotes > 0 && (
          <span className="rounded-full bg-warning/15 px-3 py-1 text-warning">
            🔥 Bugün {poll.todayVotes} oy
          </span>
        )}
      </div>

      <h3 className="font-heading text-lg font-semibold leading-snug">
        <Link href={`/anket/${poll.id}`} className="hover:text-primary">
          {poll.title}
        </Link>
      </h3>

      <p className="text-sm text-text-muted">{poll.productCount} ürün</p>

      <ul className="flex flex-wrap gap-x-2 text-sm text-text-muted">
        {visibleProducts.map((name) => (
          <li key={name}>{name}</li>
        ))}
        {remaining > 0 && <li>+{remaining}</li>}
      </ul>

      {poll.minPrice !== null && poll.maxPrice !== null && (
        <p className="font-heading text-sm font-medium text-text">
          {formatTl(poll.minPrice)} – {formatTl(poll.maxPrice)}
        </p>
      )}

      <div className="mt-auto flex items-center justify-between text-xs text-text-muted">
        <span>{poll.totalVotes} oy</span>
        <span>
          @{poll.authorUsername} · {timeAgo(poll.createdAt)}
        </span>
      </div>
    </article>
  );
}
