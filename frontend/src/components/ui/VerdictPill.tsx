import { VERDICT_META, Verdict } from "@/types";
import clsx from "clsx";

interface Props {
  verdict: Verdict | null;
  layer?: number | null;
  size?: "sm" | "md";
}

const LAYER_LABELS: Record<number, string> = {
  1: "PIB / Alpha Defence",
  2: "Source consensus",
  3: "AI analysis",
};

export default function VerdictPill({ verdict, layer, size = "md" }: Props) {
  if (!verdict) return null;
  const meta = VERDICT_META[verdict];
  if (!meta) return null;

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full border font-medium",
        meta.color,
        meta.textColor,
        meta.borderColor,
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm"
      )}
    >
      <span
        className={clsx(
          "rounded-full",
          verdict === "credible" && "bg-emerald-500",
          verdict === "suspicious" && "bg-amber-500",
          verdict === "debunked" && "bg-red-500",
          size === "sm" ? "h-1.5 w-1.5" : "h-2 w-2"
        )}
      />
      {meta.label}
      {layer && (
        <span className="opacity-60">· {LAYER_LABELS[layer] ?? `Layer ${layer}`}</span>
      )}
    </span>
  );
}
