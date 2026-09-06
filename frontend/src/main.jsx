import React, { Component, useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import './styles.css';

const API = '/api';
const SUBSCRIPTION_BUY_URL = import.meta.env.VITE_SUBSCRIPTION_BUY_URL || '';
const SUBSCRIPTION_PLANS = [
  {months:1, price:'৪১৯৯ ৳'},
  {months:3, price:'৭৭৯৯ ৳'},
  {months:6, price:'১১১৯৯ ৳'},
  {months:12, price:'১৭৯৯৯ ৳'}
];
const SUBJECTS = ['Mathematics', 'Physics', 'Chemistry'];
const SUBJECT_BN = { Mathematics: 'গণিত', Physics: 'পদার্থবিজ্ঞান', Chemistry: 'রসায়ন' };
const UI = {
  loading: 'পরীক্ষা সিস্টেম চালু হচ্ছে…',
  serverError: 'পরীক্ষা সার্ভারের সাথে সংযোগ করা যাচ্ছে না',
  retry: 'পুনরায় চেষ্টা করুন',
  studentName: 'শিক্ষার্থীর নাম',
  enterName: 'আপনার নাম লিখুন',
  buildExam: 'লিখিত পরীক্ষা তৈরি করুন',
  selectSubjects: 'বিষয়, অধ্যায় ও প্রশ্নসংখ্যা নির্বাচন করুন। পুরো পরীক্ষার জন্য একটি নির্দিষ্ট সময়সীমা প্রযোজ্য হবে।',
  question: 'প্রশ্ন',
  questions: 'প্রশ্ন',
  answered: 'উত্তর দেওয়া হয়েছে',
  submit: 'খাতা জমা দিন',
  submitConfirm: 'খাতা জমা দেবেন? জমা দেওয়ার পর আর পরিবর্তন করা যাবে না।',
  saveProgress: 'অগ্রগতি সংরক্ষণ',
  resumeExam: 'সংরক্ষিত পরীক্ষা চালিয়ে যান',
  noSavedExam: 'কোনো সংরক্ষিত পরীক্ষা পাওয়া যায়নি।',
  save: 'সংরক্ষণ',
  previous: 'পূর্ববর্তী',
  next: 'পরবর্তী',
  shortcuts: 'শর্টকাট',
  uploadAnswer: 'উত্তরের ছবি আপলোড করুন',
  examTime: 'পরীক্ষার সময় (মিনিট)',
  totalQuestions: 'মোট প্রশ্ন',
  startExam: 'পরীক্ষা শুরু করুন',
  offlineReview: 'অফলাইন পর্যালোচনা প্রতিবেদন',
  reviewDescription: 'AI মূল্যায়নের আগে আপনার উত্তরগুলো রেফারেন্স উত্তরের সঙ্গে মিলিয়ে দেখে নিজে নম্বর নির্ধারণ করুন।',
  selfEstimate: 'নিজস্ব মূল্যায়ন',
  submittedAnswer: 'আপনার জমা দেওয়া উত্তর',
  referenceAnswer: 'রেফারেন্স উত্তর',
  detailedSolution: 'বিস্তারিত সমাধান',
  noTypedAnswer: 'কোনো লিখিত উত্তর দেওয়া হয়নি।',
  referenceUnavailable: 'রেফারেন্স উত্তর পাওয়া যায়নি।',
  questionBank: 'প্রশ্নব্যাংক',
  edit: 'সম্পাদনা',
  archive: 'আর্কাইভ',
  addQuestion: '＋ প্রশ্ন যোগ করুন'
};

function Latex({ source }) {
  const parts = useMemo(() => {
    if (!source) return [];
    return source.split(/(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\$[^$\n]+\$|\\\([^\n]*?\))/g).filter(Boolean);
  }, [source]);

  const renderMath = (part, key) => {
    const isBlock = part.startsWith('\\[') && part.endsWith('\\]');
    const isMath = (part.startsWith('$$') && part.endsWith('$$')) ||
      (part.startsWith('$') && part.endsWith('$')) ||
      (part.startsWith('\\(') && part.endsWith('\\)')) || isBlock;
    let tex = part;
    if (!isMath) return null;
    if (isBlock) tex = part.slice(2, -2);
    else if (part.startsWith('$$')) tex = part.slice(2, -2);
    else if (part.startsWith('$')) tex = part.slice(1, -1);
    else tex = part.slice(2, -2);
    let html;
    try { html = katex.renderToString(tex, { displayMode: isBlock, throwOnError: false, strict: 'ignore' }); }
    catch { html = `<span class="latex-error">${tex.replace(/</g, '&lt;')}</span>`; }
    return <span key={key} className={isBlock ? 'latex-block' : 'latex-inline'} dangerouslySetInnerHTML={{ __html: html }} />;
  };

  // A lot of the curated question text uses compact TeX-like notation for units
  // without math delimiters (for example "4 m s^{-1}"). Render just those
  // exponent fragments as math so they remain readable without rewriting data.
  const renderPlain = (text, keyPrefix) => {
    // Curated imports sometimes contain TeX commands without $...$ delimiters.
    // Tokenize those fragments so expressions such as \hat i, \vec A, \Delta,
    // superscripts/subscripts, fractions and common functions render cleanly.
    const loose = /(\\(?:frac\{[^{}]+\}\{[^{}]+\}|sqrt\{[^{}]+\}|(?:hat|vec|bar|dot|ddot|tilde|overrightarrow|overline)\s*[A-Za-z][A-Za-z0-9]*|(?:alpha|beta|gamma|delta|theta|phi|psi|lambda|mu|nu|rho|sigma|omega|Delta|Sigma|Theta|Phi|Psi|Lambda|Omega)|(?:sin|cos|tan|cot|sec|csc|log|ln|lim)\b))|([A-Za-z0-9]+)\^\{([^{}]+)\}|([A-Za-z0-9]+)_\{([^{}]+)\}|([A-Za-z0-9]+)\^([0-9+-]+)/g;
    const chunks = [];
    let last = 0, m, n = 0;
    while ((m = loose.exec(text))) {
      if (m.index > last) chunks.push(<span key={`${keyPrefix}-t-${n++}`}>{text.slice(last, m.index)}</span>);
      let token = m[1];
      if (!token) token = m[2] ? `${m[2]}^{${m[3]}}` : m[4] ? `${m[4]}_{${m[5]}}` : `${m[6]}^{${m[7]}}`;
      chunks.push(renderMath(`$${token}$`, `${keyPrefix}-m-${n++}`));
      last = m.index + m[0].length;
    }
    if (last < text.length) chunks.push(<span key={`${keyPrefix}-t-${n++}`}>{text.slice(last)}</span>);
    return chunks.length ? chunks : [<span key={`${keyPrefix}-plain`}>{text}</span>];
  };

  return <>{parts.map((part, i) => renderMath(part, `math-${i}`) || renderPlain(part, `plain-${i}`))}</>;
}

class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(error) { return { error }; }
  render() {
    if (this.state.error) {
      return <div className="center"><div className="card loading-card"><div className="eyebrow">BUET AI EXAM ENGINE</div><h1>সামনের অংশে সমস্যা হয়েছে</h1><p className="muted error-text">{String(this.state.error?.message || this.state.error)}</p><button className="primary retry" onClick={() => window.location.reload()}>পুনরায় লোড করুন</button></div></div>;
    }
    return this.props.children;
  }
}

