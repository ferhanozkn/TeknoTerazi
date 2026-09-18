"use client";

import { postJson } from "./csrf";

export interface AuthUser {
  authenticated: boolean;
  username: string | null;
}

export type FieldErrors = Record<string, string[]>;

export class AuthFormError extends Error {
  errors: FieldErrors;

  constructor(errors: FieldErrors) {
    super(errors.__all__?.[0] ?? "İşlem başarısız oldu.");
    this.errors = errors;
  }
}

export async function fetchMe(): Promise<AuthUser> {
  const res = await fetch("/api/auth/me/", { credentials: "include" });
  return res.json();
}

async function postAuth(path: string, body: unknown): Promise<AuthUser> {
  const res = await postJson(path, body);
  const data = await res.json();
  if (!res.ok) {
    throw new AuthFormError(data.errors ?? {});
  }
  return data;
}

export function signup(input: {
  username: string;
  email: string;
  password1: string;
  password2: string;
  turnstileToken: string;
}): Promise<AuthUser> {
  return postAuth("/api/auth/signup/", {
    username: input.username,
    email: input.email,
    password1: input.password1,
    password2: input.password2,
    turnstile_token: input.turnstileToken,
  });
}

export function login(input: { email: string; password: string }): Promise<AuthUser> {
  return postAuth("/api/auth/login/", input);
}

export async function logout(): Promise<AuthUser> {
  const res = await postJson("/api/auth/logout/", {});
  return res.json();
}

export async function updateUsername(username: string): Promise<{ username: string }> {
  const res = await postJson("/api/auth/profile/username/", { username });
  const data = await res.json();
  if (!res.ok) {
    throw new AuthFormError(data.errors ?? {});
  }
  return data;
}
