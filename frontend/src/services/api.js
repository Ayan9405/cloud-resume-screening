/**
 * API Service for AI Resume Screening Pipeline.
 * Handles presigned S3 uploads, direct uploads, candidate leaderboard,
 * and job description operations with graceful fallback for offline demos.
 */

import { INITIAL_JOBS, INITIAL_CANDIDATES } from "./mockData";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Fallback in-memory state for offline/demo mode
let localCandidates = [...INITIAL_CANDIDATES];
let localJobs = [...INITIAL_JOBS];

export async function fetchActiveJob() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/jobs/active`);
    if (!res.ok) throw new Error("Failed to fetch active job from API");
    return await res.json();
  } catch (err) {
    console.warn("API unavailable, using local active job:", err.message);
    return localJobs.find((j) => j.is_active) || localJobs[0];
  }
}

export async function fetchJobs() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/jobs`);
    if (!res.ok) throw new Error("Failed to fetch jobs from API");
    const data = await res.json();
    return data.jobs || [];
  } catch (err) {
    console.warn("API unavailable, using local jobs list:", err.message);
    return localJobs;
  }
}

export async function saveJob(jobData) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/jobs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(jobData),
    });
    if (!res.ok) throw new Error("Failed to save job");
    const data = await res.json();
    return data.job;
  } catch (err) {
    console.warn("API unavailable, updating local job:", err.message);
    const existingIndex = localJobs.findIndex((j) => j.job_id === jobData.job_id);
    if (existingIndex >= 0) {
      localJobs[existingIndex] = { ...localJobs[existingIndex], ...jobData };
    } else {
      localJobs.push({ ...jobData, job_id: jobData.job_id || `job-${Date.now()}` });
    }
    return jobData;
  }
}

export async function fetchCandidates(jobId) {
  try {
    const url = jobId
      ? `${API_BASE_URL}/api/candidates?job_id=${encodeURIComponent(jobId)}`
      : `${API_BASE_URL}/api/candidates`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch candidates from API");
    const data = await res.json();
    return data.candidates || [];
  } catch (err) {
    console.warn("API unavailable, using local candidates list:", err.message);
    let list = [...localCandidates];
    if (jobId) {
      list = list.filter((c) => c.job_id === jobId);
    }
    return list.sort((a, b) => (b.match_score || 0) - (a.match_score || 0));
  }
}

export async function deleteCandidate(candidateId) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/candidates/${candidateId}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete candidate");
    return true;
  } catch (err) {
    console.warn("API unavailable, deleting from local candidates:", err.message);
    localCandidates = localCandidates.filter((c) => c.candidate_id !== candidateId);
    return true;
  }
}

export async function rescoreCandidates(jobId) {
  try {
    const url = jobId
      ? `${API_BASE_URL}/api/candidates/rescore?job_id=${encodeURIComponent(jobId)}`
      : `${API_BASE_URL}/api/candidates/rescore`;
    const res = await fetch(url, { method: "POST" });
    if (!res.ok) throw new Error("Failed to rescore candidates");
    const data = await res.json();
    return data.candidates || [];
  } catch (err) {
    console.warn("API unavailable, re-scoring local candidates:", err.message);
    // Simple local score recalculation
    const targetJob = localJobs.find((j) => j.job_id === jobId) || localJobs[0];
    const reqSet = new Set((targetJob.required_skills || []).map((s) => s.toLowerCase()));

    localCandidates = localCandidates.map((c) => {
      const candSkills = (c.skills || []).map((s) => s.toLowerCase());
      const matched = targetJob.required_skills.filter((s) => candSkills.includes(s.toLowerCase()));
      const missing = targetJob.required_skills.filter((s) => !candSkills.includes(s.toLowerCase()));
      const overlapPct = reqSet.size > 0 ? (matched.length / reqSet.size) * 100 : 80;
      const score = Math.min(99.0, Math.round((overlapPct * 0.6 + (c.experience_years / targetJob.min_experience_years) * 35) * 10) / 10);

      return {
        ...c,
        job_id: targetJob.job_id,
        match_score: score,
        matched_skills: matched,
        missing_skills: missing,
        status: score >= 80 ? "Strong Match" : score >= 60 ? "Moderate Match" : "Low Match",
        badge_color: score >= 80 ? "green" : score >= 60 ? "yellow" : "red",
      };
    });
    return [...localCandidates].sort((a, b) => b.match_score - a.match_score);
  }
}

