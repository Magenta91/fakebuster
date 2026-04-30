"use client";

import { useEffect, useState } from "react";
import { getDebunkedArticles } from "@/lib/api";
import { Article } from "@/types";
import DebunkedCard from "@/components/cards/DebunkedCard";

export default function DebunkedPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  const loadArticles = () => {
    setLoading(true);
    getDebunkedArticles({ limit: 50 })
      .then(setArticles)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadArticles();
  }, []);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-red-500 border-t-transparent" />
      </div>
    );
  }

  // Separate PIB Fact Check posts from regular debunked articles
  const pibPosts = articles.filter((a) => a.is_factcheck_post);
  const regularDebunked = articles.filter((a) => !a.is_factcheck_post);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-red-100 bg-red-50 px-6 py-5">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-red-100">
            <span className="text-lg">🚫</span>
          </div>
          <div>
            <h1 className="text-base font-bold text-red-900">Debunked News</h1>
            <p className="mt-0.5 text-sm text-red-600">
              These articles have been verified as false or misleading by trusted
              fact-checkers. Includes PIB Fact Check posts and articles matched
              against fact-checker databases.
            </p>
          </div>
        </div>
      </div>

      {/* Stats bar */}
      <div className="flex items-center gap-6 text-sm text-gray-500">
        <span>
          <strong className="text-red-700">{articles.length}</strong> debunked articles
        </span>
        <span className="text-gray-300">|</span>
        <span>{pibPosts.length} PIB posts, {regularDebunked.length} matched articles</span>
      </div>

      {/* Empty state */}
      {articles.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <span className="text-4xl mb-4">⏳</span>
          <p className="text-sm font-medium text-gray-600">
            No debunked articles yet
          </p>
          <p className="text-xs text-gray-400 mt-1 mb-4">
            The pipeline will populate this on the next scheduled run
          </p>
          <button
            onClick={loadArticles}
            className="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition"
          >
            Refresh
          </button>
        </div>
      ) : (
        <>
          {/* PIB Fact Check Posts */}
          {pibPosts.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                <span className="inline-block px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                  PIB Fact Check
                </span>
                Official Government Fact-Checks
              </h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {pibPosts.map((article) => (
                  <div
                    key={article.id}
                    className="rounded-xl border-2 border-blue-200 bg-blue-50 p-4 hover:shadow-md transition"
                  >
                    <div className="flex items-start gap-2 mb-2">
                      <span className="inline-block px-2 py-1 bg-blue-600 text-white text-xs font-semibold rounded">
                        PIB FACT CHECK
                      </span>
                    </div>
                    <h3 className="text-sm font-medium text-gray-900 mb-2 line-clamp-3">
                      {article.title}
                    </h3>
                    <p className="text-xs text-gray-600 mb-3 line-clamp-2">
                      {article.content}
                    </p>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>
                        {new Date(article.published_at).toLocaleDateString()}
                      </span>
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        View on Telegram →
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Regular Debunked Articles */}
          {regularDebunked.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-gray-700">
                Matched Against Fact-Checker Database
              </h2>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {regularDebunked.map((article) => (
                  <DebunkedCard key={article.id} article={article} />
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
