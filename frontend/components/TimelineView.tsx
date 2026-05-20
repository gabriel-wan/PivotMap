import React from "react";

type ProofNode = {
  status: "matched" | "weak" | "missing";
  requirement: {
    skill: string;
  };
  evidence?: Array<{
    title: string;
  }> | null;
  gap_action?: string | null;
  sources?: Array<{
    source_url: string;
    published_at: string;
  }>;
};

type ProofGraph = {
  nodes: ProofNode[];
};

type TimelineItem = {
  phase: "Prove" | "Learn" | "Build" | "Apply";
  title: string;
  date: string;
  sourceUrl?: string;
};

type TimelineViewProps = {
  graph: ProofGraph;
};

export default function TimelineView({ graph }: TimelineViewProps) {
  const items = buildTimeline(graph);

  return (
    <section aria-label="Proof roadmap timeline">
      {items.map((item, index) => (
        <article key={`${item.phase}-${index}`} style={{ marginBottom: 18 }}>
          <p style={{ margin: 0, fontWeight: 700 }}>{item.phase}</p>
          <p style={{ margin: "4px 0" }}>{item.title}</p>
          {item.sourceUrl ? (
            <a href={item.sourceUrl} style={{ color: "#2563eb" }}>
              {item.date}
            </a>
          ) : (
            <span>{item.date}</span>
          )}
        </article>
      ))}
    </section>
  );
}

function buildTimeline(graph: ProofGraph): TimelineItem[] {
  const now = new Date().toISOString().slice(0, 10);
  const items = graph.nodes.map((node): TimelineItem => {
    const source = node.sources?.[0];
    if (node.status === "matched") {
      return {
        phase: "Prove",
        title: node.evidence?.[0]?.title ?? node.requirement.skill,
        date: source?.published_at?.slice(0, 10) ?? now,
        sourceUrl: source?.source_url,
      };
    }
    if (node.status === "weak") {
      return {
        phase: "Build",
        title: node.gap_action ?? node.requirement.skill,
        date: source?.published_at?.slice(0, 10) ?? now,
        sourceUrl: source?.source_url,
      };
    }
    return {
      phase: "Learn",
      title: node.gap_action ?? node.requirement.skill,
      date: source?.published_at?.slice(0, 10) ?? now,
      sourceUrl: source?.source_url,
    };
  });

  items.push({
    phase: "Apply",
    title: "Submit the strongest matched proof nodes with the tailored resume.",
    date: now,
  });

  const phaseOrder = { Prove: 0, Learn: 1, Build: 2, Apply: 3 };
  return items.sort((left, right) => phaseOrder[left.phase] - phaseOrder[right.phase]);
}
