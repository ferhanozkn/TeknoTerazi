export type PollCategory =
  | "telefon"
  | "laptop"
  | "kulaklik"
  | "beyaz_esya"
  | "diger";

export type UsagePurpose = "gunluk" | "oyun" | "is" | "fotografcilik";

export type BudgetTier = "ekonomik" | "orta" | "premium";

export type VoteValue = "worth" | "not_worth";

export interface Comment {
  id: number;
  body: string;
  authorUsername: string;
  createdAt: string;
  canDelete: boolean;
}

export interface Product {
  id: number;
  name: string;
  price: number;
  imageUrl: string | null;
  productUrl: string | null;
  features: string[];
  attributes: Record<string, string>;
  worthCount: number;
  notWorthCount: number;
  worthRatio: number | null;
  showResults: boolean;
  userVote: VoteValue | null;
  isCheapest: boolean;
  isFavorite: boolean;
  comments: Comment[];
}

export interface Poll {
  id: number;
  title: string;
  description: string | null;
  category: PollCategory;
  usagePurpose: UsagePurpose | null;
  budgetTier: BudgetTier | null;
  authorUsername: string;
  createdAt: string;
  expiresAt: string | null;
  isActive: boolean;
  isExpired: boolean;
  hideResultsUntilVote: boolean;
  viewCount: number;
  totalVotes: number;
  todayVotes: number;
  minPrice: number | null;
  maxPrice: number | null;
  products: Product[];
}

export const CATEGORY_LABELS: Record<PollCategory, string> = {
  telefon: "📱 Telefon",
  laptop: "💻 Laptop",
  kulaklik: "🎧 Kulaklık",
  beyaz_esya: "🧺 Beyaz Eşya",
  diger: "🔧 Diğer",
};

export const USAGE_PURPOSE_LABELS: Record<UsagePurpose, string> = {
  gunluk: "Günlük kullanım",
  oyun: "Oyun",
  is: "İş",
  fotografcilik: "Fotoğrafçılık",
};

export const BUDGET_TIER_LABELS: Record<BudgetTier, string> = {
  ekonomik: "Ekonomik",
  orta: "Orta segment",
  premium: "Premium",
};

export function formatTl(amount: number): string {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    maximumFractionDigits: 0,
  }).format(amount);
}
