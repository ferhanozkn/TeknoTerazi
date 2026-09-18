"use client";

import type { VoteValue } from "./types";

export interface VoteResult {
  product_id: number;
  user_vote: VoteValue | null;
  worth_count: number;
  not_worth_count: number;
  total_votes: number;
  worth_ratio: number | null;
}

function readCsrfCookie(): string {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

async function ensureCsrfCookie(): Promise<void> {
  if (readCsrfCookie()) return;
  await fetch("/api/csrf/", { credentials: "include" });
}

export async function castVote(productId: number, value: VoteValue): Promise<VoteResult> {
  await ensureCsrfCookie();
  const res = await fetch(`/api/products/${productId}/vote/`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": readCsrfCookie(),
    },
    body: JSON.stringify({ value }),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error ?? "Oy verilemedi.");
  }
  return data;
}
