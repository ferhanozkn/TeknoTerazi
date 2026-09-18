import Link from "next/link";
import { redirect } from "next/navigation";
import { fetchCurrentUser, fetchMyPolls } from "@/lib/api";
import { MyPollRowActions } from "@/components/my-poll-row-actions";

export default async function MyPollsPage() {
  const user = await fetchCurrentUser();
  if (!user.authenticated) redirect("/giris");

  const polls = await fetchMyPolls();

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-6 px-4 py-10">
      <h1 className="font-heading text-2xl font-semibold">Anketlerim</h1>

      {polls.length === 0 ? (
        <p className="text-text-muted">Henüz anket oluşturmadın.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {polls.map((poll) => (
            <div
              key={poll.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border bg-surface p-4"
            >
              <div className="flex flex-col gap-1">
                <Link href={`/anket/${poll.id}`} className="font-medium hover:text-primary">
                  {poll.title}
                </Link>
                <p className="text-sm text-text-muted">
                  {poll.totalVotes} oy · {poll.viewCount} görüntülenme
                  {poll.conversionRate !== null && ` · %${poll.conversionRate} dönüşüm`}
                  {" · "}
                  {poll.isActive ? "Açık" : "Kapalı"}
                </p>
              </div>
              <MyPollRowActions pollId={poll.id} title={poll.title} isActive={poll.isActive} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