function App() {
  const initialRoute = ['question-bank','problems','written','settings','subscription'].includes(window.location.hash.slice(1)) ? window.location.hash.slice(1) : 'home';
  const [route, setRoute] = useState(initialRoute);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [authOpen, setAuthOpen] = useState(false);
  const adminMode = route === 'question-bank';
  useEffect(() => {
    const onHash = () => { const r=window.location.hash.slice(1); setRoute(['question-bank','problems','written','settings','subscription'].includes(r)?r:'home'); };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);
  const navigate = (next) => {
    window.location.hash = next === 'home' ? '' : next;
  };
  const [catalog, setCatalog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingError, setLoadingError] = useState('');
  const [name, setName] = useState('');
  const [config, setConfig] = useState({ Mathematics: 20, Physics: 0, Chemistry: 0 });
  const [chapterConfig, setChapterConfig] = useState({ Mathematics: null, Physics: null, Chemistry: null });
  const [duration, setDuration] = useState(60);
  const [attempt, setAttempt] = useState(null);
  const [answers, setAnswers] = useState({});
  const [current, setCurrent] = useState(0);
  const [secondsLeft, setSecondsLeft] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState(null);
  const [report, setReport] = useState(null);
  const [selfScores, setSelfScores] = useState(() => {
    try { return JSON.parse(localStorage.getItem('buet_self_scores') || '{}'); } catch (_) { return {}; }
  });
  const [uploading, setUploading] = useState(false);
  const saveTimer = useRef(null);
  const answersRef = useRef({});
  const submittingRef = useRef(false);
  const [saveState, setSaveState] = useState('');

  useEffect(() => { answersRef.current = answers; }, [answers]);
  useEffect(() => { try { localStorage.setItem('buet_self_scores', JSON.stringify(selfScores)); } catch (_) {} }, [selfScores]);

  async function loadCatalog() {
    setLoading(true); setLoadingError('');
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 6000);
    try {
      const r = await fetch(`${API}/questions/catalog`, { signal: controller.signal });
      if (!r.ok) throw new Error(`Backend returned HTTP ${r.status}`);
      const data = await r.json();
      setCatalog(data);
      const math = Math.min(20, Number(data?.available_by_subject?.Mathematics || 0));
      setConfig({ Mathematics: math, Physics: 0, Chemistry: 0 });
      setChapterConfig({ Mathematics: null, Physics: null, Chemistry: null });
    } catch (err) {
      setLoadingError(err?.name === 'AbortError' ? 'The backend did not respond within 6 seconds.' : `Could not connect to the exam server. ${err?.message || ''}`);
    } finally {
      clearTimeout(timeout); setLoading(false);
    }
  }

  useEffect(() => {
    fetch(`${API}/auth/me`, { credentials:'include' })
      .then(r => r.ok ? r.json() : null)
      .then(data => { if (data) { setUser(data); setName(data.name || ''); } })
      .catch(() => {})
      .finally(() => setAuthLoading(false));
  }, []);

  useEffect(() => { if (!adminMode) loadCatalog(); }, [adminMode]);

  useEffect(() => {
    const id = localStorage.getItem('buet_active_attempt_id');
    if (!id || attempt || !catalog) return;
    (async () => {
      try {
        const r = await fetch(`${API}/attempts/${id}`, { credentials:'include' });
        if (!r.ok) { localStorage.removeItem('buet_active_attempt_id'); return; }
        const data = await r.json();
        if (data.submitted) { localStorage.removeItem('buet_active_attempt_id'); return; }
        const restored={};
        Object.entries(data.answers||{}).forEach(([qid,a]) => restored[qid]={text:a.text||'',images:a.images||[],handwriting:a.handwriting||[],mode:a.mode||'typing'});
        setName(data.student_name || ''); setAttempt(data); setCatalog(prev=>({...prev,questions:data.questions||[]}));
        setAnswers(restored); answersRef.current=restored; setCurrent(0);
      } catch (_) {}
    })();
  }, [catalog, attempt]);

  useEffect(() => {
    if (!attempt || submitted) return;
    const id = setInterval(() => {
      if (!submittingRef.current) saveAllProgress();
    }, 10000);
    return () => clearInterval(id);
  }, [attempt, submitted]);

  useEffect(() => {
    if (!attempt) return;
    const end = new Date(attempt.ends_at).getTime();
    const tick = () => {
      const left = Math.max(0, Math.floor((end - Date.now()) / 1000));
      setSecondsLeft(left);
      if (left === 0 && !submittingRef.current) submit(true);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [attempt]);

  if (adminMode) return <AppShell route={route} navigate={navigate} user={user} onAuthClick={()=>setAuthOpen(true)} authOpen={authOpen} onAuthClose={()=>setAuthOpen(false)} onAuthSuccess={(u)=>{setUser(u);setName(u.name||'');setAuthOpen(false)}} onLogout={async()=>{await fetch(`${API}/auth/logout`,{method:'POST',credentials:'include'});setUser(null);setAuthOpen(false);localStorage.removeItem('buet_active_attempt_id');}}><QuestionBankAdmin onBack={() => navigate('written')} /></AppShell>;

  async function start() {
    if (!name.trim()) return alert('Enter your name first.');
    const selected = SUBJECTS.filter(s => Number(config[s]) > 0).map(subject => ({
      subject,
      count: Number(config[subject]),
      chapter_ids: (chapterConfig[subject] && chapterConfig[subject].length) ? chapterConfig[subject] : ['all']
    }));
    const total = selected.reduce((sum, x) => sum + x.count, 0);
    if (total < 1 || total > 60) return alert('Choose between 1 and 60 questions in total.');
    if (!duration || Number(duration) < 1) return alert('Enter a valid exam duration.');
    try {
      const r = await fetch(`${API}/exams/start`, { credentials:'include', method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ student_name:name.trim(), duration_minutes:Number(duration), subjects:selected }) });
      const data = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
      setAttempt(data); localStorage.setItem('buet_active_attempt_id', String(data.attempt_id)); setCatalog(prev => ({ ...prev, questions: data.questions })); setAnswers({}); answersRef.current = {}; setCurrent(0); setSecondsLeft(null); setSubmitted(false); setResult(null); setReport(null); setSelfScores({});
    } catch (e) { alert(`Could not start exam: ${e.message}`); }
  }

  async function saveAnswerForQuestion(questionId, answerState) {
    if (!attempt) return;
    await fetch(`${API}/attempts/${attempt.attempt_id}/answers/${questionId}`, { credentials:'include',
      method:'PUT', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({ answer_text: answerState?.text || '', handwriting_data: JSON.stringify(answerState?.handwriting || []), answer_mode: answerState?.mode || 'typing' })
    }).catch(() => {});
  }

  function updateAnswer(v) {
    const q = catalog.questions[current];
    const next = { ...(answersRef.current[q.id] || { images: [], handwriting: [] }), text: v, mode: 'typing' };
    const nextAll = { ...answersRef.current, [q.id]: next };
    answersRef.current = nextAll; setAnswers(nextAll);
    clearTimeout(saveTimer.current); saveTimer.current = setTimeout(() => saveAnswerForQuestion(q.id, next), 600);
  }

  function updateHandwriting(strokes) {
    const q = catalog.questions[current];
    const next = { ...(answersRef.current[q.id] || { text: '', images: [] }), handwriting: strokes, mode: 'handwriting' };
    const nextAll = { ...answersRef.current, [q.id]: next };
    answersRef.current = nextAll; setAnswers(nextAll);
    clearTimeout(saveTimer.current); saveTimer.current = setTimeout(() => saveAnswerForQuestion(q.id, next), 600);
  }

  function setAnswerMode(mode) {
    const q = catalog.questions[current];
    const next = { ...(answersRef.current[q.id] || { text: '', images: [], handwriting: [] }), mode };
    const nextAll = { ...answersRef.current, [q.id]: next };
    answersRef.current = nextAll; setAnswers(nextAll);
    clearTimeout(saveTimer.current); saveTimer.current = setTimeout(() => saveAnswerForQuestion(q.id, next), 150);
  }

  async function saveAllProgress() {
    if (!attempt || !catalog?.questions?.length) return;
    setSaveState('saving');
    try {
      const live=answersRef.current;
      await Promise.all(catalog.questions.map(q=>saveAnswerForQuestion(q.id, live[q.id] || {text:'',images:[],handwriting:[],mode:'typing'})));
      localStorage.setItem('buet_active_attempt_id', String(attempt.attempt_id));
      setSaveState('saved');
      setTimeout(()=>setSaveState(''),1800);
    } catch (_) { setSaveState('error'); }
  }

  async function saveCurrent() {
    if (!attempt || !catalog?.questions?.length) return;
    const q = catalog.questions[current];
    await saveAnswerForQuestion(q.id, answersRef.current[q.id] || { text: '', images: [], handwriting: [], mode: 'typing' });
  }

  async function uploadImages(e) {
    const files = [...e.target.files]; if (!files.length) return;
    const q = catalog.questions[current]; setUploading(true);
    try {
      for (const file of files) {
        if (!file.type.startsWith('image/')) continue;
        const form = new FormData(); form.append('file', file);
        const r = await fetch(`${API}/attempts/${attempt.attempt_id}/answers/${q.id}/images`, { credentials:'include', method:'POST', body:form });
        const data = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(data.detail || 'Upload failed');
        setAnswers(a => ({ ...a, [q.id]: { ...(a[q.id] || { text:'' }), images:[...(a[q.id]?.images || []), data.image_url] } }));
      }
    } catch (e) { alert(`Could not upload image: ${e.message}`); }
    finally { setUploading(false); e.target.value = ''; }
  }

  async function removeImage(url) {
    const q = catalog.questions[current];
    await fetch(`${API}/attempts/${attempt.attempt_id}/answers/${q.id}/images`, { credentials:'include', method:'DELETE', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ image_url:url }) }).catch(() => {});
    setAnswers(a => ({ ...a, [q.id]: { ...(a[q.id] || { text:'' }), images:(a[q.id]?.images || []).filter(x => x !== url) } }));
  }

  async function submit(auto=false) {
    if (submittingRef.current || !attempt) return;
    submittingRef.current = true;
    try {
      const live = answersRef.current;
      for (const q of catalog.questions) await saveAnswerForQuestion(q.id, live[q.id] || { text:'', images:[], handwriting:[], mode:'typing' });
      const sr = await fetch(`${API}/attempts/${attempt.attempt_id}/submit`, { credentials:'include', method:'POST' });
      if (!sr.ok) throw new Error(`Submit failed (HTTP ${sr.status})`);
      const rr = await fetch(`${API}/attempts/${attempt.attempt_id}/result`, { credentials:'include' });
      if (!rr.ok) throw new Error(`Report failed (HTTP ${rr.status})`);
      const reportData = await rr.json();
      setReport(reportData);
      setResult(reportData);
      localStorage.removeItem('buet_active_attempt_id');
      localStorage.setItem(`buet_submitted_${attempt.attempt_id}`, JSON.stringify(reportData));
      setSubmitted(true);
    } catch (e) {
      submittingRef.current = false;
      alert(auto ? `Time is up but submission failed: ${e.message}` : `Could not submit: ${e.message}`);
    }
  }

  const selectedTotal = SUBJECTS.reduce((sum, s) => sum + Number(config[s] || 0), 0);

  if (loading) return <div className="center"><div className="card loading-card"><div className="eyebrow">BUET AI EXAM ENGINE</div><h1>{UI.loading}</h1><div className="spinner" /></div></div>;
  if (loadingError || !catalog) return <div className="center"><div className="card loading-card"><div className="eyebrow">BUET AI EXAM ENGINE</div><h1>{UI.serverError}</h1><p className="muted error-text">{loadingError || 'কোনো প্রশ্নের ক্যাটালগ পাওয়া যায়নি।'}</p><button className="primary retry" onClick={loadCatalog}>{UI.retry}</button></div></div>;

  if (!attempt && route === 'problems') return <AppShell route={route} navigate={navigate} user={user} onAuthClick={()=>setAuthOpen(true)} authOpen={authOpen} onAuthClose={()=>setAuthOpen(false)} onAuthSuccess={(u)=>{setUser(u);setName(u.name||'');setAuthOpen(false)}} onLogout={async()=>{await fetch(`${API}/auth/logout`,{method:'POST',credentials:'include'});setUser(null);setAuthOpen(false);localStorage.removeItem('buet_active_attempt_id');}}><ProblemsPage user={user} onLogin={()=>setAuthOpen(true)} /></AppShell>;

  if (!attempt && route === 'settings') return <AppShell route={route} navigate={navigate} user={user} onAuthClick={()=>setAuthOpen(true)} authOpen={authOpen} onAuthClose={()=>setAuthOpen(false)} onAuthSuccess={(u)=>{setUser(u);setName(u.name||'');setAuthOpen(false)}} onLogout={async()=>{await fetch(`${API}/auth/logout`,{method:'POST',credentials:'include'});setUser(null);setAuthOpen(false);localStorage.removeItem('buet_active_attempt_id');}}><SettingsPage user={user} setUser={setUser} onLogout={async()=>{await fetch(`${API}/auth/logout`,{method:'POST',credentials:'include'});setUser(null);setAuthOpen(false);localStorage.removeItem('buet_active_attempt_id');navigate('home')}} onLogin={()=>setAuthOpen(true)} /></AppShell>;
  if (!attempt && route === 'subscription') return <AppShell route={route} navigate={navigate} user={user} onAuthClick={()=>setAuthOpen(true)} authOpen={authOpen} onAuthClose={()=>setAuthOpen(false)} onAuthSuccess={(u)=>{setUser(u);setName(u.name||'');setAuthOpen(false)}} onLogout={async()=>{await fetch(`${API}/auth/logout`,{method:'POST',credentials:'include'});setUser(null);setAuthOpen(false);localStorage.removeItem('buet_active_attempt_id');}}><SubscriptionPage user={user} /></AppShell>;

  if (!attempt) return <AppShell route={route} navigate={navigate} user={user} onAuthClick={()=>setAuthOpen(true)} authOpen={authOpen} onAuthClose={()=>setAuthOpen(false)} onAuthSuccess={(u)=>{setUser(u);setName(u.name||'');setAuthOpen(false)}} onLogout={async()=>{await fetch(`${API}/auth/logout`,{method:'POST',credentials:'include'});setUser(null);setAuthOpen(false);localStorage.removeItem('buet_active_attempt_id');}}>
    {route === 'home' ? <HomeDashboard navigate={navigate} hasSavedAttempt={Boolean(localStorage.getItem('buet_active_attempt_id'))} /> : !user ? <RequireLogin onLogin={()=>setAuthOpen(true)} /> : <Setup name={name} setName={setName} config={config} setConfig={setConfig} chapterConfig={chapterConfig} setChapterConfig={setChapterConfig} duration={duration} setDuration={setDuration} catalog={catalog} selectedTotal={selectedTotal} start={start} navigate={navigate} />}
  </AppShell>;
  if (submitted) return <OfflineReport report={report || result} selfScores={selfScores} setSelfScores={setSelfScores} />;

  const questions = catalog.questions || [];
  const q = questions[current];
  const answer = answers[q.id] || { text:'', images:[], handwriting:[], mode:'typing' };
  const answered = questions.filter(x => (answers[x.id]?.text || '').trim() || (answers[x.id]?.images || []).length || (answers[x.id]?.handwriting || []).length).length;
  const groups = SUBJECTS.map(subject => ({ subject, qs:questions.filter(x => x.subject===subject) })).filter(g => g.qs.length);
  const clock = secondsLeft == null ? '--:--' : `${String(Math.floor(secondsLeft/60)).padStart(2,'0')}:${String(secondsLeft%60).padStart(2,'0')}`;

  return <div className="app">
    <header><div className="brand"><strong>BUET লিখিত পরীক্ষা</strong><span>{name}</span></div><div className="top-meta"><span>{saveState==='saving'?'সংরক্ষণ হচ্ছে…':saveState==='saved'?'সংরক্ষিত ✓':''}</span><button className="save-progress" onClick={saveAllProgress}>{UI.saveProgress}</button><span>{questions.length}টি প্রশ্ন</span><div className={`timer ${secondsLeft !== null && secondsLeft < 300 ? 'danger' : ''}`}>{clock}</div><button className="submit" onClick={() => { if(confirm(UI.submitConfirm)) submit(false); }}>{UI.submit}</button></div></header>
    <div className="layout"><aside><div className="progress"><span>{UI.answered}</span><b>{answered}/{questions.length}</b></div><div className="subject-groups">{groups.map(group => <section key={group.subject}><div className="group-title">{SUBJECT_BN[group.subject]}</div><div className="grid">{group.qs.map(x => { const idx=questions.findIndex(y=>y.id===x.id); const done=(answers[x.id]?.text||'').trim()||(answers[x.id]?.images||[]).length||(answers[x.id]?.handwriting||[]).length; return <button key={x.id} className={`${idx===current?'active ':''}${done?'answered':''}`} onClick={()=>setCurrent(idx)}>{x.number}</button>; })}</div></section>)}</div><div className="shortcuts"><b>{UI.shortcuts}</b><br/>N = {UI.next} · P = {UI.previous} · S = {UI.save}</div></aside>
      <ExamMain q={q} answer={answer} current={current} total={questions.length} uploading={uploading} updateAnswer={updateAnswer} updateHandwriting={updateHandwriting} setAnswerMode={setAnswerMode} uploadImages={uploadImages} removeImage={removeImage} saveCurrent={saveCurrent} previous={()=>setCurrent(c=>Math.max(0,c-1))} next={()=>setCurrent(c=>Math.min(questions.length-1,c+1))} />
    </div>
  </div>;
}

