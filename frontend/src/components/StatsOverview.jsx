import React from "react";
import { Users, Award, TrendingUp, CheckCircle, FileText } from "lucide-react";

export function StatsOverview({ candidates = [] }) {
  const total = candidates.length;
  const topScore = total > 0 ? Math.max(...candidates.map((c) => c.match_score || 0)) : 0;
  const avgScore = total > 0 ? (candidates.reduce((sum, c) => sum + (c.match_score || 0), 0) / total).toFixed(1) : 0;
  const shortlisted = candidates.filter((c) => (c.match_score || 0) >= 80).length;

  const stats = [
    {
      label: "Total Screened",
      value: total,
      sub: "Processed documents",
      icon: Users,
      color: "from-blue-500 to-indigo-600",
      textColor: "text-blue-400",
      borderColor: "border-blue-500/20",
    },
    {
      label: "Top Match Score",
      value: total > 0 ? `${topScore.toFixed(1)}%` : "0%",
      sub: "Highest ranking fit",
      icon: Award,
      color: "from-emerald-500 to-teal-600",
      textColor: "text-emerald-400",
      borderColor: "border-emerald-500/20",
    },
    {
      label: "Average Match",
      value: total > 0 ? `${avgScore}%` : "0%",
      sub: "Cohort mean score",
      icon: TrendingUp,
      color: "from-cyan-500 to-blue-600",
      textColor: "text-cyan-400",
      borderColor: "border-cyan-500/20",
    },
    {
      label: "Interview Ready",
      value: shortlisted,
      sub: "Score ≥ 80% (Recommended)",
      icon: CheckCircle,
      color: "from-purple-500 to-pink-600",
      textColor: "text-purple-400",
      borderColor: "border-purple-500/20",
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {stats.map((stat, idx) => {
        const Icon = stat.icon;
        return (
          <div
            key={idx}
            className={`p-4 rounded-xl bg-slate-900/70 border ${stat.borderColor} backdrop-blur-sm relative overflow-hidden group hover:border-slate-600 transition-all`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{stat.label}</p>
                <p className="text-2xl font-bold text-white mt-1 group-hover:scale-105 transition-transform origin-left">
                  {stat.value}
                </p>
                <p className="text-[11px] text-slate-500 mt-1">{stat.sub}</p>
              </div>
              <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} text-white shadow-md`}>
                <Icon className="w-5 h-5" />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
