"use client";

import { useState } from "react";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface VerificationResult {
  headline: string;
  credibility_score: number;
  verdict: string;
  explanation: string;
  confidence: number;
}

export default function AskAIPage() {
  const [headline, setHeadline] = useState("");
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!headline.trim() || headline.trim().length < 10) {
      setError("Please enter a headline (at least 10 characters)");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await axios.post(`${API_URL}/chat/verify-headline`, {
        headline: headline.trim(),
      });
      setResult(response.data);
    } catch (err: any) {
      if (err.response?.status === 503) {
        setError("AI service is temporarily unavailable. The API quota may be exhausted. Please try again later.");
      } else {
        setError(err.response?.data?.detail || "Failed to verify headline. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 7) return "#10b981"; // green
    if (score >= 4.5) return "#f59e0b"; // amber
    return "#ef4444"; // red
  };

  const getVerdictColor = (verdict: string) => {
    switch (verdict) {
      case "verified":
      case "credible":
        return "bg-green-100 text-green-800 border-green-200";
      case "suspicious":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "debunked":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-indigo-100 bg-indigo-50 px-6 py-5">
        <div className="flex items-start gap-4">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-indigo-100">
            <span className="text-lg">🤖</span>
          </div>
          <div>
            <h1 className="text-base font-bold text-indigo-900">Ask AI</h1>
            <p className="mt-0.5 text-sm text-indigo-600">
              Paste any news headline and get instant credibility analysis powered by AI
            </p>
          </div>
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <label htmlFor="headline" className="block text-sm font-semibold text-gray-700 mb-2">
            Enter a news headline
          </label>
          <textarea
            id="headline"
            value={headline}
            onChange={(e) => setHeadline(e.target.value)}
            placeholder="e.g., Scientists discover new treatment for common disease"
            className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-100 resize-none"
            rows={4}
            maxLength={500}
            disabled={loading}
          />
          <div className="mt-2 flex items-center justify-between text-xs text-gray-400">
            <span>{headline.length}/500 characters</span>
            <span>Minimum 10 characters required</span>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || headline.trim().length < 10}
          className="w-full rounded-xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white transition-all hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
              Analyzing...
            </span>
          ) : (
            "Verify Headline"
          )}
        </button>
      </form>

      {/* Error Message */}
      {error && (
        <div className="rounded-2xl border-2 border-red-200 bg-red-50 p-5">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-4">
          {/* Verdict Badge */}
          <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-2">
                  Your headline
                </p>
                <p className="text-sm font-medium text-gray-900 leading-relaxed">
                  {result.headline}
                </p>
              </div>
              <span
                className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold capitalize ${getVerdictColor(
                  result.verdict
                )}`}
              >
                {result.verdict}
              </span>
            </div>

            {/* Credibility Score */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700">Credibility Score</span>
                <span
                  className="font-bold text-lg"
                  style={{ color: getScoreColor(result.credibility_score) }}
                >
                  {result.credibility_score.toFixed(1)} / 10
                </span>
              </div>
              <div className="h-3 w-full rounded-full bg-gray-100 overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${(result.credibility_score / 10) * 100}%`,
                    backgroundColor: getScoreColor(result.credibility_score),
                  }}
                />
              </div>
              <p className="text-xs text-gray-500">
                Confidence: {Math.round(result.confidence * 100)}%
              </p>
            </div>
          </div>

          {/* AI Explanation */}
          <div className="rounded-2xl border border-indigo-100 bg-indigo-50 p-5 space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-lg">💡</span>
              <p className="text-xs font-semibold uppercase tracking-wide text-indigo-400">
                AI Analysis
              </p>
            </div>
            <p className="text-sm text-indigo-900 leading-relaxed">
              {result.explanation}
            </p>
          </div>

          {/* Try Another */}
          <button
            onClick={() => {
              setHeadline("");
              setResult(null);
              setError("");
            }}
            className="w-full rounded-xl border-2 border-gray-200 bg-white px-6 py-3 text-sm font-semibold text-gray-700 transition-all hover:border-indigo-200 hover:bg-indigo-50"
          >
            Try Another Headline
          </button>
        </div>
      )}

      {/* Examples */}
      {!result && !loading && (
        <div className="rounded-2xl border border-gray-100 bg-white p-5 space-y-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">
            Example headlines to try
          </p>
          <div className="space-y-2">
            {[
              "Scientists discover new species in Amazon rainforest",
              "Local man wins lottery 10 times using secret formula",
              "Government announces new infrastructure development plan",
            ].map((example, i) => (
              <button
                key={i}
                onClick={() => setHeadline(example)}
                className="w-full text-left rounded-lg border border-gray-200 px-3 py-2 text-xs text-gray-600 hover:border-indigo-200 hover:bg-indigo-50 transition-all"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
