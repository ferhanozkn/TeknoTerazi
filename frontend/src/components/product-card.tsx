"use client";

import { useState } from "react";
import { formatTl, type Product, type VoteValue } from "@/lib/types";
import { castVote } from "@/lib/vote-client";
import { CommentSection } from "./comment-section";

export function ProductCard({
  product,
  canVote,
  hideResultsUntilVote,
  isAuthenticated,
}: {
  product: Product;
  canVote: boolean;
  hideResultsUntilVote: boolean;
  isAuthenticated: boolean;
}) {
  const [userVote, setUserVote] = useState<VoteValue | null>(product.userVote);
  const [worthCount, setWorthCount] = useState(product.worthCount);
  const [notWorthCount, setNotWorthCount] = useState(product.notWorthCount);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  const hasVoted = userVote !== null;
  const showResults = !hideResultsUntilVote || hasVoted || !canVote;
  const totalVotes = worthCount + notWorthCount;
  const worthRatio = totalVotes > 0 ? Math.round((worthCount / totalVotes) * 100) : 0;

  async function handleVote(value: VoteValue) {
    if (pending || !canVote) return;
    setPending(true);
    setError(null);
    const previous = { userVote, worthCount, notWorthCount };
    try {
      const result = await castVote(product.id, value);
      setUserVote(result.user_vote);
      setWorthCount(result.worth_count);
      setNotWorthCount(result.not_worth_count);
    } catch (err) {
      setUserVote(previous.userVote);
      setWorthCount(previous.worthCount);
      setNotWorthCount(previous.notWorthCount);
      setError(err instanceof Error ? err.message : "Oy verilemedi.");
    } finally {
      setPending(false);
    }
  }

  return (
    <article className="flex flex-col gap-3 rounded-3xl border border-border bg-surface p-5 shadow-[var(--shadow-card)]">
      {product.isFavorite && showResults && (
        <span className="w-fit rounded-full bg-warning/15 px-3 py-1 text-xs font-medium text-warning">
          🏆 Topluluğun Favorisi
        </span>
      )}

      <h3 className="font-heading text-lg font-semibold">{product.name}</h3>

      <p className="flex items-center gap-2 text-sm">
        <span className="font-heading font-medium text-text">{formatTl(product.price)}</span>
        {product.isCheapest && (
          <span className="rounded-full bg-worth-tint px-2 py-0.5 text-xs font-medium text-worth">
            En uygun fiyat
          </span>
        )}
      </p>

      <ul className="flex flex-col gap-1 text-sm text-text-muted">
        {product.features.map((feature) => (
          <li key={feature}>• {feature}</li>
        ))}
      </ul>

      {product.productUrl && (
        <a
          href={product.productUrl}
          target="_blank"
          rel="noopener noreferrer nofollow"
          className="text-sm font-medium text-primary hover:underline"
        >
          Ürüne git ↗
        </a>
      )}

      {showResults ? (
        <div className="flex flex-col gap-1">
          <div className="h-2 overflow-hidden rounded-full bg-not-worth-tint">
            <div
              className="h-full rounded-full bg-worth transition-[width]"
              style={{ width: `${worthRatio}%` }}
            />
          </div>
          <p className="text-sm font-medium">%{worthRatio} buna değer diyor</p>
          <p className="flex gap-3 text-xs text-text-muted">
            <span>👍 {worthCount}</span>
            <span>👎 {notWorthCount}</span>
          </p>
        </div>
      ) : (
        <p className="text-sm text-text-muted">Sonuçları görmek için önce oy ver.</p>
      )}

      <div className="mt-1 flex gap-2">
        <button
          type="button"
          onClick={() => handleVote("worth")}
          disabled={!canVote || pending}
          aria-pressed={userVote === "worth"}
          className={`flex-1 rounded-full border px-3 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50 ${
            userVote === "worth"
              ? "border-worth bg-worth-tint text-worth"
              : "border-border text-text-muted hover:border-worth hover:text-worth"
          }`}
        >
          👍 Buna değer
        </button>
        <button
          type="button"
          onClick={() => handleVote("not_worth")}
          disabled={!canVote || pending}
          aria-pressed={userVote === "not_worth"}
          className={`flex-1 rounded-full border px-3 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50 ${
            userVote === "not_worth"
              ? "border-not-worth bg-not-worth-tint text-not-worth"
              : "border-border text-text-muted hover:border-not-worth hover:text-not-worth"
          }`}
        >
          👎 Buna değmez
        </button>
      </div>
      {error && <p className="text-sm text-not-worth">{error}</p>}

      <CommentSection
        productId={product.id}
        initialComments={product.comments}
        isAuthenticated={isAuthenticated}
      />
    </article>
  );
}
