import React from "react";
import { Cloud, Server, Sparkles, CheckCircle2, ShieldCheck, Cpu } from "lucide-react";

export function Header({ activeJob, serverStatus, onToggleMode }) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Cpu className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-tight">CloudScreen AI</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Serverless Pipeline
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Automated AI Resume & Document Screening · Team: <span className="text-slate-300 font-medium">Biswajit</span> (Frontend) · <span className="text-slate-300 font-medium">Baibhab</span> (Backend) · <span className="text-slate-300 font-medium">Ayan</span> (IaC)
            </p>
          </div>
        </div>

        {/* Right Info Badges */}
        <div className="flex items-center space-x-3">
          {/* Active Job Pill */}
          {activeJob && (
            <div className="hidden md:flex items-center space-x-2 px-3 py-1 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-400">Target Role:</span>
              <span className="font-semibold text-slate-200 truncate max-w-[180px]">{activeJob.title}</span>
            </div>
          )}

          {/* Cloud / Environment Status Badge */}
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300">
            <Cloud className="w-4 h-4 text-cyan-400" />
            <span className="font-medium text-slate-200">AWS Ready</span>
            <span className="text-slate-500">|</span>
            <span className="text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Live S3 & OCR
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
