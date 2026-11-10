# Final Presentation Guide & Viva Defense Script

**Project Title:** Automated AI Resume & Document Screening Pipeline  
**Target Duration:** 15 – 20 Minutes (5–6 mins per member)  
**Team Members:** Ayan Bag (@Ayan9405), Baibhab Sarkar (@Baibhabsarkar41), Biswajit Saha (@BiswajitSaha-45)  

---

## 🎤 Presentation Role Distribution

```
┌────────────────────────────────┐
│  Speaker 1: Ayan Bag (5 min)   │
│  - Cloud Architecture & IaC    │
│  - S3 Storage & DynamoDB NoSQL │
│  - IAM Least Privilege & CI/CD │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────────┐
│  Speaker 2: Baibhab Sarkar (6 min) │
│  - Serverless Event Pipeline       │
│  - AWS Textract OCR & NLP          │
│  - Vector Semantic Match Engine    │
│  - DynamoDB CRUD & GSI Index       │
└───────────────┬────────────────────┘
                │
                ▼
┌───────────────────────────────────┐
│  Speaker 3: Biswajit Saha (6 min) │
│  - React Dashboard & UI/UX        │
│  - Direct S3 Presigned Upload     │
│  - LIVE DEMO & Leaderboard        │
│  - Conclusion & Future Scope      │
└───────────────────────────────────┘
```

---

## 📊 Slide-by-Slide Deck Outline & Script

### Slide 1: Title & Team Introduction (Speaker: Ayan)
- **Title:** Automated AI Resume & Document Screening Pipeline
- **Subtitle:** Event-Driven Serverless Cloud Computing Project
- **Presenter:** Ayan Bag
- **Speaking Script:**
  > *"Good morning / afternoon Ma'am and classmates. Today our team—comprising Baibhab Sarkar, Biswajit Saha, and myself, Ayan Bag—presents our Cloud Computing project: 'Automated AI Resume & Document Screening Pipeline'. In enterprise recruitment, HR teams review hundreds of candidate resumes per day. Manual screening is slow, error-prone, and biased. We built an event-driven serverless cloud system on AWS that automatically ingests resumes, extracts text using OCR, identifies technical skills and experience using NLP, and ranks candidates using vector semantic matching."*

---

### Slide 2: Problem Statement & Cloud Motivation (Speaker: Ayan)
- **Challenges:** Traditional recruiter bottlenecks, server maintenance costs, handling bursty document upload spikes.
- **Why Cloud Computing:**
  - **Auto-scalability:** Serverless compute scales from 0 to thousands of concurrent resume uploads without dedicated server instances.
  - **Cost-efficiency:** Zero idle costs with AWS Lambda and DynamoDB on-demand billing.
  - **Decoupled Architecture:** Asynchronous event processing via S3 bucket notifications.

---

### Slide 3: End-to-End System Architecture (Speaker: Ayan)
- **Diagram:** Present the sequence diagram from `README.md`.
- **Infrastructure as Code (IaC):**
  > *"All infrastructure was authored declaratively using HashiCorp Terraform across 7 modular files. We provisioned an Amazon S3 storage bucket with CORS and lifecycle rules, Amazon DynamoDB on-demand NoSQL tables, HTTP API Gateway v2, and least-privilege IAM policies. To automate quality, we implemented a GitHub Actions CI/CD workflow that tests backend and frontend code and validates Terraform on every commit."*

---

### Slide 4: Serverless Event-Driven Pipeline (Speaker: Baibhab)
- **Presenter:** Baibhab Sarkar
- **Speaking Script:**
  > *"Thank you, Ayan. I will now explain the backend processing pipeline. Our backend uses an asynchronous, event-driven pattern. When a recruiter or candidate uploads a resume to S3, an `s3:ObjectCreated:*` event triggers our Python AWS Lambda function within milliseconds. The function downloads the document bytes, bypassing any long-running HTTP server bottlenecks."*

---

### Slide 5: Document OCR & NLP Information Extraction (Speaker: Baibhab)
- **OCR Engine:** Amazon Textract integration (`detect_document_text`) with local PDF and DOCX fallback.
- **NLP Extraction Pipeline:**
  - **Contact Information:** Email (RFC regex), international phone formatting, candidate full name inference.
  - **Skill Taxonomy:** 60+ curated technology entities across Cloud (AWS, Azure, GCP, Terraform), DevOps (Docker, K8s, CI/CD), Languages (Python, Go, JS), and AI/ML.
  - **Experience & Tenure:** Date-range parser (e.g. `2021 – Present`), tenure calculation, and career accomplishment snippets.
  - **Education:** Degree classification (B.S., B.Tech, M.S., Ph.D.).

---

### Slide 6: Vector Semantic Matching Algorithm (Speaker: Baibhab)
- **Composite Scoring Formula:**
  $$\text{Final Score} = (\text{Skill Match} \times 0.45) + (\text{Semantic Cosine} \times 0.40) + (\text{Tenure Ratio} \times 0.15)$$
- **Scoring Explanation:**
  - **Skill Match (45%):** Weighted overlap of mandatory required skills (75%) vs preferred skills (25%).
  - **Semantic Cosine (40%):** TF-IDF n-gram vectorization comparing the semantic context of the resume against the job description.
  - **Tenure Ratio (15%):** Verified candidate experience versus target minimum years.
