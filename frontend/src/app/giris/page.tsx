"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { AuthFormError, login } from "@/lib/auth-client";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<string[]>([]);
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setErrors([]);
    try {
      await login({ email, password });
      router.push("/");
      router.refresh();
    } catch (err) {
      if (err instanceof AuthFormError) {
        setErrors(Object.values(err.errors).flat());
      } else {
        setErrors(["Giriş yapılamadı."]);
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="mx-auto flex max-w-sm flex-col gap-6 px-4 py-16">
      <h1 className="font-heading text-2xl font-semibold">Giriş Yap</h1>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          E-posta
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded-full border border-border bg-surface px-4 py-2 text-sm outline-none focus:border-primary"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Parola
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
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

        <button
          type="submit"
          disabled={pending}
          className="rounded-full bg-primary px-4 py-2 text-sm font-medium text-white transition hover:bg-primary-600 disabled:opacity-50"
        >
          {pending ? "Giriş yapılıyor..." : "Giriş Yap"}
        </button>
      </form>

      <p className="text-sm text-text-muted">
        Hesabın yok mu? <Link href="/kayit" className="text-primary hover:underline">Kayıt ol</Link>
      </p>
    </div>
  );
}
