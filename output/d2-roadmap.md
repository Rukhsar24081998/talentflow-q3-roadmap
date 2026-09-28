# D2 — 6 Engineer-Week Q3 Roadmap

**Author**: Product Management, TalentFlow  
**Context**: Q3 Product Roadmap allocation for Acme Corp design partnership  
**Available Capacity**: Exactly **6 engineer-weeks**  
**Data Foundation**: Verified production audit (`data/raw/`, `output/verification-pass.md`, `output/d1-vp-claims.md`, `output/d3-offer-acceptance-metric.md`)  
**Deliverable**: D2 (20 marks · 20 minutes)

---

## A. THREE THINGS TO BUILD

### Initiative 1 (Priority #1): Requisition Lifecycle Automation & Cascade Dispositioning
- **What to build**:
  - Automated triggers that detect when a Job Opening reaches its headcount limit (`Actual Hires >= Headcount`) and transition the requisition status to `Filled`, or block additional hiring when a req is `Cancelled`.
  - A cascade-dispositioning workflow: when a requisition closes (Filled or Cancelled), the system prompts recruiters with a bulk-action interface to disposition remaining active candidates (e.g. bulk-reject with customizable email templates or transfer to talent pools), preventing candidates from being stranded in active stages.
- **Problem being solved**:
  - The active pipeline exhibits substantial lifecycle hygiene issues: **56.19% of active applications (59 of 105)** are stranded in active stages (`Applied`, `Screening`, `Interview`) on Job Openings that are already `Filled` (55 apps) or `Cancelled` (4 apps).
  - 5 Open jobs currently have hires meeting or exceeding headcount, yet remain open.
  - Recruiters waste time reviewing candidates for closed roles, and candidates are left indefinitely without communication.
- **Target user**:
  - Recruiting Operations Leads, Corporate Recruiters, and Hiring Managers.
- **Rough engineering size**:
  - **2.5 engineer-weeks** (Backend webhook/trigger on requisition status change, cascade candidate evaluation service, and recruiter bulk-disposition UI modal).
- **Primary evidence / number justifying it**:
  - **`56.19%`** *(59 of 105 active applications are currently stranded on closed or filled requisitions).*
- **Why this belongs in Q3**:
  - 59 of 105 active applications are attached to Filled or Cancelled requisitions. Before Acme attempts to scale sourcing or improve velocity, the core requisition lifecycle must function reliably. Cleaning this up immediately unburdens recruiters.
- **What success would look like**:
  - 0 active applications remaining on Filled or Cancelled requisitions.
  - 100% of requisitions automatically updating to Filled upon final offer acceptance.

---

### Initiative 2 (Priority #2): Application-Level Source Tracking & Employee Referral Capture
- **What to build**:
  - Data architecture migration: move the `Source` attribute from the `Candidate` entity to the `Application` entity, enabling multi-application candidates to record distinct acquisition channels for each application.
  - An internal Employee Referral capture module that ties the `Referred By` employee foreign key directly to the application upon submission, capturing referral metadata at intake.
- **Problem being solved**:
  - Sourcing is currently tracked statically at the candidate level. 24 applications have an employee logged in `Referred By`, but inherit non-referral candidate sources (Job Board, Agency, Career Site).
  - Employee Referrals convert at **53.85%** (7 hires from 13 applications), compared to Job Boards which convert at only **2.97%** (7 hires from 236 applications). Referrals are **18.1x more efficient**, yet Acme has no dedicated application-level referral tracking or submission mechanism.
- **Target user**:
  - Internal Employees (referrers), Candidates, and Recruiting Operations.
- **Rough engineering size**:
  - **2.0 engineer-weeks** (Database migration to add `Source` to Applications, backfill script from initial candidate sources, referral link generator, and application submission endpoint update).
- **Primary evidence / number justifying it**:
  - **`53.85%`** *(Referral application-to-hire conversion rate, yielding 7 hires from only 13 applications, compared to 2.97% for Job Boards).*
- **Why this belongs in Q3**:
  - The VP of People wants more hires. The data shows that referrals deliver equal hiring output to job boards (7 hires each) with $\frac{1}{18}\text{th}$ of the applicant volume. Empowering and properly attributing referrals expands Acme's highest-quality channel.
- **What success would look like**:
  - 100% of new applications capturing an application-specific source.
  - Elimination of attribution conflicts where referred applicants are misclassified as job board leads.

---

### Initiative 3 (Priority #3): Offer Lifecycle Guardrails & Metric Dashboard Instrumentation
- **What to build**:
  - Expand the `Offers` table status schema to include terminal non-acceptance states: `Withdrawn` and `Rescinded` (currently only `Accepted`, `Declined`, `Pending`).
  - Automated offer staleness monitoring: flags offers where `Decision On` has passed or where $>14$ days have elapsed without resolution, prompting recruiters to update the status.
  - Implement the D3 metric specification on the executive dashboard: displays **Closed Offer Acceptance Rate** ($26/31 = \mathbf{83.87\%}$) alongside an operational **Pending Offer Exposure** card (showing active vs. overdue pending offers).