function AppShell({ route, navigate, children, user, onAuthClick, onAuthSuccess, authOpen, onAuthClose, onLogout }) {
  return <div className="shell-page">
    <header className="app-shell-header">
      <button className="shell-brand" onClick={()=>navigate('home')}><span className="brand-mark">B</span><span><strong>BUET Written</strong><small>Engineering Practice Engine</small></span></button>
      <nav className="shell-nav" aria-label="Main navigation">
        <button className={route==='home'?'active':''} onClick={()=>navigate('home')}>Home</button>
        <button className={route==='written'?'active':''} onClick={()=>navigate('written')}>Written Exam</button>
        <button className={route==='question-bank'?'active':''} onClick={()=>navigate('question-bank')}>Question Bank</button>
        <button className={route==='problems'?'active':''} onClick={()=>navigate('problems')}>Problems</button>
        <button className={route==='settings'?'active':''} onClick={()=>navigate('settings')}>Settings</button>
        <button className={route==='subscription'?'active':''} onClick={()=>navigate('subscription')}>Subscription</button>
      </nav>
      {user ? <div className="account-menu"><span className="account-name">{user.name}</span><button className="login-btn" onClick={onLogout}>Log out</button></div> : <button className="login-btn" onClick={onAuthClick}>Log in / Sign up</button>}
    </header>
    <main className="shell-content">{children}</main>
    {authOpen && <AuthModal onClose={onAuthClose} onSuccess={onAuthSuccess} />}
  </div>;
}

function RequireLogin({ onLogin }) {
  return <div className="card auth-required"><div className="eyebrow">ACCOUNT REQUIRED</div><h1>Log in to use Written Exams</h1><p className="muted">Create an account with your name, Bangladeshi phone number, and password. Your exam attempts and saved progress will stay attached to your account.</p><button className="primary" onClick={onLogin}>Log in / Sign up</button></div>;
}

