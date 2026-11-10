import React, { useState, useMemo } from "react";
import {
  Trophy,
  Search,
  Filter,
  Download,
  Trash2,
  ExternalLink,
  ChevronRight,
  Sparkles,
  CheckCircle,
  AlertTriangle,
  XCircle,
} from "lucide-react";

export function CandidateLeaderboard({
  candidates = [],
  activeJob,
  onSelectCandidate,
  onDeleteCandidate,
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [minScore, setMinScore] = useState(0);

  // Filtered and sorted candidate list
  const filteredCandidates = useMemo(() => {
    return candidates
      .filter((cand) => {
        // Search term check
        const term = searchTerm.toLowerCase();
        const matchesSearch =
          (cand.name || "").toLowerCase().includes(term) ||
          (cand.email || "").toLowerCase().includes(term) ||
          (cand.skills || []).some((s) => s.toLowerCase().includes(term));

        if (!matchesSearch) return false;

        // Minimum score check
        if ((cand.match_score || 0) < minScore) return false;

        // Status filter check
        if (statusFilter === "strong" && (cand.match_score || 0) < 80) return false;
        if (statusFilter === "review" && ((cand.match_score || 0) < 60 || (cand.match_score || 0) >= 80)) return false;
        if (statusFilter === "low" && (cand.match_score || 0) >= 60) return false;

        return true;
      })
      .sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
  }, [candidates, searchTerm, statusFilter, minScore]);

  // Export to CSV
  const handleExportCSV = () => {
    if (filteredCandidates.length === 0) return;
    const headers = ["Rank", "Name", "Email", "Phone", "Match Score %", "Status", "Experience Years", "Extracted Skills", "Matched Skills", "Missing Skills"];
    const rows = filteredCandidates.map((c, idx) => [
      idx + 1,
      `"${c.name || ""}"`,
      `"${c.email || ""}"`,
      `"${c.phone || ""}"`,
      c.match_score || 0,
      `"${c.status || ""}"`,
      c.experience_years || 0,
      `"${(c.skills || []).join(", ")}"`,
      `"${(c.matched_skills || []).join(", ")}"`,
      `"${(c.missing_skills || []).join(", ")}"`,
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Candidate_Leaderboard_${activeJob?.job_id || "export"}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getBadgeStyle = (score) => {
    if (score >= 80) {
      return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
    } else if (score >= 60) {
      return "bg-yellow-500/10 text-yellow-400 border-yellow-500/30";
    }
    return "bg-red-500/10 text-red-400 border-red-500/30";
  };

  const getRankBadge = (rank) => {
    if (rank === 1) return "bg-gradient-to-r from-amber-400 to-yellow-500 text-slate-950 font-black shadow-md shadow-amber-500/20";
    if (rank === 2) return "bg-slate-300 text-slate-950 font-black";
    if (rank === 3) return "bg-amber-700/80 text-white font-bold";
    return "bg-slate-800 text-slate-400 font-semibold";
  };

  return (
    <div className="rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl overflow-hidden backdrop-blur-md">
      {/* Table Header and Controls */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Trophy className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white tracking-tight">Candidate Leaderboard</h2>
                <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  {filteredCandidates.length} Active
                </span>
              </div>
              <p className="text-xs text-slate-400">Ranked by Vector Semantic Similarity and Skill Coverage</p>
            </div>
          </div>

          {/* Export CSV button */}
          <button
            onClick={handleExportCSV}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700/80 text-slate-200 border border-slate-700 text-xs font-medium transition"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        </div>

        {/* Filters Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4 pt-4 border-t border-slate-800/80">
          {/* Search Input */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by name, email, or skill..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-slate-400 shrink-0" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="all">All Qualifications (Any)</option>
              <option value="strong">Strong Match (≥ 80%)</option>
              <option value="review">Review Required (60 - 79%)</option>
              <option value="low">Low Match (&lt; 60%)</option>
            </select>
          </div>

          {/* Score Slider */}
          <div className="flex items-center space-x-3 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/60 text-xs">
            <span className="text-slate-400 shrink-0">Min Score:</span>
            <input
              type="range"
              min="0"
              max="95"
              step="5"
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="w-full accent-cyan-500 h-1.5 bg-slate-700 rounded-lg cursor-pointer"
            />
            <span className="text-cyan-400 font-bold w-10 text-right">{minScore}%</span>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-800/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
            <tr>
              <th className="py-3 px-4 w-14 text-center">Rank</th>
              <th className="py-3 px-4">Candidate</th>
              <th className="py-3 px-4">Extracted Skills</th>
              <th className="py-3 px-4 text-center">Tenure</th>
              <th className="py-3 px-4 text-center">Match Score</th>
              <th className="py-3 px-4 text-center">Status</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredCandidates.length === 0 ? (
              <tr>
                <td colSpan="7" className="py-12 text-center text-slate-500">
                  No candidate records found matching current filters.
                </td>
              </tr>
            ) : (
              filteredCandidates.map((cand, idx) => {
                const rank = idx + 1;
                const score = cand.match_score || 0;
                const matchedSet = new Set((cand.matched_skills || []).map((s) => s.toLowerCase()));

                return (
                  <tr
                    key={cand.candidate_id || idx}
                    className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                    onClick={() => onSelectCandidate(cand)}
                  >
                    {/* Rank */}
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs ${getRankBadge(
                          rank
                        )}`}
                      >
                        #{rank}
                      </span>
                    </td>

                    {/* Candidate Name & Contact */}
                    <td className="py-3.5 px-4">
                      <div>
                        <p className="font-semibold text-slate-100 group-hover:text-cyan-400 transition-colors text-sm">
                          {cand.name}
                        </p>
                        <p className="text-slate-400 text-[11px] truncate">{cand.email}</p>
                        {cand.phone && cand.phone !== "N/A" && (
                          <p className="text-slate-500 text-[10px]">{cand.phone}</p>
                        )}
                      </div>
                    </td>

                    {/* Skills Chips */}
                    <td className="py-3.5 px-4 max-w-xs">
                      <div className="flex flex-wrap gap-1">
                        {(cand.skills || []).slice(0, 5).map((skill) => {
                          const isMatch = matchedSet.has(skill.toLowerCase());
                          return (
                            <span
                              key={skill}
                              className={`px-2 py-0.5 rounded text-[10px] font-medium border ${
                                isMatch
                                  ? "bg-emerald-950/60 text-emerald-300 border-emerald-500/30 font-semibold"
                                  : "bg-slate-800 text-slate-400 border-slate-700"
                              }`}
                            >
                              {skill}
                            </span>
                          );
                        })}
                        {(cand.skills || []).length > 5 && (
                          <span className="px-1.5 py-0.5 rounded text-[10px] text-slate-500 bg-slate-800/50">
                            +{(cand.skills || []).length - 5} more
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Experience Tenure */}
                    <td className="py-3.5 px-4 text-center font-medium text-slate-300">
                      {cand.experience_years ? `${cand.experience_years} yrs` : "N/A"}
                    </td>

                    {/* Match Score */}
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold border ${getBadgeStyle(
                          score
                        )}`}
                      >
                        {score.toFixed(1)}%
                      </span>
                    </td>

                    {/* Status Verdict */}
                    <td className="py-3.5 px-4 text-center">
                      <span className="text-[11px] font-medium text-slate-300">
                        {cand.status}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-right">
                      <div
                        className="flex items-center justify-end space-x-1"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <button
                          onClick={() => onSelectCandidate(cand)}
                          title="View Evaluation Breakdown"
                          className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-400 hover:bg-slate-800 transition"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onDeleteCandidate(cand.candidate_id)}
                          title="Delete Candidate"
                          className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
