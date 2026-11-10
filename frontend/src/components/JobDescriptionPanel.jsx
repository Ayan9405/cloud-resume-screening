import React, { useState, useEffect } from "react";
import { Briefcase, Plus, X, Sparkles, Check, RefreshCw } from "lucide-react";

export function JobDescriptionPanel({
  activeJob,
  allJobs = [],
  onSelectJob,
  onSaveJob,
  onRescoreAll,
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(activeJob?.title || "");
  const [department, setDepartment] = useState(activeJob?.department || "Engineering");
  const [minExp, setMinExp] = useState(activeJob?.min_experience_years || 3);
  const [requiredSkills, setRequiredSkills] = useState(activeJob?.required_skills || []);
  const [preferredSkills, setPreferredSkills] = useState(activeJob?.preferred_skills || []);
  const [description, setDescription] = useState(activeJob?.description || "");
  const [newSkillInput, setNewSkillInput] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    if (activeJob) {
      setTitle(activeJob.title || "");
      setDepartment(activeJob.department || "Engineering");
      setMinExp(activeJob.min_experience_years || 3);
      setRequiredSkills(activeJob.required_skills || []);
      setPreferredSkills(activeJob.preferred_skills || []);
      setDescription(activeJob.description || "");
    }
  }, [activeJob]);

  const handleAddSkill = (e) => {
    e.preventDefault();
    const clean = newSkillInput.trim();
    if (clean && !requiredSkills.includes(clean)) {
      setRequiredSkills([...requiredSkills, clean]);
      setNewSkillInput("");
    }
  };

  const handleRemoveSkill = (skillToRemove) => {
    setRequiredSkills(requiredSkills.filter((s) => s !== skillToRemove));
  };

  const handleSave = async () => {
    setIsSaving(true);
    const updated = {
      ...activeJob,
      title,
      department,
      min_experience_years: Number(minExp),
      required_skills: requiredSkills,
      preferred_skills: preferredSkills,
      description,
      is_active: true,
    };
    await onSaveJob(updated);
    setIsSaving(false);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 2500);
  };

  return (
    <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl backdrop-blur-md">
      {/* Panel Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Job Screening Profile</h2>
            <p className="text-xs text-slate-400">Target requirements used by the AI matching engine</p>
          </div>
        </div>

        {/* Preset Selector Dropdown */}
        <div className="flex items-center space-x-2">
          <select
            value={activeJob?.job_id || ""}
            onChange={(e) => onSelectJob(e.target.value)}
            className="text-xs bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            {allJobs.map((j) => (
              <option key={j.job_id} value={j.job_id}>
                {j.title}
              </option>
            ))}
          </select>

          <button
            onClick={onRescoreAll}
            title="Recalculate all candidate scores against this job description"
            className="flex items-center space-x-1 px-3 py-1.5 text-xs font-medium rounded-lg bg-slate-800 text-cyan-400 border border-slate-700 hover:bg-slate-700/80 transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Rescore All</span>
          </button>
        </div>
      </div>

      {/* Form Fields */}
      <div className="space-y-4">
        {/* Title and Experience Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-2">
            <label className="block text-xs font-semibold text-slate-300 mb-1">Job Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700 rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-1 focus:ring-cyan-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Min Experience: <span className="text-cyan-400 font-bold">{minExp} Yrs</span>
            </label>
            <input
              type="range"
              min="0"
              max="12"
              step="0.5"
              value={minExp}
              onChange={(e) => setMinExp(e.target.value)}
              className="w-full accent-cyan-500 h-2 bg-slate-700 rounded-lg cursor-pointer mt-3"
            />
          </div>
        </div>

        {/* Required Skills Chips */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-2">
            Target Required Skills <span className="text-slate-500 font-normal">({requiredSkills.length} defined)</span>
          </label>
          <div className="flex flex-wrap gap-1.5 mb-2.5">
            {requiredSkills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-cyan-950/70 border border-cyan-500/30 text-cyan-300 text-xs font-medium"
              >
                {skill}
                <button
                  type="button"
                  onClick={() => handleRemoveSkill(skill)}
                  className="text-cyan-400 hover:text-cyan-100 hover:bg-cyan-800/50 rounded p-0.5"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>

          {/* Add Skill Input */}
          <form onSubmit={handleAddSkill} className="flex gap-2">
            <input
              type="text"
              placeholder="Add skill (e.g. AWS, Terraform, Docker)..."
              value={newSkillInput}
              onChange={(e) => setNewSkillInput(e.target.value)}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
            <button
              type="submit"
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-cyan-500/30 rounded-lg text-xs font-medium flex items-center gap-1 transition"
            >
              <Plus className="w-3.5 h-3.5" /> Add
            </button>
          </form>
        </div>

        {/* Full Job Description Textarea */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1">
            Job Description & Qualifications (Used for Vector / Semantic Cosine Match)
          </label>
          <textarea
            rows="3"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-slate-800/90 border border-slate-700 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-cyan-500 font-mono leading-relaxed resize-y"
          />
        </div>

        {/* Action Button */}
        <div className="flex items-center justify-end gap-3 pt-2">
          {saveSuccess && (
            <span className="text-xs text-emerald-400 flex items-center gap-1 font-medium">
              <Check className="w-4 h-4" /> Requirements Saved!
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-lg text-xs font-semibold shadow-lg shadow-cyan-500/20 transition flex items-center gap-1.5"
          >
            {isSaving ? "Saving..." : "Save Requirements"}
          </button>
        </div>
      </div>
    </div>
  );
}
