"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { deletePoll, togglePollActive } from "@/lib/poll-client";

export function MyPollRowActions({ pollId, title, isActive }: { pollId: number; title: string; isActive: boolean }) {
  const router = useRouter();
  const [pending, setPending] = useState(false);

  async function handleToggle() {
    setPending(true);
    try {
      await togglePollActive(pollId);
      router.refresh();
    } finally {
      setPending(false);
    }
  }

  async function handleDelete() {
    if (!window.confirm(`"${title}" anketini silmek istediğine emin misin? Bu işlem geri alınamaz.`)) {
      return;
    }
    setPending(true);
    try {
      await deletePoll(pollId);
      router.refresh();
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex gap-2">
      <button
        type="button"
        onClick={handleToggle}
        disabled={pending}
        className="rounded-full border border-border px-3 py-1.5 text-sm transition hover:border-primary hover:text-primary disabled:opacity-50"
      >
        {isActive ? "Kapat" : "Aç"}
      </button>
      <button
        type="button"
        onClick={handleDelete}
        disabled={pending}
        className="rounded-full border border-border px-3 py-1.5 text-sm text-not-worth transition hover:border-not-worth disabled:opacity-50"
      >
        Sil
      </button>
    </div>
  );
}
