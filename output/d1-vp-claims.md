# D1 — VP Claim Verdicts

**Author**: Product Management, TalentFlow  
**Context**: Evaluation of Q3 Roadmap requests from Acme Corp VP of People  
**Source Data**: Verified local production dataset (`data/raw/`, 892 records)  
**Deliverable**: D1 (16 marks · 15 minutes)

---

## Claim 1 — Job Boards

### What the VP claims
> *"Job boards are our biggest channel by a wide margin and they bring in 26.9% of our hires. I want the job-board integration work brought forward."*

The VP asserts that job boards represent Acme's primary source of talent by a substantial lead, justifying bringing forward engineering work to build deep integrations with commercial job boards in Q3.

---

### Raw calculation
- **Exact Numerator**: **7** (Hired applications where candidate `Source == "Job Board"`)
- **Exact Denominator**: **26** (Total applications across all sources where `Stage == "Hired"`)
- **Raw Formula**:
  $$\text{Job Board Share of Hires} = \frac{7}{26} = \mathbf{26.92\%} \quad (\approx 26.9\%)$$

The arithmetic behind the VP's stated claim (quoted as 26.9%) is reproducible from the raw records ($7/26 = \mathbf{26.92\%}$). However, the premise that job boards lead *"by a wide margin"* is demonstrably false.

---

### Data-quality concerns

1. **The Hidden Parity with Referrals (Zero Margin of Lead)**:
   - While Job Boards generated 7 hires (26.92%), **Employee Referrals also generated 7 hires (26.92%)**.
   - Job boards are tied for first place with employee referrals; there is **zero margin** (0.0%) separating them in hiring output.
2. **Sourcing Channel Inversion & Funnel Inefficiency**:
   - Job Boards generated **236 applications** (67.43% of total applicant volume) to yield 7 hires:
     $$\text{Job Board Conversion Rate} = \frac{7 \text{ hires}}{236 \text{ applications}} = \mathbf{2.97\%}$$
   - Employee Referrals generated **13 applications** (3.7% of total applicant volume) to yield 7 hires:
     $$\text{Referral Conversion Rate} = \frac{7 \text{ hires}}{13 \text{ applications}} = \mathbf{53.85\%}$$
   - Referrals are **18.1x more efficient** at producing hires than job boards. Job boards generate high applicant volume with low observed conversion.
3. **Ambiguous Referral Attribution (Candidate-Level vs. Application-Level Sourcing)**:
   - Sourcing is stored exclusively on the `Candidates` table (`Candidate.Source`). There is no source channel field on the `Applications` table.
   - When a candidate re-applies or is subsequently referred by an employee, the application permanently inherits the original lead channel.
   - **24 applications** contain an internal employee referral logged in `Referred By`, but are categorized under non-referral sources (12 Job Board, 4 Agency, 3 Career Site).
   - Specifically, **Hire `recOQKvwlqxac6vRX`** was referred by employee Deepak Dubey (`rec25IaBcJAP9TN3h`), but was credited to "Job Board" because candidate Kavya Menon originally entered via a job board. If reattributed to referrals, Referrals become the undisputed #1 channel with 8 hires (30.8%) and Job Boards drop to #2 with 6 hires (23.1%).

---

### Alternative interpretation(s)

1. **Duplicate Profiles and Verified Reapplication**:
   - The dataset contains 6 duplicate candidate pairs sharing identical identifying fields.
   - These establish duplicate/split candidate records, not proven double hires.
   - The Vinay Khanna case was specifically verified and does NOT establish a double hire; evidence is consistent with legitimate reapplication/rehire workflow (two applications 5 months apart for Support Specialist).
   - On a unique individual basis across distinct candidate entities (24 individuals):
     - **Job Board**: 7 unique individuals / 24 = **29.17%**
     - **Referral**: 5 unique individuals / 24 = **20.83%**
     - **Career Site**: 5 unique individuals / 24 = **20.83%**
     - **Agency**: 4 unique individuals / 24 = **16.67%**
     - **LinkedIn**: 3 unique individuals / 24 = **12.50%**
2. **Application Reattribution via `Referred By`**:
   - If hire `recOQKvwlqxac6vRX` is credited to the referring employee, Job Boards drop to **23.08%** (6/26) and Referrals rise to **30.77%** (8/26).
