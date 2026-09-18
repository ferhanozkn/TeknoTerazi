"use client";

import { postJson } from "./csrf";
import type { ReportReason } from "./types";

export class ReportFormError extends Error {
  errors: Record<string, string[]>;

  constructor(message: string, errors: Record<string, string[]> = {}) {
    super(message);
    this.errors = errors;
  }
}

export async function reportPoll(
  pollId: number,
  reason: ReportReason,
  detail: string,
): Promise<void> {
  const res = await postJson(`/api/polls/${pollId}/sikayet/`, { reason, detail });
  const data = await res.json();
  if (!res.ok) {
    throw new ReportFormError(data.error ?? "Şikayet gönderilemedi.", data.errors ?? {});
  }
}
