"use client";

interface Props {
  score: number | null;   // 0–10 scale
  confidence?: number | null;
  hideForOfficialSource?: boolean;  // Hide for PIB posts
}

function getColor(score: number): string {
  if (score >= 7) return "#10b981";   // emerald - high credibility
  if (score >= 4.5) return "#f59e0b"; // amber - medium credibility
  return "#ef4444";                    // red - low credibility
}

export default function CredibilityMeter({ score, confidence, hideForOfficialSource }: Props) {
  // Don't show for official sources (PIB posts)
  if (hideForOfficialSource) return null;
  if (score === null || score === undefined) return null;
  
  const pct = Math.round((score / 10) * 100);
  const color = getColor(score);

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>Credibility score</span>
        <span className="font-semibold" style={{ color }}>
          {score.toFixed(1)} / 10
        </span>
      </div>
      <div className="h-2 w-full rounded-full bg-gray-100 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      {confidence != null && (
        <p className="text-xs text-gray-400">
          Confidence: {Math.round(confidence * 100)}%
        </p>
      )}
    </div>
  );
}
