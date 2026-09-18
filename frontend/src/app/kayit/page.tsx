"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { AuthFormError, signup } from "@/lib/auth-client";
import { TurnstileWidget } from "@/components/turnstile-widget";

export default function SignupPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password1, setPassword1] = useState("");
  const [password2, setPassword2] = useState("");
  const [turnstileToken, setTurnstileToken] = useState("");
  const [errors, setErrors] = useState<string[]>([]);
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setErrors([]);
    try {
      await signup({ username, email, password1, password2, turnstileToken });
      router.push("/");
      router.refresh();
    } catch (err) {
      if (err instanceof AuthFormError) {
        setErrors(Object.values(err.errors).flat());
      } else {
        setErrors(["Kayıt olunamadı."]);
      }
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="mx-auto flex max-w-sm flex-col gap-6 px-4 py-16">
      <h1 className="font-heading text-2xl font-semibold">Kayıt Ol</h1>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          Kullanıcı adı
          <input
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="rounded-full border border-border bg-surface px-4 py-2 text-sm outline-none focus:border-primary"
          />
        </label>
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
            value={password1}
            onChange={(e) => setPassword1(e.target.value)}
            className="rounded-full border border-border bg-surface px-4 py-2 text-sm outline-none focus:border-primary"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Parola (tekrar)
          <input
            type="password"
            required
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
            className="rounded-full border border-border bg-surface px-4 py-2 text-sm outline-none focus:border-primary"
          />
        </label>

        <TurnstileWidget onToken={setTurnstileToken} />

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
          {pending ? "Kayıt olunuyor..." : "Kayıt Ol"}
        </button>
      </form>

      <p className="text-sm text-text-muted">
        Zaten hesabın var mı? <Link href="/giris" className="text-primary hover:underline">Giriş yap</Link>
      </p>
    </div>
  );
}
