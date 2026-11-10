import React, { useState, useEffect } from "react";
import { Header } from "./components/Header";
import { StatsOverview } from "./components/StatsOverview";
import { JobDescriptionPanel } from "./components/JobDescriptionPanel";
import { ResumeUploader } from "./components/ResumeUploader";
import { CandidateLeaderboard } from "./components/CandidateLeaderboard";
import { CandidateDetailModal } from "./components/CandidateDetailModal";
import {
  fetchActiveJob,
  fetchJobs,
  saveJob,
  fetchCandidates,
  deleteCandidate,
  rescoreCandidates,
} from "./services/api";

export function App() {
  const [activeJob, setActiveJob] = useState(null);
  const [allJobs, setAllJobs] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initial load
  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const [job, jobsList, candidateList] = await Promise.all([
          fetchActiveJob(),
          fetchJobs(),
          fetchCandidates(),
        ]);
        setActiveJob(job);
        setAllJobs(jobsList);
        setCandidates(candidateList);
      } catch (err) {
        console.error("Initialization error:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  // Job selection change
  const handleSelectJob = (jobId) => {
    const found = allJobs.find((j) => j.job_id === jobId);
    if (found) {
      setActiveJob(found);
      // Fetch or re-score candidates for this specific job
      fetchCandidates(jobId).then(setCandidates);
    }
  };

  // Save updated job description
  const handleSaveJob = async (updatedJob) => {
    const saved = await saveJob(updatedJob);
    setActiveJob(saved);
    setAllJobs((prev) => prev.map((j) => (j.job_id === saved.job_id ? saved : j)));
  };

  // Batch re-score all candidates against active job
  const handleRescoreAll = async () => {
    if (!activeJob) return;
    const updated = await rescoreCandidates(activeJob.job_id);
    setCandidates(updated);
  };

  // Upload complete handler
  const handleUploadComplete = async (newCandidate) => {
    if (newCandidate) {
      setCandidates((prev) => {
        const filtered = prev.filter((c) => c.candidate_id !== newCandidate.candidate_id);
        const next = [newCandidate, ...filtered];
        return next.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
      });
    } else {
      // Re-fetch latest candidate list from API
      const updated = await fetchCandidates(activeJob?.job_id);
      setCandidates(updated);
    }
  };

  // Delete candidate handler
  const handleDeleteCandidate = async (candidateId) => {
    if (window.confirm("Are you sure you want to delete this candidate record?")) {
      await deleteCandidate(candidateId);
      setCandidates((prev) => prev.filter((c) => c.candidate_id !== candidateId));
      if (selectedCandidate?.candidate_id === candidateId) {
        setSelectedCandidate(null);
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navigation */}
      <Header activeJob={activeJob} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* KPI / Stats Overview */}
        <StatsOverview candidates={candidates} />

        {/* Top Split Section: Job Profile & Drag-and-Drop Ingestion */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          <JobDescriptionPanel
            activeJob={activeJob}
            allJobs={allJobs}
            onSelectJob={handleSelectJob}
            onSaveJob={handleSaveJob}
            onRescoreAll={handleRescoreAll}
          />
          <ResumeUploader
            activeJob={activeJob}
            onUploadComplete={handleUploadComplete}
          />
        </div>

        {/* Bottom Full-Width Section: Candidate Leaderboard Table */}
        <CandidateLeaderboard
          candidates={candidates}
          activeJob={activeJob}
          onSelectCandidate={setSelectedCandidate}
          onDeleteCandidate={handleDeleteCandidate}
        />
      </main>

      {/* Evaluation Detail Modal */}
      {selectedCandidate && (
        <CandidateDetailModal
          candidate={selectedCandidate}
          onClose={() => setSelectedCandidate(null)}
        />
      )}

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500">
        <p>Cloud Computing Semester Project · Automated AI Resume & Document Screening Pipeline</p>
        <p className="mt-1">Built with React, Tailwind CSS, Python AWS Lambda, Amazon S3, Textract, and DynamoDB.</p>
      </footer>
    </div>
  );
}

export default App;