- **Problem being solved**:
  - The raw 72.22% rate includes 5 unresolved Pending offers in the denominator; the defined closed-offer acceptance rate is 83.87% (26/31).
  - 4 of the 5 pending offers have past Decision On dates, and 1 application explicitly records candidate withdrawal. Recruiters have no workflow forcing resolution.
- **Target user**:
  - VP of People, Head of Talent, Executive Leadership, and Recruiters extending offers.
- **Rough engineering size**:
  - **1.5 engineer-weeks** (Offers status schema expansion, scheduled cron task for offer staleness alerts, and dashboard UI metric card implementation).
- **Primary evidence / number justifying it**:
  - **`83.87%`** *(The verified Closed Offer Acceptance Rate on resolved offers ($26/31$), showing that the raw 72.22% figure is driven by 5 unclosed pending offers).*
- **Why this belongs in Q3**:
  - It immediately clarifies executive and board reporting with verified data, prevents unclosed offers from skewing future conversion metrics, and requires minimal engineering effort.
- **What success would look like**:
  - Executive dashboard displaying verified 83.87% Closed Offer Acceptance Rate.
  - Reduction of stale pending offers older than 14 days to 0.

---

## B. THREE THINGS NOT TO BUILD

### Item 1: Job-Board Commercial Integrations
- **What we are explicitly not building**:
  - Automated API integrations to ingest additional candidate feeds from commercial job boards (e.g. Indeed, ZipRecruiter).
- **Why**:
  - Job boards already represent **67.43% of all applicant volume (236 of 350 applications)**, yet yield an observed **2.97% hire conversion rate** (7 hires).
  - Job boards and referrals are tied at 7 hires each, but job boards convert at only 2.97% (compared to 53.85% for referrals). With 56.19% of active applications (59 of 105) stranded on closed requisitions and 55.24% (58 of 105) active for $>90$ days, addressing pipeline hygiene and dispositioning backlog is a higher operational priority in Q3 than expanding top-of-funnel job board integrations.
- **Evidence / number supporting the decision**:
  - **`2.97%`** *(Job board application-to-hire conversion rate: 236 applications yielded only 7 hires).*
- **What would need to change to reconsider**:
  - Demonstration that Acme has implemented automated candidate screening filters, cleared its pipeline backlog, and identified specific specialized roles that cannot be filled via referrals or direct applicants.

---

### Item 2: Candidate Offer-Nudging & E-Sign Acceleration Portal
- **What we are explicitly not building**:
  - Automated candidate SMS/email nudging, mobile offer-signing portals, or accelerated closing workflows aimed at increasing candidate acceptance.
- **Why**:
  - True offer acceptance on resolved offers is **83.87%** (and candidate-level acceptance is **85.71%**), showing high candidate conversion on closed offers.
  - Review of the 5 declined offers reveals that candidate declinations were driven by **Counter Offers** (3), **Compensation** (1), and **Location** (1). None of the recorded decline reasons identify signing or workflow friction.
- **Evidence / number supporting the decision**:
  - **`0 of 5`** *(None of the 5 recorded offer decline reasons identify signing or workflow friction; 60% declined due to counter-offers from current employers).*
- **What would need to change to reconsider**:
  - If verified closed offer acceptance falls significantly below 80%, with documented exit data indicating candidate drop-out during the signing process.

---

### Item 3: AI Candidate Scoring / Automated Resume Ranking
- **What we are explicitly not building**:
  - Machine learning algorithms or LLM-based resume scoring to rank incoming applicants.
- **Why**:
  - While **7 of 26 hires (26.92%)** had negative interview recommendations, all 7 negative recommendations trace to a single interviewer (Rakesh Sethi: 28 negative recommendations across 30 interview records, with 2 records having no recommendation).
  - The interview scorecard data is not calibrated or consistent enough to serve as a reliable training signal or evaluation baseline for AI resume scoring, rather than demonstrating organizational disregard of scorecards.
- **Evidence / number supporting the decision**:
  - **`26.92%`** *(7 of 26 hires had negative interview recommendations, all tracing to Rakesh Sethi).*
- **What would need to change to reconsider**:
  - Consistent adherence to structured interview scorecards and hiring committee sign-offs across all requisitions.

---

## C. CAPACITY CHECK

