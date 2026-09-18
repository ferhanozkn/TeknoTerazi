import Link from "next/link";
import { fetchCurrentUser } from "@/lib/api";
import { LogoutButton } from "./logout-button";

export async function Navbar() {
  const user = await fetchCurrentUser();

  return (
    <header className="sticky top-0 z-10 border-b border-border bg-surface/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <Link href="/" className="font-heading text-lg font-semibold text-text">
          ⚖️ TeknoTerazi
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          <Link
            href="/anket-olustur"
            className="rounded-full bg-primary px-4 py-2 font-medium text-white transition hover:bg-primary-600"
          >
            Anket Oluştur
          </Link>
          {user.authenticated ? (
            <>
              <Link href="/profil" className="text-text-muted transition hover:text-text">
                @{user.username}
              </Link>
              <Link href="/anketlerim" className="text-text-muted transition hover:text-text">
                Anketlerim
              </Link>
              <LogoutButton />
            </>
          ) : (
            <>
              <Link href="/giris" className="text-text-muted transition hover:text-text">
                Giriş Yap
              </Link>
              <Link href="/kayit" className="text-text-muted transition hover:text-text">
                Kayıt Ol
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
