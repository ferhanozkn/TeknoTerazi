"use client";

import { postJson } from "./csrf";
import type { VoteValue } from "./types";

export interface VoteResult {
  product_id: number;
  user_vote: VoteValue | null;
  worth_count: number;
  not_worth_count: number;
  total_votes: number;
  worth_ratio: number | null;
}

export async function castVote(productId: number, value: VoteValue): Promise<VoteResult> {
  const res = await postJson(`/api/products/${productId}/vote/`, { value });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error ?? "Oy verilemedi.");
  }
  return data;
}
