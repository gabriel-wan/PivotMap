import React from "react";
import ReactFlow, { Background, Controls, Edge, Node } from "reactflow";

type GapStatus = "matched" | "weak" | "missing";

export type CareerProofGraph = {
  user_id: string;
  sources: Array<{
    id: string;
    source_url: string;
    title: string;
    source_type: string;
  }>;
  evidence_nodes: Array<{
    id: string;
    kind: string;
    title: string;
    description: string;
    source_ids: string[];
  }>;
  claim_nodes: Array<{
    id: string;
    evidence_id: string;
    claim_text: string;
    confidence_status: string;
    confidence_score: number;
    source_ids: string[];
  }>;
  skill_nodes: Array<{
    id: string;
    skill: string;
    category: string;
    confidence_score: number;
    evidence_ids: string[];
    claim_ids: string[];
  }>;
  gap_nodes: Array<{
    id: string;
    target_role: string;
    requirement: string;
    status: GapStatus;
    recommended_action: string | null;
    linked_evidence_ids: string[];
    source_ids: string[];
  }>;
  trace_events: Array<{
    id: string;
    stage: string;
    message: string;
  }>;
};

type CareerGraphCanvasProps = {
  graph: CareerProofGraph;
};

const gapColours: Record<GapStatus, string> = {
  matched: "#e1f5ee",
  weak: "#faeeda",
  missing: "#faece7",
};

const gapBorders: Record<GapStatus, string> = {
  matched: "#1d9e75",
  weak: "#ba7517",
  missing: "#d85a30",
};

const gapLabels: Record<GapStatus, string> = {
  matched: "matched proof",
  weak: "needs stronger proof",
  missing: "missing proof",
};

export default function CareerGraphCanvas({ graph }: CareerGraphCanvasProps) {
  const evidenceNodes: Node[] = graph.evidence_nodes.map((node, index) => ({
    id: node.id,
    position: { x: 0, y: index * 135 },
    data: {
      label: <NodeLabel eyebrow="career evidence" title={node.title} detail={node.description} />,
    },
    style: baseStyle("#f2f9fd", "#2ea6d1"),
  }));

  const claimNodes: Node[] = graph.claim_nodes.map((node, index) => ({
    id: node.id,
    position: { x: 220, y: index * 135 },
    data: {
      label: (
        <NodeLabel
          eyebrow="proof claim"
          title={node.claim_text}
          detail={`${Math.round(node.confidence_score * 100)}% confidence`}
        />
      ),
    },
    style: baseStyle("#ffffff", "#8bbbd0"),
  }));

  const skillNodes: Node[] = graph.skill_nodes.map((node, index) => ({
    id: node.id,
    position: { x: 440, y: index * 135 },
    data: {
      label: (
        <NodeLabel
          eyebrow="proven skill"
          title={node.skill}
          detail={`${Math.round(node.confidence_score * 100)}% skill confidence`}
        />
      ),
    },
    style: baseStyle("#f0fbf6", "#1f8f4d"),
  }));

  const gapNodes: Node[] = graph.gap_nodes.map((node, index) => ({
    id: node.id,
    position: { x: 660, y: index * 135 },
    data: {
      label: (
        <NodeLabel
          eyebrow={gapLabels[node.status]}
          title={node.requirement}
          detail={node.recommended_action ?? node.target_role}
        />
      ),
    },
    style: baseStyle(gapColours[node.status], gapBorders[node.status]),
  }));

  const edges: Edge[] = [
    ...graph.claim_nodes.map((claim) => ({
      id: `evidence-${claim.evidence_id}-${claim.id}`,
      source: claim.evidence_id,
      target: claim.id,
      label: "supports",
      style: edgeStyle,
    })),
    ...graph.skill_nodes.flatMap((skill) =>
      skill.claim_ids.map((claimId) => ({
        id: `claim-${claimId}-${skill.id}`,
        source: claimId,
        target: skill.id,
        label: "proves",
        style: edgeStyle,
      })),
    ),
    ...graph.gap_nodes.flatMap((gap) =>
      gap.linked_evidence_ids.map((evidenceId) => ({
        id: `evidence-${evidenceId}-${gap.id}`,
        source: evidenceId,
        target: gap.id,
        label: gapLabels[gap.status],
        style: edgeStyle,
      })),
    ),
  ];

  return (
    <div style={{ width: "100%", height: "100%", minHeight: 300 }}>
      <ReactFlow
        nodes={[...evidenceNodes, ...claimNodes, ...skillNodes, ...gapNodes]}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.04 }}
        maxZoom={1.8}
        minZoom={0.35}
        nodesDraggable={false}
        panOnScroll
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#d8edf4" gap={22} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}

function NodeLabel({
  detail,
  eyebrow,
  title,
}: {
  detail: string;
  eyebrow: string;
  title: string;
}) {
  return (
    <div style={{ maxWidth: 162 }}>
      <div style={{ color: "#2e7f9f", fontSize: 10, fontWeight: 800, letterSpacing: 0.6, textTransform: "uppercase" }}>
        {eyebrow}
      </div>
      <strong style={{ display: "block", fontSize: 12, lineHeight: 1.3, marginTop: 5 }}>{title}</strong>
      <div style={{ color: "#64716f", fontSize: 10, lineHeight: 1.35, marginTop: 5, maxHeight: 40, overflow: "hidden" }}>{detail}</div>
    </div>
  );
}

function baseStyle(background: string, border: string) {
  return {
    background,
    border: `2px solid ${border}`,
    borderRadius: 12,
    boxShadow: "0 14px 32px rgba(46, 166, 209, 0.08)",
    color: "#15202b",
    padding: 10,
    width: 190,
  };
}

const edgeStyle = {
  stroke: "#9fb5b9",
  strokeWidth: 1.4,
};
