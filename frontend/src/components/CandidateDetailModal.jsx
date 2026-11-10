import React from "react";
import {
  X,
  Mail,
  Phone,
  FileText,
  Calendar,
  CheckCircle,
  XCircle,
  Award,
  BookOpen,
  Briefcase,
  ExternalLink,
  Globe,
  Link2,
} from "lucide-react";

export function CandidateDetailModal({ candidate, onClose }) {
  if (!candidate) return null;

  const score = candidate.match_score || 0;
  const breakdown = candidate.breakdown || {};

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-3xl max-h-[90vh] bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl flex flex-col overflow-hidden text-slate-200">
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/90 sticky top-0 z-10">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold text-white tracking-tight">{candidate.name}</h2>
              <span
                className={`px-3 py-0.5 rounded-full text-xs font-bold border ${
                  score >= 80
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                    : score >= 60
                    ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/30"
                    : "bg-red-500/10 text-red-400 border-red-500/30"
                }`}
              >
                {score.toFixed(1)}% Match
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-4">
              <span className="flex items-center gap-1">
                <Mail className="w-3.5 h-3.5 text-slate-400" /> {candidate.email}
              </span>
              {candidate.phone && candidate.phone !== "N/A" && (
                <span className="flex items-center gap-1">
                  <Phone className="w-3.5 h-3.5 text-slate-400" /> {candidate.phone}
                </span>
              )}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Scrollable Body */}
        <div className="p-6 space-y-6 overflow-y-auto">
          {/* Executive Verdict Callout */}
          <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/80">
            <div className="flex items-start gap-3">
              <Award className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
              <div>
                <p className="text-xs font-bold text-cyan-400 uppercase tracking-wider">AI Hiring Recommendation</p>
                <p className="text-sm font-semibold text-white mt-0.5">{candidate.verdict || candidate.status}</p>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed">{candidate.summary}</p>
              </div>
            </div>
          </div>

          {/* Three-Factor Scoring Breakdown */}
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Scoring Vector Breakdown</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {/* Skill Match */}
              <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/60">
                <div className="flex justify-between items-center text-xs mb-1.5">
                  <span className="text-slate-400">Skill Coverage (45%)</span>
                  <span className="font-bold text-emerald-400">{breakdown.skill_score_pct || 80}%</span>
                </div>
                <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-400 rounded-full"
                    style={{ width: `${breakdown.skill_score_pct || 80}%` }}
                  />
                </div>
              </div>

              {/* Semantic Similarity */}
              <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/60">
                <div className="flex justify-between items-center text-xs mb-1.5">
                  <span className="text-slate-400">Semantic Cosine (40%)</span>
                  <span className="font-bold text-cyan-400">{breakdown.semantic_score_pct || 85}%</span>
                </div>
                <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-400 rounded-full"
                    style={{ width: `${breakdown.semantic_score_pct || 85}%` }}
                  />
                </div>
              </div>

              {/* Experience Match */}
              <div className="p-3.5 rounded-xl bg-slate-800/40 border border-slate-700/60">
                <div className="flex justify-between items-center text-xs mb-1.5">
                  <span className="text-slate-400">Tenure Ratio (15%)</span>
                  <span className="font-bold text-purple-400">{breakdown.experience_score_pct || 100}%</span>
                </div>
                <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-purple-400 rounded-full"
                    style={{ width: `${breakdown.experience_score_pct || 100}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Matched vs Missing Skills */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Matched Skills */}
            <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20">
              <div className="flex items-center space-x-2 text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">
                <CheckCircle className="w-4 h-4" />
                <span>Verified Matched Skills ({candidate.matched_skills?.length || 0})</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(candidate.matched_skills || []).map((skill) => (
                  <span
                    key={skill}
                    className="px-2.5 py-1 rounded-md bg-emerald-900/40 text-emerald-300 border border-emerald-500/30 text-xs font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="p-4 rounded-xl bg-red-950/20 border border-red-500/20">
              <div className="flex items-center space-x-2 text-xs font-bold text-red-400 uppercase tracking-wider mb-2">
                <XCircle className="w-4 h-4" />
                <span>Target Skills Missing ({candidate.missing_skills?.length || 0})</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(candidate.missing_skills || []).length === 0 ? (
                  <p className="text-xs text-slate-400 italic">All target skills satisfied!</p>
                ) : (
                  (candidate.missing_skills || []).map((skill) => (
                    <span
                      key={skill}
                      className="px-2.5 py-1 rounded-md bg-red-900/40 text-red-300 border border-red-500/30 text-xs font-medium"
                    >
                      {skill}
                    </span>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Experience Snippets */}
          {candidate.experience_snippets && candidate.experience_snippets.length > 0 && (
            <div>
              <div className="flex items-center space-x-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                <Briefcase className="w-4 h-4 text-cyan-400" />
                <span>Extracted Work Experience Snippets</span>
              </div>
              <div className="space-y-2">
                {candidate.experience_snippets.map((snip, i) => (
                  <div key={i} className="p-3 rounded-lg bg-slate-800/50 border border-slate-700/50 text-xs text-slate-300 leading-relaxed">
                    • {snip}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Education & Links */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {candidate.education && candidate.education.length > 0 && (
              <div>
                <div className="flex items-center space-x-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  <BookOpen className="w-4 h-4 text-cyan-400" />
                  <span>Education & Degrees</span>
                </div>
                <div className="space-y-1.5">
                  {candidate.education.map((edu, idx) => (
                    <p key={idx} className="text-xs text-slate-300 bg-slate-800/40 p-2 rounded-lg border border-slate-700/40">
                      {edu}
                    </p>
                  ))}
                </div>
              </div>
            )}

            {candidate.links && Object.keys(candidate.links).length > 0 && (
              <div>
                <div className="flex items-center space-x-2 text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  <ExternalLink className="w-4 h-4 text-cyan-400" />
                  <span>Verified Profiles</span>
                </div>
                <div className="space-y-1.5">
                  {candidate.links.linkedin && (
                    <a
                      href={candidate.links.linkedin}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-2 text-xs text-cyan-400 hover:text-cyan-300 bg-slate-800/40 p-2 rounded-lg border border-slate-700/40 truncate"
                    >
                      <Link2 className="w-3.5 h-3.5 shrink-0" />
                      <span className="truncate">{candidate.links.linkedin}</span>
                    </a>
                  )}
                  {candidate.links.github && (
                    <a
                      href={candidate.links.github}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-2 text-xs text-cyan-400 hover:text-cyan-300 bg-slate-800/40 p-2 rounded-lg border border-slate-700/40 truncate"
                    >
                      <Globe className="w-3.5 h-3.5 shrink-0" />
                      <span className="truncate">{candidate.links.github}</span>
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/90 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition"
          >
            Close Profile
          </button>
        </div>
      </div>
    </div>
  );
}
