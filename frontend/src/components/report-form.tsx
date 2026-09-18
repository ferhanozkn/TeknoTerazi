"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { REPORT_REASON_LABELS, type ReportReason } from "@/lib/types";
import { reportPoll } from "@/lib/report-client";

export function ReportForm({ pollId }: { pollId: number }) {
  const router = useRouter();
  const [reason, setReason] = useState<ReportReason>("inappropriate");
  const [detail, setDetail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      await reportPoll(pollId, reason, detail);
      router.push(`/anket/${pollId}`);
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Şikayet gönderilemedi.");
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <label className="flex flex-col gap-1 text-sm">
        Şikayet nedeni
        <select
          value={reason}
          onChange={(e) => setReason(e.target.value as ReportReason)}
          className="rounded-full border border-border bg-surface px-4 py-2 text-sm"
        >
          {Object.entries(REPORT_REASON_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-1 text-sm">
        Detay (opsiyonel)
        <textarea
          rows={3}
          value={detail}
          onChange={(e) => setDetail(e.target.value)}
          placeholder="İstersen kısaca açıkla (opsiyonel)…"
          className="rounded-2xl border border-border bg-surface px-4 py-2 text-sm outline-none focus:border-primary"
        />
      </label>

      {error && <p className="text-sm text-not-worth">{error}</p>}

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={pending}
          className="rounded-full bg-primary px-4 py-2 text-sm font-medium text-white transition hover:bg-primary-600 disabled:opacity-50"
        >
          Şikayeti gönder
        </button>
        <Link
          href={`/anket/${pollId}`}
          className="rounded-full border border-border px-4 py-2 text-sm transition hover:border-primary hover:text-primary"
        >
          Vazgeç
        </Link>
      </div>
    </form>
  );
}
