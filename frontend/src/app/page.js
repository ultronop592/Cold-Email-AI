"use client";

import { useState, useEffect } from "react";
import { Send, FileText, Upload, Sparkles, CheckCircle, ArrowRight, BarChart, Target, Zap, BrainCircuit } from "lucide-react";
import { ParticleHero } from "@/components/ui/animated-hero";

function formatEmail(value) {
  if (value == null) return "AI is ready to draft your email.";
  if (typeof value === "string") return value;
  return JSON.stringify(value, null, 2);
}

function extractBullets(text) {
  return text
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("-") || line.startsWith("*") || line.startsWith("•"))
    .map((line) => line.replace(/^[-*•]\s*/, "").trim())
    .filter(Boolean);
}

function parseSuggestions(result) {
  if (!result) return { improvements: [], tips: [] };

  const suggestionText = (result.suggestion_text || "").trim();
  const quickTips = Array.isArray(result.tips) ? result.tips.filter(Boolean) : [];

  if (!suggestionText) return { improvements: [], tips: quickTips };
  const hasQuickTips = /quick\s*tips\s*:/i.test(suggestionText);

  if (!hasQuickTips) {
    return { improvements: extractBullets(suggestionText), tips: quickTips };
  }

  const parts = suggestionText.split(/quick\s*tips\s*:/i);
  const improvementBullets = extractBullets(parts[0] || "");
  const textTipBullets = extractBullets(parts[1] || "");
  const mergedTips = textTipBullets.length ? textTipBullets : quickTips;

  return { improvements: improvementBullets, tips: mergedTips };
}

