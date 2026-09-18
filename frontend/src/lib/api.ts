import { cookies } from "next/headers";
import type {
  BudgetTier,
  Comment,
  Poll,
  PollCategory,
  PollSummary,
  Product,
  UsagePurpose,
} from "./types";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

interface RawPollSummary {
  id: number;
  title: string;
  category: PollCategory;
  usage_purpose: UsagePurpose | null;
  budget_tier: BudgetTier | null;
  author_username: string;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
  is_expired: boolean;
  total_votes: number;
  today_votes: number;
  min_price: number | null;
  max_price: number | null;
  product_names: string[];
  product_count: number;
}

interface RawComment {
  id: number;
  body: string;
  author_username: string;
  created_at: string;
  can_delete: boolean;
}

interface RawProduct {
  id: number;
  name: string;
  price: number;
  currency: string;
  image_url: string | null;
  product_url: string | null;
  features: string[];
  attributes: Record<string, string>;
  worth_count: number;
  not_worth_count: number;
  worth_ratio: number | null;
  user_vote: "worth" | "not_worth" | null;
  show_results: boolean;
  is_cheapest: boolean;
  is_favorite: boolean;
  comments: RawComment[];
}

interface RawPollDetail {
  id: number;
  title: string;
  description: string | null;
  category: PollCategory;
  usage_purpose: UsagePurpose | null;
  budget_tier: BudgetTier | null;
  author_username: string;
  is_owner: boolean;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
  is_expired: boolean;
  hide_results_until_vote: boolean;
  view_count: number;
  total_votes: number;
  can_vote: boolean;
  poll_has_votes: boolean;
  attribute_keys: string[];
  products: RawProduct[];
}

function toPollSummary(raw: RawPollSummary): PollSummary {
  return {
    id: raw.id,
    title: raw.title,
    category: raw.category,
    usagePurpose: raw.usage_purpose,
    budgetTier: raw.budget_tier,
    authorUsername: raw.author_username,
    createdAt: raw.created_at,
    expiresAt: raw.expires_at,
    isActive: raw.is_active,
    isExpired: raw.is_expired,
    totalVotes: raw.total_votes,
    todayVotes: raw.today_votes,
    minPrice: raw.min_price,
    maxPrice: raw.max_price,
    productNames: raw.product_names,
    productCount: raw.product_count,
  };
}

function toComment(raw: RawComment): Comment {
  return {
    id: raw.id,
    body: raw.body,
    authorUsername: raw.author_username,
    createdAt: raw.created_at,
    canDelete: raw.can_delete,
  };
}

function toProduct(raw: RawProduct): Product {
  return {
    id: raw.id,
    name: raw.name,
    price: raw.price,
    currency: raw.currency,
    imageUrl: raw.image_url,
    productUrl: raw.product_url,
    features: raw.features,
    attributes: raw.attributes,
    worthCount: raw.worth_count,
    notWorthCount: raw.not_worth_count,
    worthRatio: raw.worth_ratio,
    showResults: raw.show_results,
    userVote: raw.user_vote,
    isCheapest: raw.is_cheapest,
    isFavorite: raw.is_favorite,
    comments: raw.comments.map(toComment),
  };
}

function toPoll(raw: RawPollDetail): Poll {
  return {
    id: raw.id,
    title: raw.title,
    description: raw.description,
    category: raw.category,
    usagePurpose: raw.usage_purpose,
    budgetTier: raw.budget_tier,
    authorUsername: raw.author_username,
    isOwner: raw.is_owner,
    createdAt: raw.created_at,
    expiresAt: raw.expires_at,
    isActive: raw.is_active,
    isExpired: raw.is_expired,
    hideResultsUntilVote: raw.hide_results_until_vote,
    viewCount: raw.view_count,
    totalVotes: raw.total_votes,
    canVote: raw.can_vote,
    pollHasVotes: raw.poll_has_votes,
    attributeKeys: raw.attribute_keys,
    products: raw.products.map(toProduct),
  };
}

/** Forwards the visitor's cookies (anon voter id, session) so the backend can
 * personalize `user_vote`/`show_results` on the very first server render. */
async function backendFetch(path: string, init?: RequestInit) {
  const cookieHeader = (await cookies()).toString();
  const res = await fetch(`${BACKEND_URL}${path}`, {
    ...init,
    headers: { ...init?.headers, cookie: cookieHeader },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`TeknoTerazi API ${path} -> ${res.status}`);
  }
  return res.json();
}

export interface PollListFilters {
  q?: string;
  kategori?: string;
  amac?: string;
  butce?: string;
  durum?: string;
  sirala?: string;
  sayfa?: string;
}

export interface PollListResult {
  results: PollSummary[];
  count: number;
  numPages: number;
  currentPage: number;
  hasNext: boolean;
  hasPrevious: boolean;
  querystringPrefix: string;
}

export async function fetchPollList(filters: PollListFilters = {}): Promise<PollListResult> {
  const params = new URLSearchParams(
    Object.entries(filters).filter(([, value]) => Boolean(value)) as [string, string][],
  );
  const data = await backendFetch(`/api/polls/?${params.toString()}`);
  return {
    results: data.results.map(toPollSummary),
    count: data.count,
    numPages: data.num_pages,
    currentPage: data.current_page,
    hasNext: data.has_next,
    hasPrevious: data.has_previous,
    querystringPrefix: data.querystring_prefix,
  };
}

export async function fetchTrendingPolls(): Promise<PollSummary[]> {
  const data = await backendFetch("/api/polls/trending/");
  return data.results.map(toPollSummary);
}

export async function fetchPoll(id: number): Promise<Poll | null> {
  try {
    const data = await backendFetch(`/api/polls/${id}/`);
    return toPoll(data);
  } catch {
    return null;
  }
}
