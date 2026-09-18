"use client";

import { postJson } from "./csrf";
import type { Comment } from "./types";

export class CommentFormError extends Error {
  errors: Record<string, string[]>;

  constructor(errors: Record<string, string[]>) {
    super(errors.body?.[0] ?? "Yorum gönderilemedi.");
    this.errors = errors;
  }
}

export async function addComment(productId: number, body: string): Promise<Comment> {
  const res = await postJson(`/api/products/${productId}/yorum/`, { body });
  const data = await res.json();
  if (!res.ok) {
    throw new CommentFormError(data.errors ?? {});
  }
  return {
    id: data.id,
    body: data.body,
    authorUsername: data.author_username,
    createdAt: data.created_at,
    canDelete: data.can_delete,
  };
}

export async function deleteComment(commentId: number): Promise<void> {
  const res = await postJson(`/api/yorum/${commentId}/sil/`, {});
  if (!res.ok) throw new Error("Yorum silinemedi.");
}