/**
 * 1. Request Presigned URL from Backend API
 */
export async function getPresignedUploadUrl(filename, contentType, jobId) {
  try {
    const res = await fetch(`${API_BASE_URL}/api/upload-url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename, content_type: contentType, job_id: jobId }),
    });
    if (!res.ok) throw new Error("Failed to get presigned upload URL");
    return await res.json();
  } catch (err) {
    console.warn("API unavailable, falling back to direct mock upload URL:", err.message);
    return {
      upload_url: `${API_BASE_URL}/api/upload-direct`,
      s3_key: `resumes/${jobId}/${Date.now()}_${filename}`,
      filename,
      is_mock: true,
    };
  }
}

/**
 * 2. Upload file directly to S3 Bucket using Presigned PUT URL (or fallback)
 */
export function uploadFileToPresignedUrl(uploadUrl, file, onProgress) {
  return new Promise((resolve, reject) => {
    // If it's a mock or local upload route
    if (uploadUrl.includes("/api/upload-direct")) {
      const formData = new FormData();
      formData.append("file", file);

      const xhr = new XMLHttpRequest();
      xhr.open("POST", uploadUrl);

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable && onProgress) {
          const percent = Math.round((e.loaded / e.total) * 100);
          onProgress(percent);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const data = JSON.parse(xhr.responseText);
            if (data.candidate) {
              localCandidates.unshift(data.candidate);
            }
            resolve(data);
          } catch {
            resolve({ status: "success" });
          }
        } else {
          // If server responded with error, simulate mock candidate in local mode
          simulateLocalParsedCandidate(file).then(resolve).catch(reject);
        }
      };

      xhr.onerror = () => {
        // Backend offline -> simulate client-side parsed candidate
        simulateLocalParsedCandidate(file).then(resolve).catch(reject);
      };

      xhr.send(formData);
      return;
    }

    // Direct S3 Presigned URL PUT
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", uploadUrl);
    xhr.setRequestHeader("Content-Type", file.type || "application/pdf");

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        const percent = Math.round((e.loaded / e.total) * 100);
        onProgress(percent);
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve({ status: "uploaded_to_s3", s3_url: uploadUrl.split("?")[0] });
      } else {
        reject(new Error(`S3 Upload failed with HTTP status ${xhr.status}`));
      }
    };

    xhr.onerror = () => {
      reject(new Error("Network error during S3 direct upload"));
    };

    xhr.send(file);
  });
}

/**
 * Helper that creates a parsed candidate if uploading completely offline
 */
function simulateLocalParsedCandidate(file) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const nameGuess = file.name
        .replace(/\.[^/.]+$/, "")
        .replace(/[_-]/g, " ")
        .replace(/\b(resume|cv|pdf|docx)\b/gi, "")
        .trim();

      const newCand = {
        candidate_id: `cand-${Date.now()}`,
        job_id: "job-cloud-architect",
        name: nameGuess || "New Candidate",
        email: `${(nameGuess || "candidate").toLowerCase().replace(/\s+/g, ".")}@example.com`,
        phone: "+1 (555) 019-2831",
        filename: file.name,
        skills: ["AWS", "Terraform", "Docker", "Python", "CI/CD", "FastAPI"],
        experience_years: 4.5,
        match_score: 87.5,
        status: "Strong Match",
        badge_color: "green",
        verdict: "Recommended for Technical Screening",
        matched_skills: ["AWS", "Terraform", "Docker", "Python", "CI/CD"],
        missing_skills: ["Kubernetes"],
        summary: `Successfully parsed ${file.name}. Matched 5 key skills with 4.5 years experience.`,
        uploaded_at: new Date().toISOString(),
        breakdown: {
          skill_score_pct: 83.3,
          semantic_score_pct: 88.0,
          experience_score_pct: 100.0,
          candidate_experience_years: 4.5,
          required_experience_years: 4.0,
        },
        education: ["B.S. in Computer Science"],
      };

      localCandidates.unshift(newCand);
      resolve({ status: "success", candidate: newCand });
    }, 1200);
  });
}
