"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

type Profile = {
  full_name: string; email: string; phone: string; location: string; headline: string;
  professional_summary: string; current_role: string; target_roles: string[];
  preferred_locations: string[]; preferred_work_modes: string[]; minimum_salary: number | null;
  skills: string[]; tools_and_technologies: string[]; preferred_job_types: string[];
};
type Job = {
  id: number; title: string; company: string; location?: string | null; work_mode?: string | null;
  source: string; url?: string | null; required_skills: string[]; status: string;
};
type Match = { score: number; decision: string; matched_skills: string[]; missing_skills: string[]; reasons: string[] };
type Application = { id: number; job_id: number; status: string; notes: string; next_action?: string | null; follow_up_date?: string | null; job_title: string; company: string };
const emptyProfile: Profile = {
  full_name: "", email: "", phone: "", location: "", headline: "", professional_summary: "",
  current_role: "", target_roles: [], preferred_locations: [], preferred_work_modes: [],
  minimum_salary: null, skills: [], tools_and_technologies: [], preferred_job_types: [],
};

function splitList(value: string): string[] {
  return value.split(",").map((part) => part.trim()).filter(Boolean);
}

export default function Home() {
  const [section, setSection] = useState("overview");
  const [profile, setProfile] = useState<Profile>(emptyProfile);
  const [profileExists, setProfileExists] = useState(false);
  const [profileLoading, setProfileLoading] = useState(true);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [matches, setMatches] = useState<Record<number, Match>>({});
  const [message, setMessage] = useState("");
  const [apiOnline, setApiOnline] = useState(false);
  const [jobDraft, setJobDraft] = useState({ title: "", company: "", location: "Chennai", work_mode: "Hybrid", source: "manual", description: "", required_skills: "" });

  const loadProfile = useCallback(async () => {
    try {
      const response = await fetch(`${API}/api/v1/profile`);
      if (!response.ok) throw new Error("Could not load profile");
      const data = await response.json();
      if (data?.profile) {
        const p = data.profile;
        setProfile({ ...emptyProfile, ...p,
          target_roles: p.target_roles || [], preferred_locations: p.preferred_locations || [],
          preferred_work_modes: p.preferred_work_modes || [], skills: p.skills || [],
          tools_and_technologies: p.tools_and_technologies || [], preferred_job_types: p.preferred_job_types || [] });
        setProfileExists(true);
      }
      setApiOnline(true);
    } catch { setApiOnline(false); }
    finally { setProfileLoading(false); }
  }, []);

  const loadApplications = useCallback(async () => {
    try {
      const response = await fetch(`${API}/api/v1/applications`);
      if (!response.ok) throw new Error("Could not load applications");
      const data = await response.json();
      setApplications(data.items || []);
      setApiOnline(true);
    } catch { setApiOnline(false); }
  }, []);

  const loadJobs = useCallback(async () => {
    try {
      const response = await fetch(`${API}/api/v1/jobs`);
      if (!response.ok) throw new Error("Could not load jobs");
      const data = await response.json();
      setJobs(data.items || []);
      setApiOnline(true);
    } catch { setApiOnline(false); }
  }, []);

  useEffect(() => { void loadProfile(); void loadJobs(); void loadApplications(); }, [loadProfile, loadJobs, loadApplications]);

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setMessage("");
    const payload = { ...profile, years_experience: null, salary_currency: "INR",
      target_roles: profile.target_roles, preferred_locations: profile.preferred_locations,
      preferred_work_modes: profile.preferred_work_modes, skills: profile.skills,
      tools_and_technologies: profile.tools_and_technologies, preferred_job_types: profile.preferred_job_types };
    try {
      const response = await fetch(`${API}/api/v1/profile`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail?.[0]?.msg || data.detail || "Profile could not be saved");
      setProfileExists(true); setMessage("Your profile was saved locally on this device.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Could not connect to the API."); }
  }

  async function addJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setMessage("");
    try {
      const response = await fetch(`${API}/api/v1/jobs`, { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...jobDraft, required_skills: splitList(jobDraft.required_skills) }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Job could not be saved");
      setJobDraft({ title: "", company: "", location: "Chennai", work_mode: "Hybrid", source: "manual", description: "", required_skills: "" });
      setMessage("Job saved to your local opportunity list."); await loadJobs();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Could not save job."); }
  }

  async function trackJob(jobId: number) {
    try {
      const response = await fetch(`${API}/api/v1/applications`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ job_id: jobId, status: "saved" }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not track this job");
      setMessage("Job added to your application tracker."); await loadApplications();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Could not track job."); }
  }

  async function updateApplicationStatus(id: number, status: string) {
    try {
      const response = await fetch(`${API}/api/v1/applications/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not update tracker");
      setApplications(current => current.map(item => item.id === id ? { ...item, status: data.status } : item));
      setMessage("Application tracker updated.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Could not update application."); }
  }

  async function scoreJob(jobId: number) {
    try {
      const response = await fetch(`${API}/api/v1/jobs/${jobId}/match`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Could not calculate match");
      setMatches((current) => ({ ...current, [jobId]: data }));
    } catch (error) { setMessage(error instanceof Error ? error.message : "Match failed."); }
  }

  const nav = [
    ["overview", "Overview", "◫"], ["jobs", "Job discovery", "⌕"],
    ["applications", "Applications", "▤"], ["profile", "Career profile", "◎"],
    ["interviews", "Interview center", "▦"], ["settings", "Settings", "⚙"],
  ];
  const updateList = (key: "target_roles" | "preferred_locations" | "preferred_work_modes" | "skills" | "tools_and_technologies" | "preferred_job_types", value: string) =>
    setProfile((current) => ({ ...current, [key]: splitList(value) }));

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand-mark">CP</div><div className="brand-copy"><strong>CareerPilot</strong><span>PERSONAL CAREER AGENT</span></div>
        <nav aria-label="Main navigation">{nav.map(([id, label, icon]) =>
          <button key={id} className={`nav-item ${section === id ? "active" : ""}`} onClick={() => { setSection(id); setMessage(""); }}>
            {icon} <span>{label}</span>
          </button>)}</nav>
        <div className="sidebar-foot"><span className="status-dot" />Local workspace<small>Your candidate data stays on this device</small></div>
      </aside>
      <section className="content">
        <header className="topbar"><div><span className="eyebrow">YOUR CAREER WORKSPACE</span><h1>{nav.find(([id]) => id === section)?.[1]}</h1></div>
          <div className="local-pill"><span className={`status-dot ${apiOnline ? "" : "offline"}`} />{apiOnline ? "API CONNECTED" : "API OFFLINE"}</div></header>

        {message && <div className="notice" role="status">{message}</div>}

        {section === "overview" && <>
          <section className="welcome"><div><span className="eyebrow light">CAREERPILOT AI · LOCAL-FIRST</span>
            <h2>A clearer path to<br />your next opportunity.</h2>
            <p>Build your verified career profile, organize opportunities, and understand which roles fit your experience.</p>
            <button className="primary-button" onClick={() => setSection(profileExists ? "jobs" : "profile")}>{profileExists ? "Explore opportunities" : "Create your career profile"} <span>→</span></button>
          </div><div className="welcome-art" aria-hidden="true"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="orbit-core">✳</div><div className="orbit-tag tag-top">DISCOVER</div><div className="orbit-tag tag-bottom">PREPARE · TRACK</div></div></section>
          <section className="metric-grid"><article className="metric-card"><span>Jobs saved</span><strong>{jobs.length}</strong><small>Stored in your local database</small></article>
            <article className="metric-card"><span>Profile status</span><strong>{profileExists ? "Ready" : "—"}</strong><small>{profileExists ? "Candidate profile saved" : "Profile setup required"}</small></article>
            <article className="metric-card"><span>Matches scored</span><strong>{Object.keys(matches).length}</strong><small>Explainable fit assessments</small></article>
            <article className="metric-card"><span>Applications</span><strong>{applications.length}</strong><small>Tracked opportunities · no auto submission</small></article></section>
          <section className="lower-grid"><article className="panel"><span className="eyebrow">YOUR WORKFLOW</span><h3>Build your career pipeline</h3>
            {[["01","Complete your profile","Add verified skills, experience, and role preferences."],["02","Save job opportunities","Add jobs manually while source connectors are being built."],["03","Review match explanations","See matched skills, gaps, and fit reasons."],["04","Prepare applications","Keep submissions candidate-controlled and truthful."]].map(([n,t,d]) =>
              <div className="step" key={n}><span className="step-number">{n}</span><div><strong>{t}</strong><p>{d}</p></div><span className="step-state">READY</span></div>)}
          </article><article className="panel"><span className="eyebrow">SYSTEM STATUS</span><h3>Safe by default.</h3>
            <p>External job discovery and application submission are not enabled yet.</p>
            <div className="status-row"><span>Backend API</span><span className={apiOnline ? "state good" : "state pending"}>{apiOnline ? "Connected" : "Not connected"}</span></div>
            <div className="status-row"><span>Candidate profile</span><span className="state">{profileExists ? "Configured" : "Not configured"}</span></div>
            <div className="status-row"><span>Browser automation</span><span className="state locked">Disabled</span></div>
            <div className="status-row"><span>Auto submission</span><span className="state locked">Disabled</span></div>
            <div className="privacy-note"><span>◇</span><div><strong>Privacy first</strong><small>Profile and job records are stored locally.</small></div></div>
          </article></section>
        </>}

        {section === "profile" && <section className="panel form-panel"><div className="panel-heading"><div><span className="eyebrow">CANDIDATE DATA</span><h3>Your verified career profile</h3></div><span className="muted-tag">LOCAL STORAGE</span></div>
          <p className="form-intro">Only enter accurate information. This form saves to your local CareerPilot API, not to the GitHub repository.</p>
          {profileLoading ? <p>Loading profile…</p> : <form onSubmit={saveProfile} className="profile-form">
            <label>Full name<input required value={profile.full_name} onChange={e => setProfile({...profile, full_name:e.target.value})} /></label>
            <div className="form-two"><label>Email<input type="email" value={profile.email} onChange={e => setProfile({...profile,email:e.target.value})} /></label><label>Phone<input value={profile.phone} onChange={e => setProfile({...profile,phone:e.target.value})} /></label></div>
            <div className="form-two"><label>Current location<input value={profile.location} onChange={e => setProfile({...profile,location:e.target.value})} placeholder="e.g. Chennai, India" /></label><label>Current role<input value={profile.current_role} onChange={e => setProfile({...profile,current_role:e.target.value})} /></label></div>
            <label>Professional headline<input value={profile.headline} onChange={e => setProfile({...profile,headline:e.target.value})} placeholder="e.g. AI Engineer · GenAI · Backend" /></label>
            <label>Professional summary<textarea rows={3} value={profile.professional_summary} onChange={e => setProfile({...profile,professional_summary:e.target.value})} /></label>
            <label>Target roles <small>Separate multiple values with commas</small><input value={profile.target_roles.join(", ")} onChange={e => updateList("target_roles",e.target.value)} placeholder="AI Engineer, GenAI Engineer" /></label>
            <label>Preferred locations<input value={profile.preferred_locations.join(", ")} onChange={e => updateList("preferred_locations",e.target.value)} placeholder="Chennai, Bengaluru, Remote" /></label>
            <div className="form-two"><label>Work modes<input value={profile.preferred_work_modes.join(", ")} onChange={e => updateList("preferred_work_modes",e.target.value)} placeholder="Remote, Hybrid, On-site" /></label><label>Minimum salary (INR; same unit as job listings)<input type="number" min="0" value={profile.minimum_salary ?? ""} onChange={e => setProfile({...profile,minimum_salary:e.target.value ? Number(e.target.value) : null})} /></label></div>
            <label>Skills<input value={profile.skills.join(", ")} onChange={e => updateList("skills",e.target.value)} placeholder="Python, LLMs, RAG, FastAPI" /></label>
            <label>Tools and technologies<input value={profile.tools_and_technologies.join(", ")} onChange={e => updateList("tools_and_technologies",e.target.value)} placeholder="Next.js, PostgreSQL, Ollama" /></label>
            <label>Preferred job types<input value={profile.preferred_job_types.join(", ")} onChange={e => updateList("preferred_job_types",e.target.value)} placeholder="Full-time, Contract" /></label>
            <button className="submit-button" type="submit">Save profile locally</button>
          </form>}
        </section>}

        {section === "jobs" && <div className="jobs-layout"><section className="panel"><div className="panel-heading"><div><span className="eyebrow">OPPORTUNITY DATABASE</span><h3>Saved jobs <span className="count">{jobs.length}</span></h3></div><button className="small-button" onClick={() => void loadJobs()}>Refresh</button></div>
          {jobs.length === 0 ? <div className="empty-state"><strong>No opportunities saved yet</strong><p>Add a job using the form. External job-source connectors are the next development phase.</p></div> :
            <div className="job-list">{jobs.map(job => <article className="job-card" key={job.id}><div className="job-card-top"><div><strong>{job.title}</strong><p>{job.company} · {job.location || "Location not specified"}</p></div><span className="job-source">{job.source}</span></div>
              <div className="skill-chips">{job.required_skills.map(skill => <span key={skill}>{skill}</span>)}</div>
              <div className="job-actions"><span>{job.work_mode || "Work mode unspecified"}</span><button className="small-button" onClick={() => void scoreJob(job.id)}>Calculate match</button><button className="small-button" onClick={() => void trackJob(job.id)}>Track job</button>{job.url && <a href={job.url} target="_blank" rel="noreferrer">Open listing ↗</a>}</div>
              {matches[job.id] && <div className="match-result"><div className="score"><strong>{matches[job.id].score}</strong><small>/ 100 match</small></div><div><strong>{matches[job.id].decision.replace("_"," ")}</strong><p>{matches[job.id].reasons.join(" · ")}</p><p>Matched: {matches[job.id].matched_skills.join(", ") || "None"} · Gaps: {matches[job.id].missing_skills.join(", ") || "None"}</p></div></div>}
            </article>)}</div>}
        </section><section className="panel"><span className="eyebrow">MANUAL JOB CAPTURE</span><h3>Add an opportunity</h3><p className="form-intro">Save a role you found on a job board or company career page.</p>
          <form className="profile-form" onSubmit={addJob}><label>Job title<input required value={jobDraft.title} onChange={e => setJobDraft({...jobDraft,title:e.target.value})} /></label>
            <label>Company<input required value={jobDraft.company} onChange={e => setJobDraft({...jobDraft,company:e.target.value})} /></label>
            <label>Location<input value={jobDraft.location} onChange={e => setJobDraft({...jobDraft,location:e.target.value})} /></label>
            <label>Work mode<select value={jobDraft.work_mode} onChange={e => setJobDraft({...jobDraft,work_mode:e.target.value})}><option>Hybrid</option><option>Remote</option><option>On-site</option></select></label>
            <label>Required skills<input value={jobDraft.required_skills} onChange={e => setJobDraft({...jobDraft,required_skills:e.target.value})} placeholder="Python, FastAPI, RAG" /></label>
            <label>Job description<textarea rows={4} value={jobDraft.description} onChange={e => setJobDraft({...jobDraft,description:e.target.value})} /></label>
            <button className="submit-button" type="submit">Save opportunity</button></form>
        </section></div>}

        {section === "applications" && <section className="panel"><div className="panel-heading"><div><span className="eyebrow">APPLICATION TRACKER</span><h3>Your tracked opportunities <span className="count">{applications.length}</span></h3></div><button className="small-button" onClick={() => void loadApplications()}>Refresh</button></div>
          {applications.length === 0 ? <div className="empty-state"><strong>No tracked opportunities yet</strong><p>Open Job discovery and select “Track job” on an opportunity you want to follow.</p></div> :
            <div className="job-list">{applications.map(item => <article className="job-card" key={item.id}><div className="job-card-top"><div><strong>{item.job_title}</strong><p>{item.company}</p></div><span className="job-source">#{item.id}</span></div>
              <div className="application-controls"><label>Status<select value={item.status} onChange={event => void updateApplicationStatus(item.id,event.target.value)}>{["saved","shortlisted","preparing","applied","assessment","interview","offer","rejected","withdrawn"].map(status => <option key={status} value={status}>{status.replace("_"," ")}</option>)}</select></label><span className="application-note">Status changes are recorded locally. This does not submit an application.</span></div>
            </article>)}</div>}
        </section>}
        {section === "interviews" && <section className="panel empty-state"><span className="eyebrow">INTERVIEW CENTER</span><h3>Interview scheduling is not connected.</h3><p>Calendar integration and reminders will be added after the application tracker. Candidate participation in interviews and assessments remains manual.</p></section>}
        {section === "settings" && <section className="panel empty-state"><span className="eyebrow">LOCAL CONFIGURATION</span><h3>Integration controls</h3><p>API endpoint: <code>{API}</code></p><p>Browser automation, external account connections, and application submission remain disabled by default.</p></section>}
        <footer>CAREERPILOT AI <span>LOCAL-FIRST · BUILT FOR YOUR NEXT MOVE</span></footer>
      </section>
    </main>
  );
}
