import {
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type MutableRefObject,
  type ReactNode,
} from "react";

const commands = [
  "Modify my resume to fit this LinkedIn post",
  "Show me what skills I lack for this job, and the skill roadmap",
];

const modules = [
  ["BT2102", "Predictive Analytics"],
  ["CS1010S", "Programming Methodology"],
  ["DAO2702", "Data Management"],
  ["EC2104", "Management Economics"],
];

const requirements = [
  "Python",
  "SQL",
  "Data Visualization",
  "Dashboards",
  "Stakeholder Communication",
  "Business Analysis",
  "Problem Solving",
  "Tableau (nice to have)",
];

const actions = [
  ["Build a Tableau dashboard project", "High"],
  ["Add communication project or experience", "Medium"],
  ["Learn advanced SQL window functions", "Medium"],
];

const stats = [
  ["Strong", "5", "bg-pivot-teal"],
  ["Weak", "2", "bg-pivot-amber"],
  ["Missing", "1", "bg-pivot-coral"],
];

const steps = [
  {
    action: "Import modules",
    body: "Start with modules, projects, internships, and certifications. PivotMap keeps the raw evidence visible before any matching happens.",
    eyebrow: "Step 1",
    title: "Import your academic journey",
  },
  {
    action: "Parse JD",
    body: "The JD becomes requirement nodes: skills, categories, importance, and confidence. The target is explicit before matching proof.",
    eyebrow: "Step 2",
    title: "Paste job description",
  },
  {
    action: "View proof map",
    body: "Matched, weak, and missing evidence becomes a source-backed roadmap: what to prove now, what to build next, and what to learn before applying.",
    eyebrow: "Step 3",
    title: "Get your proof map",
  },
];

const logoTiles = [
  { kind: "module", title: "Module source" },
  { kind: "evidence", title: "Evidence box" },
  { kind: "school", title: "Student profile" },
  { kind: "linkedin", title: "LinkedIn post" },
];

const evidenceCards = [
  {
    className: "left-[5%] top-[24%] rotate-[-5deg]",
    label: "Module evidence",
    title: "BT2102 Predictive Analytics",
  },
  {
    className: "right-[6%] top-[22%] rotate-[4deg]",
    label: "LinkedIn post",
    title: "Data Analyst Intern",
  },
  {
    className: "left-[12%] bottom-[18%] rotate-[3deg]",
    label: "Proof node",
    title: "SQL matched with module project",
  },
  {
    className: "right-[12%] bottom-[20%] rotate-[-4deg]",
    label: "Roadmap action",
    title: "Build Tableau dashboard",
  },
];

