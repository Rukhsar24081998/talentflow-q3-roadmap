# TalentFlow Q3 Roadmap — Product Decision Package (Acme Corp)

This repository contains the complete, reproducible product management submission package for the **TalentFlow Q3 Roadmap** assignment for design partner **Acme Corp**.

---

## 1. Project Overview & Deliverables

This project evaluates two executive requests from Acme's VP of People (accelerating commercial job-board integrations and addressing a reported 72% offer acceptance rate), audits 892 production recruiting records across 8 tables, specifies a mathematically sound closed offer acceptance metric, and allocates an exact 6.0 engineer-week budget across high-leverage ATS infrastructure.

### Final Submission Deliverables
The primary deliverables required by the assignment are organized as follows:

| Deliverable | File Path | Description |
| :--- | :--- | :--- |
| **D5: Executive Memo** | `deliverables/d5-one-page-memo.md` | **1-Page Executive Product Decision Memo** summarizing key findings, the 6.0 engineer-week roadmap, what we are not doing, and the metric definition. |
| **D1: VP Claims Evaluation** | `deliverables/d1-vp-claims.md` | **Reconstruction & Evaluation of the VP's Two Claims** (Job boards 26.92% parity with referrals; raw 72.22% vs 83.87% closed acceptance; verdicts: DON'T BUILD IT for both). |
| **D2: Q3 Roadmap** | `deliverables/d2-roadmap.md` | **6 Engineer-Week Roadmap** detailing 3 build initiatives (2.5w + 2.0w + 1.5w = 6.0w) and 3 explicit not-to-build initiatives. |
| **D3: Metric Specification** | `deliverables/d3-offer-acceptance-metric.md` | **Closed Offer Acceptance Rate Specification** including exact numerator, closed denominator, edge cases, and dashboard UI logic. |
| **D4: Findings (Markdown)** | `findings/findings.md` | **Structured Supporting Findings Table** containing 13 programmatically verified findings with methodology, confidence, and fact/interpretation boundaries. |
| **D4: Findings (CSV)** | `findings/findings.csv` | Machine-readable CSV export of the 13 structured findings (`Claim, Metric, Value, Method, Confidence, Evidence Classification`). |
| **Process Documentation** | `PROCESS.md` | **Complete Session Documentation** containing verbatim prompt log, elapsed time, directional shifts, and self-reflection. |

---

## 2. Engineering Capacity Allocation

The Q3 roadmap commits exactly **6.0 engineer-weeks** across three high-leverage foundational initiatives:

1. **Initiative #1: Requisition Lifecycle Automation & Cascade Dispositioning** — **2.5 engineer-weeks**  
   *Justification*: 56.19% of the active pipeline (59 of 105 active applications) is stranded on closed/filled requisitions.
2. **Initiative #2: Application-Level Source Tracking & Referral Capture** — **2.0 engineer-weeks**  
   *Justification*: Referrals convert at 53.85% (7 hires / 13 apps) vs. 2.97% for Job Boards (7 hires / 236 apps), yet 24 applications have ambiguous referral attribution.
3. **Initiative #3: Offer Lifecycle Guardrails & Metric Dashboard** — **1.5 engineer-weeks**  
   *Justification*: Decided offer acceptance is 83.87% (26 of 31), showing that the reported 72.22% rate includes unresolved Pending offers and should be separated from the defined closed-offer acceptance metric (4 unclosed pending offers past decision date).

**Total Allocation**: $2.5 + 2.0 + 1.5 = \mathbf{6.0\text{ engineer-weeks}}$ (100% capacity utilized).

---

## 3. Workflow Architecture

The investigation was conducted across a strict, phased data-trust methodology:

```
[1. Plan] ──► [2. Extract] ──► [3. Audit] ──► [4. Verify] ──► [5. Specify D3] ──► [6. Roadmap D2] ──► [7. Memo D5]
```

1. **Read-Only Data Extraction**: Fetched all 892 records via Airtable REST API using pagination and rate limiting.
2. **Relational Quality Audit**: Audited foreign key links, candidate duplicates, sourcing attribution, offer states, and scorecards.
3. **Focused Verification Pass**: Tested high-impact findings (5 pending offers, 7 negative-rated hires tracing 100% to single interviewer Rakesh Sethi).
4. **Metric & Roadmap Synthesis**: Structured findings, built specifications, and drafted the executive decision memo.

---

## 4. How to Rerun the Analysis

### Prerequisites
- Python 3.8+ (standard library only; no external third-party packages required).

### Step 1: Supply Read-Only Airtable Credentials (If re-extracting)
The Airtable source is **strictly read-only** (only HTTP `GET` requests are issued; zero create/update/delete operations). Credentials must be supplied via environment variables or a local `.env` file (never committed):

```bash
# Option A: Export environment variables in shell
export AIRTABLE_TOKEN="your_personal_access_token"
export AIRTABLE_BASE_ID="your_base_id"

# Option B: Create a local .env file based on .env.example
cp .env.example .env
# Edit .env with your credentials
```

### Step 2: Run Data Extraction (Optional / If starting from scratch)
To re-extract all 8 tables directly from Airtable:
```bash
python3 scripts/fetch_airtable.py
```
*The script throttles requests to 250ms (well under the 5 req/sec Airtable limit), traverses pagination, and caches raw data into `data/raw/`.*

### Step 3: Run the Comprehensive Data Audit & Verification Script
To reproduce all data-quality checks, metrics, and findings against the local data:
```bash
python3 scripts/audit_data.py
```
This script validates:
- Department, People, Job Opening, Candidate, Application, Interview, and Offer record counts.
- Referral vs. Job Board hire counts (7 each) and conversion rates (53.85% vs. 2.97%).
- Stranded active applications on inactive requisitions (59 of 105 = 56.19%).
- Raw offer acceptance (26/36 = 72.22%) vs. Closed offer acceptance (26/31 = 83.87%).
- The 5 pending offers (4 past decision dates, 1 candidate withdrawal).
- Sourcing attribution discrepancies (24 applications with `Referred By` on non-referral candidates).
- Duplicate candidate profiles (6 pairs).
- Negative interview evaluations (7 of 26 hires tracing 100% to Rakesh Sethi: 28 negative recommendations across 30 interview records, with 2 records having no recommendation).

---

## 5. Security & Privacy Notice

- **No Credentials Committed**: Neither `.env` nor any API tokens/keys are included in this package. `.gitignore` strictly excludes credential files.
- **Read-Only Operation**: All scripts interact with external data sources using read-only `GET` calls.
- **Data Protection**: Production candidate and employee records are stored locally for audit reproducibility and excluded from public version control.
