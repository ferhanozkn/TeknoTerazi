"use client";

import { postJson } from "./csrf";

export async function togglePollActive(pollId: number): Promise<{ is_active: boolean }> {
  const res = await postJson(`/api/polls/${pollId}/durum/`, {});
  if (!res.ok) throw new Error("İşlem başarısız oldu.");
  return res.json();
}

export async function deletePoll(pollId: number): Promise<void> {
  const res = await postJson(`/api/polls/${pollId}/sil/`, {});
  if (!res.ok) throw new Error("Anket silinemedi.");
}