export default function Home() {
  const [activeStep, setActiveStep] = useState(0);
  const [isDark, setIsDark] = useState(false);
  const prefersReducedMotion = usePrefersReducedMotion();
  const typedCommand = useTypedCommands(commands, prefersReducedMotion);
  const heroRef = useRef<HTMLElement | null>(null);
  const [scrollProgress, setScrollProgress] = useState(0);
  const active = steps[activeStep];
  const themeStyle = (isDark ? darkTheme : lightTheme) as CSSProperties;

  useEffect(() => {
    if (prefersReducedMotion) {
      setScrollProgress(0);
      return;
    }

    const updateProgress = () => {
      const hero = heroRef.current;
      if (!hero) return;

      const rect = hero.getBoundingClientRect();
      const distance = Math.max(rect.height - window.innerHeight * 0.35, 1);
      const raw = (window.innerHeight * 0.12 - rect.top) / distance;
      setScrollProgress(Math.min(Math.max(raw, 0), 1));
    };

    updateProgress();
    window.addEventListener("scroll", updateProgress, { passive: true });
    window.addEventListener("resize", updateProgress);

    return () => {
      window.removeEventListener("scroll", updateProgress);
      window.removeEventListener("resize", updateProgress);
    };
  }, [prefersReducedMotion]);

  return (
    <main className="min-h-screen bg-pivot-bg text-pivot-body transition-colors duration-300" style={themeStyle}>
      <nav className="sticky top-0 z-20 border-b border-pivot-border bg-pivot-paper/95">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8">
          <a className="flex items-center gap-2 text-pivot-ink" href="#">
            <span className="grid h-10 w-10 place-items-center rounded-[11px] bg-pivot-purple text-sm font-black tracking-[-0.04em] text-white">
              PM
            </span>
            <span className="text-[26px] font-black leading-none tracking-[-0.055em] text-pivot-ink">
              PivotMap
            </span>
          </a>
          <div className="hidden items-center gap-8 text-sm font-medium text-pivot-muted md:flex">
            <a className="hover:text-pivot-ink" href="#command">
              Command
            </a>
            <a className="hover:text-pivot-ink" href="#resume-proof">
              Resume proof
            </a>
            <a className="hover:text-pivot-ink" href="#console">
              Demo
            </a>
          </div>
          <div className="flex items-center gap-3">
            <button
              aria-label={`Switch to ${isDark ? "light" : "dark"} mode`}
              className="rounded-lg border border-pivot-border bg-pivot-paper px-4 py-2 text-sm font-semibold text-pivot-ink transition hover:bg-pivot-purple-soft"
              onClick={() => setIsDark((value) => !value)}
              type="button"
            >
              {isDark ? "Light" : "Dark"}
            </button>
            <button className="hidden rounded-lg bg-pivot-purple px-4 py-2 text-sm font-semibold text-white transition hover:bg-pivot-purple-mid sm:block">
              Map my fit
            </button>
          </div>
        </div>
      </nav>

      <CommandHero
        command={typedCommand}
        heroRef={heroRef}
        prefersReducedMotion={prefersReducedMotion}
        scrollProgress={scrollProgress}
      />

      <section id="console" className="mx-auto max-w-7xl px-5 pb-16 pt-10 sm:px-8">
        <div className="mb-8 max-w-3xl">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-pivot-purple">
            Product demo
          </p>
          <h2 className="mt-3 font-serif text-5xl leading-none text-pivot-ink sm:text-6xl">
            The proof map stays one click away.
          </h2>
        </div>

        <div className="grid min-h-[640px] items-center gap-10 lg:grid-cols-[1.1fr_0.8fr]">
          <div className="relative flex h-[560px] items-center rounded-[32px] border border-pivot-border bg-pivot-surface p-5 shadow-2xl shadow-pivot-purple/10 transition-colors duration-300">
            <div className="h-full w-full transition-all duration-300 ease-out" key={activeStep}>
              {activeStep === 0 ? <ModulesVisual /> : null}
              {activeStep === 1 ? <JobDescriptionVisual /> : null}
              {activeStep === 2 ? <ProofMapVisual /> : null}
            </div>
          </div>

          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-pivot-purple">
              {active.eyebrow}
            </p>
            <h3 className="mt-4 max-w-lg font-serif text-5xl leading-none text-pivot-ink sm:text-6xl">
              {active.title}
            </h3>
            <p className="mt-5 max-w-md text-lg font-light leading-8 text-pivot-muted">
              {active.body}
            </p>
            <button className="mt-7 rounded-xl bg-pivot-purple px-5 py-3 text-sm font-semibold text-white transition hover:bg-pivot-purple-mid">
              {active.action}
            </button>

            <div className="mt-12 space-y-5">
              {steps.map((step, index) => {
                const isActive = index === activeStep;
                return (
                  <button
                    className={`flex w-full items-center gap-4 rounded-2xl border p-4 text-left text-2xl font-semibold transition ${
                      isActive
                        ? "border-pivot-purple bg-pivot-purple-soft text-pivot-ink"
                        : "border-transparent text-pivot-muted/65 hover:border-pivot-border hover:bg-pivot-paper"
                    }`}
                    key={step.title}
                    onClick={() => setActiveStep(index)}
                    type="button"
                  >
                    <span
                      className={`grid h-8 w-8 place-items-center rounded-lg text-sm ${
                        isActive ? "bg-pivot-purple text-white" : "bg-pivot-paper text-pivot-purple"
                      }`}
                    >
                      {index + 1}
                    </span>
                    <span>{step.title}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <div id="sources" className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs font-semibold text-pivot-purple">
          <span>Powered by MiroFlow agents</span>
          <span>Live research</span>
          <span>Verified sources</span>
          <span>Proof graphs</span>
        </div>
      </section>

      <section id="workflow" className="mx-auto grid max-w-7xl gap-5 px-5 pb-20 sm:px-8 lg:grid-cols-3">
        {[
          ["1", "Parse the job", "The JD becomes requirement nodes with skill, category, importance, confidence, and source metadata."],
          ["2", "Map the evidence", "Modules, projects, internships, and claims are scored against each requirement as matched, weak, or missing."],
          ["3", "Export the roadmap", "The synthesiser returns resume bullets, learning actions, portfolio tasks, and source-backed timelines."],
        ].map(([number, title, body]) => (
          <article className="border-t border-pivot-border pt-5" key={title}>
            <p className="font-serif text-5xl italic text-pivot-purple">{number}</p>
            <h3 className="mt-4 text-xl font-semibold text-pivot-ink">{title}</h3>
            <p className="mt-3 leading-7 text-pivot-muted">{body}</p>
          </article>
        ))}
      </section>

      <ResumeProofPreview />
    </main>
  );
}

const lightTheme = {
  "--color-pivot-bg": "#FAFAF8",
  "--color-pivot-paper": "#FFFFFF",
  "--color-pivot-ink": "#111111",
  "--color-pivot-body": "#444441",
  "--color-pivot-muted": "#76746D",
  "--color-pivot-border": "rgba(17, 17, 17, 0.12)",
  "--color-pivot-purple": "#2ea6d1",
  "--color-pivot-purple-soft": "#eaf7fc",
  "--color-pivot-purple-mid": "#208bad",
  "--color-pivot-surface": "#f2f9fd",
};

const darkTheme = {
  "--color-pivot-bg": "#10100E",
  "--color-pivot-paper": "#171714",
  "--color-pivot-ink": "#F5F2EA",
  "--color-pivot-body": "#D7D2C8",
  "--color-pivot-muted": "#8C887F",
  "--color-pivot-border": "rgba(245, 242, 234, 0.13)",
  "--color-pivot-purple": "#5ec9ef",
  "--color-pivot-purple-soft": "rgba(46, 166, 209, 0.16)",
  "--color-pivot-purple-mid": "#8bd9f4",
  "--color-pivot-surface": "#151512",
};

function CommandHero({
  command,
  heroRef,
  prefersReducedMotion,
  scrollProgress,
}: {
  command: string;
  heroRef: MutableRefObject<HTMLElement | null>;
  prefersReducedMotion: boolean;
  scrollProgress: number;
}) {
  return (
    <section
      className="relative isolate min-h-[calc(100vh-65px)] overflow-hidden px-5 py-16 sm:px-8"
      id="command"
      ref={heroRef}
    >
      <div className="pointer-events-none absolute inset-0 opacity-55 [background-image:radial-gradient(var(--color-pivot-border)_1px,transparent_1px)] [background-size:22px_22px]" />

      <div className="pointer-events-none absolute inset-0 hidden lg:block">
        {evidenceCards.map((card, index) => (
          <EvidenceCard
            className={card.className}
            index={index}
            key={card.title}
            label={card.label}
            title={card.title}
          />
        ))}
      </div>

      <div className="relative z-10 mx-auto flex min-h-[calc(100vh-170px)] max-w-5xl flex-col items-center justify-center text-center">
        <div className="relative mb-[-8px] h-24 w-full max-w-xl">
          {logoTiles.map((tile, index) => (
            <LogoTile
              index={index}
              key={tile.title}
              prefersReducedMotion={prefersReducedMotion}
              progress={scrollProgress}
              tile={tile}
            />
          ))}
        </div>

        <div className="relative w-full max-w-4xl rounded-[28px] border border-pivot-border bg-pivot-paper p-3 shadow-2xl shadow-pivot-purple/10">
          <div className="min-h-[220px] rounded-[22px] bg-pivot-surface p-6 text-left sm:p-8">
            <p className="max-w-3xl text-3xl font-medium leading-tight text-pivot-ink sm:text-5xl">
              {command}
              <span className="typing-cursor ml-1 inline-block h-[1em] w-px translate-y-1 bg-pivot-ink" />
            </p>

            <div className="mt-14 flex items-end justify-between gap-4">
              <button
                aria-label="Add source"
                className="grid h-11 w-11 place-items-center rounded-full border border-pivot-border bg-pivot-paper text-2xl text-pivot-ink transition hover:bg-pivot-purple-soft"
                type="button"
              >
                +
              </button>
              <div className="flex items-center gap-3">
                <button
                  aria-label="Voice input"
                  className="grid h-11 w-11 place-items-center rounded-full border border-pivot-border bg-pivot-paper text-pivot-ink transition hover:bg-pivot-purple-soft"
                  type="button"
                >
                  <MicIcon />
                </button>
                <button
                  aria-label="Run proof map"
                  className="grid h-12 w-12 place-items-center rounded-full bg-pivot-ink text-pivot-bg transition hover:bg-pivot-purple"
                  type="button"
                >
                  <ArrowIcon />
                </button>
              </div>
            </div>
          </div>
        </div>

        <p className="mt-8 max-w-2xl text-base leading-7 text-pivot-muted sm:text-lg">
          Drop in a job post, transcript, module plan, or resume. PivotMap turns scattered evidence into a proof-backed career map.
        </p>
      </div>
    </section>
  );
}

function ResumeProofPreview() {
  return (
    <section className="mx-auto max-w-7xl px-5 pb-24 pt-4 sm:px-8" id="resume-proof">
      <div className="grid gap-5 rounded-[32px] border border-pivot-border bg-pivot-paper p-5 shadow-2xl shadow-pivot-purple/5 lg:grid-cols-[1.1fr_0.9fr] lg:p-8">
        <div className="relative rounded-none border-2 border-black bg-white p-3 shadow-[10px_10px_0_#111]">
          <div className="rounded-none bg-black p-6 text-white">
            <div className="flex flex-wrap items-start justify-between gap-4 border-b border-white/20 pb-5">
            <div>
              <p className="font-mono text-xs font-bold uppercase tracking-[0.22em] text-[#2ea6d1]">
                Resume proof
              </p>
              <h2 className="mt-3 font-serif text-5xl leading-none text-white">
                Data Analyst Intern
              </h2>
            </div>
            <span className="rounded-none border border-white px-3 py-1.5 font-mono text-xs font-bold uppercase text-white">
              verified
            </span>
          </div>

          <div className="mt-6 space-y-3">
            {[
              "Built predictive analytics workflow using BT2102 coursework, translating raw datasets into explainable model outputs.",
              "Applied SQL and Python to clean, join, and summarize business data for dashboard-ready analysis.",
              "Mapped weak Tableau evidence into a portfolio action with source-backed milestones.",
            ].map((bullet) => (
              <div className="flex gap-3 rounded-none border border-white/20 bg-white p-4 text-black" key={bullet}>
                <span className="mt-2 h-2.5 w-2.5 shrink-0 bg-[#2ea6d1]" />
                <p className="leading-7">{bullet}</p>
              </div>
            ))}
          </div>
          </div>
        </div>

        <div className="grid gap-4">
          <ProofSummaryCard count="5" label="matched evidence" tone="teal" />
          <ProofSummaryCard count="2" label="weak claims to build" tone="amber" />
          <ProofSummaryCard count="1" label="missing proof gap" tone="coral" />
          <div className="rounded-[24px] border border-pivot-border bg-pivot-bg p-5">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-pivot-muted">
              Source-backed labels
            </p>
            <div className="mt-4 flex flex-wrap gap-2">
              {["module evidence", "verified source", "roadmap action", "resume bullet"].map((label) => (
                <span className="rounded-full border border-pivot-border bg-pivot-paper px-3 py-1.5 text-xs font-semibold text-pivot-body" key={label}>
                  {label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function ModulesVisual() {
  return (
    <LightPanel title="NUSMods Planner" badge="Connected">
      <div className="space-y-2">
        {modules.map(([code, title]) => (
          <div className="flex items-center justify-between rounded-xl bg-pivot-paper p-3" key={code}>
            <div className="flex items-center gap-3">
              <span className="grid h-7 w-7 place-items-center rounded-md bg-pivot-purple text-[10px] font-bold text-white">
                OK
              </span>
              <div>
                <p className="text-sm font-bold text-pivot-ink">{code}</p>
                <p className="mt-0.5 text-xs text-pivot-muted">{title}</p>
              </div>
            </div>
            <span className="text-xs font-semibold text-pivot-muted">4 MC</span>
          </div>
        ))}
      </div>
      <p className="mt-4 text-xs font-semibold text-pivot-muted">
        + 2 more modules ready for verification
      </p>
    </LightPanel>
  );
}

function JobDescriptionVisual() {
  return (
    <LightPanel title="Data Analyst Intern" icon="JD">
      <p className="mb-4 text-sm font-bold text-pivot-ink">Key Requirements</p>
      <div className="grid gap-2 sm:grid-cols-2">
        {requirements.map((requirement) => (
          <span className="rounded-xl bg-pivot-purple-soft px-4 py-3 text-sm font-semibold text-pivot-body" key={requirement}>
            {requirement}
          </span>
        ))}
      </div>
      <div className="mt-5 rounded-2xl border border-pivot-border bg-pivot-paper p-4">
        <p className="text-xs font-bold uppercase tracking-[0.14em] text-pivot-muted">
          JD requirement node
        </p>
        <p className="mt-2 text-sm text-pivot-body">
          skill, importance, category, confidence, source pointers
        </p>
      </div>
    </LightPanel>
  );
}

function ProofMapVisual() {
  return (
    <LightPanel title="Your Proof Map">
      <div className="grid gap-6 md:grid-cols-[0.8fr_1fr]">
        <div className="flex items-center gap-5">
          <div className="relative grid h-28 w-28 shrink-0 place-items-center rounded-full border-[12px] border-pivot-purple bg-pivot-paper">
            <span className="font-serif text-4xl italic text-pivot-purple">78%</span>
            <span className="absolute -bottom-6 text-[10px] font-bold uppercase tracking-[0.1em] text-pivot-muted">
              overall fit
            </span>
          </div>
          <div className="flex-1 space-y-3">
            {stats.map(([label, value, color]) => (
              <div className="flex items-center justify-between gap-3 text-sm" key={label}>
                <span className="flex items-center gap-2 font-semibold text-pivot-body">
                  <span className={`h-2.5 w-2.5 rounded-full ${color}`} />
                  {label}
                </span>
                <span className="font-bold text-pivot-ink">{value}</span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <p className="mb-3 text-sm font-bold text-pivot-ink">Next Best Actions</p>
          <div className="space-y-2">
            {actions.map(([title, impact]) => (
              <div className="rounded-xl border border-pivot-border bg-pivot-paper p-3" key={title}>
                <p className="text-sm font-bold text-pivot-ink">{title}</p>
                <span className={`mt-1 inline-flex rounded-full px-2 py-1 text-[10px] font-bold ${
                  impact === "High"
                    ? "bg-pivot-teal-soft text-pivot-teal"
                    : "bg-pivot-amber-soft text-pivot-amber"
                }`}>
                  {impact} impact
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-7 grid gap-3 border-t border-pivot-border pt-5 sm:grid-cols-2">
        <MiniBar label="Python" tone="teal" width="w-4/5" />
        <MiniBar label="Data Analysis" tone="teal" width="w-3/4" />
        <MiniBar label="Tableau" tone="coral" width="w-1/4" />
        <MiniBar label="Stakeholder Communication" tone="coral" width="w-1/5" />
      </div>
    </LightPanel>
  );
}

function EvidenceCard({
  className,
  index,
  label,
  title,
}: {
  className: string;
  index: number;
  label: string;
  title: string;
}) {
  return (
    <div
      className={`evidence-card-float absolute w-56 rounded-2xl border border-pivot-border bg-pivot-paper/80 p-4 text-left shadow-xl shadow-pivot-purple/5 backdrop-blur ${className}`}
      style={{ animationDelay: `${index * 0.7}s` }}
    >
      <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-pivot-purple">
        {label}
      </p>
      <p className="mt-2 text-sm font-semibold leading-5 text-pivot-ink">{title}</p>
    </div>
  );
}

function LogoTile({
  index,
  prefersReducedMotion,
  progress,
  tile,
}: {
  index: number;
  prefersReducedMotion: boolean;
  progress: number;
  tile: { kind: string; title: string };
}) {
  const initialX = [-168, -56, 56, 168][index];
  const initialY = [0, -14, -14, 0][index];
  const convergeY = 390;
  const x = prefersReducedMotion ? initialX : initialX * (1 - progress);
  const y = prefersReducedMotion ? initialY : initialY + convergeY * progress;
  const rotate = prefersReducedMotion ? 0 : [-7, 4, -4, 7][index] * (1 - progress);
  const scale = prefersReducedMotion ? 1 : 1 - progress * 0.38;
  const opacity = prefersReducedMotion ? 1 : Math.max(1 - progress * 1.25, 0);

  return (
    <div
      aria-label={tile.title}
      className="logo-tile-float absolute left-1/2 top-0 grid h-20 w-20 place-items-center rounded-2xl border border-pivot-border bg-pivot-paper shadow-xl shadow-pivot-purple/10 transition-[opacity,transform] duration-150"
      style={{
        animationDelay: `${index * 0.18}s`,
        opacity,
        transform: `translate3d(calc(-50% + ${x}px), ${y}px, 0) rotate(${rotate}deg) scale(${scale})`,
      }}
    >
      <LogoMark kind={tile.kind} />
    </div>
  );
}

function LogoMark({ kind }: { kind: string }) {
  if (kind === "module") {
    return (
      <svg aria-hidden="true" className="h-12 w-12" fill="none" viewBox="0 0 64 64">
        <path
          d="M32 4 55 17.2v29.6L32 60 9 46.8V17.2L32 4Z"
          fill="none"
          stroke="#ff4c3b"
          strokeLinejoin="round"
          strokeWidth="7"
        />
        <path
          d="M20 43V23l12 14 12-14v20"
          stroke="#ff4c3b"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="7"
        />
      </svg>
    );
  }

  if (kind === "evidence") {
    return (
      <svg aria-hidden="true" className="h-14 w-14" fill="none" viewBox="0 0 64 64">
        <path d="M11 25 31 15l23 10-20 11-23-11Z" fill="#fff" stroke="#0B1020" strokeLinejoin="round" strokeWidth="4" />
        <path d="M11 25v23l22 10 21-11V25L33 36 11 25Z" fill="#fff" stroke="#0B1020" strokeLinejoin="round" strokeWidth="4" />
        <path d="M28 35c5-8 12-9 18-8-5 3-8 7-10 12" stroke="#D6A94B" strokeLinecap="round" strokeWidth="4" />
        <path d="M26 7 34 39M50 5 34 39" stroke="#fff" strokeLinecap="round" strokeWidth="6" />
        <path d="M26 7 34 39M50 5 34 39" stroke="#111" strokeLinecap="round" strokeWidth="3" />
      </svg>
    );
  }

  if (kind === "school") {
    return (
      <svg aria-hidden="true" className="h-12 w-12" fill="none" viewBox="0 0 64 64">
        <path d="M6 25 32 12l26 13-26 13L6 25Z" fill="#B8842E" />
        <path d="M18 34v10c7 5 21 5 28 0V34L32 41 18 34Z" fill="#111" />
        <path d="M51 28v15" stroke="#B8842E" strokeLinecap="round" strokeWidth="4" />
        <circle cx="51" cy="47" r="4" fill="#B8842E" />
      </svg>
    );
  }

  return (
    <svg aria-hidden="true" className="h-12 w-12" viewBox="0 0 64 64">
      <rect fill="#0A86C6" height="64" rx="13" width="64" />
      <circle cx="19" cy="18" fill="white" r="7" />
      <path d="M13 29h12v24H13V29Zm18 0h11v4.4c1.8-3 5-5.1 9.5-5.1 7.1 0 11.5 4.7 11.5 13.4V53H51V42.9c0-3.5-1.5-5.4-4.4-5.4-3.1 0-4.7 2.1-4.7 5.4V53H31V29Z" fill="white" />
    </svg>
  );
}

function ProofSummaryCard({
  count,
  label,
  tone,
}: {
  count: string;
  label: string;
  tone: "teal" | "amber" | "coral";
}) {
  const toneClass =
    tone === "teal"
      ? "bg-pivot-teal text-white"
      : tone === "amber"
        ? "bg-pivot-amber text-white"
        : "bg-pivot-coral text-white";

  return (
    <div className="flex items-center justify-between rounded-[24px] border border-pivot-border bg-pivot-bg p-5">
      <div>
        <p className="text-xs font-bold uppercase tracking-[0.14em] text-pivot-muted">
          {label}
        </p>
        <p className="mt-2 font-serif text-5xl italic text-pivot-ink">{count}</p>
      </div>
      <span className={`h-4 w-4 rounded-full ${toneClass}`} />
    </div>
  );
}

function LightPanel({
  badge,
  children,
  icon,
  title,
}: {
  badge?: string;
  children: ReactNode;
  icon?: string;
  title: string;
}) {
  return (
    <section className="h-full min-h-[500px] rounded-2xl border border-pivot-border bg-pivot-paper/90 p-5 shadow-xl shadow-pivot-purple/5 backdrop-blur transition-colors duration-300">
      <div className="mb-4 flex items-center justify-between gap-3">
        <p className="flex items-center gap-2 text-sm font-bold text-pivot-ink">
          {icon ? (
            <span className="grid h-7 w-7 place-items-center rounded-md bg-pivot-purple text-[10px] text-white">
              {icon}
            </span>
          ) : null}
          {title}
        </p>
        {badge ? (
          <span className="rounded-full bg-pivot-teal-soft px-2 py-1 text-[10px] font-bold text-pivot-teal">
            {badge}
          </span>
        ) : null}
      </div>
      {children}
    </section>
  );
}

function MiniBar({
  label,
  tone,
  width,
}: {
  label: string;
  tone: "teal" | "coral";
  width: string;
}) {
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[11px] font-semibold text-pivot-body">
        <span>{label}</span>
      </div>
      <div className="h-1.5 rounded-full bg-pivot-purple-soft">
        <div className={`h-full rounded-full ${width} ${tone === "teal" ? "bg-pivot-teal" : "bg-pivot-coral"}`} />
      </div>
    </div>
  );
}

function MicIcon() {
  return (
    <svg aria-hidden="true" className="h-5 w-5" fill="none" viewBox="0 0 24 24">
      <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Z" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
      <path d="M19 11a7 7 0 0 1-14 0M12 18v3M8 21h8" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
    </svg>
  );
}

function ArrowIcon() {
  return (
    <svg aria-hidden="true" className="h-5 w-5" fill="none" viewBox="0 0 24 24">
      <path d="M12 19V5M5 12l7-7 7 7" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
    </svg>
  );
}

function usePrefersReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setPrefersReducedMotion(query.matches);

    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  return prefersReducedMotion;
}

function useTypedCommands(values: string[], prefersReducedMotion: boolean) {
  const [text, setText] = useState(values[0]);

  useEffect(() => {
    if (prefersReducedMotion) {
      setText(values[0]);
      return;
    }

    let commandIndex = 0;
    let charIndex = 0;
    let deleting = false;
    let timeoutId: ReturnType<typeof setTimeout>;

    const tick = () => {
      const current = values[commandIndex];
      setText(current.slice(0, charIndex));

      if (!deleting && charIndex < current.length) {
        charIndex += 1;
        timeoutId = setTimeout(tick, 42);
        return;
      }

      if (!deleting && charIndex === current.length) {
        deleting = true;
        timeoutId = setTimeout(tick, 1500);
        return;
      }

      if (deleting && charIndex > 0) {
        charIndex -= 1;
        timeoutId = setTimeout(tick, 20);
        return;
      }

      deleting = false;
      commandIndex = (commandIndex + 1) % values.length;
      timeoutId = setTimeout(tick, 320);
    };

    timeoutId = setTimeout(tick, 250);
    return () => clearTimeout(timeoutId);
  }, [prefersReducedMotion, values]);

  return text;
}
