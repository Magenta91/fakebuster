"use client";

import { useEffect, useRef } from "react";
import { Chart, ArcElement, Tooltip, Legend, DoughnutController } from "chart.js";
import { Article } from "@/types";

Chart.register(ArcElement, Tooltip, Legend, DoughnutController);

interface Props {
  articles: Article[];
}

export default function VerdictChart({ articles }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    if (!canvasRef.current || articles.length === 0) return;

    const counts = { credible: 0, suspicious: 0, debunked: 0 };
    for (const a of articles) {
      if (a.verdict && a.verdict in counts) {
        counts[a.verdict as keyof typeof counts]++;
      }
    }

    if (chartRef.current) chartRef.current.destroy();

    chartRef.current = new Chart(canvasRef.current, {
      type: "doughnut",
      data: {
        labels: ["Credible", "Suspicious", "Debunked"],
        datasets: [
          {
            data: [counts.credible, counts.suspicious, counts.debunked],
            backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
            borderWidth: 0,
            hoverOffset: 4,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "70%",
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ${ctx.raw}`,
            },
          },
        },
      },
    });

    return () => chartRef.current?.destroy();
  }, [articles]);

  const counts = { credible: 0, suspicious: 0, debunked: 0 };
  for (const a of articles) {
    if (a.verdict && a.verdict in counts) {
      counts[a.verdict as keyof typeof counts]++;
    }
  }

  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-gray-400 mb-4">
        Verdict breakdown
      </p>
      <div className="flex items-center gap-6">
        <div className="relative h-24 w-24 flex-shrink-0">
          <canvas ref={canvasRef} />
        </div>
        <div className="space-y-2">
          {(
            [
              { key: "credible", label: "Credible", color: "#10b981" },
              { key: "suspicious", label: "Suspicious", color: "#f59e0b" },
              { key: "debunked", label: "Debunked", color: "#ef4444" },
            ] as const
          ).map(({ key, label, color }) => (
            <div key={key} className="flex items-center gap-2 text-xs">
              <span
                className="h-2.5 w-2.5 rounded-sm flex-shrink-0"
                style={{ backgroundColor: color }}
              />
              <span className="text-gray-600">{label}</span>
              <span className="ml-auto font-semibold text-gray-900">
                {counts[key]}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