function AuthModal({ onClose, onSuccess }) {
  const [mode,setMode]=useState('login'); const [name,setName]=useState(''); const [phone,setPhone]=useState(''); const [password,setPassword]=useState(''); const [busy,setBusy]=useState(false); const [error,setError]=useState('');
  async function submit(){
    setBusy(true); setError('');
    try {
      const endpoint = mode==='login' ? '/auth/login' : '/auth/signup';
      const body = mode==='login' ? {phone,password} : {name,phone,password};
      const r=await fetch(`${API}${endpoint}`,{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      const d=await r.json().catch(()=>({})); if(!r.ok) throw new Error(d.detail||'Could not authenticate');
      onSuccess(d);
    } catch(e){ setError(e.message); } finally { setBusy(false); }
  }
  return <div className="modal-backdrop auth-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)onClose();}}><div className="modal auth-modal card"><div className="modal-head"><div><div className="eyebrow">BUET WRITTEN</div><h2>{mode==='login'?'Welcome back':'Create your account'}</h2></div><button className="tool-btn" onClick={onClose}>×</button></div><div className="auth-tabs"><button className={mode==='login'?'active':''} onClick={()=>setMode('login')}>Log in</button><button className={mode==='signup'?'active':''} onClick={()=>setMode('signup')}>Sign up</button></div>{mode==='signup'&&<label>Name<input value={name} onChange={e=>setName(e.target.value)} placeholder="Your name"/></label>}<label>Bangladeshi phone number<input value={phone} onChange={e=>setPhone(e.target.value)} placeholder="01712345678" inputMode="tel"/></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="At least 8 characters"/></label>{error&&<div className="auth-error">{error}</div>}<button className="primary auth-submit" disabled={busy} onClick={submit}>{busy?'Please wait…':mode==='login'?'Log in':'Create account'}</button><p className="auth-note">Your password is stored securely as a password hash. Never share it with anyone.</p></div></div>;
}

function HomeDashboard({ navigate, hasSavedAttempt }) {
  return <div className="home-page">
    <section className="hero-card card">
      <div className="hero-copy">
        <div className="eyebrow">BUET WRITTEN EXAM ENGINE</div>
        <h1>Practice like the real written exam.</h1>
        <p className="muted">Timed written mocks, chapter-based question selection, stylus handwriting, saved progress, and reference-answer review in one place.</p>
        <div className="hero-actions"><button className="primary" onClick={()=>navigate('written')}>Start Written Exam <span>→</span></button><button className="nav-btn" onClick={()=>navigate('question-bank')}>Explore Question Bank</button><button className="nav-btn premium-nav-btn" onClick={()=>{if(SUBSCRIPTION_BUY_URL) window.location.href=SUBSCRIPTION_BUY_URL; else navigate('subscription')}}>Subscription ↗</button></div>
      </div>
      <div className="hero-preview"><div className="preview-window"><div className="preview-top"><span></span><b>BUET Written</b><span>48:32</span></div><div className="preview-body"><div className="preview-rail"><i></i><i className="on"></i><i></i><i></i></div><div className="preview-paper"><small>Question 03 · Physics</small><strong>Find the acceleration of the block…</strong><div className="preview-lines"><span></span><span></span><span></span><span></span></div><div className="preview-pen">✎</div></div></div></div></div>
    </section>
    <section className="feature-grid">
      <article className="feature-card card"><span className="feature-icon">✍</span><h3>Write with a stylus</h3><p className="muted">Use a bounded paper-like answer area with pen, eraser, undo, and autosave.</p></article>
      <article className="feature-card card"><span className="feature-icon">◫</span><h3>Randomized papers</h3><p className="muted">Questions are shuffled within each subject so chapter blocks do not repeat predictably.</p></article>
      <article className="feature-card card"><span className="feature-icon">↺</span><h3>Resume anytime</h3><p className="muted">Your active attempt, order, and answers are saved so you can return after a refresh.</p></article>
    </section>
    {hasSavedAttempt && <div className="resume-banner card"><div><b>Saved exam found</b><span className="muted">You have an unfinished written exam.</span></div><button className="nav-btn" onClick={()=>navigate('written')}>Resume exam →</button></div>}
  </div>;
}

function Setup({ name,setName,config,setConfig,chapterConfig,setChapterConfig,duration,setDuration,catalog,selectedTotal,start,navigate }) {
  const papers = catalog.papers || {};

  const toggleSubject = (subject, checked) => {
    setConfig(c => ({ ...c, [subject]: checked ? 1 : 0 }));
    setChapterConfig(c => ({ ...c, [subject]: checked ? (c[subject] || ['all']) : [] }));
  };

  const availableForSelection = (subject) => {
    const selected = chapterConfig[subject];
    if (!selected || selected.length === 0 || selected.includes('all')) return Number(catalog.available_by_subject?.[subject] || 0);
    return selected.reduce((sum, id) => sum + Number(catalog.chapter_question_counts?.[`${subject}:${id}`] || 0), 0);
  };

  const updateCount = (subject, value) => setConfig(c => ({ ...c, [subject]: Number(value) }));

  const toggleChapter = (subject, id) => {
    setChapterConfig(prev => {
      const current = prev[subject] || ['all'];
      if (id === 'all') return { ...prev, [subject]: current.includes('all') ? [] : ['all'] };
      const next = current.filter(x => x !== 'all');
      const exists = next.includes(id);
      const updated = exists ? next.filter(x => x !== id) : [...next, id];
      return { ...prev, [subject]: updated.length ? updated : [] };
    });
  };

  useEffect(() => {
    SUBJECTS.forEach(subject => {
      const n = Number(config[subject] || 0);
      if (!n) return;
      const available = availableForSelection(subject);
      if (available && n > available) updateCount(subject, available);
    });
  }, [chapterConfig]);

  return <div className="center setup-center"><div className="setup setup-wide card">
    <div className="eyebrow">BUET AI EXAM ENGINE</div><button className="admin-link" onClick={() => navigate('question-bank')}>{UI.questionBank} →</button>
    <h1>{UI.buildExam}</h1>
    <p className="muted">{UI.selectSubjects}</p>
    <label>{UI.studentName}<input value={name} onChange={e=>setName(e.target.value)} placeholder={UI.enterName} /></label>

    <div className="subject-list">
      {SUBJECTS.map(subject => {
        const selected = Number(config[subject]) > 0;
        const chaptersByPaper = papers[subject] || [];
        const selectedChapters = chapterConfig[subject] || ['all'];
        const max = Math.max(1, Math.min(60, availableForSelection(subject)));
        return <div className={`subject-block ${selected ? 'selected' : ''}`} key={subject}>
          <div className="subject-row">
            <label className="check-wrap"><input type="checkbox" checked={selected} onChange={e=>toggleSubject(subject,e.target.checked)}/><span className="fake-check">✓</span></label>
            <div className="subject-name">{SUBJECT_BN[subject]}</div>
            <select value={selected ? Math.min(Number(config[subject]), max) : 0} disabled={!selected} onChange={e=>updateCount(subject,e.target.value)}>
              {!selected && <option value={0}>0 questions</option>}
              {selected && Array.from({length:max},(_,i)=><option key={i+1} value={i+1}>{i+1}টি {UI.question}</option>)}
            </select>
          </div>
          {selected && <div className="chapter-panel">
            <div className="chapter-toolbar">
              <div><b>অধ্যায়সমূহ</b><span>{selectedChapters.includes('all') ? 'সব অধ্যায়' : `${selectedChapters.length}টি নির্বাচিত`}</span></div>
              <button type="button" className={`chapter-toggle ${selectedChapters.includes('all') ? 'checked' : ''}`} aria-pressed={selectedChapters.includes('all')} onClick={()=>toggleChapter(subject,'all')}><span className="fake-check">✓</span> সব অধ্যায়</button>
            </div>
            {chaptersByPaper.map(paper => <div className="paper" key={paper.id}>
              <div className="paper-title">{paper.name}</div>
              <div className="chapter-grid">
                {paper.chapters.map(ch => {
                  const checked = selectedChapters.includes('all') || selectedChapters.includes(ch.id);
                  const count = Number(catalog.chapter_question_counts?.[`${subject}:${ch.id}`] || 0);
                  return <button type="button" className={`chapter-item ${checked ? 'checked' : ''} ${count===0 ? 'unavailable' : ''}`} aria-pressed={checked} disabled={selectedChapters.includes('all') || count===0} onClick={()=>toggleChapter(subject,ch.id)} key={ch.id}>
                    <span className="fake-check">✓</span>
                    <span>{ch.name}<small className="chapter-count">{count}টি প্রশ্ন</small></span>
                  </button>;
                })}
              </div>
            </div>)}
            <div className="chapter-note">নির্বাচিত অধ্যায়ে উপলব্ধ প্রশ্ন: <b>{availableForSelection(subject)}</b></div>
          </div>}
        </div>;
      })}
    </div>

    <small>প্রতিটি নির্বাচিত বিষয়ে কমপক্ষে ১টি প্রশ্ন থাকতে হবে। মোট প্রশ্নসংখ্যা ১ থেকে ৬০-এর মধ্যে হতে পারবে।</small>
    <label>{UI.examTime}<input type="number" min="1" max="600" value={duration} onChange={e=>setDuration(e.target.value)} /></label>
    <div className={`selection-total ${selectedTotal>=1 && selectedTotal<=60?'ok':'bad'}`}><span>{UI.totalQuestions}</span><b>{selectedTotal} / 60 max</b></div>
    <button className="primary start" disabled={selectedTotal<1 || selectedTotal>60} onClick={start}>{UI.startExam} <span>→</span></button>
    <small>{UI.shortcuts}: <b>N</b> {UI.next} · <b>P</b> {UI.previous} · <b>S</b> {UI.save}</small>
  </div></div>;
}

function HandwritingCanvas({ strokes, onChange, height, readOnly=false }) {
  const canvasRef = useRef(null);
  const drawingRef = useRef(null);
  const [tool, setTool] = useState('pen');
  const [size, setSize] = useState(2.2);

  const redraw = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    const sx = canvas.width / rect.width || 1;
    const sy = canvas.height / rect.height || 1;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#fffef9'; ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'rgba(90,130,170,.16)'; ctx.lineWidth = 1 * sx;
    const gap = 34 * sy;
    for (let y = gap; y < canvas.height; y += gap) { ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(canvas.width,y); ctx.stroke(); }
    (strokes || []).forEach(stroke => {
      if (!stroke.points?.length) return;
      ctx.beginPath(); ctx.lineCap='round'; ctx.lineJoin='round';
      ctx.strokeStyle = stroke.tool === 'eraser' ? '#fffef9' : '#172033';
      ctx.lineWidth = (stroke.size || 2.2) * sx;
      const pts=stroke.points; ctx.moveTo(pts[0].x*sx, pts[0].y*sy);
      for (let i=1;i<pts.length;i++) ctx.lineTo(pts[i].x*sx, pts[i].y*sy); ctx.stroke();
    });
  };
  useEffect(()=>{ const c=canvasRef.current; if(!c)return; const resize=()=>{const r=c.getBoundingClientRect();const d=window.devicePixelRatio||1;c.width=Math.max(1,Math.round(r.width*d));c.height=Math.max(1,Math.round(r.height*d));redraw();}; resize(); const ro=new ResizeObserver(resize); ro.observe(c); return()=>ro.disconnect(); },[]);
  useEffect(()=>{redraw();},[strokes,tool]);
  const pointFor=e=>{const r=canvasRef.current.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top,p:e.pressure||0.5};};
  const begin=e=>{if(readOnly)return;e.preventDefault();canvasRef.current.setPointerCapture?.(e.pointerId);drawingRef.current={tool,size:tool==='eraser'?Math.max(14,size*5):size,points:[pointFor(e)]};};
  const move=e=>{if(readOnly || !drawingRef.current)return;e.preventDefault();drawingRef.current.points.push(pointFor(e));redraw();};
  const end=e=>{if(readOnly || !drawingRef.current)return;e.preventDefault();const next=drawingRef.current.points.length>1?[...(strokes||[]),drawingRef.current]:(strokes||[]);drawingRef.current=null;onChange(next);};
  return <div className="handwriting-wrap">
    {!readOnly && <div className="handwriting-toolbar"><div className="tool-group"><button className={`tool-btn ${tool==='pen'?'active':''}`} onClick={()=>setTool('pen')}>✎ কলম</button><button className={`tool-btn ${tool==='eraser'?'active':''}`} onClick={()=>setTool('eraser')}>⌫ ইরেজার</button></div><label className="pen-size">আকার <input type="range" min="1" max="6" step="0.5" value={size} onChange={e=>setSize(Number(e.target.value))}/></label><div className="tool-group"><button className="tool-btn" onClick={()=>onChange((strokes||[]).slice(0,-1))} disabled={!strokes?.length}>↶</button><button className="tool-btn" onClick={()=>onChange([])} disabled={!strokes?.length}>মুছুন</button></div></div>}
    <canvas ref={canvasRef} className="handwriting-canvas" style={{height}} onPointerDown={begin} onPointerMove={move} onPointerUp={end} onPointerCancel={end}/>
    <div className="handwriting-hint">{readOnly?'আপনার জমা দেওয়া হাতে-লেখা সমাধান':'স্টাইলাস দিয়ে এই নির্ধারিত জায়গার ভিতরে লিখুন।'}</div>
  </div>;
}

