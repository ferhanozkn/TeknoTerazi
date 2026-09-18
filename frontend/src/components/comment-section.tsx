"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import type { Comment } from "@/lib/types";
import { addComment, deleteComment } from "@/lib/comment-client";

export function CommentSection({
  productId,
  initialComments,
  isAuthenticated,
}: {
  productId: number;
  initialComments: Comment[];
  isAuthenticated: boolean;
}) {
  const [comments, setComments] = useState(initialComments);
  const [body, setBody] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      const comment = await addComment(productId, body);
      setComments((current) => [comment, ...current]);
      setBody("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Yorum gönderilemedi.");
    } finally {
      setPending(false);
    }
  }

  async function handleDelete(commentId: number) {
    await deleteComment(commentId);
    setComments((current) => current.filter((c) => c.id !== commentId));
  }

  return (
    <section className="mt-2 flex flex-col gap-2 border-t border-border pt-3">
      <h4 className="text-sm font-medium">Yorumlar ({comments.length})</h4>
      <ul className="flex flex-col gap-2">
        {comments.length === 0 ? (
          <li className="text-sm text-text-muted">Henüz yorum yok. İlk yorumu sen yaz!</li>
        ) : (
          comments.map((comment) => (
            <li key={comment.id} className="text-sm">
              <p>{comment.body}</p>
              <p className="flex items-center gap-2 text-xs text-text-muted">
                @{comment.authorUsername}
                {comment.canDelete && (
                  <button
                    type="button"
                    onClick={() => handleDelete(comment.id)}
                    className="text-not-worth hover:underline"
                  >
                    Sil
                  </button>
                )}
              </p>
            </li>
          ))
        )}
      </ul>

      {isAuthenticated ? (
        <form onSubmit={handleSubmit} className="flex flex-col gap-2">
          <textarea
            rows={2}
            maxLength={500}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Neden buna değer ya da değmez? Kısa bir not bırak…"
            className="rounded-2xl border border-border bg-bg px-4 py-2 text-sm outline-none focus:border-primary"
          />
          {error && <p className="text-xs text-not-worth">{error}</p>}
          <button
            type="submit"
            disabled={pending}
            className="w-fit rounded-full bg-primary px-4 py-1.5 text-sm font-medium text-white transition hover:bg-primary-600 disabled:opacity-50"
          >
            Yorum yap
          </button>
        </form>
      ) : (
        <p className="text-sm text-text-muted">
          Yorum yapmak için{" "}
          <Link href="/giris" className="text-primary hover:underline">
            giriş yap
          </Link>
          .
        </p>
      )}
    </section>
  );
}
