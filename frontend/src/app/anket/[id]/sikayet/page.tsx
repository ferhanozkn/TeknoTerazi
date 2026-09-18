import { notFound, redirect } from "next/navigation";
import { fetchCurrentUser, fetchPoll } from "@/lib/api";
import { ReportForm } from "@/components/report-form";

export default async function ReportPollPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const [poll, user] = await Promise.all([fetchPoll(Number(id)), fetchCurrentUser()]);
  if (!poll) notFound();
  if (!user.authenticated) redirect("/giris");

  return (
    <div className="mx-auto flex max-w-sm flex-col gap-6 px-4 py-16">
      <h1 className="font-heading text-2xl font-semibold">Anketi şikayet et</h1>
      <p className="text-sm text-text-muted">&quot;{poll.title}&quot; anketini neden şikayet ediyorsun?</p>
      <ReportForm pollId={poll.id} />
    </div>
  );
}
