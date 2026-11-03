"use client";

import { useEffect, useState, type FormEvent } from "react";

const API = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
type BoardLink = { provider: string; url: string; mode: string };
type GmailMessage = { id: string; thread_id?: string; from: string; to: string; subject: string; date: string; snippet: string; message_id_header?: string; references_header?: string };

export default function IntegrationsPage() {
  const [query, setQuery] = useState("AI Engineer");
  const [location, setLocation] = useState("Chennai");
  const [boards, setBoards] = useState<BoardLink[]>([]);
  const [boardNotice, setBoardNotice] = useState("");
  const [gmail, setGmail] = useState({ enabled: false, configured: false, connected: false });
  const [gmailQuery, setGmailQuery] = useState("newer_than:90d (recruiter OR interview OR application)");
  const [messages, setMessages] = useState<GmailMessage[]>([]);
  const [recipient, setRecipient] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [replyThreadId, setReplyThreadId] = useState("");
  const [replyInReplyTo, setReplyInReplyTo] = useState("");
  const [replyReferences, setReplyReferences] = useState("");
  const [applicationId, setApplicationId] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function request(path: string, init?: RequestInit) {
    const response = await fetch(`${API}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
    return data;
  }

  async function searchBoards(event?: FormEvent) {
    event?.preventDefault();
    setBusy(true);
    try {
      const data = await request(`/api/v1/integrations/job-boards?query=${encodeURIComponent(query)}&location=${encodeURIComponent(location)}`);
      setBoards(data.items || []);
      setBoardNotice(data.notice || "");
      setMessage("Search links are ready. Open a job board in your own browser session.");
    } catch (error) { setMessage(error instanceof Error ? error.message : "Could not create search links."); }
    finally { setBusy(false); }
  }

  async function refreshGmail() {
    try { setGmail(await request("/api/v1/gmail/status")); }
    catch (error) { setMessage(error instanceof Error ? error.message : "Gmail status unavailable."); }
  }

  async function connectGmail() {
    setBusy(true);
    try {
      const data = await request("/api/v1/gmail/auth/start", { method: "POST" });
      window.location.assign(data.authorization_url);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Could not start Gmail OAuth."); setBusy(false); }
  }

  async function searchMail(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      const data = await request(`/api/v1/gmail/messages?q=${encodeURIComponent(gmailQuery)}&max_results=25`);
      setMessages(data.items || []);
      setMessage(`Loaded ${(data.items || []).length} Gmail messages.`);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Gmail search failed."); }
    finally { setBusy(false); }
  }

  async function saveDraft(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      const data = await request("/api/v1/gmail/drafts", {
        method: "POST",
        body: JSON.stringify({ to: recipient.split(",").map(value => value.trim()), subject, body, thread_id: replyThreadId || undefined, in_reply_to: replyInReplyTo || undefined, references: replyReferences || undefined }),
      });
      setMessage(`Gmail draft saved (${data.id}).`);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Could not save draft."); }
    finally { setBusy(false); }
  }

  async function sendMail() {
    const confirmation = window.prompt("Type SEND EMAIL to send this message from your Gmail account.");
    if (confirmation !== "SEND EMAIL") return;
    setBusy(true);
    try {
      const data = await request("/api/v1/gmail/send", {
        method: "POST",
        body: JSON.stringify({ to: recipient.split(",").map(value => value.trim()), subject, body, thread_id: replyThreadId || undefined, in_reply_to: replyInReplyTo || undefined, references: replyReferences || undefined }),
      });
      setMessage(`Email sent. Gmail message ID: ${data.id}`);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Could not send email."); }
    finally { setBusy(false); }
  }

  async function prepareApplication() {
    const id = Number(applicationId);
    if (!Number.isInteger(id) || id <= 0) { setMessage("Enter a valid tracked application ID."); return; }
    setBusy(true);
    try {
      const data = await request(`/api/v1/browser/applications/${id}/prepare`, { method: "POST" });
      setMessage(`Opened ${data.page_title}. Filled: ${data.filled_fields.join(", ") || "none"}. Review the visible browser and complete missing fields yourself.`);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Could not prepare application."); }
    finally { setBusy(false); }
  }

  async function submitApplication() {
    const id = Number(applicationId);
    if (!Number.isInteger(id) || id <= 0) { setMessage("Enter a valid tracked application ID."); return; }
    const confirmation = window.prompt("This will click the submit button on the visible application page. Type SUBMIT APPLICATION to continue.");
    if (confirmation !== "SUBMIT APPLICATION") return;
    setBusy(true);
    try {
      const data = await request(`/api/v1/browser/applications/${id}/submit`, {
        method: "POST", body: JSON.stringify({ confirmation }),
      });
      setMessage(data.message || data.status);
    } catch (error) { setMessage(error instanceof Error ? error.message : "Could not submit application."); }
    finally { setBusy(false); }
  }

  useEffect(() => {\n    fetch(`${API}/api/v1/gmail/status`).then(response => response.json()).then(data => setGmail(data)).catch(() => undefined);\n  }, []);

  return (
    <main style={{ maxWidth: 1040, margin: "40px auto", padding: "0 22px 60px", color: "#e8edf5", fontFamily: "Arial, sans-serif" }}>
      <style>{`
        body{background:#0b1020} input,textarea{width:100%;box-sizing:border-box;background:#111a2e;color:#eef2ff;border:1px solid #33415e;border-radius:9px;padding:11px;margin-top:6px}
        button{background:#315bd6;color:white;border:0;border-radius:9px;padding:11px 15px;cursor:pointer;font-weight:600} button:disabled{opacity:.5}
        label{display:block;color:#b9c5da;font-size:13px;margin:12px 0} .panel{background:#111a2e;border:1px solid #273550;border-radius:16px;padding:22px;margin:18px 0}
        .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px} a{color:#8db6ff;overflow-wrap:anywhere}
        small,.muted{color:#91a0ba} h1{font-size:30px;margin-bottom:8px} h2{font-size:19px;margin:0 0 8px} .item{padding:12px 0;border-top:1px solid #273550}
      `}</style>
      <a href="/" style={{ textDecoration: "none" }}>← CareerPilot dashboard</a>
      <h1>CareerPilot integrations</h1>
      <p className="muted">Job-board search, browser-assisted application preparation and recruiter communication.</p>
      {message && <div className="panel" role="status">{message}</div>}

      <section className="panel">
        <h2>Job boards · LinkedIn, Naukri, Indeed and Foundit</h2>
        <p className="muted">Generate live search links using your keywords. Each site opens in your own authenticated browser session; no passwords are stored here.</p>
        <form onSubmit={searchBoards} className="grid">
          <label>Role or keywords<input value={query} onChange={e => setQuery(e.target.value)} required /></label>
          <label>Location<input value={location} onChange={e => setLocation(e.target.value)} required /></label>
          <div style={{ alignSelf: "end", paddingBottom: 12 }}><button disabled={busy}>Generate search links</button></div>
        </form>
        <div className="grid">{boards.map(board => <div className="item" key={board.provider}><strong>{board.provider}</strong><p><a href={board.url} target="_blank" rel="noreferrer">Open {board.provider} search ↗</a></p></div>)}</div>
        {boardNotice && <p className="muted">{boardNotice}</p>}
      </section>

      <section className="panel">
        <h2>Application assistant</h2>
        <p className="muted">Uses a visible local Chromium profile. It fills only basic verified profile fields; review the page, attach your resume and complete declarations manually.</p>
        <label>Tracked application ID<input type="number" min="1" value={applicationId} onChange={e => setApplicationId(e.target.value)} placeholder="Find this in Applications" /></label>
        <div className="grid">
          <button disabled={busy} onClick={() => void prepareApplication()}>Open page and fill safe fields</button>
          <button disabled={busy} onClick={() => void submitApplication()}>Confirm and click submit</button>
        </div>
        <p className="muted">Requires BROWSER_AUTOMATION_ENABLED=true, APPLICATION_SUBMISSION_ENABLED=true for submission, plus Playwright and Chromium. CAPTCHA, passwords, identity declarations and protected assessments are never automated.</p>
      </section>

      <section className="panel">
        <div className="grid" style={{ alignItems: "center" }}>
          <div><h2>Gmail recruiter communication</h2><p className="muted">Search recruiter threads, save drafts and send after explicit confirmation.</p></div>
          <div><strong>{gmail.connected ? "Connected" : gmail.configured ? "Not connected" : "Needs OAuth setup"}</strong><p><button disabled={busy || !gmail.configured} onClick={() => void connectGmail()}>{gmail.connected ? "Reconnect Gmail" : "Connect Gmail"}</button> <button onClick={() => void refreshGmail()}>Refresh</button></p></div>
        </div>
        <form onSubmit={searchMail}>
          <label>Gmail search query<input value={gmailQuery} onChange={e => setGmailQuery(e.target.value)} /></label>
          <button disabled={busy || !gmail.connected}>Search inbox</button>
        </form>
        {messages.map(item => <div className="item" key={item.id}><strong>{item.subject}</strong><p className="muted">{item.from} · {item.date}</p><p>{item.snippet}</p><button onClick={() => { setRecipient(item.from.match(/<([^>]+)>/)?.[1] || item.from); setSubject(item.subject.startsWith("Re:") ? item.subject : `Re: ${item.subject}`); setBody(`\n\nThank you for your email.\n`); setReplyThreadId(item.thread_id || ""); setReplyInReplyTo(item.message_id_header || ""); setReplyReferences([item.references_header, item.message_id_header].filter(Boolean).join(" ")); }}>Reply draft</button></div>)}
        <form onSubmit={saveDraft} style={{ marginTop: 20 }}>
          <h2>Compose recruiter email</h2>
          <label>To (comma-separated)<input value={recipient} onChange={e => setRecipient(e.target.value)} required /></label>
          <label>Subject<input value={subject} onChange={e => setSubject(e.target.value)} required /></label>
          <label>Message<textarea rows={7} value={body} onChange={e => setBody(e.target.value)} required /></label>
          <div className="grid"><button disabled={busy || !gmail.connected}>Save Gmail draft</button><button type="button" disabled={busy || !gmail.connected} onClick={() => void sendMail()}>Send after confirmation</button></div>
        </form>
      </section>
      <p className="muted">Local-first: OAuth tokens and browser profile stay on this machine. Keep this repository private before configuring real account credentials.</p>
    </main>
  );
}
