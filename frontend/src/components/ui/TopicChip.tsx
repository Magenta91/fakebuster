"use client";

import clsx from "clsx";
import { Topic } from "@/types";

interface Props {
  topic: Topic;
  active: boolean;
  onClick: () => void;
}

export default function TopicChip({ topic, active, onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-all",
        active
          ? "border-indigo-300 bg-indigo-600 text-white shadow-sm"
          : "border-gray-200 bg-white text-gray-600 hover:border-indigo-200 hover:text-indigo-700"
      )}
    >
      {topic.region === "india" && (
        <span className="text-[10px]">🇮🇳</span>
      )}
      {topic.name}
      {topic.trend_score > 0 && (
        <span
          className={clsx(
            "rounded-full px-1.5 py-0.5 text-[10px] font-semibold",
            active ? "bg-indigo-500 text-white" : "bg-gray-100 text-gray-500"
          )}
        >
          {Math.round(topic.trend_score)}
        </span>
      )}
    </button>
  );
}