- **NoSQL Persistence:**
  - Stored in DynamoDB `ResumeScreeningCandidates` with a Global Secondary Index (`CandidateScoreIndex`) that sorts candidates by score descending in $O(1)$ lookup time.

---

### Slide 7: Frontend Architecture & UI/UX (Speaker: Biswajit)
- **Presenter:** Biswajit Saha
- **Speaking Script:**
  > *"Thank you, Baibhab. I engineered the frontend dashboard using React 18, Tailwind CSS, and Vite. Our design philosophy focuses on recruiter speed and clarity. The dashboard features four cohesive zones: KPI metrics, a Job Description panel, direct storage ingestion, and an interactive candidate leaderboard."*

---

### Slide 8: Direct Cloud Storage / Presigned URL Flow (Speaker: Biswajit)
- **Why Presigned URLs?**
  > *"In conventional web architectures, users upload heavy files directly through backend API servers, which exhausts server memory, causes timeouts, and inflates compute bills. Instead, our frontend requests an S3 Presigned PUT URL from our API, and then streams the PDF or DOCX file directly from the browser to the Amazon S3 Bucket via an encrypted XHR PUT request with real-time 0% to 100% progress tracking."*

---

### Slide 9: LIVE PRODUCT DEMONSTRATION (Speaker: Biswajit)
*(Biswajit switches screen to `http://localhost:3000`)*
1. **Show KPI Bar:** Point out Total Screened, Top Score, and Interview Ready candidates.
2. **Select Job Profile:** Switch between *Senior Cloud Solutions Architect* and *ML Engineer*.
3. **Upload Resume:** Click **"Upload Demo Resume"** or drag a real PDF into the box. Show the progress bar animate and process.
4. **Leaderboard & Badges:** Show the new candidate ranked in real-time with green/yellow/red badges.
5. **Open Candidate Modal:** Click the row to show Ma'am the 3-factor breakdown:
   - Verified matched skills (e.g. AWS, Terraform, Docker, Python).
   - Missing skills.
   - Verified work experience snippets.
6. **Click "Rescore All":** Modify a required skill and click "Rescore All" to show dynamic batch re-ranking!
7. **Export CSV:** Click "Export CSV" to show the recruiter-ready report.

---

### Slide 10: Summary of Cloud Best Practices (Speaker: Ayan)
- **Security:** Least-privilege IAM roles, S3 private bucket with SSE-S3 encryption.
- **Performance:** HTTP API Gateway v2, direct S3 streaming, DynamoDB GSI.
- **Maintainability:** Declarative Terraform IaC, automated GitHub Actions CI/CD.

---

### Slide 11: Conclusion & Future Enhancements (Speaker: All)
- **Biswajit:** Add recruiter multi-user authentication (AWS Cognito) and email notifications (Amazon SES).
- **Baibhab:** Integrate LLM-powered candidate interview question generation (AWS Bedrock / Claude).
- **Ayan:** Multi-region active-active deployment using AWS Route 53 and DynamoDB Global Tables.

---

## 🎯 Professor Viva Q&A Defense Sheet (Be Ready!)

### Question 1 (For Ayan):
> *"Why did you use S3 Presigned URLs instead of sending the file payload to a Lambda function?"*
**Answer (Ayan):**  
*"AWS Lambda has a payload size limit of 6 MB for synchronous requests and API Gateway has a 10 MB payload ceiling. Furthermore, routing large binary files through serverless compute incurs unnecessary memory duration costs. S3 Presigned URLs allow the browser to stream files directly into object storage securely, completely eliminating compute bottleneck and saving costs."*

---

### Question 2 (For Baibhab):
> *"How does your matching algorithm prevent keyword stuffing?"*
**Answer (Baibhab):**  
*"We use a composite three-tier scoring formula. Skill keywords account for 45% of the score. Another 40% comes from TF-IDF vector cosine similarity, which penalizes unnatural word frequency distribution. The remaining 15% requires verified date ranges and tenure snippets extracted via NLP date range parsing. Thus, simply listing keywords without contextual experience yields a low semantic and experience score."*

---

### Question 3 (For Biswajit):
> *"How does the frontend handle asynchronous processing if a resume takes a few seconds to parse in the cloud?"*
**Answer (Biswajit):**  
*"Our UI implements optimistic state updating with upload status tracking (`requesting_url` -> `uploading` -> `completed`). The frontend monitors the S3 upload progress via XHR event listeners, and upon upload completion, triggers a refresh query against the DynamoDB leaderboard endpoint to display the newly ranked candidate immediately."*

---

### Question 4 (General / Cloud):
> *"What makes DynamoDB better than a relational database like PostgreSQL for this project?"*
**Answer (Ayan/Baibhab):**  
*"DynamoDB is fully serverless with on-demand capacity, meaning zero idle server costs. Resume documents have flexible, semi-structured schemas (varying degrees, varying skill lists, dynamic social links) which fit NoSQL document models naturally. Furthermore, our Global Secondary Index `CandidateScoreIndex` provides consistent single-digit millisecond query performance for leaderboard retrieval regardless of database size."*