3. **Top-of-Funnel Applicant Share**:
   - Job boards represent **67.43%** of all applications (236 of 350) and **63.67%** of candidate profiles (191 of 300). While job boards dominate applicant volume, they do not dominate hiring outcomes.

---

### Verdict
**DON'T BUILD IT**

*(Strategic Direction: Reject bringing forward job-board integrations. If engineering capacity is spent on sourcing, build an automated Inbound Screening filter or an Employee Referral Portal instead.)*

---

### Decision number
$$\mathbf{2.97\%}$$
*(The application-to-hire conversion rate of job boards: 7 hires from 236 applications. In contrast, Referrals convert at 53.85%.)*

---

### Product implication
Bringing forward job-board integrations would add more top-of-funnel applicant volume to a pipeline experiencing substantial operational backlog: 56.19% of the active pipeline (59 of 105 active applications) is stranded on jobs that are already filled or cancelled, and 58 of 105 active applications (55.24%) have been active for >90 days.

Given that job boards and referrals yield equal hires (7 each) but job boards convert at an observed 2.97% versus 53.85% for referrals, and given the substantial backlog of 59 active applications on closed jobs, commercial job-board integrations are a lower Q3 priority than pipeline hygiene and referral capture.

---

## Claim 2 — Offer Acceptance

### What the VP claims
> *"Our offer acceptance rate is sitting at around 72% and the board is asking about it. I need that number moving."*

The VP asserts that offer acceptance has deteriorated to ~72%, alarming the board of directors and demanding roadmap investment to improve candidate offer conversion.

---

### Raw calculation
- **Exact Numerator**: **26** (Offers with `Status == "Accepted"`)
- **Exact Denominator**: **36** (Total offers extended in `offers.json`, including Pending)
- **Raw Formula**:
  $$\text{Raw Offer Acceptance Rate} = \frac{26}{36} = \mathbf{72.22\%} \quad (\approx 72\%)$$

The arithmetic matches the VP's stated number, but the metric construction conflates open deliberation and unclosed status with candidate rejections.

---

### Data-quality concerns

1. **The Denominator Trap (Treating Pending Offers as Rejections)**:
   - The VP included **all 36 offers ever created**, treating **5 Pending Offers** as failed conversions.
   - On decided offers where a candidate decision has been reached (26 Accepted + 5 Declined):
     $$\text{True Closed Offer Acceptance Rate} = \frac{26}{26 + 5} = \frac{26}{31} = \mathbf{83.87\%}$$
   - On decided offers ($26/31$), the defined closed offer acceptance rate is **83.87%** (26 accepted / 31 decided). The raw 72.22% rate includes 5 unresolved Pending offers in the denominator.
2. **Classification of the 5 Pending Offers**:
   - Inspection of the 5 pending offers (4 having past Decision On dates) reveals:
     - **1 candidate withdrawal / missing Withdrawn state**: OFF-00002 (`recUzh2Vj5NyAPwRO`) application explicitly records candidate "Withdrew" on 2026-02-02, but the Offers schema lacks a `Withdrawn` status.
     - **2 offers associated with On Hold requisitions and stale decision dates**: OFF-00013 (`recMJLFhIqQcUh6A9`, Decision On 2026-07-05) and OFF-00020 (`rec5GeU3frNNkZrws`, Decision On 2026-08-15).
     - **1 pending offer with a past decision date / status inconsistency**: OFF-00007 (`recQq6ghz7ksCfsKV`, Decision On 2026-08-20, candidate already had a previous accepted record).
     - **1 genuinely unresolved / abandoned outcome**: OFF-00021 (`rec0bHaqPWKwbh666`, Offered 2026-05-02, Proposed Start Date 2026-07-02, final outcome unrecorded).
3. **Decline Reasons Show Zero Product Friction**:
   - Of the 5 declined offers, reasons provided are: **Counter Offer** (3, 60%), **Compensation** (1, 20%), and **Location** (1, 20%).
   - Candidates are declining due to compensation leverage and competing counter-offers, not because of TalentFlow's offer delivery, signing experience, or workflow friction.

---

### Alternative interpretation(s)

1. **Closed Cohort Acceptance Rate (Offer Level)**:
   - $\frac{26 \text{ Accepted}}{31 \text{ Decided}} = \mathbf{83.87\%}$.
