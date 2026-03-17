"use client";

import { useState, useEffect } from "react";
import { Send, FileText, Upload, CheckCircle, ArrowRight, BarChart, Target, Zap, BrainCircuit, Copy, Check, Trophy, Lightbulb, Sparkles } from "lucide-react";

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

  let rawSuggestion = result.suggestion_text;
  let suggestionText = "";
  if (typeof rawSuggestion === "string") {
    suggestionText = rawSuggestion.trim();
  } else if (Array.isArray(rawSuggestion)) {
    suggestionText = rawSuggestion.filter(Boolean).join("\n- ");
  } else if (rawSuggestion && typeof rawSuggestion === "object") {
    suggestionText = JSON.stringify(rawSuggestion);
  }

  const quickTips = Array.isArray(result.tips) ? result.tips.map(t => typeof t === "string" ? t : JSON.stringify(t)).filter(Boolean) : [];

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

function getStrategyLabel(style) {
  const s = (style || "").toLowerCase();
  if (s.includes("achievement")) return "Achievement Lead";
  if (s.includes("problem")) return "Problem Solver";
  return style || "Strategy";
}

function getStrategyIcon(style) {
  const s = (style || "").toLowerCase();
  if (s.includes("achievement")) return Trophy;
  return Lightbulb;
}

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <button
      onClick={handleCopy}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 ${
        copied
          ? "bg-green-100 text-green-700 border border-green-200"
          : "bg-white text-neutral-600 border border-neutral-200 hover:bg-neutral-50 hover:text-neutral-900"
      }`}
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

function VariantCard({ variant, index }) {
  const rawStyle = variant?.style || variant?.reasoning?.strategy || (index === 0 ? "achievement" : "problem_solver");
  const isAchievement = rawStyle.toLowerCase().includes("achievement") || (index === 0 && !rawStyle.toLowerCase().includes("problem"));
  const style = isAchievement ? "achievement" : "problem_solver";
  const email = variant?.email || "";
  const reasoning = variant?.reasoning || {};
  const label = getStrategyLabel(style);
  const Icon = getStrategyIcon(style);

  let subject = "";
  let body = email;
  const subjectMatch = email.match(/^Subject:\s*(.+)/im);
  if (subjectMatch) {
    subject = subjectMatch[1].trim();
    body = email.replace(/^Subject:\s*.+\n*/im, "").trim();
  }

  const paragraphs = body.split(/\n\s*\n/).map(p => p.trim()).filter(Boolean);

  return (
    <div className="variant-card rounded-2xl overflow-hidden flex flex-col transition-all duration-300 hover:shadow-md">
      {/* Header */}
      <div className="p-5 border-b border-[#E8E2D6] flex items-center justify-between bg-neutral-50/50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center bg-white border border-[#E8E2D6] text-neutral-700 shadow-sm">
            <Icon size={18} />
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-500">
              STRATEGY 0{index + 1}
            </span>
            <p className="text-sm font-semibold text-neutral-900 mt-0.5">{label}</p>
          </div>
        </div>
        <CopyButton text={email} />
      </div>

      <div className="p-6 flex-1 flex flex-col gap-6">
        {/* Email Box */}
        <div className="bg-[#F9F7F4] border border-[#E8E2D6] rounded-xl p-6 relative">
          {subject && (
            <div className="mb-5 pb-4 border-b border-[#E8E2D6]">
              <p className="text-[11px] font-semibold uppercase tracking-wider text-neutral-500 mb-1.5">Subject Line</p>
              <p className="text-base font-semibold text-neutral-900 leading-snug">{subject}</p>
            </div>
          )}

          <div className="space-y-4">
            {paragraphs.map((para, i) => (
              <p key={i} className="text-[15px] leading-relaxed text-neutral-700">
                {para}
              </p>
            ))}
          </div>
        </div>

        {/* Reasoning Section */}
        {(reasoning.why_this_opening || reasoning.key_strength_used) && (
          <div className="bg-white border border-[#E8E2D6] rounded-xl p-5 mt-auto shadow-sm">
            <h5 className="text-[11px] font-bold uppercase tracking-wider text-neutral-900 mb-3 flex items-center gap-2">
              <BrainCircuit size={14} className="text-neutral-500" />
              AI Reasoning
            </h5>
            {reasoning.why_this_opening && (
              <p className="text-sm text-neutral-600 leading-relaxed mb-3">
                {reasoning.why_this_opening}
              </p>
            )}
            {reasoning.key_strength_used && (
              <div className="inline-flex items-center gap-2 bg-[#F5F1E8] px-3 py-1.5 rounded-full mt-1">
                <Target size={12} className="text-neutral-600" />
                <p className="text-xs font-medium text-neutral-700">
                  {reasoning.key_strength_used}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function MetricCard({ label, value, helper, icon: Icon, delay }) {
  return (
    <article 
      className="bg-white border border-[#E8E2D6] p-6 rounded-2xl flex flex-col gap-2 relative overflow-hidden group hover:shadow-md transition-all duration-300 animate-in fade-in slide-in-from-bottom-4"
      style={{ animationDelay: `${delay}ms` }}
    >
      <div className="flex items-center gap-2 text-neutral-500 mb-2 z-10">
        <Icon size={16} />
        <p className="text-[11px] font-bold uppercase tracking-widest">{label}</p>
      </div>
      <strong className="text-3xl font-bold text-neutral-900 tracking-tight z-10">{value ?? "-"}</strong>
      <span className="text-sm text-neutral-500 z-10">{helper}</span>
    </article>
  );
}

const pillTags = [
  "Generate email from resume",
  "Customize tone",
  "Optimize for recruiter",
  "AI personalization",
  "LinkedIn outreach ready"
];

export default function Home() {
  const [jobUrl, setJobUrl] = useState("");
  const [resumeFile, setResumeFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (result && !loading) {
      document.getElementById('results-section')?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [result, loading]);

  const { improvements, tips } = parseSuggestions(result);
  const variants = result?.variants || [];

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
      document.getElementById('generator-section')?.scrollIntoView({ behavior: 'smooth' });
      
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
    <div className="min-h-screen bg-[#F5F1E8] text-neutral-900 font-sans selection:bg-neutral-200">
      
      {/* SaaS Landing Page Hero Section */}
      <section className="container mx-auto px-4 pt-24 pb-16 flex flex-col items-center text-center max-w-[900px]">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-[#E8E2D6] text-xs font-semibold text-neutral-600 mb-8 shadow-sm">
          <Sparkles size={14} className="text-neutral-400" />
          <span>Cold Email Generator AI</span>
        </div>
        
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold tracking-tight text-neutral-900 mb-6 leading-[1.15]">
          Generate High-Converting <br className="hidden md:block" /> Cold Emails in Seconds
        </h1>
        
        <p className="text-lg md:text-xl text-neutral-600 max-w-2xl mx-auto mb-10 leading-relaxed font-light">
          Upload your resume and job link — our AI crafts personalized, job-winning cold emails tailored to your profile.
        </p>

        <div className="flex flex-wrap justify-center gap-3 max-w-3xl">
          {pillTags.map((tag, i) => (
            <div key={i} className="px-4 py-2 rounded-full bg-[#E8E2D6] text-sm text-neutral-700 font-medium transition-colors hover:bg-[#DED7C8] cursor-default">
              {tag}
            </div>
          ))}
        </div>
      </section>

      {/* Main Application Area */}
      <main id="generator-section" className="container mx-auto px-4 pb-32">
        <div className="flex flex-col gap-16 max-w-7xl mx-auto">
          
          {/* Top Section: Input Panel - Centered */}
          <div className={`max-w-2xl mx-auto w-full flex flex-col gap-6 transition-all duration-1000 ${isReady ? 'opacity-100' : 'opacity-0'}`}>
            <div className="glass-panel-light p-8 rounded-3xl relative">
              <div className="mb-6">
                <h3 className="text-lg font-bold flex items-center gap-2 mb-1 text-neutral-900">
                  <BrainCircuit size={20} className="text-neutral-500" />
                  Campaign Setup
                </h3>
                <p className="text-sm text-neutral-500">Provide context for the AI.</p>
              </div>

              <form onSubmit={handleSubmit} className="flex flex-col gap-6">
                <div className="flex flex-col gap-2">
                  <label className="text-[11px] font-bold uppercase tracking-wider text-neutral-600">Job Post URL</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-neutral-400">
                      <Send size={16} />
                    </div>
                    <input
                      type="url"
                      placeholder="https://linkedin.com/jobs/..."
                      value={jobUrl}
                      onChange={(e) => setJobUrl(e.target.value)}
                      required
                      className="w-full pl-10 pr-4 py-3.5 bg-white border border-[#E8E2D6] rounded-xl focus:ring-2 focus:ring-neutral-900 focus:border-neutral-900 outline-none transition-all placeholder:text-neutral-400 text-sm shadow-sm"
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-[11px] font-bold uppercase tracking-wider text-neutral-600">Resume PDF</label>
                  <label className={`relative cursor-pointer flex flex-col items-center justify-center w-full h-40 border-2 border-dashed rounded-xl transition-all ${resumeFile ? 'border-neutral-900 bg-neutral-50' : 'border-[#E8E2D6] bg-white hover:bg-neutral-50 hover:border-neutral-300'}`}>
                    <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center">
                      {resumeFile ? (
                         <>
                          <div className="w-12 h-12 rounded-full bg-neutral-100 flex items-center justify-center mb-3">
                            <FileText size={24} className="text-neutral-900" />
                          </div>
                          <p className="text-sm font-semibold text-neutral-900 truncate max-w-[200px] px-2">{resumeFile.name}</p>
                          <p className="text-xs text-neutral-500 mt-1">Attached for context</p>
                         </>
                      ) : (
                        <>
                          <div className="w-12 h-12 rounded-full bg-neutral-50 border border-[#E8E2D6] flex items-center justify-center mb-3">
                            <Upload size={20} className="text-neutral-500" />
                          </div>
                          <p className="text-sm font-medium text-neutral-700">Click to upload <span className="text-neutral-500 font-normal">or drag & drop</span></p>
                          <p className="text-xs text-neutral-400 mt-1">PDF max 5MB</p>
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
                  className={`mt-2 w-full py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 ${loading ? 'bg-[#E8E2D6] text-neutral-500 cursor-not-allowed' : 'bg-neutral-900 text-white hover:bg-neutral-800 shadow-lg hover:shadow-xl hover:-translate-y-0.5'}`}
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 rounded-full border-2 border-neutral-400 border-t-transparent animate-spin mr-2"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      Generate Emails
                      <ArrowRight size={18} />
                    </>
                  )}
                </button>
              </form>

              {error && (
                <div className="mt-5 p-4 rounded-xl bg-red-50 border border-red-100 flex gap-3">
                  <Zap size={18} className="text-red-500 shrink-0 mt-0.5" />
                  <p className="text-sm text-red-700 leading-relaxed">{error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Bottom Section: Output & Metrics - Full width */}
          <div className={`w-full flex flex-col gap-8 transition-all duration-1000 delay-200 ${isReady ? 'opacity-100' : 'opacity-0'}`}>
            
            {/* Metrics Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
              <MetricCard label="Fit Score" value={result?.score_dashboard?.breakdown?.match_score?.score} helper="Skill alignment" icon={Target} delay={0} />
              <MetricCard label="ATS Match" value={result?.score_dashboard?.breakdown?.ats_score?.score} helper="Keyword fit" icon={BarChart} delay={100} />
              <MetricCard label="Resume" value={result?.score_dashboard?.breakdown?.resume_score?.score} helper="Impact level" icon={FileText} delay={200} />
              <MetricCard label="Tone" value={result?.score_dashboard?.breakdown?.tone_score?.score} helper="Communication" icon={Zap} delay={300} />
            </div>

            {/* Main Output Area */}
            <div id="results-section" className={`glass-panel-light rounded-3xl min-h-[500px] flex flex-col relative transition-all duration-500`}>
               {!result && !loading && (
                 <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-8 text-neutral-500">
                   <div className="w-20 h-20 rounded-full bg-white border border-[#E8E2D6] shadow-sm flex items-center justify-center mb-6">
                     <Lightbulb size={32} className="text-neutral-400" />
                   </div>
                   <h3 className="text-lg font-bold mb-2 text-neutral-900">Ready to Draft</h3>
                   <p className="max-w-md leading-relaxed">Provide your target job and context document. The engine will instantly write two strategic cold email variants.</p>
                 </div>
               )}

               {loading && (
                 <div className="absolute inset-0 flex flex-col items-center justify-center bg-white/50 backdrop-blur-sm z-20 rounded-3xl">
                   <div className="w-16 h-16 rounded-full border-4 border-[#E8E2D6] border-t-neutral-900 animate-spin mb-6"></div>
                   <p className="text-sm font-semibold text-neutral-900 tracking-widest uppercase">Analyzing Profile & Writing...</p>
                 </div>
               )}

               {result && (
                 <div className="animate-in fade-in slide-in-from-bottom-4 duration-500 h-full flex flex-col p-8">
                   <div className="flex justify-between items-end mb-8 pb-6 border-b border-[#E8E2D6]">
                     <div>
                       <h2 className="text-2xl font-bold mb-1 text-neutral-900 tracking-tight">Strategy Selector</h2>
                       <p className="text-sm text-neutral-500">Compare and export the best cold email for your outreach.</p>
                     </div>
                     <div className="text-right bg-[#F5F1E8] px-4 py-2 rounded-xl">
                       <div className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 mb-1">Effectiveness</div>
                       <div className="text-3xl font-black text-neutral-900 leading-none">{result.score_dashboard?.overall_score || "N/A"}</div>
                     </div>
                   </div>

                   {variants.length > 0 ? (
                     <div className="grid md:grid-cols-2 gap-6 flex-1">
                       {variants.map((variant, i) => (
                         <VariantCard key={i} variant={variant} index={i} />
                       ))}
                     </div>
                   ) : (
                     <div className="flex-1 flex flex-col bg-white border border-[#E8E2D6] shadow-sm rounded-2xl p-8">
                       <div className="flex justify-end mb-4">
                         <CopyButton text={formatEmail(result.email)} />
                       </div>
                       <pre className="flex-1 text-base leading-relaxed text-neutral-700 whitespace-pre-wrap overflow-y-auto custom-scrollbar font-sans">
                         {formatEmail(result.email)}
                       </pre>
                     </div>
                   )}
                 </div>
               )}
            </div>
            
            {result && (
              <div className="grid sm:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-8">
                <div className="bg-white border border-[#E8E2D6] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <h4 className="text-xs font-bold tracking-wider uppercase text-neutral-900 mb-4 flex items-center gap-2">
                    <CheckCircle size={16} className="text-neutral-500" />
                    Strategic Insights
                  </h4>
                  {tips.length > 0 ? (
                    <ul className="space-y-3">
                      {tips.map((tip, i) => (
                         <li key={i} className="text-sm text-neutral-600 leading-relaxed pl-4 relative">
                           <span className="absolute left-0 top-2 w-1.5 h-1.5 bg-neutral-300 rounded-full"></span>
                           {tip}
                         </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-neutral-500 italic">No additional strategic insights.</p>
                  )}
                </div>

                <div className="bg-white border border-[#E8E2D6] rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow">
                  <h4 className="text-xs font-bold tracking-wider uppercase text-neutral-900 mb-4 flex items-center gap-2">
                    <Zap size={16} className="text-neutral-500" />
                    Improvement Areas
                  </h4>
                  {improvements.length > 0 ? (
                    <ul className="space-y-3">
                      {improvements.map((imp, i) => (
                        <li key={i} className="text-sm text-neutral-600 leading-relaxed pl-4 relative">
                           <span className="absolute left-0 top-2 w-1.5 h-1.5 bg-neutral-800 rounded-full"></span>
                           {imp}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-neutral-500 italic">Profile analysis complete. No immediate improvements needed.</p>
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
