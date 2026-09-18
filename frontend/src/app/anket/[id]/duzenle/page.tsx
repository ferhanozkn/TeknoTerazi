import { redirect } from "next/navigation";
import { fetchPollEditData } from "@/lib/api";
import { PollEditForm } from "@/components/poll-edit-form";

export default async function PollEditPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const poll = await fetchPollEditData(Number(id));
  if (!poll) redirect(`/anket/${id}`);

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6 px-4 py-10">
      <h1 className="font-heading text-2xl font-semibold">Anketi düzenle</h1>
      <p className="text-sm text-text-muted">
        Bu anket henüz oy almadığı için düzenleyebilirsin. Oy alınca düzenleme kapanır.
      </p>
      <PollEditForm poll={poll} />
    </div>
  );
}
