"use client";

import { useState } from "react";

export function ShareButton() {
  const [copied, setCopied] = useState(false);

  async function handleClick() {
    await navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 4000);
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className="w-fit rounded-full border border-border px-4 py-2 text-sm font-medium transition hover:border-primary hover:text-primary"
    >
      {copied ? "Bağlantı kopyalandı!" : "Bu anketi paylaş"}
    </button>
  );
}
