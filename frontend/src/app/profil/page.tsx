import Link from "next/link";
import { redirect } from "next/navigation";
import { fetchCurrentUser, fetchProfile } from "@/lib/api";
import { UsernameForm } from "@/components/username-form";

export default async function ProfilePage() {
  const user = await fetchCurrentUser();
  if (!user.authenticated) redirect("/giris");

  const profile = await fetchProfile();
  if (!profile) redirect("/giris");

  return (
    <div className="mx-auto flex max-w-sm flex-col gap-6 px-4 py-16">
      <h1 className="font-heading text-2xl font-semibold">Profilim</h1>

      <dl className="flex flex-col gap-2 text-sm">
        <div className="flex justify-between">
          <dt className="text-text-muted">E-posta</dt>
          <dd>{profile.email}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-text-muted">Katılma tarihi</dt>
          <dd>{new Date(profile.dateJoined).toLocaleDateString("tr-TR")}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-text-muted">Oluşturduğun anket sayısı</dt>
          <dd>{profile.pollCount}</dd>
        </div>
      </dl>

      <UsernameForm currentUsername={profile.username} />

      <Link href="/anketlerim" className="text-sm text-primary hover:underline">
        Anketlerime dön
      </Link>
    </div>
  );
}
