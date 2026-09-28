# TalentFlow Q3 Roadmap: Structured Findings Table

**Document**: D4 Supporting Evidence Table  
**Source Data**: Cached local production tables (`data/raw/`, 892 records)  
**Deliverable**: D4 Supporting Artifact (`output/findings.md` & `output/findings.csv`)  
**Methodology**: 100% programmatically verified against local JSON files; zero external benchmarks or fabricated assumptions.

---

## 1. Structured Findings Table

| # | Claim | Metric | Value | Method | Confidence | Evidence Classification |
| :-: | :--- | :--- | :---: | :--- | :---: | :---: |
| **1** | **VP Claim 1**: Job boards are our biggest channel by a wide margin | **Job Board Share of Hires** | **7 / 26 (26.92%)** | Count of applications where `Stage == 'Hired'` and linked `Candidate.Source == 'Job Board'` (7) divided by total applications where `Stage == 'Hired'` (26) in `applications.json` and `candidates.json`. | **High** | **FACT** |
| **2** | **Sourcing channel comparison against VP Claim 1** | **Employee Referral Share of Hires** | **7 / 26 (26.92%)** | Count of applications where `Stage == 'Hired'` and linked `Candidate.Source == 'Referral'` (7) divided by total applications where `Stage == 'Hired'` (26) in `applications.json` and `candidates.json`. | **High** | **FACT** |
| **3** | **Pipeline efficiency of Job Boards** | **Job Board Application-to-Hire Conversion Rate** | **7 / 236 (2.97%)** | Count of hired applications with `Candidate.Source == 'Job Board'` (7) divided by total applications with `Candidate.Source == 'Job Board'` (236) in `applications.json` and `candidates.json`. | **High** | **FACT** |
| **4** | **Pipeline efficiency of Employee Referrals** | **Employee Referral Application-to-Hire Conversion Rate** | **7 / 13 (53.85%)** | Count of hired applications with `Candidate.Source == 'Referral'` (7) divided by total applications with `Candidate.Source == 'Referral'` (13) in `applications.json` and `candidates.json`. | **High** | **FACT** |
| **5** | **Requisition lifecycle & pipeline status consistency** | **Active Applications on Inactive Requisitions Share** | **59 / 105 (56.19% of active; 59 / 350 = 16.86% of total)** | Count of applications where `Status == 'Active'` attached to Job Openings where `Status IN ('Filled', 'Cancelled')` (59) divided by total applications where `Status == 'Active'` (105) in `applications.json` and `job_openings.json`. | **High** | **FACT** |
| **6** | **Pipeline aging & recruiter disposition hygiene** | **Stale Active Applications Share (>90 Days)** | **58 / 105 (55.24% of active; 58 / 350 = 16.57% of total)** | Count of applications where `Status == 'Active'` and `Applied On < '2026-05-27'` (58) divided by total applications where `Status == 'Active'` (105) in `applications.json`. | **High** | **FACT** |
| **7** | **VP Claim 2**: Offer acceptance rate is ~72% | **Raw Offer Acceptance Rate (All Extended Offers)** | **26 / 36 (72.22%)** | Count of offers where `Status == 'Accepted'` (26) divided by total offers in `offers.json` (36). Includes 5 unresolved Pending offers in denominator. | **High** | **FACT** |
| **8** | **True candidate closing rate on decided offers** | **Closed Offer Acceptance Rate (Decided Offers Only)** | **26 / 31 (83.87%)** | Count of offers where `Status == 'Accepted'` (26) divided by count of offers where `Status IN ('Accepted', 'Declined')` (31) in `offers.json`. Excludes 5 unresolved Pending offers. | **High** | **FACT (Calculation)** /<br>**INTERPRETATION (Metric choice)** |
| **9** | **Investigation of unclosed offer inventory inflating raw denominator** | **Pending Offer Count & Stale Decision Exposure** | **5 pending offers (13.89% of offers); 4 of 5 (80.0%) have past Decision On dates** | Count of offers where `Status == 'Pending'` (5), and count of pending offers where `Decision On` is not null and precedes dataset cutoff (4) in `offers.json`. | **High** | **FACT** |
| **10** | **Accuracy of sourcing channel attribution across applications** | **Cross-Entity Referral Attribution Discrepancy** | **24 applications (6.86% of total; includes 3 hired applications)** | Count of applications where `Referred By` is populated but linked `Candidate.Source != 'Referral'` (24) in `applications.json` and `candidates.json`. Source is stored strictly at Candidate level, not Application level. | **Medium** | **AMBIGUOUS** |
| **11** | **Candidate deduplication & profile integrity** | **Duplicate Candidate Profile Count** | **6 pairs (12 candidate records; 4.00% of candidates)** | Identified candidate records sharing identical Full Name, identical Phone, and identical Current Company across distinct Candidate IDs and emails in `candidates.json`. | **High** | **FACT (Duplicate records)** /<br>**INTERPRETATION (Profile splitting)** |
| **12** | **Evaluation scorecard alignment with hiring outcomes** | **Hires with Stored Negative Interview Recommendations Share** | **7 / 26 (26.92% of hires)** | Count of applications where `Stage == 'Hired'` with $\ge 1$ linked interview where stored `Recommendation IN ('Strong No Hire', 'No Hire')` (7) divided by total hires (26) in `applications.json` and `interviews.json`. | **High** | **FACT (Stored field values)** /<br>**AMBIGUOUS (Causal impact)** |
| **13** | **Origin and calibration of negative interview ratings** | **Single-Interviewer Negative Rating Concentration (Rakesh Sethi)** | **7 / 7 (100.0% of negative hire ratings); 28 of 30 interview records had a negative recommendation; 2 had no recommendation** | Grouped all interviews by Interviewer ID (`recyNjT2YZqOFbyMW`, Rakesh Sethi) in `interviews.json`; 28 of 30 interview records had a negative recommendation (26 `Strong No Hire`, 2 `No Hire`), 2 had no recommendation, and 0 had a positive recommendation. | **High** | **FACT** |