function ExamMain({ q,answer,current,total,uploading,updateAnswer,updateHandwriting,setAnswerMode,uploadImages,removeImage,saveCurrent,previous,next }) {
  const mode=answer.mode||'typing';
  const answerHeight=Math.min(760,Math.max(300,260+Number(q.marks||5)*32));
  const sourceSession = q.source_session || q.source_year;
  const source = [q.source_exam, sourceSession ? `Session ${sourceSession}` : ''].filter(Boolean).join(' · ');
  return <main><div className="qmeta"><span>{SUBJECT_BN[q.subject]} · {UI.question} {q.number} / {total} · {q.marks} নম্বর</span>{source && <span className="question-source">সূত্র: {source}</span>}</div><div className="question"><Latex source={q.text} />{q.content_blocks?.filter(b=>b.type==='image' && String(b.content||'').startsWith('/')).map((b,i)=><img key={i} className="question-image" src={b.content} alt={b.alt||'Question diagram'} />)}</div>
    <div className="answer-panel"><div className="answer-panel-head"><div><strong>আপনার উত্তর</strong><span className="muted"> · {q.marks} নম্বরের জন্য নির্ধারিত জায়গা</span></div><div className="answer-toggle" role="tablist"><button className={mode==='handwriting'?'active':''} onClick={()=>setAnswerMode('handwriting')}>✍ হাতে লিখুন</button><button className={mode==='typing'?'active':''} onClick={()=>setAnswerMode('typing')}>⌨ টাইপ করুন</button></div></div>
      {mode==='typing'?<textarea className="typed-answer" autoFocus value={answer.text||''} onChange={e=>updateAnswer(e.target.value)} placeholder="এখানে আপনার সমাধান লিখুন…" style={{minHeight:answerHeight}}/>:<HandwritingCanvas strokes={answer.handwriting||[]} onChange={updateHandwriting} height={answerHeight}/>}</div>
    <div className="upload-row"><label className="upload"><input type="file" accept="image/*" multiple onChange={uploadImages}/>{uploading?'আপলোড হচ্ছে…':UI.uploadAnswer}</label><span className="muted">JPG, PNG, WEBP · অতিরিক্ত ডায়াগ্রাম/ছবি</span></div>{answer.images?.length?<div className="image-grid">{answer.images.map(url=><div className="image-card" key={url}><img src={url} alt="Uploaded answer"/><button onClick={()=>removeImage(url)}>×</button></div>)}</div>:null}<div className="nav"><button onClick={previous} disabled={current===0}>← {UI.previous}</button><button onClick={saveCurrent}>{UI.save}</button><button onClick={next} disabled={current===total-1}>{UI.next} →</button></div></main>;
}

function SubmittedHandwritingViewer({ strokes=[] }) {
  const viewportRef = useRef(null);
  const [x, setX] = useState(0);
  const [y, setY] = useState(0);
  const [scale, setScale] = useState(1.2);
  const [bounds, setBounds] = useState({x:0,y:0});
  const [viewport, setViewport] = useState({width:640,height:360});

  useEffect(() => {
    const update = () => {
      const r = viewportRef.current?.getBoundingClientRect();
      if (r) setViewport({width:r.width,height:Math.max(300, Math.min(520, r.height || 360))});
    };
    update(); const ro = new ResizeObserver(update); if(viewportRef.current) ro.observe(viewportRef.current); return () => ro.disconnect();
  }, []);

  const content = useMemo(() => {
    const pts = (strokes||[]).flatMap(s => s.points||[]);
    if (!pts.length) return {w:900,h:760};
    const maxX = Math.max(...pts.map(p=>Number(p.x)||0), 0);
    const maxY = Math.max(...pts.map(p=>Number(p.y)||0), 0);
    return {w:Math.max(900,maxX+80), h:Math.max(760,maxY+80)};
  }, [strokes]);

  useEffect(() => {
    setX(v => Math.min(v, Math.max(0, content.w*scale - viewport.width)));
    setY(v => Math.min(v, Math.max(0, content.h*scale - 300)));
  }, [content.w, content.h, scale, viewport.width]);

  const maxX = Math.max(0, content.w*scale - viewport.width);
  const maxY = Math.max(0, content.h*scale - 300);
  const canvasHeight = Math.max(300, Math.round(content.h*scale));
  const canvasWidth = Math.max(600, Math.round(content.w*scale));

  return <div className="submitted-viewer">
    <div className="submitted-viewer-viewport" ref={viewportRef}>
      <div className="submitted-viewer-stage" style={{width:canvasWidth, height:canvasHeight, transform:`translate(${-x}px, ${-y}px)`}}>
        <HandwritingCanvas strokes={strokes} height={canvasHeight} readOnly />
      </div>
    </div>
    <div className="viewer-controls">
      <label>X <input type="range" min="0" max={Math.max(1,Math.round(maxX))} value={Math.min(x,maxX)} onChange={e=>setX(Number(e.target.value))}/><output>{Math.round(x)}</output></label>
      <label>Y <input type="range" min="0" max={Math.max(1,Math.round(maxY))} value={Math.min(y,maxY)} onChange={e=>setY(Number(e.target.value))}/><output>{Math.round(y)}</output></label>
      <label>Zoom <input type="range" min="0.8" max="2" step="0.05" value={scale} onChange={e=>setScale(Number(e.target.value))}/><output>{Math.round(scale*100)}%</output></label>
      <button className="tool-btn" onClick={()=>{setX(0);setY(0);setScale(1.2)}}>Reset view</button>
    </div>
  </div>;
}

