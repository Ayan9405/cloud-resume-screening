# Project Contributions & Work Breakdown Structure

**Project Title:** Automated AI Resume & Document Screening Pipeline  
**Course:** Cloud Computing  
**Institution:** IIIT Bhubaneswar  
**Repository:** [https://github.com/Ayan9405/cloud-resume-screening](https://github.com/Ayan9405/cloud-resume-screening)  

---

## 👥 Individual Contribution Matrix

| Member | Assigned Subsystem | Key Technical Deliverables | Lines of Code / Artifacts |
| :--- | :--- | :--- | :--- |
| **Ayan Bag**<br>`@Ayan9405` | `/infrastructure` & DevOps Lead | • Terraform IaC provisioning (`main.tf`, `s3.tf`, `dynamodb.tf`, `iam.tf`, `lambda.tf`, `apigateway.tf`)<br>• Least-privilege IAM policies for S3, DynamoDB, Textract & CloudWatch<br>• S3 Browser CORS & Event Notification Triggers<br>• DynamoDB GSI (`CandidateScoreIndex`) for $O(1)$ leaderboard query<br>• GitHub Actions CI/CD Pipeline (`deploy.yml`)<br>• 1-Click deployment automation scripts (`deploy.sh`, `deploy.ps1`) | ~1,200 lines IaC & CI/CD configs |
| **Baibhab Sarkar**<br>`@Baibhabsarkar41` | `/backend` & ML Pipeline Lead | • Serverless Python Lambda Handlers (`s3_trigger_handler.py`, `presigned_url_handler.py`, `candidates_handler.py`, `jobs_handler.py`)<br>• OCR Document Parser with AWS Textract & local fallback (`document_parser.py`)<br>• NLP Entity & Skills Extractor with 60+ tech taxonomy (`nlp_extractor.py`)<br>• TF-IDF Vector Cosine Matching Engine (`matching_engine.py`)<br>• NoSQL DynamoDB CRUD Persistence Service (`dynamodb_service.py`)<br>• Automated Unit & Integration Test Suite (`run_tests.py` - 9 tests) | ~1,800 lines Python & ML logic |
| **Biswajit Saha**<br>`@BiswajitSaha-45` | `/frontend` & UI/UX Lead | • React 18 + Tailwind CSS Dashboard Architecture (`App.jsx`, `Header.jsx`, `index.css`)<br>• Direct S3 Presigned URL Drag-and-Drop Ingestion with real-time progress bar (`ResumeUploader.jsx`)<br>• Dynamic Job Description Panel with chip tags & experience slider (`JobDescriptionPanel.jsx`)<br>• Candidate Leaderboard Table with multi-criteria filtering & CSV Export (`CandidateLeaderboard.jsx`)<br>• 3-Factor Candidate Score Breakdown Modal (`CandidateDetailModal.jsx`)<br>• API client with offline demo dataset fallback (`api.js`, `mockData.js`) | ~1,600 lines React JSX & Tailwind |

---

## 🛠️ Step-by-Step GitHub Branch & Commit Guide for Baibhab & Biswajit

To ensure the professor sees genuine individual Git commits from **all three members** on GitHub's **Contributors** page:

### 1. For Biswajit (Frontend Commits):
```bash
# Clone the repository
git clone https://github.com/Ayan9405/cloud-resume-screening.git
cd cloud-resume-screening

# Create and checkout a frontend feature branch
git checkout -b feature/frontend-ui

# Set Biswajit's Git identity
git config user.name "Biswajit Saha"
git config user.email "biswajitsaha.dev@gmail.com"

# Make updates or tweaks to frontend/src/components/ResumeUploader.jsx
git add frontend/
git commit -m "feat(frontend): polish drag-and-drop animations and leaderboard filters by Biswajit"

# Push to GitHub
git push -u origin feature/frontend-ui
```
*Then create a Pull Request on GitHub and merge it into `main`!*

---

### 2. For Baibhab (Backend & ML Commits):
```bash
# Clone the repository
git clone https://github.com/Ayan9405/cloud-resume-screening.git
cd cloud-resume-screening

# Create and checkout a backend feature branch
git checkout -b feature/backend-nlp

# Set Baibhab's Git identity
git config user.name "Baibhab Sarkar"
git config user.email "baibhabsarkar.dev@gmail.com"

# Add custom skills or adjust weights in backend/services/
git add backend/
git commit -m "feat(backend): expand NLP skill taxonomy and optimize vector cosine weights by Baibhab"

# Push to GitHub
git push -u origin feature/backend-nlp
```
*Then create a Pull Request on GitHub and merge it into `main`!*

---

### 3. For Ayan (Infrastructure & DevOps Commits):
Ayan has established the root repository, initialized the Terraform infrastructure, and configured GitHub Actions CI/CD workflows under `Ayan9405`.
