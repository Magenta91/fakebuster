"use client";

import Link from "next/link";
import { Article } from "@/types";
import VerdictPill from "@/components/ui/VerdictPill";
import CredibilityMeter from "@/components/ui/CredibilityMeter";
import { formatDistanceToNow } from "date-fns";

interface Props {
  article: Article;
}

export default function ArticleCard({ article }: Props) {
  const timeAgo = article.published_at
    ? formatDistanceToNow(new Date(article.published_at), { addSuffix: true })
    : null;

  return (
    <Link href={`/article/${article.id}`}>
      <div className="group flex flex-col gap-3 rounded-2xl border border-gray-100 bg-white p-5 shadow-sm transition-all hover:border-gray-200 hover:shadow-md">
        {/* Header */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium uppercase tracking-wide text-gray-400 mb-1">
              {article.source_name}
              {timeAgo && <span className="ml-2 normal-case font-normal">· {timeAgo}</span>}
            </p>
            <h3 className="text-sm font-semibold text-gray-900 leading-snug line-clamp-3 group-hover:text-indigo-700 transition-colors">
              {article.title}
            </h3>
          </div>
          <VerdictPill verdict={article.verdict} size="sm" />
        </div>

        {/* Summary */}
        {article.summary && (
          <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">
            {article.summary}
          </p>
        )}

        {/* Score */}
        <CredibilityMeter 
          score={article.credibility_score} 
          confidence={article.confidence}
          hideForOfficialSource={article.is_factcheck_post}
        />
      </div>
    </Link>
  );
}
