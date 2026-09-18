"use client";

function readCsrfCookie(): string {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

async function ensureCsrfCookie(): Promise<void> {
  if (readCsrfCookie()) return;
  await fetch("/api/csrf/", { credentials: "include" });
}

/** Builds fetch init for a same-origin JSON POST to a Django API route,
 * always re-reading the csrftoken cookie fresh — Django rotates it after
 * login, so a value cached earlier in the call chain would be stale. */
export async function postJson(path: string, body: unknown): Promise<Response> {
  await ensureCsrfCookie();
  return fetch(path, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": readCsrfCookie(),
    },
    body: JSON.stringify(body),
  });
}

/** Same as postJson but for multipart form data (file uploads) — no
 * Content-Type header, the browser sets the multipart boundary itself. */
export async function postFormData(path: string, body: FormData): Promise<Response> {
  await ensureCsrfCookie();
  return fetch(path, {
    method: "POST",
    credentials: "include",
    headers: { "X-CSRFToken": readCsrfCookie() },
    body,
  });
}
