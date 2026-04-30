export type Verdict = "credible" | "suspicious" | "debunked";

export interface Topic {
  id: number;
  name: string;
  keywords: string;
  trend_score: number;
  region: string;
  detected_at: string;
}

export interface Article {
  id: number;
  title: string;
  summary: string | null;
  source_name: string;
  url: string;
  published_at: string | null;
  verdict: Verdict | null;
  credibility_score: number | null;
  confidence: number | null;
  verdict_layer: number | null;
  topic_id: number | null;
  created_at: string;
  is_factcheck_post?: number; // 1 = PIB Telegram post, 0 = regular article
  content?: string; // For PIB posts
}

export interface FactCheckRef {
  id: number;
  source_name: string;
  claim_text: string;
  verdict: string;
  source_url: string | null;
}

export interface ArticleDetail extends Article {
  content: string | null;
  explanation: string | null;
  corroboration_count: number | null;
  corroborating_sources: string | null; // JSON string
  factcheck: FactCheckRef | null;
}

export interface VerdictMeta {
  label: string;
  color: string;        // Tailwind class
  textColor: string;
  borderColor: string;
  description: string;
}

export const VERDICT_META: Record<string, VerdictMeta> = {
  credible: {
    label: "Credible",
    color: "bg-emerald-50",
    textColor: "text-emerald-800",
    borderColor: "border-emerald-200",
    description: "Verified by multiple credible sources",
  },
  suspicious: {
    label: "Suspicious",
    color: "bg-amber-50",
    textColor: "text-amber-800",
    borderColor: "border-amber-200",
    description: "Limited corroboration found",
  },
  debunked: {
    label: "Debunked",
    color: "bg-red-50",
    textColor: "text-red-800",
    borderColor: "border-red-200",
    description: "Flagged by trusted fact-checkers",
  },
};

export const LAYER_LABELS: Record<number, string> = {
  1: "PIB / Alpha Defence",
  2: "Source consensus",
  3: "AI analysis",
};
