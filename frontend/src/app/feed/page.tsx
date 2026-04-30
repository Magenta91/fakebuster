"use client";

import { useEffect, useState } from "react";
import { getActiveTopics, getArticles } from "@/lib/api";
import { Article, Topic } from "@/types";
import ArticleCard from "@/components/cards/ArticleCard";
import TopicChip from "@/components/ui/TopicChip";

export default function FeedPage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [articles, setArticles] = useState<Article[]>([]);
  const [activeTopic, setActiveTopic] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getActiveTopics(), getArticles({ limit: 100 })])
      .then(([t, a]) => {
        setTopics(t);
        // Filter out PIB Fact Check posts and debunked articles from main feed
        const feedArticles = a.filter(
          (article) => !article.is_factcheck_post && article.verdict !== "debunked"
        );
        setArticles(feedArticles);
      })
      .finally(() => setLoading(false));
  }, []);

  const filtered = activeTopic
    ? articles.filter((a) => a.topic_id === activeTopic)
    : articles;

  // Categorize articles by credibility
  const verifiedNews = filtered.filter((a) => 
    a.credibility_score !== null && a.credibility_score >= 7.0
  );
  
  const suspiciousNews = filtered.filter((a) => 
    a.credibility_score !== null && a.credibility_score < 7.0
  );
  
  const pendingNews = filtered.filter((a) => 
    a.credibility_score === null || a.is_analyzed === 0
  );

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="flex gap-8">
      {/* Main content */}
      <div className="flex-1 min-w-0 space-y-8">
        {/* Topic filter bar */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h1 className="text-lg font-bold text-gray-900">Today's News</h1>
            <span className="text-xs text-gray-400">
              {articles.length} articles analyzed
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setActiveTopic(null)}
              className={`inline-flex items-center rounded-full border px-3 py-1.5 text-xs font-medium transition-all ${
                activeTopic === null
                  ? "border-indigo-300 bg-indigo-600 text-white"
                  : "border-gray-200 bg-white text-gray-600 hover:border-indigo-200"
              }`}
            >
              All topics
            </button>
            {topics.map((topic) => (
              <TopicChip
                key={topic.id}
                topic={topic}
                active={activeTopic === topic.id}
                onClick={() =>
                  setActiveTopic(activeTopic === topic.id ? null : topic.id)
                }
              />
            ))}
          </div>
        </div>

        {/* Empty state */}
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <span className="text-4xl mb-4">⏳</span>
            <p className="text-sm font-medium text-gray-600">
              No articles found
            </p>
            <p className="text-xs text-gray-400 mt-1 mb-4">
              Try selecting a different topic or wait for the pipeline to run
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition"
            >
              Refresh
            </button>
          </div>
        ) : (
          <div className="space-y-10">
            {/* Verified News Section */}
            {verifiedNews.length > 0 && (
              <section>
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-green-100">
                      <span className="text-base">✓</span>
                    </span>
                    <div>
                      <h2 className="text-sm font-semibold text-gray-900">
                        Verified News
                      </h2>
                      <p className="text-xs text-gray-500">
                        High credibility (7.0+/10) • {verifiedNews.length} articles
                      </p>
                    </div>
                  </div>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  {verifiedNews.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
                </div>
              </section>
            )}

            {/* Suspicious/Low Credibility Section */}
            {suspiciousNews.length > 0 && (
              <section>
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-red-100">
                      <span className="text-base">⚠️</span>
                    </span>
                    <div>
                      <h2 className="text-sm font-semibold text-gray-900">
                        Suspicious / Low Credibility
                      </h2>
                      <p className="text-xs text-gray-500">
                        Needs caution (below 7.0/10) • {suspiciousNews.length} articles
                      </p>
                    </div>
                  </div>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  {suspiciousNews.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
                </div>
              </section>
            )}

            {/* Pending Analysis Section */}
            {pendingNews.length > 0 && (
              <section>
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gray-100">
                      <span className="text-base">⏳</span>
                    </span>
                    <div>
                      <h2 className="text-sm font-semibold text-gray-900">
                        Pending Analysis
                      </h2>
                      <p className="text-xs text-gray-500">
                        Awaiting verification • {pendingNews.length} articles
                      </p>
                    </div>
                  </div>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  {pendingNews.map((article) => (
                    <ArticleCard key={article.id} article={article} />
                  ))}
                </div>
              </section>
            )}
          </div>
        )}
      </div>

      {/* Sidebar */}
      <aside className="hidden w-64 shrink-0 space-y-4 lg:block">
        {/* Stats Card */}
        <div className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
            News Categories
          </p>
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-green-500" />
                <span className="text-gray-700">Verified</span>
              </div>
              <span className="font-semibold text-green-700">{verifiedNews.length}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-red-500" />
                <span className="text-gray-700">Suspicious</span>
              </div>
              <span className="font-semibold text-red-700">{suspiciousNews.length}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-gray-400" />
                <span className="text-gray-700">Pending</span>
              </div>
              <span className="font-semibold text-gray-700">{pendingNews.length}</span>
            </div>
          </div>
        </div>

        {/* Info Card */}
        <div className="rounded-2xl border border-indigo-100 bg-indigo-50 p-4 space-y-2">
          <p className="text-xs font-semibold text-indigo-900">
            How we verify news
          </p>
          <ul className="space-y-1 text-xs text-indigo-700">
            <li>• Fact-check database matching</li>
            <li>• Multi-source consensus</li>
            <li>• AI credibility analysis</li>
          </ul>
        </div>
      </aside>
    </div>
  );
}
