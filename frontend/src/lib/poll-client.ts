"use client";

import { postFormData, postJson } from "./csrf";

export interface NewProductInput {
  name: string;
  price: string;
  features: string;
  productUrl: string;
  imageUrl: string;
  attributes: string;
  imageFile: File | null;
}

export interface NewPollInput {
  title: string;
  category: string;
  description: string;
  usagePurpose: string;
  budgetTier: string;
  hideResultsUntilVote: boolean;
  expiresAt: string;
  products: NewProductInput[];
}

export interface PollCreateErrors {
  pollErrors: Record<string, string[]>;
  productErrors: Record<string, string[]>[];
  nonFormErrors: string[];
  productUploadErrors: Record<number, string>;
}

export class PollCreateError extends Error {
  errors: PollCreateErrors;

  constructor(errors: PollCreateErrors) {
    super(errors.nonFormErrors[0] ?? "Anket oluşturulamadı.");
    this.errors = errors;
  }
}

export async function createPoll(input: NewPollInput): Promise<{ id: number }> {
  const form = new FormData();
  form.set("title", input.title);
  form.set("category", input.category);
  form.set("description", input.description);
  form.set("usage_purpose", input.usagePurpose);
  form.set("budget_tier", input.budgetTier);
  if (input.hideResultsUntilVote) form.set("hide_results_until_vote", "on");
  form.set("expires_at", input.expiresAt);

  form.set("products-TOTAL_FORMS", String(input.products.length));
  form.set("products-INITIAL_FORMS", "0");
  form.set("products-MIN_NUM_FORMS", "2");
  form.set("products-MAX_NUM_FORMS", "5");
  input.products.forEach((product, index) => {
    form.set(`products-${index}-name`, product.name);
    form.set(`products-${index}-price`, product.price);
    form.set(`products-${index}-features`, product.features);
    form.set(`products-${index}-product_url`, product.productUrl);
    form.set(`products-${index}-image_url`, product.imageUrl);
    form.set(`products-${index}-attributes`, product.attributes);
    if (product.imageFile) form.set(`products-${index}-image`, product.imageFile);
  });

  const res = await postFormData("/api/polls/yeni/", form);
  const data = await res.json();
  if (!res.ok) {
    throw new PollCreateError({
      pollErrors: data.poll_errors ?? {},
      productErrors: data.product_errors ?? [],
      nonFormErrors: data.non_form_errors ?? [],
      productUploadErrors: data.product_upload_errors ?? {},
    });
  }
  return data;
}

export interface EditProductInput {
  id: number;
  name: string;
  price: string;
  features: string;
  productUrl: string;
  imageUrl: string;
  attributes: string;
  imageFile: File | null;
}

export interface EditPollInput {
  title: string;
  category: string;
  description: string;
  usagePurpose: string;
  budgetTier: string;
  hideResultsUntilVote: boolean;
  expiresAt: string;
  products: EditProductInput[];
}

export interface PollEditErrors {
  pollErrors: Record<string, string[]>;
  productErrors: Record<number, Record<string, string[]>>;
  nonFormErrors: string[];
  productUploadErrors: Record<number, string>;
}

export class PollEditError extends Error {
  errors: PollEditErrors;

  constructor(errors: PollEditErrors) {
    super(errors.nonFormErrors[0] ?? "Anket güncellenemedi.");
    this.errors = errors;
  }
}

export async function updatePoll(pollId: number, input: EditPollInput): Promise<{ id: number }> {
  const form = new FormData();
  form.set("title", input.title);
  form.set("category", input.category);
  form.set("description", input.description);
  form.set("usage_purpose", input.usagePurpose);
  form.set("budget_tier", input.budgetTier);
  if (input.hideResultsUntilVote) form.set("hide_results_until_vote", "on");
  form.set("expires_at", input.expiresAt);

  input.products.forEach((product) => {
    form.set(`products-${product.id}-name`, product.name);
    form.set(`products-${product.id}-price`, product.price);
    form.set(`products-${product.id}-features`, product.features);
    form.set(`products-${product.id}-product_url`, product.productUrl);
    form.set(`products-${product.id}-image_url`, product.imageUrl);
    form.set(`products-${product.id}-attributes`, product.attributes);
    if (product.imageFile) form.set(`products-${product.id}-image`, product.imageFile);
  });

  const res = await postFormData(`/api/polls/${pollId}/duzenle/`, form);
  const data = await res.json();
  if (!res.ok) {
    throw new PollEditError({
      pollErrors: data.poll_errors ?? {},
      productErrors: data.product_errors ?? {},
      nonFormErrors: data.non_form_errors ?? [],
      productUploadErrors: data.product_upload_errors ?? {},
    });
  }
  return data;
}

export async function togglePollActive(pollId: number): Promise<{ is_active: boolean }> {
  const res = await postJson(`/api/polls/${pollId}/durum/`, {});
  if (!res.ok) throw new Error("İşlem başarısız oldu.");
  return res.json();
}

export async function deletePoll(pollId: number): Promise<void> {
  const res = await postJson(`/api/polls/${pollId}/sil/`, {});
  if (!res.ok) throw new Error("Anket silinemedi.");
}