2. **Resolved Cohort Including Documented Withdrawals**:
   - Treating OFF-00002 (candidate withdrew) as a resolved outcome:
   - $\frac{26}{32} = \mathbf{81.25\%}$.
3. **Unique Candidate-Level Acceptance Rate (Closed)**:
   - Deduplicating repeat offers across unique individuals (24 candidates accepted, 4 only declined):
   - $\frac{24}{28} = \mathbf{85.71\%}$.
4. **Unique Candidate-Level Acceptance Rate (All Extended)**:
   - Deduplicating across all 32 offer recipients:
   - $\frac{24}{32} = \mathbf{75.00\%}$.

---

### Verdict
**DON'T BUILD IT**

*(Strategic Direction: Do not build candidate offer-acceleration features, e-sign nudges, or offer portal redesigns. The ~72% number is a data-hygiene artifact, not a conversion problem.)*

---

### Decision number
$$\mathbf{83.87\%}$$
*(The true closed offer acceptance rate across decided offers: 26 accepted / 31 resolved.)*

---

### Product implication
Allocating engineering capacity to candidate-facing offer acceleration misdirects resources away from the primary data-quality defect. On decided offers, closed acceptance is 83.87% (26 of 31).

The reported 72.22% raw rate includes 5 unresolved pending offers in the denominator. The appropriate solution is not candidate-facing software, but **metric instrumentation (D3)** and **automated offer expiration / status validation** to ensure pending offers are excluded from the closed metric and surfaced separately.

---

## D1 Summary

| Claim | Raw Number | Key Issue | Verdict | Decision Number | Primary Rationale |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **Claim 1: Job Boards** | **26.92%** | Tied with Referrals (7 hires each); converts at only 2.97% vs. 53.85% for Referrals; referral attribution ambiguous (24 applications). | **DON'T BUILD IT** | **2.97%** | Job boards and referrals are tied in hires (7 each), but job boards show lower observed conversion (2.97% vs 53.85%). Given existing pipeline hygiene backlog, integrations are a lower Q3 priority. |
| **Claim 2: Offer Acceptance** | **72.22%** | Denominator includes 5 pending offers (4 with past decision dates). Defined closed acceptance is 83.87% (26/31). | **DON'T BUILD IT** | **83.87%** | On decided offers, closed acceptance is 83.87%. Pending offers are excluded from the closed metric and surfaced separately. |

---

## Analytical Integrity: Fact, Interpretation, and Assumption

To maintain complete objectivity and rigor, all assertions in D1 are explicitly categorized:

### FACT (Directly Provable from Raw Data)
- Job boards generated 7 hires out of 26 total hired applications ($26.92\%$).
- Employee Referrals also generated 7 hires out of 26 total hired applications ($26.92\%$).
- Job boards generated 236 applications; 7 were hired ($2.97\%$).
- Referrals generated 13 applications; 7 were hired ($53.85\%$).
- 26 offers are Accepted, 5 are Declined, and 5 are Pending in `offers.json` ($26/36 = 72.22\%$).
- 26 Accepted divided by 31 Decided offers equals $83.87\%$.
- 4 of the 5 Pending offers have historical `Decision On` dates in the past, and one application explicitly has `Rejection Reason == "Withdrew"`.
- 3 applications resulting in hires have an employee in `Referred By` but non-referral `Candidate.Source`.

### INTERPRETATION (Analytical Conclusions Derived from Facts)
- The VP's 72.22% claim was derived by including unresolved pending offers in the denominator.
- Job boards do not lead "by a wide margin"; they are tied with referrals in output and significantly lag in quality.
- The 5 pending offers include unclosed terminal outcomes and on-hold requisitions rather than ongoing candidate negotiations.
- Allocating Q3 engineering capacity to job board integrations or offer acceleration would fail to address Acme's actual operational bottlenecks.

### ASSUMPTION (Plausible Hypotheses Requiring Stakeholder Confirmation)
- It is assumed that Acme intends `Candidate.Source` to represent original first-touch acquisition, while `Application.Referred By` represents internal employee endorsements.
- It is assumed that the candidates associated with stale pending offers (e.g. Manish Singh, Jatin Sharma) are not currently deliberating active offers and have either withdrawn, ghosted, or had their requisitions frozen.
- It is assumed that the board of directors would be satisfied if shown the true closed acceptance rate (83.87%) accompanied by proper metric instrumentation.