function OfflineReport({report, selfScores, setSelfScores}) {
  const questions = report?.questions || [];
  const [problemIds, setProblemIds] = useState(new Set());
  const [problemBusy, setProblemBusy] = useState('');
  useEffect(()=>{ fetch(`${API}/problems`,{credentials:'include'}).then(r=>r.ok?r.json():[]).then(rows=>setProblemIds(new Set((rows||[]).map(x=>x.question_id)))).catch(()=>{}); },[]);
  async function toggleProblem(questionId){
    setProblemBusy(String(questionId));
    const has=problemIds.has(questionId);
    try {
      const r=await fetch(`${API}/problems/${questionId}`,{method:has?'DELETE':'POST',credentials:'include'});
      if(!r.ok) throw new Error('Could not update problems');
      setProblemIds(prev=>{ const next=new Set(prev); has?next.delete(questionId):next.add(questionId); return next; });
    } catch(e){ alert(e.message); } finally { setProblemBusy(''); }
  }
  const selfTotal = Object.values(selfScores).reduce((s,v)=>s + (Number.isFinite(Number(v)) ? Number(v) : 0), 0);
  const maxTotal = report?.max_score ?? questions.reduce((s,q)=>s + q.max_score, 0);
  return <div className="report-page">
    <header className="report-head"><div><div className="eyebrow">পরীক্ষা জমা দেওয়া হয়েছে</div><h1>{UI.offlineReview}</h1><p className="muted">{UI.reviewDescription}</p></div><div className="report-score"><span>{UI.selfEstimate}</span><b>{selfTotal.toFixed(1)} / {maxTotal}</b></div></header>
    <div className="report-list">{questions.map(q => <article className="card report-card" key={q.question_id}>
      <div className="report-q-head"><div><div className="eyebrow">{UI.question} {q.number} · {SUBJECT_BN[q.subject]}</div><span className="muted">{q.max_score} নম্বর</span>{[q.source_exam,q.source_year,q.source_session].filter(Boolean).length>0 && <div className="report-source">সূত্র: {[q.source_exam, q.source_session || q.source_year ? `Session ${q.source_session || q.source_year}` : ''].filter(Boolean).join(' · ')}</div>}</div><label className="self-score">আপনার নম্বর / {q.max_score}<input type="number" min="0" max={q.max_score} step="0.5" value={selfScores[q.question_id] ?? ''} onChange={e=>setSelfScores(s=>({...s,[q.question_id]:e.target.value}))} /></label><button className={`problem-check ${problemIds.has(q.question_id)?'checked':''}`} onClick={()=>toggleProblem(q.question_id)} disabled={problemBusy===String(q.question_id)} aria-pressed={problemIds.has(q.question_id)}>{problemIds.has(q.question_id)?'✓ Saved to Problems':'＋ Save to Problems'}</button></div>
      <div className="report-question"><Latex source={q.question_text}/>{q.content_blocks?.filter(b=>b.type==='image' && String(b.content||'').startsWith('/')).map((b,i)=><img key={i} className="question-image" src={b.content} alt={b.alt||'Question diagram'} />)}</div>
      <div className="report-cols">
        <section><h3>{UI.submittedAnswer}</h3>{q.student_handwriting?.length ? <SubmittedHandwritingViewer strokes={q.student_handwriting} /> : q.student_answer?.trim() ? <div className="answer-box"><Latex source={q.student_answer}/></div> : <div className="empty-answer">{UI.noTypedAnswer}</div>}{q.student_images?.length ? <div className="report-images">{q.student_images.map(u=><img key={u} src={u} alt="Submitted answer"/>)}</div>:null}</section>
        <section><h3>{UI.referenceAnswer}</h3><div className="answer-box"><Latex source={q.reference_answer || UI.referenceUnavailable}/></div>{q.reference_solution ? <details className="ref-solution"><summary>{UI.detailedSolution}</summary><div className="answer-box"><Latex source={q.reference_solution}/></div></details>:null}</section>
      </div>
    </article>)}</div>
  </div>;
}

