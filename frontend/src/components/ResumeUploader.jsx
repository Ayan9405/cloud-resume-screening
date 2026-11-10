import React, { useState, useRef } from "react";
import { UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2, Sparkles, ArrowUpRight } from "lucide-react";
import { getPresignedUploadUrl, uploadFileToPresignedUrl } from "../services/api";

export function ResumeUploader({ activeJob, onUploadComplete }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadQueue, setUploadQueue] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFiles(Array.from(e.dataTransfer.files));
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFiles(Array.from(e.target.files));
    }
  };

  const processFiles = async (files) => {
    const validExtensions = [".pdf", ".docx", ".doc", ".txt"];
    const validFiles = files.filter((f) => {
      const ext = f.name.substring(f.name.lastIndexOf(".")).toLowerCase();
      return validExtensions.includes(ext);
    });

    if (validFiles.length === 0) {
      alert("Please upload valid PDF or DOCX resume documents.");
      return;
    }

    // Add files to local progress queue
    const newItems = validFiles.map((file) => ({
      id: `${Date.now()}-${file.name}`,
      file,
      name: file.name,
      size: (file.size / 1024).toFixed(1) + " KB",
      progress: 0,
      status: "requesting_url", // requesting_url -> uploading -> parsing -> completed -> error
      errorMsg: null,
    }));

    setUploadQueue((prev) => [...newItems, ...prev]);
    setIsProcessing(true);

    for (const item of newItems) {
      await uploadSingleDocument(item);
    }
    setIsProcessing(false);
  };

  const uploadSingleDocument = async (item) => {
    try {
      // Step 1: Request Presigned URL from Backend
      updateItemStatus(item.id, { status: "requesting_url", progress: 10 });
      const presignedData = await getPresignedUploadUrl(
        item.file.name,
        item.file.type || "application/pdf",
        activeJob?.job_id || "job-cloud-architect"
      );

      // Step 2: Direct HTTP PUT to Cloud Object Storage (S3 / Presigned)
      updateItemStatus(item.id, { status: "uploading", progress: 30 });
      const uploadResult = await uploadFileToPresignedUrl(
        presignedData.upload_url,
        item.file,
        (progressPercent) => {
          updateItemStatus(item.id, {
            status: "uploading",
            progress: Math.min(90, Math.round(30 + progressPercent * 0.6)),
          });
        }
      );

      // Step 3: Serverless Processing Complete (S3 Trigger -> Textract -> NLP -> DynamoDB)
      updateItemStatus(item.id, {
        status: "completed",
        progress: 100,
        result: uploadResult.candidate,
      });

      if (onUploadComplete) {
        onUploadComplete(uploadResult.candidate);
      }
    } catch (err) {
      console.error("Upload error for:", item.name, err);
      updateItemStatus(item.id, {
        status: "error",
        errorMsg: err.message || "Failed to upload document",
      });
    }
  };

  const updateItemStatus = (id, updates) => {
    setUploadQueue((prev) =>
      prev.map((item) => (item.id === id ? { ...item, ...updates } : item))
    );
  };

  // 1-Click Demo Resume Uploader
  const handleUploadDemoResume = () => {
    const demoCandidates = [
      {
        filename: "David_Vance_Cloud_DevOps.pdf",
        content: `DAVID VANCE
david.vance@example.com | +1 (555) 443-2211
Senior Cloud Platform Engineer with 5+ years of experience architecting AWS workloads with Terraform, Docker, Kubernetes, and CI/CD.
Proficient in Python, AWS Lambda, DynamoDB, Microservices, and Linux.
EDUCATION: B.S. in Computer Engineering`,
      },
      {
        filename: "Elena_Rostova_FullStack.pdf",
        content: `ELENA ROSTOVA
elena.rostova@example.com | +1 (555) 778-9900
Full Stack Cloud Engineer with 3 years experience.
Skills: Python, React, Docker, Git, REST API, AWS, PostgreSQL.
EDUCATION: B.Tech in Information Technology`,
      },
    ];

    const pick = demoCandidates[Math.floor(Math.random() * demoCandidates.length)];
    const blob = new Blob([pick.content], { type: "application/pdf" });
    const file = new File([blob], pick.filename, { type: "application/pdf" });
    processFiles([file]);
  };

  return (
    <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl backdrop-blur-md">
      {/* Box Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <UploadCloud className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Direct Storage Document Ingestion</h2>
            <p className="text-xs text-slate-400">Direct S3 Presigned Upload + Event-Driven Serverless OCR</p>
          </div>
        </div>

        <button
          onClick={handleUploadDemoResume}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-medium transition"
        >
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          Upload Demo Resume
        </button>
      </div>

      {/* Drag & Drop Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200 ${
          isDragging
            ? "border-cyan-400 bg-cyan-950/20 scale-[0.99]"
            : "border-slate-700/80 hover:border-slate-500 bg-slate-800/40 hover:bg-slate-800/70"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.doc,.txt"
          onChange={handleFileSelect}
          className="hidden"
        />

        <div className="flex flex-col items-center justify-center space-y-3">
          <div className="w-14 h-14 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center shadow-inner group-hover:scale-110 transition-transform">
            <UploadCloud className="w-7 h-7 text-cyan-400" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-200">
              Drop resumes here, or <span className="text-cyan-400 underline">browse files</span>
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Supports PDF, DOCX, DOC up to 25 MB · Secure Direct Presigned S3 PUT
            </p>
          </div>
        </div>
      </div>

      {/* Upload Progress Queue */}
      {uploadQueue.length > 0 && (
        <div className="mt-5 space-y-2.5 max-h-48 overflow-y-auto pr-1">
          {uploadQueue.map((item) => (
            <div
              key={item.id}
              className="p-3 rounded-lg bg-slate-800/70 border border-slate-700/60 flex items-center justify-between text-xs"
            >
              <div className="flex items-center space-x-3 truncate">
                <FileText className="w-4 h-4 text-cyan-400 shrink-0" />
                <div className="truncate">
                  <p className="font-medium text-slate-200 truncate">{item.name}</p>
                  <p className="text-[11px] text-slate-400">{item.size}</p>
                </div>
              </div>

              {/* Status and Progress Bar */}
              <div className="flex items-center space-x-3 shrink-0">
                <div className="w-28 bg-slate-700 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${
                      item.status === "completed"
                        ? "bg-emerald-400"
                        : item.status === "error"
                        ? "bg-red-400"
                        : "bg-cyan-400 animate-pulse"
                    }`}
                    style={{ width: `${item.progress}%` }}
                  />
                </div>

                <div className="w-24 text-right">
                  {item.status === "completed" && (
                    <span className="text-emerald-400 flex items-center justify-end gap-1 font-medium">
                      <CheckCircle2 className="w-3.5 h-3.5" /> Screened
                    </span>
                  )}
                  {item.status === "uploading" && (
                    <span className="text-cyan-400 flex items-center justify-end gap-1 font-medium">
                      <Loader2 className="w-3 h-3 animate-spin" /> {item.progress}%
                    </span>
                  )}
                  {item.status === "requesting_url" && (
                    <span className="text-slate-400 flex items-center justify-end gap-1">
                      <Loader2 className="w-3 h-3 animate-spin" /> Presigning...
                    </span>
                  )}
                  {item.status === "error" && (
                    <span className="text-red-400 flex items-center justify-end gap-1 font-medium">
                      <AlertCircle className="w-3.5 h-3.5" /> Failed
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
