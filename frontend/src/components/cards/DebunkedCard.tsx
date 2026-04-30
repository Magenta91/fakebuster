"use client";

import Link from "next/link";
import { Article } from "@/types";
import { formatDistanceToNow } from "date-fns";

interface Props {
  article: Article;
}

export default function DebunkedCard({ article }: Props) {
  const timeAgo = article.published_at
    ? formatDistanceToNow(new Date(article.published_at), { addSuffix: true })
    : null;

  return (
    <Link href={`/article/${article.id}`}>
      <div className="group relative flex flex-col gap-3 rounded-2xl border border-red-100 bg-red-50 p-5 transition-all hover:border-red-200 hover:bg-red-100/60">
        {/* Debunked badge */}
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-red-100 border border-red-200 px-2.5 py-0.5 text-xs font-semibold text-red-800">
            <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
            Debunked
          </span>
          {article.verdict_layer === 1 && (
            <span className="text-xs text-red-600 font-medium">
              · Verified by fact-checker
            </span>
          )}
        </div>

        {/* Title */}
        <h3 className="text-sm font-semibold text-red-900 leading-snug line-clamp-3 group-hover:text-red-700 transition-colors">
          {article.title}
        </h3>

        {/* Meta */}
        <div className="flex items-center justify-between">
          <p className="text-xs text-red-500">
            {article.source_name}
            {timeAgo && <span className="ml-1">· {timeAgo}</span>}
          </p>
          {/* Don't show credibility score for PIB posts (official source) */}
          {!article.is_factcheck_post && article.credibility_score !== null && (
            <span className="text-xs font-semibold text-red-700">
              Credibility: {article.credibility_score.toFixed(1)}/10
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
