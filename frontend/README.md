# /frontend - Candidate Screening Dashboard

> **Team Member:** Biswajit Saha (GitHub: @BiswajitSaha-45)  
> **Role:** Frontend Engineer & UI/UX Developer  
> **Stack:** React 18, Vite, Tailwind CSS, Lucide React, Fetch / Direct S3 XHR

---

## 🎯 Features Built

1. **Dashboard KPI Overview**:
   - Total resumes screened, Top match score %, Cohort average %, and Interview Ready counts.
2. **Job Description Configuration Panel**:
   - Preset selector ("Cloud Solutions Architect", "Machine Learning Engineer", "Full Stack Developer").
   - Target required skills tag management (add/remove skills with chips).
   - Experience slider (0 - 12 years).
   - Full job description text box used for TF-IDF / vector semantic matching.
   - 1-click **Rescore All** button.
3. **Direct Cloud Storage / Presigned URL Drag & Drop Ingestion Box**:
   - Accepts `.pdf` and `.docx` files.
   - Secure two-phase upload flow:
     - Step 1: Requests Presigned Upload URL from backend API.
     - Step 2: Directly uploads file bytes via HTTP `PUT` to AWS S3 (or local storage handler) with live progress bar (0% -> 100%).
   - "Upload Demo Resume" button for instant 1-click testing.
4. **Candidate Leaderboard Table**:
   - Ranked entries (#1, #2, #3, ...) sorted by `match_score` descending.
   - Candidate Name, Email, Phone, Experience Years.
   - Extracted Skills pills: matched target skills highlighted in emerald, missing in slate.
   - Color-coded score badges (≥80% Green, 60-79% Yellow, <60% Red).
   - Real-time search by name, email, or skill.
   - Filtering by qualification status and minimum score slider.
   - Export to CSV functionality.
5. **Detailed Candidate Evaluation Modal**:
   - Three-factor score breakdown: Skill coverage (45%), Semantic cosine similarity (40%), Experience tenure (15%).
   - Verified matched skills vs missing target skills.
   - Extracted work experience bullet points and education degrees.
   - Verified profile links (LinkedIn, GitHub).

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Run Local Development Server
```bash
npm run dev
```
Open `http://localhost:3000` (or `http://localhost:5173`) in your browser.

### 3. Build for Production (S3 / CloudFront Hosting)
```bash
npm run build
```
The production bundle will be generated in `frontend/dist/`.
