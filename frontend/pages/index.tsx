export default function Home() {
  return (
    <main
      style={{
        minHeight: "100vh",
        padding: "48px",
        fontFamily:
          "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
        background: "#f7f8fb",
        color: "#172033",
      }}
    >
      <section style={{ maxWidth: "760px" }}>
        <p style={{ margin: 0, color: "#4b6475", fontWeight: 700 }}>
          PivotMap
        </p>
        <h1 style={{ fontSize: "48px", lineHeight: 1.05, margin: "12px 0" }}>
          Career proof maps for students.
        </h1>
        <p style={{ fontSize: "20px", lineHeight: 1.6, color: "#405166" }}>
          AI-powered requirement matching built on MiroFlow research agents,
          institution module adapters, and sourced proof graphs.
        </p>
      </section>
    </main>
  );
}
