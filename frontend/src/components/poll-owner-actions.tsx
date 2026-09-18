"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { deletePoll, togglePollActive } from "@/lib/poll-client";

export function PollOwnerActions({
  pollId,
  title,
  isActive,
  isExpired,
  pollHasVotes,
}: {
  pollId: number;
  title: string;
  isActive: boolean;
  isExpired: boolean;
  pollHasVotes: boolean;
}) {
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
      router.push("/anketlerim");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex flex-wrap gap-2">
      {!pollHasVotes && (
        <Link
          href={`/anket/${pollId}/duzenle`}
          className="w-fit rounded-full border border-border px-4 py-2 text-sm font-medium transition hover:border-primary hover:text-primary"
        >
          Düzenle
        </Link>
      )}
      {!isExpired && (
        <button
          type="button"
          onClick={handleToggle}
          disabled={pending}
          className="rounded-full border border-border px-4 py-2 text-sm font-medium transition hover:border-primary hover:text-primary disabled:opacity-50"
        >
          {isActive ? "Kapat" : "Yeniden Aç"}
        </button>
      )}
      <button
        type="button"
        onClick={handleDelete}
        disabled={pending}
        className="rounded-full border border-border px-4 py-2 text-sm font-medium text-not-worth transition hover:border-not-worth disabled:opacity-50"
      >
        Sil
      </button>
    </div>
  );
}
