"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { AuthFormError, updateUsername } from "@/lib/auth-client";

export function UsernameForm({ currentUsername }: { currentUsername: string }) {
  const router = useRouter();
  const [username, setUsername] = useState(currentUsername);
  const [errors, setErrors] = useState<string[]>([]);
  const [success, setSuccess] = useState(false);
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setErrors([]);
    setSuccess(false);
    try {
      await updateUsername(username);
      setSuccess(true);
      router.refresh();
    } catch (err) {
      setErrors(err instanceof AuthFormError ? Object.values(err.errors).flat() : ["Güncellenemedi."]);
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3">
      <label className="flex flex-col gap-1 text-sm">
        Kullanıcı adı
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="rounded-full border border-border bg-surface px-4 py-2 text-sm outline-none focus:border-primary"
        />
      </label>
      {errors.length > 0 && (
        <ul className="flex flex-col gap-1 text-sm text-not-worth">
          {errors.map((error) => (
            <li key={error}>{error}</li>
          ))}
        </ul>
      )}
      {success && <p className="text-sm text-worth">Kullanıcı adın güncellendi.</p>}
      <button
        type="submit"
        disabled={pending}
        className="w-fit rounded-full bg-primary px-4 py-2 text-sm font-medium text-white transition hover:bg-primary-600 disabled:opacity-50"
      >
        Kaydet
      </button>
    </form>
  );
}