function MetricCard({ label, value, helper, icon: Icon, delay }) {
  return (
    <article 
      className={`glass-panel-dark p-5 rounded-2xl flex flex-col gap-2 relative overflow-hidden group hover:-translate-y-1 hover:border-red-500/30 hover:shadow-[0_8px_30px_rgba(220,38,38,0.15)] transition-all duration-300 animate-in fade-in slide-in-from-bottom-4`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-20 group-hover:scale-110 group-hover:text-red-500 transition-all duration-500">
        <Icon size={48} />
      </div>
      <div className="flex items-center gap-2 text-neutral-400 mb-1 z-10">
        <Icon size={16} className="text-red-500/70" />
        <p className="text-xs font-semibold uppercase tracking-wider">{label}</p>
      </div>
      <strong className="text-4xl font-black text-white tracking-tight z-10">{value ?? "-"}</strong>
      <span className="text-sm text-neutral-500 z-10">{helper}</span>
    </article>
  );
}

export default function Home() {
  const [jobUrl, setJobUrl] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    
    // Smooth scroll to results
    if (result && !loading) {
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
  }, [result, loading]);

  const { improvements, tips } = parseSuggestions(result);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(null);

    if (!jobUrl.trim() || !resumeFile) {
      setError("Please provide a job URL and upload a resume file.");
      return;
    }

    const formData = new FormData();
    formData.append("job_url", jobUrl.trim());
    formData.append("resume", resumeFile);

    try {
      setLoading(true);
      const response = await fetch("/api/generate-email", {
        method: "POST",
        body: formData,
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload?.error || "Request failed.");
      }

      setResult(payload);
    } catch (submitError) {
      setError(submitError.message || "Unable to process the request.");
    } finally {
      setLoading(false);
    }
  }

  const isReady = mounted;

  return (
    <div className="min-h-screen bg-black text-white relative font-sans">
      
      {/* Background Interactive Particle Hero */}
      <div className="fixed inset-0 z-0 pointer-events-auto">
        <ParticleHero 
          title="" 
          subtitle="" 
          description="" 
          interactiveHint="" 
          particleCount={20}
          hideContent={true}
        />
        {/* Dark gradient overlay so the text remains very readable over the red particles */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-black/60 to-black/90 pointer-events-none"></div>
      </div>

      <main className="max-w-6xl mx-auto px-6 relative z-10 pb-24">
        {/* Navigation / Header */}
        <nav className={`pt-8 pb-12 flex justify-between items-center transition-all duration-1000 ${isReady ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}`}>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-red-600 to-orange-600 flex items-center justify-center text-white shadow-[0_0_15px_rgba(220,38,38,0.5)]">
              <Sparkles size={16} />
            </div>
            <span className="font-bold text-lg tracking-tight">Cold Email <span className="text-red-500">Gen AI</span></span>
          </div>
          <div className="px-4 py-1.5 rounded-full bg-black/40 border border-white/10 text-xs font-semibold text-neutral-300 shadow-sm backdrop-blur-md flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${loading ? 'bg-orange-500 animate-pulse' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]'}`}></div>
            {loading ? "LLM Pipeline Running..." : "AI Agent Online"}
          </div>
        </nav>

        {/* Hero Section */}
        <section className={`max-w-3xl mb-16 transition-all duration-1000 delay-100 ${isReady ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <h1 className="text-5xl sm:text-7xl font-black tracking-tighter mb-6 leading-[1.1] uppercase">
            AI-Powered Cold <br />
            <span className="text-gradient-red drop-shadow-2xl text-transparent bg-clip-text">Email Pipeline.</span>
          </h1>
          <p className="text-xl text-red-200/70 font-medium mb-3">
            From job URL to personalized outreach in seconds.
          </p>
          <p className="text-lg text-red-100/50 font-light max-w-2xl leading-relaxed">
            Paste a job posting URL and upload your resume. Our LangChain pipeline scrapes, analyzes, scores, and writes — so you don&apos;t have to.
          </p>
        </section>

        <div className="grid lg:grid-cols-12 gap-8">
          {/* Left Column: Input Panel */}
          <div className={`lg:col-span-5 flex flex-col gap-6 transition-all duration-1000 delay-200 ${isReady ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-8'}`}>
            <div className="glass-panel-dark p-8 rounded-3xl relative overflow-hidden group">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-600 to-orange-500"></div>
              
              <div className="mb-6">
                <h2 className="text-xl font-bold flex items-center gap-2 mb-1 text-white uppercase tracking-wide">
                  <BrainCircuit size={20} className="text-red-500" />
                  Pipeline Inputs
                </h2>
                <p className="text-sm text-neutral-400 font-light">Paste a job posting URL and upload your resume to run the pipeline.</p>
              </div>

              <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                <div className="flex flex-col gap-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-neutral-400 ml-1">Job Listing URL</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-neutral-500">
                      <Send size={16} />
                    </div>
                    <input
                      type="url"
                      placeholder="Paste job listing URL for AI analysis..."
                      value={jobUrl}
                      onChange={(e) => setJobUrl(e.target.value)}
                      required
                      className="w-full pl-10 pr-4 py-3.5 bg-black/60 border border-white/10 rounded-2xl focus:ring-1 focus:ring-red-500/50 focus:border-red-500 outline-none transition-all placeholder:text-neutral-600 text-white shadow-inner"
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-xs font-bold uppercase tracking-wider text-neutral-400 ml-1">Resume PDF (AI Context Source)</label>
                  <label className={`relative cursor-pointer flex flex-col items-center justify-center w-full h-36 border border-dashed rounded-2xl transition-all duration-300 ${resumeFile ? 'border-red-500 bg-red-950/20' : 'border-neutral-700 bg-black/40 hover:bg-neutral-900 hover:border-red-500/50'}`}>
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      {resumeFile ? (
                         <>
                          <FileText size={32} className="text-red-500 mb-2 drop-shadow-[0_0_8px_rgba(239,68,68,0.5)]" />
                          <p className="text-sm font-medium text-red-200 truncate max-w-[200px] px-2">{resumeFile.name}</p>
                          <p className="text-xs text-red-500/70 mt-1 uppercase tracking-widest hidden sm:block">Ready for AI processing</p>
                         </>
                      ) : (
                        <>
                          <div className="bg-neutral-900 border border-neutral-800 p-3 rounded-full mb-3 text-neutral-500">
                            <Upload size={24} />
                          </div>
                          <p className="text-sm font-medium text-neutral-400"><span className="text-red-500 font-semibold hover:text-red-400 transition-colors">Click to upload</span> or drag & drop</p>
                          <p className="text-xs text-neutral-600 mt-1">PDF format max 5MB</p>
                        </>
                      )}
                    </div>
                    <input
                      type="file"
                      accept=".pdf"
                      onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                      required
                      className="hidden"
                    />
                  </label>
                </div>

                <button 
                  type="submit" 
                  disabled={loading}
                  className={`mt-4 w-full py-4 px-6 rounded-2xl font-bold uppercase tracking-widest text-sm shadow-lg transition-all duration-300 flex items-center justify-center gap-2 ${loading ? 'bg-neutral-800 text-neutral-500 cursor-not-allowed border border-neutral-700' : 'bg-transparent border border-red-500/30 text-red-200 hover:text-white hover:border-red-500 hover:shadow-[0_0_20px_rgba(220,38,38,0.3)] hover:bg-red-950/30'}`}
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 rounded-full border-2 border-neutral-500 border-t-transparent animate-spin mr-2"></div>
                      AI Generating...
                    </>
                  ) : (
                    <>
                      Generate with AI
                      <ArrowRight size={16} />
                    </>
                  )}
                </button>
              </form>

              {error && (
                <div className="mt-4 p-4 rounded-xl bg-red-950/50 border border-red-900/50 flex gap-3 animate-in fade-in slide-in-from-top-2">
                  <div className="text-red-500 mt-0.5 shrink-0">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                  </div>
                  <p className="text-sm text-red-400">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Output & Metrics */}
          <div className={`lg:col-span-7 flex flex-col gap-6 transition-all duration-1000 delay-300 ${isReady ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-8'}`}>
            
            {/* Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <MetricCard
                label="AI Match"
                value={result?.score_dashboard?.breakdown?.match_score?.score}
                helper="AI skill analysis"
                icon={Target}
                delay={0}
              />
              <MetricCard
                label="ATS Score"
                value={result?.score_dashboard?.breakdown?.ats_score?.score}
                helper="LLM keyword fit"
                icon={BarChart}
                delay={100}
              />
              <MetricCard
                label="Resume"
                value={result?.score_dashboard?.breakdown?.resume_score?.score}
                helper="AI impact score"
                icon={FileText}
                delay={200}
              />
              <MetricCard
                label="Tone"
                value={result?.score_dashboard?.breakdown?.tone_score?.score}
                helper="AI tone analysis"
                icon={Zap}
                delay={300}
              />
            </div>

            {/* Main Result Card */}
            <div className={`glass-panel-dark p-8 rounded-3xl min-h-[500px] flex flex-col relative transition-all duration-500 ${result ? 'ring-1 ring-red-500/40 shadow-[0_0_30px_rgba(220,38,38,0.1)]' : ''}`}>
               {!result && !loading && (
                 <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8 opacity-40">
                   <div className="w-20 h-20 mb-6 rounded-full bg-neutral-900 border border-neutral-800 flex items-center justify-center">
                     <Sparkles size={32} className="text-neutral-500" />
                   </div>
                   <h3 className="text-xl font-bold mb-2 text-neutral-300 uppercase tracking-widest">Pipeline Ready</h3>
                   <p className="text-neutral-500 max-w-sm font-light">Paste a job URL and upload your resume — the LangChain pipeline will scrape, analyze, score, and write for you.</p>
                 </div>
               )}

               {loading && (
                 <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/60 backdrop-blur-md z-20 rounded-3xl">
                   <div className="relative w-24 h-24">
                     <div className="absolute inset-0 border border-red-900/50 rounded-full"></div>
                     <div className="absolute inset-0 border border-red-500 rounded-full border-t-transparent animate-spin shadow-[0_0_15px_rgba(220,38,38,0.5)]"></div>
                     <div className="absolute inset-0 flex items-center justify-center">
                       <Zap size={24} className="text-red-500 animate-pulse" />
                     </div>
                   </div>
                   <p className="mt-8 text-xs font-bold text-red-500/80 tracking-[0.3em] uppercase animate-pulse">LangChain Pipeline Running...</p>
                 </div>
               )}

               {result && (
                 <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 h-full flex flex-col">
                   <div className="flex justify-between items-end mb-6 pb-6 border-b border-white/5">
                     <div>
                       <h2 className="text-2xl font-black mb-1 text-white uppercase tracking-wider">Pipeline Output</h2>
                       <p className="text-sm text-neutral-400 font-light">From job URL to personalized outreach — generated by your LangChain pipeline.</p>
                     </div>
                     <div className="text-right">
                       <div className="text-4xl font-black text-red-500 mb-1 leading-none drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]">{result.score_dashboard?.overall_score || "N/A"}</div>
                       <div className="text-xs font-bold uppercase tracking-[0.2em] text-neutral-500">AI Effectiveness</div>
                     </div>
                   </div>

                   <pre className="flex-1 w-full bg-black/60 border border-white/5 rounded-2xl p-6 text-[0.9rem] leading-relaxed text-neutral-300 font-mono whitespace-pre-wrap overflow-y-auto custom-scrollbar shadow-inner max-h-[400px]">
                     <span className="text-red-500/50 block mb-4">/* AI-GENERATED COLD EMAIL */</span>
                     {formatEmail(result.email)}
                   </pre>
                 </div>
               )}
            </div>
            
            {/* Feedback & Suggestions */}
            {result && (
              <div className="grid sm:grid-cols-2 gap-4 animate-in fade-in slide-in-from-bottom-8 duration-700">
                <div className="bg-black/40 backdrop-blur-sm rounded-2xl p-6 border border-orange-500/20 shadow-[0_4px_20px_rgba(249,115,22,0.05)]">
                  <h4 className="text-xs font-bold text-orange-400 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                    <CheckCircle size={14} />
                    AI Recommendations
                  </h4>
                  {tips.length > 0 ? (
                    <ul className="space-y-3">
                      {tips.map((tip, i) => (
                        <li key={i} className="flex gap-3 text-sm text-neutral-400 items-start font-light">
                          <span className="text-orange-500 mt-0.5 shrink-0"><CheckCircle size={14} /></span>
                          <span className="leading-relaxed">{tip}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-neutral-600 italic">No AI recommendations at this time.</p>
                  )}
                </div>

                <div className="bg-black/40 backdrop-blur-sm rounded-2xl p-6 border border-red-500/20 shadow-[0_4px_20px_rgba(239,68,68,0.05)]">
                  <h4 className="text-xs font-bold text-red-400 uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                    <Zap size={14} />
                    LLM Refinements
                  </h4>
                  {improvements.length > 0 ? (
                    <ul className="space-y-3">
                      {improvements.map((imp, i) => (
                        <li key={i} className="flex gap-3 text-sm text-neutral-400 items-start font-light">
                          <span className="text-red-500 mt-1 shrink-0"><div className="w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_5px_rgba(239,68,68,1)]"></div></span>
                          <span className="leading-relaxed">{imp}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-neutral-600 italic">AI assessment optimal. No further refinements needed.</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
