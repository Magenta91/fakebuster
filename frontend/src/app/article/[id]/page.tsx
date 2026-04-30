"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getArticle } from "@/lib/api";
import { ArticleDetail, LAYER_LABELS } from "@/types";
import VerdictPill from "@/components/ui/VerdictPill";
import CredibilityMeter from "@/components/ui/CredibilityMeter";
import { formatDistanceToNow, format } from "date-fns";

export default function ArticleDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [article, setArticle] = useState<ArticleDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    getArticle(Number(id))
      .then(setArticle)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="py-24 text-center">
        <p className="text-sm text-gray-500">Article not found.</p>
        <Link href="/feed" className="mt-2 inline-block text-xs text-indigo-600 hover:underline">
          ← Back to feed
        </Link>
      </div>
    );
  }

  const corroboratingSources: string[] = (() => {
    try {
      return JSON.parse(article.corroborating_sources || "[]");
    } catch {
      return [];
    }
  })();

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Back */}
      <Link href="/feed" className="text-xs text-gray-400 hover:text-indigo-600 transition-colors">
        ← Back to feed
      </Link>

      {/* Article header */}
      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-1 flex-1">
            <p className="text-xs font-medium uppercase tracking-wide text-gray-400">
              {article.source_name}
              {article.published_at && (
                <span className="ml-2 normal-case font-normal">
                  · {format(new Date(article.published_at), "dd MMM yyyy")}
                </span>
              )}
            </p>
            <h1 className="text-lg font-bold text-gray-900 leading-snug">
              {article.title}
            </h1>
          </div>
          <VerdictPill verdict={article.verdict} layer={article.verdict_layer} />
        </div>

        {/* Don't show credibility meter for PIB posts */}
        <CredibilityMeter 
          score={article.credibility_score} 
          confidence={article.confidence}
          hideForOfficialSource={article.is_factcheck_post}
        />

        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-xs text-indigo-600 hover:underline"
        >
          {article.is_factcheck_post ? "View on Telegram" : "Read original article"} ↗
        </a>
      </div>

      {/* PIB Fact Check Banner - Show for official government fact-checks */}
      {article.is_factcheck_post && (
        <div className="rounded-2xl border-2 border-blue-200 bg-blue-50 p-5 space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🇮🇳</span>
            <p className="text-sm font-bold text-blue-900">
              Official Government Fact-Check
            </p>
          </div>
          <p className="text-sm text-blue-700 leading-relaxed">
            This article was officially fact-checked and debunked by PIB Fact Check 
            (Press Information Bureau, Government of India). No additional verification needed.
          </p>
        </div>
      )}

      {/* Verdict explanation - LLM Commentary */}
      {article.explanation && (
        <div className="rounded-2xl border border-indigo-100 bg-indigo-50 p-5 space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-lg">💡</span>
            <p className="text-xs font-semibold uppercase tracking-wide text-indigo-400">
              AI Analysis - Why this rating?
            </p>
          </div>
          <p className="text-sm text-indigo-900 leading-relaxed">{article.explanation}</p>
        </div>
      )}

      {/* Verification chain - Don't show for PIB posts (they don't need verification) */}
      {!article.is_factcheck_post && (
        <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm space-y-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
            Verification chain
          </p>

          <div className="space-y-3">
            {/* Layer 1 */}
            <VerificationStep
              layer={1}
              label="Fact-checker database"
              active={article.verdict_layer === 1}
              success={article.verdict_layer === 1}
              detail={
                article.factcheck
                  ? `Matched: ${article.factcheck.source_name} — "${article.factcheck.claim_text.slice(0, 80)}..."`
                  : "No match found in PIB or Alpha Defence"
              }
            />

            {/* Layer 2 */}
            <VerificationStep
              layer={2}
              label="Source consensus"
              active={(article.verdict_layer ?? 0) >= 2}
              success={article.verdict_layer === 2}
              detail={
                corroboratingSources.length > 0
                  ? `Corroborated by: ${corroboratingSources.join(", ")}`
                  : article.corroboration_count === 0
                  ? "No corroborating sources found"
                  : `${article.corroboration_count} source(s) found`
              }
            />

            {/* Layer 3 */}
            <VerificationStep
              layer={3}
              label="AI analysis"
              active={(article.verdict_layer ?? 0) >= 3}
              success={article.verdict_layer === 3}
              detail="Gemini used to generate a plain-language explanation based on available evidence"
            />
          </div>
        </div>
      )}

      {/* Fact-check source card */}
      {article.factcheck && (
        <div className="rounded-2xl border border-red-100 bg-red-50 p-5 space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-red-400">
            Fact-checker source
          </p>
          <div className="space-y-1">
            <p className="text-sm font-semibold text-red-900">
              {article.factcheck.source_name}
            </p>
            <p className="text-sm text-red-700">{article.factcheck.claim_text}</p>
            <p className="text-xs text-red-500 capitalize">
              Verdict: <strong>{article.factcheck.verdict}</strong>
            </p>
          </div>
          {article.factcheck.source_url && (
            <a
              href={article.factcheck.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-red-600 hover:underline"
            >
              View original fact-check ↗
            </a>
          )}
        </div>
      )}

      {/* Article content */}
      {article.content && (
        <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
            Article content
          </p>
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
            {article.content.slice(0, 1500)}
            {article.content.length > 1500 && (
              <span className="text-gray-400">... [truncated]</span>
            )}
          </p>
        </div>
      )}
    </div>
  );
}

// ─── Sub-component ────────────────────────────────────────────────────────────

function VerificationStep({
  layer,
  label,
  active,
  success,
  detail,
}: {
  layer: number;
  label: string;
  active: boolean;
  success: boolean;
  detail: string;
}) {
  return (
    <div className={`flex gap-3 ${active ? "" : "opacity-40"}`}>
      <div className="flex flex-col items-center">
        <div
          className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
            success
              ? "bg-indigo-600 text-white"
              : active
              ? "bg-gray-200 text-gray-600"
              : "bg-gray-100 text-gray-400"
          }`}
        >
          {layer}
        </div>
        {layer < 3 && <div className="mt-1 h-4 w-px bg-gray-200" />}
      </div>
      <div className="pb-3">
        <p className="text-xs font-semibold text-gray-800">{label}</p>
        <p className="text-xs text-gray-500 mt-0.5">{detail}</p>
      </div>
    </div>
  );
}
