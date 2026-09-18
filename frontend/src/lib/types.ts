export type PollCategory =
  | "phone"
  | "laptop"
  | "tablet"
  | "headphone"
  | "smartwatch"
  | "gaming"
  | "camera"
  | "tv"
  | "pc_part"
  | "other";

export type UsagePurpose = "gaming" | "school" | "work" | "daily" | "other";

export type BudgetTier = "economic" | "mid" | "premium";

export type VoteValue = "worth" | "not_worth";

export type ReportReason = "inappropriate" | "spam" | "misleading" | "other";

export const REPORT_REASON_LABELS: Record<ReportReason, string> = {
  inappropriate: "Uygunsuz içerik",
  spam: "Spam veya tanıtım",
  misleading: "Yanıltıcı bilgi",
  other: "Diğer",
};

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
  currency: string;
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
  isOwner: boolean;
  createdAt: string;
  expiresAt: string | null;
  isActive: boolean;
  isExpired: boolean;
  hideResultsUntilVote: boolean;
  viewCount: number;
  totalVotes: number;
  canVote: boolean;
  pollHasVotes: boolean;
  attributeKeys: string[];
  products: Product[];
}

export interface PollSummary {
  id: number;
  title: string;
  category: PollCategory;
  usagePurpose: UsagePurpose | null;
  budgetTier: BudgetTier | null;
  authorUsername: string;
  createdAt: string;
  expiresAt: string | null;
  isActive: boolean;
  isExpired: boolean;
  totalVotes: number;
  todayVotes: number;
  minPrice: number | null;
  maxPrice: number | null;
  productNames: string[];
  productCount: number;
}

export const CATEGORY_LABELS: Record<PollCategory, string> = {
  phone: "📱 Akıllı Telefon",
  laptop: "💻 Dizüstü Bilgisayar",
  tablet: "📱 Tablet",
  headphone: "🎧 Kulaklık",
  smartwatch: "⌚ Akıllı Saat",
  gaming: "🎮 Oyun & Konsol",
  camera: "📷 Kamera",
  tv: "📺 TV & Monitör",
  pc_part: "🖥️ Bilgisayar Parçası",
  other: "🔧 Diğer",
};

export const USAGE_PURPOSE_LABELS: Record<UsagePurpose, string> = {
  gaming: "Oyun",
  school: "Okul",
  work: "İş",
  daily: "Günlük kullanım",
  other: "Diğer",
};

export const BUDGET_TIER_LABELS: Record<BudgetTier, string> = {
  economic: "Ekonomik",
  mid: "Orta segment",
  premium: "Üst segment",
};

export function formatTl(amount: number): string {
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: "TRY",
    maximumFractionDigits: 0,
  }).format(amount);
}