| Priority | Initiative | Engineering Size | Primary Supporting Evidence |
| :---: | :--- | :---: | :--- |
| **#1** | **Requisition Lifecycle Automation & Cascade Dispositioning** | **2.5 engineer-weeks** | **56.19%** of active pipeline (59/105) stranded on closed/filled jobs |
| **#2** | **Application-Level Source Tracking & Referral Capture** | **2.0 engineer-weeks** | **53.85%** referral conversion vs. 2.97% for job boards (18.1x efficiency) |
| **#3** | **Offer Lifecycle Guardrails & Metric Dashboard** | **1.5 engineer-weeks** | **83.87%** defined closed acceptance rate ($26/31$) separating the 72.22% raw rate |
| **TOTAL** | **Exact Q3 Engineering Budget** | **6.0 engineer-weeks** | **100% capacity utilized across 3 high-leverage fixes** |

---

## D. ROADMAP LOGIC: A Coherent Pipeline Architecture

In plain English, these three initiatives fit together as a single, unified operational strategy for TalentFlow in Q3:

```
[Top-of-Funnel]                     [Mid-Funnel Pipeline]                 [Bottom-of-Funnel]
Initiative #2 (2.0 wks)             Initiative #1 (2.5 wks)               Initiative #3 (1.5 wks)
Attribution & Referrals     ───►    Cascade Dispositioning        ───►    Offer Guardrails & Metric
Capitalize on high-yield            Resolve 56% stranded pipeline &       Surface closed rate (84%) &
referrals (54% conversion)          keep reqs clean automatically         prevent unclosed pending offers
```

1. **Fixing the Core Foundation First (Mid-Funnel — Initiative #1, 2.5 wks)**:
   - The dataset shows a substantial requisition-lifecycle backlog: 59 of 105 active applications are attached to Filled or Cancelled requisitions, indicating a need for stronger requisition lifecycle controls. More than half of active candidates are attached to closed jobs, and open jobs remain unclosed after being filled. Building automated cascade dispositioning immediately resolves stranded active applications, ensuring recruiters only spend time on viable candidates for open headcount.
2. **Fueling the Right Source (Top-of-Funnel — Initiative #2, 2.0 wks)**:
   - Once the pipeline is clean, Acme needs hiring output. Rather than focusing on low-converting job board resumes (which convert at only 2.97%), TalentFlow shifts focus to the highest-converting channel in the dataset: Employee Referrals (converting at 53.85%). Fixing the attribution schema and providing a clean referral workflow supports candidate tracking for this channel.
3. **Restoring Executive Trust & Hygiene (Bottom-of-Funnel — Initiative #3, 1.5 wks)**:
   - At the bottom of the funnel, the raw 72.22% offer acceptance figure reflects unclosed pending offers rather than candidate drop-off. Implementing the D3 metric specification on the executive dashboard provides leadership clarity by presenting the verified 83.87% closed acceptance rate. Adding offer expiration guardrails prevents unclosed offers from lingering in the future.

Together, these three initiatives utilize **exactly 6.0 engineer-weeks**, directly address verified data defects, reject superficial executive requests with hard numbers, and establish a clean operational baseline for TalentFlow.

---

## Analytical Integrity: Fact, Interpretation, and Assumption

### FACT (Directly Provable from Data)
- 59 of 105 active applications (56.19%) are attached to Filled or Cancelled job openings.
- 58 of 105 active applications (55.24%) have been active for $>90$ days.
- Referrals produced 7 hires from 13 applications (53.85% conversion rate).
- Job Boards produced 7 hires from 236 applications (2.97% conversion rate).
- On closed offers, 26 were accepted and 5 declined (83.87% acceptance rate).
- 4 of 5 pending offers have decision dates in the past; 1 application explicitly notes candidate withdrawal.
- None of the 5 recorded offer decline reasons identify signing or workflow friction.
- 7 of 26 hires had negative interview recommendations (`Strong No Hire` or `No Hire`).
- The three proposed build initiatives total exactly $2.5 + 2.0 + 1.5 = 6.0$ engineer-weeks.

### INTERPRETATION (Analytical Conclusions Derived from Facts)
- The dataset shows a substantial requisition-lifecycle backlog, with candidates remaining in active stages on closed requisitions.
- Expanding job board volume prior to establishing pipeline hygiene adds top-of-funnel volume where the observed conversion rate is 2.97%.
- The VP's 72.22% claim is an artifact of unclosed pending offers rather than candidate dissatisfaction.
- Sourcing attribution stored at the candidate level is technically inadequate for tracking repeat applicant journeys.

### ASSUMPTION (Plausible Hypotheses Requiring Stakeholder Validation)
- It is assumed that 2.5 engineer-weeks is sufficient for a senior full-stack engineer to build cascade-dispositioning triggers and recruiter modals.
- It is assumed that Acme employees will submit more referrals if provided with a dedicated application-level referral workflow.
- It is assumed that hiring managers and recruiters will adopt automated requisition closure workflows without requiring extensive retraining.
