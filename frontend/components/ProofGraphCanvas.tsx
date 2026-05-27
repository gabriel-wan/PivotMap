import React from "react";
import ReactFlow, { Edge, Node } from "reactflow";

type ProofStatus = "matched" | "weak" | "missing";

type ProofNode = {
  requirement: {
    skill: string;
    category: string;
  };
  status: ProofStatus;
  resume_bullet?: string | null;
  gap_action?: string | null;
};

type ProofGraph = {
  nodes: ProofNode[];
  edges: Array<{
    source: string;
    target: string;
    label?: string;
  }>;
};

type ProofGraphCanvasProps = {
  graph: ProofGraph;
};

const nodeColours: Record<ProofStatus, string> = {
  matched: "#d9fbe5",
  weak: "#fff4bf",
  missing: "#ffd9d9",
};

const borderColours: Record<ProofStatus, string> = {
  matched: "#1f8f4d",
  weak: "#bd8b00",
  missing: "#c83b3b",
};

export default function ProofGraphCanvas({ graph }: ProofGraphCanvasProps) {
  const nodes: Node[] = graph.nodes.map((node, index) => ({
    id: node.requirement.skill,
    position: {
      x: (index % 3) * 280,
      y: Math.floor(index / 3) * 180,
    },
    data: {
      label: (
        <div style={{ maxWidth: 220 }}>
          <strong>{node.requirement.skill}</strong>
          <div style={{ marginTop: 6, fontSize: 12 }}>{node.status}</div>
        </div>
      ),
    },
    style: {
      background: nodeColours[node.status],
      border: `2px solid ${borderColours[node.status]}`,
      borderRadius: 8,
      color: "#15202b",
      padding: 12,
      width: 240,
    },
  }));

  const edges: Edge[] = graph.edges.map((edge, index) => ({
    id: `edge-${index}`,
    source: edge.source,
    target: edge.target,
    label: edge.label,
  }));

  return (
    <div style={{ width: "100%", height: 560 }}>
      <ReactFlow nodes={nodes} edges={edges} fitView />
    </div>
  );
}
