const metrics = [
  { label: "Jobs discovered", value: "—", note: "Connect a permitted source to begin" },
  { label: "Shortlisted", value: "—", note: "Explainable match scoring" },
  { label: "Applications", value: "—", note: "No applications submitted" },
  { label: "Interviews", value: "—", note: "Calendar integration not connected" },
];

const stages = [
  ["01", "Create your career profile", "Add verified experience, skills, projects, and preferences."],
  ["02", "Connect job sources", "Enable only sources and access methods permitted by their terms."],
  ["03", "Review matched opportunities", "See eligibility checks, fit scores, and reasons behind each match."],
  ["04", "Prepare applications", "Generate evidence-backed materials before enabling any submission workflow."],
];

export default function Home() {
  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand-mark">CP</div>
        <div className="brand-copy">
          <strong>CareerPilot</strong>
          <span>PERSONAL CAREER AGENT</span>
        </div>
        <nav aria-label="Main navigation">
          <a className="nav-item active" href="#overview">◫ <span>Overview</span></a>
          <a className="nav-item" href="#pipeline">⌕ <span>Job discovery</span></a>
          <a className="nav-item" href="#pipeline">▤ <span>Applications</span></a>
          <a className="nav-item" href="#setup">◎ <span>Career profile</span></a>
          <a className="nav-item" href="#setup">▦ <span>Interview center</span></a>
          <a className="nav-item" href="#setup">⚙ <span>Settings</span></a>
        </nav>
        <div className="sidebar-foot">
          <span className="status-dot" />
          Local workspace
          <small>Your data stays on this device</small>
        </div>
      </aside>

      <section className="content" id="overview">
        <header className="topbar">
          <div><span className="eyebrow">YOUR CAREER WORKSPACE</span><h1>Overview</h1></div>
          <div className="local-pill"><span className="status-dot" /> LOCAL MODE</div>
        </header>

        <section className="welcome">
          <div>
            <span className="eyebrow light">CAREERPILOT AI · FOUNDATION BUILD</span>
            <h2>A clearer path to<br />your next opportunity.</h2>
            <p>Build your verified career profile, discover relevant roles, and manage every application from one private workspace.</p>
            <a className="primary-button" href="#setup">Set up your workspace <span>→</span></a>
          </div>
          <div className="welcome-art" aria-hidden="true">
            <div className="orbit orbit-one" /><div className="orbit orbit-two" />
            <div className="orbit-core">✳</div>
            <div className="orbit-tag tag-top">DISCOVER</div>
            <div className="orbit-tag tag-bottom">PREPARE · TRACK</div>
          </div>
        </section>

        <section className="metric-grid" aria-label="Career metrics">
          {metrics.map((metric) => (
            <article className="metric-card" key={metric.label}>
              <span>{metric.label}</span><strong>{metric.value}</strong><small>{metric.note}</small>
            </article>
          ))}
        </section>

        <section className="lower-grid" id="pipeline">
          <article className="panel">
            <div className="panel-heading"><div><span className="eyebrow">GETTING STARTED</span><h3>Your setup journey</h3></div><span className="muted-tag">0 / 4 complete</span></div>
            <div className="steps">
              {stages.map(([number, title, description]) => (
                <div className="step" key={number}>
                  <span className="step-number">{number}</span>
                  <div><strong>{title}</strong><p>{description}</p></div>
                  <span className="step-state">PENDING</span>
                </div>
              ))}
            </div>
          </article>
          <article className="panel setup-panel" id="setup">
            <span className="eyebrow">SYSTEM STATUS</span><h3>Safe by default.</h3>
            <p>External actions are disabled until you configure and validate each integration.</p>
            <div className="status-row"><span>Backend API</span><span className="state pending">Not connected</span></div>
            <div className="status-row"><span>AI provider</span><span className="state">Not configured</span></div>
            <div className="status-row"><span>Browser automation</span><span className="state locked">Disabled</span></div>
            <div className="status-row"><span>Application submission</span><span className="state locked">Disabled</span></div>
            <div className="privacy-note"><span>◇</span><div><strong>Privacy first</strong><small>No resume or personal data has been uploaded.</small></div></div>
          </article>
        </section>
        <footer>CAREERPILOT AI <span>LOCAL-FIRST · BUILT FOR YOUR NEXT MOVE</span></footer>
      </section>
    </main>
  );
}
