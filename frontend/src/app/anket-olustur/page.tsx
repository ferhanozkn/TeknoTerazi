import { redirect } from "next/navigation";
import { fetchCurrentUser } from "@/lib/api";
import { PollCreateForm } from "@/components/poll-create-form";

export default async function PollCreatePage() {
  const user = await fetchCurrentUser();
  if (!user.authenticated) redirect("/giris");

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6 px-4 py-10">
      <h1 className="font-heading text-2xl font-semibold">Anket Oluştur</h1>
      <PollCreateForm />
    </div>
  );
}
