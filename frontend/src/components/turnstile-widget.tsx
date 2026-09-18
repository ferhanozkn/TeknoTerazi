"use client";

import Script from "next/script";
import { useRef, useState } from "react";

declare global {
  interface Window {
    turnstile?: {
      render: (
        container: HTMLElement,
        options: { sitekey: string; callback: (token: string) => void },
      ) => string;
    };
  }
}

const siteKey = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;

export function TurnstileWidget({ onToken }: { onToken: (token: string) => void }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [rendered, setRendered] = useState(false);

  if (!siteKey) return null;

  function renderWidget() {
    if (rendered || !containerRef.current || !window.turnstile) return;
    window.turnstile.render(containerRef.current, { sitekey: siteKey!, callback: onToken });
    setRendered(true);
  }

  return (
    <>
      <Script
        src="https://challenges.cloudflare.com/turnstile/v0/api.js"
        async
        defer
        onLoad={renderWidget}
      />
      <div ref={containerRef} />
    </>
  );
}