function ProblemsPage({user,onLogin}) {
  const [rows,setRows]=useState(null);
  const [subject,setSubject]=useState('All');
  const [paper,setPaper]=useState('All');
  const [chapter,setChapter]=useState('All');
  useEffect(()=>{ if(!user){setRows([]);return;} fetch(`${API}/problems`,{credentials:'include'}).then(r=>r.ok?r.json():[]).then(setRows).catch(()=>setRows([])); },[user]);
  const papers=useMemo(()=>['All',...Array.from(new Set((rows||[]).filter(q=>subject==='All'||q.subject===subject).map(q=>q.paper_id).filter(Boolean)))],[rows,subject]);
  const chapters=useMemo(()=>['All',...Array.from(new Set((rows||[]).filter(q=>(subject==='All'||q.subject===subject)&&(paper==='All'||q.paper_id===paper)).map(q=>q.chapter_id).filter(Boolean)))],[rows,subject,paper]);
  const filtered=useMemo(()=> (rows||[]).filter(q=>(subject==='All'||q.subject===subject)&&(paper==='All'||q.paper_id===paper)&&(chapter==='All'||q.chapter_id===chapter)),[rows,subject,paper,chapter]);
  if(!user) return <RequireLogin onLogin={onLogin}/>;
  return <div className="problems-page"><div className="page-hero card"><div><div className="eyebrow">YOUR SAVED PROBLEMS</div><h1>Problems</h1><p className="muted">Keep the questions you want to revisit. Filters stay account-specific.</p></div><div className="problem-count">{filtered.length}<span>saved</span></div></div>
    <section className="card problem-filters"><div className="problem-filter-title"><div><b>Filter problems</b><span>Refine by subject, paper and chapter</span></div><button className="nav-btn" onClick={()=>{setSubject('All');setPaper('All');setChapter('All')}}>Reset</button></div><div className="problem-filter-grid">
      <label>Subject<select value={subject} onChange={e=>{setSubject(e.target.value);setPaper('All');setChapter('All')}}><option>All</option>{SUBJECTS.map(s=><option key={s}>{s}</option>)}</select></label>
      <label>Paper<select value={paper} onChange={e=>{setPaper(e.target.value);setChapter('All')}}>{papers.map(x=><option key={x} value={x}>{x==='All'?'All papers':x}</option>)}</select></label>
      <label>Chapter<select value={chapter} onChange={e=>setChapter(e.target.value)}>{chapters.map(x=><option key={x} value={x}>{x==='All'?'All chapters':x}</option>)}</select></label>
    </div></section>
    {rows===null?<div className="card loading-card"><h2>Loading problems…</h2><div className="spinner"/></div>:filtered.length===0?<div className="card empty-problems"><div className="feature-icon">✓</div><h2>{rows.length?'No problems match these filters':'No saved problems yet'}</h2><p className="muted">{rows.length?'Try another subject, paper or chapter.':'After an exam, use “Save to Problems” on questions you want to practice again.'}</p></div>:<div className="problem-grid">{filtered.map(q=><article className="card problem-card" key={q.id}><div className="problem-top"><span>{SUBJECT_BN[q.subject]} · {q.source_exam||'Question'}</span>{q.source_year&&<span>{q.source_year}</span>}</div><h3><Latex source={q.text.length>300?q.text.slice(0,300)+'…':q.text}/></h3><div className="problem-meta">{q.paper_id||'—'} · {q.chapter_id||'—'}</div><div className="problem-source">{[q.source_exam,q.source_session||q.source_year ? `Session ${q.source_session||q.source_year}` : ''].filter(Boolean).join(' · ') || 'Source unavailable'}</div></article>)}</div>}
  </div>;
}
function SettingsPage({user,setUser,onLogout,onLogin}) {
  const [tab,setTab]=useState('profile');
  const [name,setName]=useState(user?.name||''); const [saving,setSaving]=useState(false); const [message,setMessage]=useState('');
  async function saveProfile(){ setSaving(true); setMessage(''); try{const r=await fetch(`${API}/auth/profile`,{method:'PATCH',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({name})}); const d=await r.json(); if(!r.ok) throw new Error(d.detail||'Could not update profile'); setUser(d); setMessage('Profile updated successfully.');}catch(e){setMessage(e.message)}finally{setSaving(false)} }
  const tabs=[['profile','Profile','👤'],['subscription','Subscription','✦'],['security','Security settings','🔒'],['logout','Logout','↪'],['about','About us','ℹ']];
  if(!user) return <RequireLogin onLogin={onLogin}/>;
  return <div className="settings-page"><div className="settings-hero card"><div><div className="eyebrow">ACCOUNT SETTINGS</div><h1>Settings</h1><p className="muted">Manage your profile, subscription and account security.</p></div><div className="settings-avatar">{(user.name||'U').slice(0,1).toUpperCase()}</div></div><div className="settings-layout"><aside className="settings-side card">{tabs.map(([id,label,icon])=><button key={id} className={tab===id?'active':''} onClick={()=>setTab(id)}><span>{icon}</span>{label}</button>)}</aside><section className="settings-content card">
    {tab==='profile'&&<div><div className="section-head"><div><div className="eyebrow">PROFILE</div><h2>Personal information</h2></div><span className="settings-chip">Account #{user.id}</span></div><label>Full name<input value={name} onChange={e=>setName(e.target.value)} placeholder="Your name"/></label><label>Phone number<input value={user.phone||''} readOnly className="readonly-input"/><small>Phone number cannot be changed from the app.</small></label>{message&&<div className="settings-message">{message}</div>}<button className="primary" disabled={saving||!name.trim()} onClick={saveProfile}>{saving?'Saving…':'Save changes'}</button></div>}
    {tab==='subscription'&&<SubscriptionPage user={user} embedded/>}
    {tab==='security'&&<div><div className="section-head"><div><div className="eyebrow">SECURITY</div><h2>Password & verification</h2></div><span className="settings-chip">OTP protected</span></div><div className="security-card"><div><h3>Change password</h3><p className="muted">Password changes will require an OTP sent to your registered Bangladeshi phone number.</p></div><button className="nav-btn" disabled>Send OTP · Coming soon</button></div><div className="settings-note">The OTP service is intentionally reserved for the next development step.</div></div>}
    {tab==='logout'&&<div><div className="section-head"><div><div className="eyebrow">ACCOUNT</div><h2>Log out</h2></div></div><p className="muted">Sign out from this device. Your saved exams and Problems remain on your account.</p><button className="danger-solid" onClick={onLogout}>Log out of account</button></div>}
    {tab==='about'&&<div><div className="section-head"><div><div className="eyebrow">BUET WRITTEN</div><h2>About us</h2></div></div><p className="muted about-copy">A focused written-exam practice engine for engineering admission preparation, built around realistic answer spaces, stylus handwriting, saved progress, source-aware questions and self-review.</p><div className="about-grid"><div><b>Version</b><span>v6</span></div><div><b>Purpose</b><span>Written exam practice</span></div></div></div>}
  </section></div></div>;
}

function SubscriptionPage({user,embedded=false}) {
  const [selected, setSelected] = useState(0);
  const plan = SUBSCRIPTION_PLANS[selected];
  const monthly = Math.round(Number(String(plan.price).replace(/[^0-9]/g,'')) / plan.months);
  const buy = ()=>{
    if(SUBSCRIPTION_BUY_URL){
      const joiner = SUBSCRIPTION_BUY_URL.includes('?') ? '&' : '?';
      window.location.href = `${SUBSCRIPTION_BUY_URL}${joiner}plan=${plan.months}`;
    } else {
      alert('Set VITE_SUBSCRIPTION_BUY_URL in the frontend environment to connect your payment/buying site.');
    }
  };
  const content=<div className={`subscription-page ${embedded?'embedded':''}`}>
    <div className="subscription-hero"><div><div className="eyebrow">PREMIUM ACCESS</div><h2>{embedded?'Upgrade your account':'Choose your plan'}</h2><p className="muted">Select a plan below. The checkout button updates instantly with your selected duration.</p></div><div className="premium-badge">PREMIUM</div></div>
    <div className="subscription-grid">{SUBSCRIPTION_PLANS.map((p,i)=>{ const isSelected=i===selected; const value=Number(String(p.price).replace(/[^0-9]/g,'')); const per=Math.round(value/p.months); return <button type="button" key={p.months} className={`plan-card ${i===0?'featured':''} ${isSelected?'selected':''}`} onClick={()=>setSelected(i)}>
      <div className="plan-card-head"><span className="plan-radio">{isSelected?'◉':'○'}</span>{i===0&&<span className="plan-tag">POPULAR</span>}</div><div className="plan-name">{p.months} মাস</div><div className="plan-price">{p.price}</div><div className="plan-monthly">≈ {per.toLocaleString('en-IN')} ৳ / মাস</div><span className="plan-select-label">{isSelected?'Selected':'Select plan'}</span>
    </button>})}</div>
    <div className="subscription-checkout card"><div><div className="eyebrow">SELECTED PLAN</div><strong>{plan.months} মাস · {plan.price}</strong><span>Approx. {monthly.toLocaleString('en-IN')} ৳ / month</span></div><button className="buy-plan checkout-btn" onClick={buy}>কিনুন <span>↗</span></button></div>
    <div className="coupon-row"><span>Have a coupon?</span><button className="nav-btn" onClick={buy}>Continue to checkout ↗</button></div>
  </div>;
  return embedded?content:<div className="subscription-shell card">{content}</div>;
}

function PlaceholderPage({title,description}){ return <div className="placeholder-page"><div className="card page-hero"><div className="eyebrow">COMING NEXT</div><h1>{title}</h1><p className="muted">{description}</p></div></div>; }

function QuestionBankAdmin({onBack}) {
  const [cfg,setCfg]=useState(null), [questions,setQuestions]=useState([]), [subject,setSubject]=useState('All'), [paper,setPaper]=useState('All'), [chapter,setChapter]=useState('All'), [search,setSearch]=useState(''), [loading,setLoading]=useState(true);
  const [editing,setEditing]=useState(null), [saving,setSaving]=useState(false), [uploadingImage,setUploadingImage]=useState(false);

  async function load(){
    setLoading(true);
    try {
      const [c,q]=await Promise.all([
        fetch(`${API}/admin/question-bank/config`).then(r=>r.json()),
        fetch(`${API}/admin/question-bank`).then(r=>r.json())
      ]);
      setCfg(c); setQuestions(q.questions||[]);
    } catch(e) { alert(`Could not load question bank: ${e.message}`); }
    finally { setLoading(false); }
  }
  useEffect(()=>{load();},[]);

  const papers = useMemo(() => {
    const set = new Set(questions.filter(q=>subject==='All'||q.subject===subject).map(q=>q.paper_id).filter(Boolean));
    return ['All',...Array.from(set)];
  },[questions,subject]);
  const chapters = useMemo(() => {
    const set = new Set(questions.filter(q=>(subject==='All'||q.subject===subject)&&(paper==='All'||q.paper_id===paper)).map(q=>q.chapter_id).filter(Boolean));
    return ['All',...Array.from(set)];
  },[questions,subject,paper]);
  const chapterName = id => {
    for (const subjectName of Object.keys(cfg?.chapters||{})) for (const p of cfg.chapters[subjectName]||[]) for (const c of p.chapters||[]) if (c.id===id) return c.name;
    return id;
  };
  const paperName = id => {
    for (const subjectName of Object.keys(cfg?.chapters||{})) for (const p of cfg.chapters[subjectName]||[]) if (p.paper_id===id) return p.paper_name;
    return id;
  };
  const chapterOptions = subject === 'All' ? [] : (cfg?.chapters?.[subject] || []).flatMap(p=>p.chapters || []).map(c=>c);
  const selectedPaper = subject === 'All' ? '' : ((cfg?.chapters?.[subject] || []).map(p=>p)[0]?.paper_id || '');
  const filtered = questions.filter(q => {
    if(subject!=='All'&&q.subject!==subject) return false;
    if(paper!=='All'&&q.paper_id!==paper) return false;
    if(chapter!=='All'&&q.chapter_id!==chapter) return false;
    if(search && !(`${q.text} ${q.source_file||''} ${q.source_year||''} ${q.source_exam||''}`.toLowerCase().includes(search.toLowerCase()))) return false;
    return true;
  });
  const grouped = useMemo(() => {
    const map = new Map();
    for(const q of filtered){ const key=`${q.subject}|||${q.paper_id}|||${q.chapter_id}`; if(!map.has(key)) map.set(key,{subject:q.subject,paper_id:q.paper_id,chapter_id:q.chapter_id,items:[]}); map.get(key).items.push(q); }
    return Array.from(map.values());
  },[filtered]);

  const blank = () => ({id:null,subject:'Mathematics',paper_id:'M1',chapter_id:'M1-1',text:'',answer_text:'',solution_text:'',difficulty:'Medium-Hard',source_file:'',source_page:'',source_exam:'',source_year:'',source_session:'',original_language:'source',content_blocks:[],rubric:[]});
  const beginNew = () => setEditing(blank());
  const beginEdit = q => setEditing({id:q.id,subject:q.subject,paper_id:q.paper_id||'M1',chapter_id:q.chapter_id||'',text:q.text||'',answer_text:q.answer_text||'',solution_text:q.solution_text||'',difficulty:q.difficulty||'Medium-Hard',source_file:q.source_file||'',source_page:q.source_page||'',source_exam:q.source_exam||'',source_year:q.source_year||'',source_session:q.source_session||'',original_language:q.original_language||'source',content_blocks:q.content_blocks||[],rubric:q.rubric||[]});

  async function uploadDiagram(e){
    const file=e.target.files?.[0]; if(!file) return;
    setUploadingImage(true);
    try {
      const form=new FormData(); form.append('file',file);
      const r=await fetch(`${API}/admin/question-bank/question-images`,{method:'POST',body:form});
      const data=await r.json(); if(!r.ok) throw new Error(data.detail||'Upload failed');
      setEditing(x=>({...x,content_blocks:[...(x?.content_blocks||[]),{type:'image',content:data.image_url,alt:'Question diagram'}]}));
    } catch(e){ alert(e.message); }
    finally{setUploadingImage(false); e.target.value='';}
  }
  function removeBlock(idx){ setEditing(x=>({...x,content_blocks:(x?.content_blocks||[]).filter((_,i)=>i!==idx)})); }

  async function saveQuestion(){
    if(!editing?.text.trim()) return alert('Question text is required.');
    setSaving(true);
    try{
      const body={...editing,source_page: editing.source_page ? Number(editing.source_page) : null,marks:10, rubric:editing.rubric||[]};
      delete body.id;
      const url=editing.id ? `${API}/admin/question-bank/questions/${editing.id}` : `${API}/admin/question-bank/questions`;
      const r=await fetch(url,{method:editing.id?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      const data=await r.json(); if(!r.ok) throw new Error(data.detail||'Save failed');
      setEditing(null); await load();
    }catch(e){alert(e.message);}finally{setSaving(false);}
  }
  async function archiveQuestion(id){
    if(!confirm('Archive this question? It will no longer appear in exams.')) return;
    const r=await fetch(`${API}/admin/question-bank/questions/${id}`,{method:'DELETE'}); if(!r.ok){const d=await r.json().catch(()=>({})); return alert(d.detail||'Could not archive');} await load();
  }

  return <div className="admin-page">
    <header className="admin-head"><div><div className="eyebrow">BUET AI EXAM ENGINE</div><h1>Question Bank</h1><p className="muted">Curated written-question bank. No generative AI is used here. Questions stay in the language you provide; math is stored as LaTeX, and diagrams/graphs are optional question assets.</p></div><div className="admin-head-actions"><button className="nav-btn" onClick={beginNew}>＋ Add question</button><button className="nav-btn" onClick={onBack}>← Exam Setup</button></div></header>
    <section className="card admin-card bank-controls">
      <div className="stats"><span><b>{questions.length}</b> published questions</span><span>AI is reserved for the grading stage</span></div>
      <div className="admin-fields">
        <label>Subject<select value={subject} onChange={e=>{setSubject(e.target.value);setPaper('All');setChapter('All')}}><option>All</option>{SUBJECTS.map(x=><option key={x}>{x}</option>)}</select></label>
        <label>Paper<select value={paper} onChange={e=>{setPaper(e.target.value);setChapter('All')}}>{papers.map(x=><option key={x} value={x}>{x==='All'?'All papers':paperName(x)}</option>)}</select></label>
        <label>Chapter<select value={chapter} onChange={e=>setChapter(e.target.value)}>{chapters.map(x=><option key={x} value={x}>{x==='All'?'All chapters':chapterName(x)}</option>)}</select></label>
        <label className="search-field"><span>⌕</span><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search questions, source, year…" /><button type="button" onClick={()=>setSearch('')} aria-label="Clear search">×</button></label>
      </div>
    </section>
    {loading ? <div className="card loading-card"><h2>Loading question bank…</h2><div className="spinner"/></div> : filtered.length===0 ? <div className="card admin-card"><p className="muted">No questions match these filters.</p></div> : <div className="bank-groups">{grouped.map(g=><section className="card bank-group" key={`${g.subject}-${g.paper_id}-${g.chapter_id}`}>
      <div className="bank-group-head"><div><div className="eyebrow">{g.subject} · {paperName(g.paper_id)}</div><h2>{chapterName(g.chapter_id)}</h2></div><b>{g.items.length} question{g.items.length!==1?'s':''}</b></div>
      <div className="bank-question-list">{g.items.map(q=><article className="bank-question" key={q.id}>
        <div className="bank-q-top"><span>Question {q.number}</span><span>{q.source_exam||'Source sheet'} {q.source_year ? `· ${q.source_year}` : ''}</span><span>{q.source_file || 'Manually added'}{q.source_page ? ` · p.${q.source_page}` : ''}{q.source_session ? ` · session ${q.source_session}` : ''}</span></div>
        <div className="bank-q-text"><Latex source={q.text}/></div>
        {q.content_blocks?.filter(b=>b.type==='image'&&String(b.content||'').startsWith('/')).map((b,i)=><img key={i} className="question-image" src={b.content} alt={b.alt||'Question figure'}/>) }
        <div className="bank-q-actions"><button className="nav-btn" onClick={()=>beginEdit(q)}>Edit</button><button className="nav-btn danger-btn" onClick={()=>archiveQuestion(q.id)}>Archive</button></div>
        {q.answer_text && <details><summary>Reference answer</summary><div className="solution"><Latex source={q.answer_text}/></div></details>}
      </article>)}</div>
    </section>)}</div>}

    {editing && <div className="modal-backdrop" onClick={()=>{if(!saving)setEditing(null)}}><div className="modal card" onClick={e=>e.stopPropagation()}>
      <div className="modal-head"><div><div className="eyebrow">QUESTION BANK</div><h2>{editing.id ? 'Edit question' : 'Add question'}</h2></div><button className="nav-btn" onClick={()=>{if(!saving)setEditing(null)}}>×</button></div>
      <div className="edit-grid">
        <label>Subject<select value={editing.subject} onChange={e=>{const v=e.target.value; const ps=cfg?.chapters?.[v]||[]; const first=ps[0]; setEditing(x=>({...x,subject:v,paper_id:first?.paper_id||'',chapter_id:first?.chapters?.[0]?.id||''}))}}>{SUBJECTS.map(x=><option key={x}>{x}</option>)}</select></label>
        <label>Paper<select value={editing.paper_id} onChange={e=>{const p=(cfg?.chapters?.[editing.subject]||[]).find(x=>x.paper_id===e.target.value);setEditing(x=>({...x,paper_id:e.target.value,chapter_id:p?.chapters?.[0]?.id||x.chapter_id}))}}>{(cfg?.chapters?.[editing.subject]||[]).map(p=><option key={p.paper_id} value={p.paper_id}>{p.paper_name}</option>)}</select></label>
        <label className="wide">Chapter<select value={editing.chapter_id} onChange={e=>setEditing(x=>({...x,chapter_id:e.target.value}))}>{(cfg?.chapters?.[editing.subject]||[]).flatMap(p=>p.chapters||[]).filter(c=>c.id.startsWith(`${editing.paper_id}-`)).map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select></label>
        <label>Difficulty<select value={editing.difficulty} onChange={e=>setEditing(x=>({...x,difficulty:e.target.value}))}><option>Medium</option><option>Medium-Hard</option><option>Hard</option></select></label>
        <label>Original language<input value={editing.original_language} onChange={e=>setEditing(x=>({...x,original_language:e.target.value}))} placeholder="e.g. bn, en, source" /></label>
        <label className="wide">Question (preserve original wording; use $...$ / $$...$$ / \\[...\\] for LaTeX)<textarea value={editing.text} onChange={e=>setEditing(x=>({...x,text:e.target.value}))} rows={7}/></label>
        <label className="wide">Reference answer<textarea value={editing.answer_text} onChange={e=>setEditing(x=>({...x,answer_text:e.target.value}))} rows={4}/></label>
        <label className="wide">Reference solution<textarea value={editing.solution_text} onChange={e=>setEditing(x=>({...x,solution_text:e.target.value}))} rows={6}/></label>
        <label>Source file<input value={editing.source_file} onChange={e=>setEditing(x=>({...x,source_file:e.target.value}))}/></label>
        <label>Source page<input type="number" value={editing.source_page} onChange={e=>setEditing(x=>({...x,source_page:e.target.value}))}/></label>
        <label>Source exam<input value={editing.source_exam} onChange={e=>setEditing(x=>({...x,source_exam:e.target.value}))} placeholder="BUET / KUET / ..."/></label>
        <label>Source year<input value={editing.source_year} onChange={e=>setEditing(x=>({...x,source_year:e.target.value}))}/></label>
        <label>Session<input value={editing.source_session} onChange={e=>setEditing(x=>({...x,source_session:e.target.value}))} placeholder="e.g. 2025-26"/></label>
      </div>
      <div className="asset-editor"><div className="asset-head"><b>Question images / diagrams</b><label className="upload"><input type="file" accept="image/png,image/jpeg,image/webp" onChange={uploadDiagram}/>{uploadingImage?'Uploading…':'＋ Add diagram / graph'}</label></div>{editing.content_blocks?.map((b,i)=><div className="asset-row" key={i}>{b.type==='image'?<img src={b.content} alt={b.alt||'Question asset'}/>:<span>{b.type}</span>}<button className="nav-btn" onClick={()=>removeBlock(i)}>Remove</button></div>)}<p className="muted tiny">Only add an image when the question itself contains a diagram, chart, graph, table or other essential visual. Do not upload the whole source page.</p></div>
      <div className="modal-actions"><button className="nav-btn" disabled={saving} onClick={()=>setEditing(null)}>Cancel</button><button className="primary" disabled={saving} onClick={saveQuestion}>{saving?'Saving…':'Save question'}</button></div>
    </div></div>}
  </div>;
}

createRoot(document.getElementById('root')).render(<ErrorBoundary><App /></ErrorBoundary>);
