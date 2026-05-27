import React from "react";
import type { CareerProofGraph } from "./ProofGraphCanvas";

type TimelineItem = {
  phase: "Prove" | "Learn" | "Build" | "Apply";
  title: string;
  detail: string;
  sourceUrl?: string;
};

type TimelineViewProps = {
  graph: CareerProofGraph;
};

export default function TimelineView({ graph }: TimelineViewProps) {
  const sourceById = new Map(graph.sources.map((source) => [source.id, source]));
  const items = buildTimeline(graph, sourceById);

  return (
    <section aria-label="Career proof timeline" className="space-y-3">
      {items.map((item, index) => (
        <article
          className="rounded-2xl border border-pivot-border bg-pivot-paper p-4"
          key={`${item.phase}-${index}`}
        >
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-pivot-purple">
            {item.phase}
          </p>
          <p className="mt-2 text-sm font-semibold leading-5 text-pivot-ink">
            {item.title}
          </p>
          {item.sourceUrl ? (
            <a className="mt-2 block text-xs font-semibold text-pivot-purple" href={item.sourceUrl}>
              {item.detail}
            </a>
          ) : (
            <span className="mt-2 block text-xs font-medium text-pivot-muted">
              {item.detail}
            </span>
          )}
        </article>
      ))}
      {items.length === 0 ? (
        <p className="rounded-2xl border border-pivot-border bg-pivot-paper p-4 text-sm leading-6 text-pivot-muted">
          Roadmap actions will appear after you map a role or capture evidence.
        </p>
      ) : null}
    </section>
  );
}

function buildTimeline(
  graph: CareerProofGraph,
  sourceById: Map<string, CareerProofGraph["sources"][number]>,
): TimelineItem[] {
  const evidenceItems = graph.evidence_nodes.map((node): TimelineItem => {
    const source = sourceById.get(node.source_ids[0]);
    return {
      phase: "Prove",
      title: node.title,
      detail: source?.title ?? node.kind,
      sourceUrl: source?.source_url,
    };
  });

  const claimItems = graph.claim_nodes.map((node): TimelineItem => ({
    phase: "Prove",
    title: node.claim_text,
    detail: `${Math.round(node.confidence_score * 100)}% confidence`,
  }));

  const gapItems = graph.gap_nodes.map((node): TimelineItem => ({
    phase: node.status === "matched" ? "Apply" : node.status === "weak" ? "Build" : "Learn",
    title: node.recommended_action ?? node.requirement,
    detail:
      node.status === "matched"
        ? "matched proof"
        : node.status === "weak"
          ? "needs stronger proof"
          : "missing proof",
    sourceUrl: sourceById.get(node.source_ids[0])?.source_url,
  }));

  const order = { Prove: 0, Learn: 1, Build: 2, Apply: 3 };
  return [...evidenceItems, ...claimItems, ...gapItems].sort(
    (left, right) => order[left.phase] - order[right.phase],
  );
}