---

## 2. Analytical Data-Trust Rules & Contextual Notes

To adhere strictly to senior product management standards and prevent unjustified conclusions, the following guardrails govern the interpretation of these findings:

1. **Referral Attribution is Ambiguous, Not a Confirmed Error**:
   - The existence of 24 applications with `Referred By` populated while `Candidate.Source != 'Referral'` reflects an architectural design where sourcing is stored at the `Candidate` level rather than the `Application` level. 
   - An employee submitting an internal endorsement for an applicant who previously entered via a job board is common industry practice. Without Acme's internal attribution SOP, this cannot be labeled a confirmed error.
2. **Duplicate Candidates Are Not Proven "Double Hires"**:
   - The 6 candidate pairs (12 records) sharing identical names, phones, and employers represent duplicate person records (split profiles) created when candidates applied with different email addresses.
   - None of these 6 pairs represent simultaneous active employment.
3. **The Vinay Khanna Case is Not Double Hiring**:
   - Candidate `rec4TPTco4kDfU2DJ` (Vinay Khanna) submitted two applications for Support Specialist 5 months apart (Jan 2026 and Jun 2026), each with distinct interviews and offers.
   - The data shows two sequential accepted offer events for one person; it does not establish concurrent active employment or fraudulent payroll duplication.
4. **Active Applications on Inactive Requisitions**:
   - We describe the 59 applications precisely as *"applications attached to Filled or Cancelled requisitions"*, rather than assuming candidate unresponsiveness.
   - The data shows that active application records remain attached to closed requisitions without automated cascade dispositioning.
5. **Interview Recommendations Trace to One Outlier Interviewer**:
   - The 7 negative interview recommendations among hires do **not** establish that Acme culturally ignores its evaluation process.
   - 100% of these negative ratings (7 of 7) were submitted by a single interviewer (Rakesh Sethi); across 30 interview records, Rakesh Sethi had 28 negative recommendations and 2 records with no recommendation. In 2 cases, another interviewer submitted a positive rating (`Hire` 4.2, `Strong Hire` 4.5).
6. **No External Benchmarks or Unverified Causal Inventions**:
   - Every metric reported above is derived directly and reproducibly from the raw dataset.
   - Raw facts are kept strictly distinct from interpretations and assumptions.
