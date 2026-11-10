# 10-Minute Video Demonstration & Speech Script

**Project Title:** Automated AI Resume & Document Screening Pipeline  
**Course:** Cloud Computing  
**Institution:** IIIT Bhubaneswar  
**Target Video Duration:** Exactly 10:00 Minutes  
**Repository:** [https://github.com/Ayan9405/cloud-resume-screening](https://github.com/Ayan9405/cloud-resume-screening)  

---

## ⏱️ Video Timeline & Speaker Breakdown

```
┌────────────────────────────────────────────────────────┐
│ 🎬 PART 1 (0:00 - 3:00) — AYAN BAG                     │
│    • Team Introduction & Project Problem Statement     │
│    • Why Cloud Computing & Architecture Overview       │
│    • Terraform IaC, S3, DynamoDB, IAM Security & CI/CD │
├────────────────────────────────────────────────────────┤
│ ⚙️ PART 2 (3:00 - 6:00) — BAIBHAB SARKAR               │
│    • Event-Driven Serverless Pipeline (S3 to Lambda)   │
│    • OCR Text Extraction (Amazon Textract) & NLP       │
│    • TF-IDF Vector Cosine Similarity & 3-Tier Scoring  │
│    • DynamoDB NoSQL Persistence & GSI Indexing         │
├────────────────────────────────────────────────────────┤
│ 🖥️ PART 3 (6:00 - 9:00) — BISWAJIT SAHA                │
│    • Frontend Architecture & Direct S3 Presigned Upload│
│    • LIVE SCREEN DEMONSTRATION                         │
│    • Job Panel, Drag-and-Drop, Leaderboard, CSV Export │
├────────────────────────────────────────────────────────┤
│ 🎯 PART 4 (9:00 - 10:00) — ALL MEMBERS (CONCLUSION)    │
│    • Final takeaways, enterprise readiness, and thanks │
└────────────────────────────────────────────────────────┘
```

---

## 🎬 PART 1: Introduction, Cloud Architecture & DevOps (0:00 – 3:00)
**Speaker:** Ayan Bag  
**Screen Display:** Slide 1 (Title & Team) $\rightarrow$ Slide 2 (Architecture Diagram) $\rightarrow$ Slide 3 (Terraform & GitHub Actions)

---

### [0:00 – 0:45] Group Formation & Problem Statement
> *"Hello everyone and respected Ma'am. Welcome to our project presentation for Cloud Computing.*
>
> *Our project is titled **'Automated AI Resume and Document Screening Pipeline'**. Our group comprises three members, each owning a distinct layer of the cloud stack:*
> * *Myself, **Ayan Bag**, leading the **Cloud Infrastructure, Security, and DevOps**.*
> * ***Baibhab Sarkar**, leading the **Backend Serverless and Machine Learning Pipeline**.*
> * *And **Biswajit Saha**, leading the **Frontend Engineering, UI/UX, and Cloud Storage Client Integration**.*
>
> *In modern enterprise recruitment, HR departments receive thousands of resumes for a single job opening. Manual screening creates massive hiring delays, human bias, and severe operational bottlenecks. We engineered an event-driven serverless cloud solution on AWS that automates resume ingestion, extracts text via OCR, parses technical qualifications using NLP, and ranks candidates against job requirements using vector semantic matching."*

---

### [0:45 – 1:45] Why Cloud Computing & System Architecture
> *(Screen switches to Architecture Diagram in `README.md`)*  
>
> *"Why did we build this natively on the Cloud rather than a traditional server?*
> 1. *First: **Auto-scalability**. Recruitment traffic is extremely bursty. When a job is posted, thousands of documents arrive simultaneously. Traditional servers would crash or suffer latency spikes. Our serverless architecture scales from zero to thousands of concurrent executions instantaneously.*
> 2. *Second: **Zero Idle Cost**. With AWS Lambda and DynamoDB on-demand billing, when no resumes are uploaded, compute cost is literally zero dollars.*
> 3. *Third: **Decoupled Asynchronous Processing**. We decouple document uploads from processing using S3 event triggers, ensuring the recruiter's UI never freezes while waiting for heavy OCR computations."*

---

### [1:45 – 3:00] Infrastructure as Code (Terraform) & Security
> *(Screen shows `infrastructure/terraform/` code and GitHub Actions tab)*  
>
> *"To ensure 100% reproducible and auditable cloud deployments, I authored all cloud infrastructure declaratively using HashiCorp Terraform across seven modular configuration files:*
> * *In `s3.tf`, I provisioned an encrypted Amazon S3 bucket with browser CORS rules, enabling direct client uploads, and configured lifecycle rules to transition old documents automatically.*
> * *In `dynamodb.tf`, I designed an on-demand NoSQL database with a Global Secondary Index called `CandidateScoreIndex`, allowing $O(1)$ constant-time retrieval of candidates sorted by match score descending.*
> * *In `iam.tf`, I enforced strict least-privilege security policies, restricting Lambda execution roles strictly to our specific S3 bucket and DynamoDB table ARNs with zero wildcard permissions.*
> * *Finally, in `.github/workflows/deploy.yml`, I built an automated CI/CD pipeline that runs automated Python unit tests, builds the React frontend, and validates Terraform code on every push.*
>
> *Now, Baibhab will explain how our serverless backend and AI pipeline process and evaluate these resumes."*

---

## ⚙️ PART 2: Serverless Backend, OCR & Vector Matching (3:00 – 6:00)
**Speaker:** Baibhab Sarkar  
**Screen Display:** Slide 4 (Event Flow) $\rightarrow$ Slide 5 (OCR/NLP Extraction) $\rightarrow$ Slide 6 (Scoring Formula & Python Code)

---

### [3:00 – 4:00] Serverless Event-Driven Trigger & Document Parsing (OCR)
> *"Thank you, Ayan. Hello Ma'am, I am Baibhab Sarkar, and I engineered the serverless backend and AI matching engine.*
>
> *Our backend operates on a purely asynchronous, event-driven paradigm. The moment a resume lands in our Amazon S3 storage bucket, S3 automatically emits an `s3:ObjectCreated:*` notification. This event instantly triggers our Python AWS Lambda function, which fetches the document bytes without routing heavy payloads through an API Gateway.*
>
> *To extract the raw text from multi-page PDFs and Word DOCX documents, I built our `DocumentParser` service. It natively integrates with Amazon Textract using the `detect_document_text` API for cloud optical character recognition, while also providing a high-speed local PDF and DOCX fallback parser for development and automated testing."*

---

### [4:00 – 5:00] NLP Entity Extraction & Keyword Mitigation
> *(Screen shows `backend/services/nlp_extractor.py` and `matching_engine.py`)*  
>
> *"Once raw text is extracted, our `NLPExtractor` pipeline structures the candidate data:*
> * *It extracts candidate contact details, including RFC-compliant email matching, international phone numbers, and full names.*
> * *For skills, it scans candidate text against our curated 60+ technology taxonomy covering Cloud platforms, DevOps, Programming languages, and AI/ML frameworks.*
> * *Crucially, to prevent keyword stuffing—where candidates simply copy-paste a list of skills—our extractor analyzes date ranges (such as '2021 to Present') to calculate verified years of professional tenure and extracts specific achievement bullet points.*
> * *It also extracts academic qualifications, identifying degrees such as B.S., B.Tech, and Master's."*

---

### [5:00 – 6:00] Vector Semantic Matching Engine & DynamoDB Persistence
> *"Next comes our core scoring intelligence. In `matching_engine.py`, I implemented a composite three-tier mathematical formula:*
>
> $$\text{Final Score} = (\text{Skill Match} \times 0.45) + (\text{Semantic Cosine} \times 0.40) + (\text{Tenure Ratio} \times 0.15)$$
>
> *1. **Skill Match (45%)** evaluates the weighted coverage of mandatory required skills versus preferred skills.*  
> *2. **Semantic Cosine (40%)** vectorizes the resume and job description using Scikit-Learn TF-IDF n-grams to calculate contextual cosine similarity.*  
> *3. **Tenure Ratio (15%)** compares verified experience against the target role requirement.*  
>
> *The resulting score, candidate profile, matched skills, missing skills, and detailed breakdown are persisted into DynamoDB via our `DynamoDBService`.*
>
> *I also wrote nine automated unit and integration tests in `run_tests.py`, which execute in under 0.03 seconds and are verified automatically by our CI/CD pipeline.*
>
> *Now, Biswajit will demonstrate our frontend dashboard and walk you through a live resume screening demonstration."*

---

## 🖥️ PART 3: Frontend Architecture & Live Demonstration (6:00 – 9:00)
**Speaker:** Biswajit Saha  
**Screen Display:** Live Browser Dashboard at `http://localhost:3000` (or Vercel Live URL)

---

### [6:00 – 7:00] Frontend Architecture & Direct S3 Presigned Uploads
> *"Thank you, Baibhab. Hello Ma'am, I am Biswajit Saha, and I designed and developed the frontend screening dashboard and direct cloud storage ingestion.*
>
> *I built the application using React 18, Vite, and Tailwind CSS with a clean glassmorphism theme designed for recruiter productivity.*
>
> *A critical cloud engineering decision I implemented is our **Direct S3 Presigned URL upload flow**. In traditional web applications, users upload files directly through backend application servers. This wastes server bandwidth, exhausts memory, and causes timeout errors on large files.*
>
> *In our architecture, when a recruiter drops a file, the frontend requests an authorized Presigned PUT URL from our API, and then streams the document directly from the user's browser to Amazon S3 via an encrypted XHR request, accompanied by a real-time 0% to 100% progress bar.*
>
> *Let's see this in action live on screen!"*

---

### [7:00 – 9:00] LIVE PRODUCT DEMONSTRATION (Step-by-Step on Screen)
*(Biswajit shares his screen showing the active dashboard at `http://localhost:3000`)*

1. **[7:00 – 7:25] KPI Overview & Job Description Panel:**
   > *(Biswajit points to top metrics)*  
   > *"At the top of our dashboard, recruiters immediately see real-time cohort statistics: Total Resumes Screened, Top Match Score, Cohort Average, and Interview Ready candidates.*
   >
   > *(Biswajit points to the left panel)*  
   > *On the left is our Job Screening Profile. We can switch between pre-configured enterprise roles—such as 'Senior Cloud Solutions Architect' or 'Machine Learning Engineer'. We can dynamically add or remove target required skills using these interactive chips, and adjust the minimum experience slider."*

2. **[7:25 – 8:05] Live Document Ingestion & Animated Progress Bar:**
   > *(Biswajit clicks the 'Upload Demo Resume' button or drags a PDF)*  
   > *"Now watch our ingestion box on the right. When I click 'Upload Demo Resume'—or drag and drop a PDF file—you can see our animated progress bar track the direct upload to storage.*
   >
   > *Within milliseconds, the S3 trigger fires, the OCR and NLP pipeline extracts skills and experience, and the candidate is immediately parsed, scored, and inserted into our Leaderboard!"*

3. **[8:05 – 8:40] Candidate Leaderboard & Evaluation Breakdown Modal:**
   > *(Biswajit points to the Leaderboard table and clicks Sarah Jenkins' row)*  
   > *"Here in our Leaderboard, candidates are ranked from highest to lowest score with color-coded badges: Green for recommended candidates above 80%, Yellow for review, and Red for low match.*
   >
   > *When I click on Sarah Jenkins, our detailed Evaluation Modal appears. It gives recruiters full transparency into the AI's hiring recommendation:*
   > * *We see the exact three-tier breakdown: 100% skill coverage, 92% semantic cosine similarity, and 100% experience tenure.*
   > * *We see verified matched skills in emerald chips, missing skills in red, verified work experience snippets, and academic degrees.*
   > * *Recruiters can also click verified LinkedIn and GitHub profiles directly."*

4. **[8:40 – 9:00] Dynamic Rescoring & CSV Export:**
   > *(Biswajit clicks 'Rescore All' and then 'Export CSV')*  
   > *"If the recruiter decides to update job requirements—say, adding another mandatory skill—clicking 'Rescore All' recalculates and re-ranks all candidates instantly.*
   >
   > *Finally, clicking 'Export CSV' downloads a formatted spreadsheet of the entire candidate leaderboard, ready for HR management."*

---

## 🎯 PART 4: Conclusion & Cloud Takeaways (9:00 – 10:00)
**Speakers:** Biswajit Saha $\rightarrow$ Baibhab Sarkar $\rightarrow$ Ayan Bag

---

### [9:00 – 9:20] Biswajit Saha:
> *"From a frontend and client perspective, adopting direct S3 presigned uploads and optimistic UI updating transformed our document processing from a slow, blocking task into a seamless, modern web experience."*

### [9:20 – 9:40] Baibhab Sarkar:
> *"From a backend perspective, pairing Amazon Textract and NLP with serverless Lambda execution gives us infinite horizontal scaling while keeping cloud operating expenses strictly proportional to usage."*

### [9:40 – 10:00] Ayan Bag (Closing Sign-off):
> *(Ayan concludes on video)*  
> *"And from a Cloud Architecture and DevOps perspective, defining our complete infrastructure as code via Terraform and automating testing through GitHub Actions gives us enterprise reliability, reproducibility, and security.*
>
> *Our full codebase, documentation, and live deployment configurations are publicly available on GitHub at `Ayan9405/cloud-resume-screening`.*
>
> *Thank you very much Ma'am for your guidance throughout this course. We are now open to any questions!"*

---
*(Video ends at 10:00)*
