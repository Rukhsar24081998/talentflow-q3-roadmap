# D3 — Metrics Specification: Offer Acceptance Rate

**Document**: Engineering Specification & Implementation Standard  
**Author**: Product Management, TalentFlow  
**Target Audience**: Data Engineering, Frontend Engineering, Product Analytics, Recruiting Operations  
**Deliverable**: D3 (15 marks · 15 minutes)  
**Objective**: Define an unambiguous, mathematically resilient Offer Acceptance Rate metric that two engineers implementing independently will calculate identically.

---

## 1. Metric Name
- **Primary Metric**: **Closed Offer Acceptance Rate** (abbreviated: **COAR**)
- **Secondary Diagnostic Metric**: **Pending Offer Exposure** (abbreviated: **POE**)
- **Alternative Cohort View**: **Cohort Offer Acceptance Rate** (abbreviated: **OAR-Cohort**)

---

## 2. Business Question
> *"When we extend formal employment offers to candidates, what percentage of those completed deliberations result in signed acceptance versus candidate rejection?"*

The metric must measure **candidate closing effectiveness** (offer attractiveness, compensation competitiveness, and closing execution). It must **not** be distorted by active deliberations, paused requisitions, or administrative logging delays.

---

## 3. Numerator Definition
- **Exact Criteria**: The count of formal offer records where the candidate formally accepted the offer within the defined time window.
- **Data Condition**:
  ```sql
  Offers.Status == 'Accepted'
  ```
- **Inclusions**:
  - Signed written offers.
  - Verbal offers that transitioned to accepted and are logged with `Status == 'Accepted'`.
- **Exclusions**:
  - Offers with `Status == 'Pending'` or `Status == 'Declined'`.
  - Replaced / superseded offer drafts (only the final accepted version counts).

---

## 4. Denominator Definition
- **Exact Criteria**: The total count of all formal offer records where a **terminal candidate decision** (Accepted or Declined) was reached within the defined time window.
- **Data Condition**:
  ```sql
  Offers.Status IN ('Accepted', 'Declined')
  ```
- **Inclusions**:
  - All offers accepted (`Status == 'Accepted'`).
  - All offers formally declined by the candidate (`Status == 'Declined'`).
  - All offers where the candidate withdrew after offer extension (categorized under candidate declines).
- **Exclusions**:
  - **Pending Offers (`Status == 'Pending'`)**: Offers currently under active deliberation, unresolved offers, or abandoned offers lacking a confirmed terminal outcome are strictly excluded from the closed rate denominator.
  - **Company Rescissions**: Offers cancelled by the employer (e.g., headcount freeze, budget cancellation, background check failure). *Rationale: An employer rescission measures corporate volatility, not candidate closing attractiveness.*
  - **Superseded Offer Drafts**: If an offer is revised with a higher salary or new bonus, the prior draft is marked superseded, not declined.

---

## 5. Mathematical Formula

$$\text{Closed Offer Acceptance Rate (COAR)} = \frac{\sum \text{Offers with Status } = \text{'Accepted'}}{\sum \text{Offers with Status } \in \{\text{'Accepted'}, \text{'Declined'}\}} \times 100$$

### Secondary Metric: Pending Offer Exposure (POE)

$$\text{Pending Offer Exposure (POE)} = \sum \text{Offers with Status } = \text{'Pending'}$$

---

## 6. Time Window & Cohort Anchoring

Metric ambiguity frequently arises when teams disagree on whether to anchor by the date the offer was sent or the date the decision was made. We define two complementary time window models:

### 6.1 Primary Model: Decision-Date Window (Activity / Performance View)
- **Anchor Field**: `Offers.Decision On`
- **Definition**: All offers where a candidate decision was recorded between the start and end of the reporting period:
  $$\text{Filter: } \text{Start Date} \le \text{Offers.Decision On} \le \text{End Date}$$
- **Why this is the Primary Executive View**:
  - It creates a **100% closed population** for the reporting period (e.g. Q2).
  - It completely eliminates the pending-offer denominator problem: by definition, zero pending offers have an unresolved decision in a closed window.
  - It aligns directly with quarterly recruiting OKRs (e.g., "What was our closing rate in Q2?").

### 6.2 Secondary Model: Offer-Date Cohort (Maturity View)
- **Anchor Field**: `Offers.Offered On`
- **Definition**: All offers extended between Start Date and End Date.
- **Cohort Maturity Rule**:
  - A cohort is considered **Matured** once all offers extended in that period have resolved, OR once 30 calendar days have elapsed since the period ended.
  - For immature cohorts (e.g. current month), the metric displays an asterisk indicating unclosed deliberations, calculated as:
    $$\text{Immature Cohort Rate} = \frac{\text{Accepted}}{\text{Accepted} + \text{Declined}} \quad \text{with } [\text{POE}] \text{ Pending}$$

---

## 7. Status Handling Specification

| Status Value in Data | Treatment in Numerator | Treatment in Denominator | Dashboard UI Representation | Handling Rule |
| :--- | :---: | :---: | :--- | :--- |
| **`Accepted`** | **Count (+1)** | **Count (+1)** | Contributes positively to rate. | Final terminal positive state. |
| **`Declined`** | **0** | **Count (+1)** | Contributes negatively to rate. | Final terminal negative state. |
| **`Pending` (Active, $\le$ 14 days old)** | **0** | **0 (Excluded)** | Shown on separate "Pending Offers" card. | Valid ongoing deliberation. Excluded from closed rate. |
| **`Pending` (Stale / Overdue, $>$ 14 days old)** | **0** | **0 (Excluded)** | Flagged in amber/red alert: *"Stale Pending"* | Recruiter hygiene gap. Excluded from rate; triggers operational task. |
| **`Withdrawn` (Candidate-initiated)** | **0** | **Count (+1)** | Counted as Declined. | Candidate opted out after offer; counts as non-acceptance. |
| **`Rescinded` (Company-initiated)** | **0** | **0 (Excluded)** | Excluded from rate; tracked on "Rescinded" card. | Company revoked offer; does not reflect candidate rejection. |

---

## 8. Edge Case Handling

### Edge Case 1: Pending Offers with Past `Decision On` Dates
- **Problem**: 4 offers in Acme's data have `Status == 'Pending'` but possess historical `Decision On` dates (e.g. `OFF-00002` decided 2026-02-02; `OFF-00013` decided 2026-07-05).
- **Rule**:
  1. For closed metric calculation, **only the `Status` field governs outcome**. If `Status` is not `Accepted` or `Declined`, it is excluded from the closed rate.
  2. If an offer has a past `Decision On` date but remains `Pending`, the system triggers an automated **Data Hygiene Exception**: *"Offer OFF-XXXXX has a decision date but status is Pending. Please transition to Accepted or Declined."*
  3. The offer is displayed in the **Pending Offer Exposure** queue with a "Data Integrity Warning" icon.

### Edge Case 2: Candidate Withdraws After Offer Extension
- **Problem**: In Application `reckLPXA8xRgWsC1l`, candidate Aarav Menon withdrew after offer `OFF-00002` was extended (`Rejection Reason == 'Withdrew'`), but the offer record remained `Pending`.
- **Rule**:
  - In a properly instrumented ATS, candidate withdrawal post-offer is mapped to `Status = 'Declined'` (Decline Reason: `Withdrew`).
  - If unmapped, the system infers a decline if `Application.Rejection Reason == 'Withdrew'` and excludes it from the numerator while including it in the closed denominator as a non-acceptance.

### Edge Case 3: Multiple Offers Extended to the Same Candidate
- **Problem**: 4 candidates received 2 offers each (e.g. Sneha Shah received offers for Data Engineer and Junior Data Analyst; Vinay Khanna received two offers for Support Specialist).
- **Specification**:
  - **Offer-Level Metric (Default)**: Evaluates each offer record independently. 2 offers accepted by 1 person count as 2 in numerator and 2 in denominator.
  - **Candidate-Level Metric (Toggle)**: Evaluates unique individuals:
    - If a candidate receives multiple offers across different roles and accepts at least one, the candidate is counted as **1 in numerator and 1 in denominator** (100% candidate conversion).
    - If a candidate declines an initial offer and accepts a renegotiated offer for the same role, the candidate counts as **1 accepted candidate**.

### Edge Case 4: Reapplication / Rehire vs. Offer Revision
- **Problem**: Re-negotiated compensation entered as a new application/offer versus a legitimate rehire months later.
- **Rule**:
  - If a second offer is extended for the **same Job Opening** within **30 days** of the first offer, it is classified as an **Offer Revision / Renegotiation**. The earlier offer is superseded (excluded from denominator), and only the final offer counts.
  - If a second offer is extended $>90$ days later (as with Vinay Khanna: Jan 2026 vs Jun 2026), it is treated as a **distinct reapplication/rehire event** and evaluated independently.

---

## 9. Dashboard Behavior & UI Specification

The dashboard must **never display a misleading single percentage** that hides data ambiguity. It must present a balanced executive card and an operational audit card:

```
┌────────────────────────────────────────────────────────────────────────┐
│  OFFER ACCEPTANCE & CONVERSION                                         │
├───────────────────────────────────┬────────────────────────────────────┤
│  Closed Offer Acceptance Rate     │  Pending Offer Exposure            │
│                                   │                                    │
│             83.87%                │             5 Offers               │
│                                   │                                    │
│   26 Accepted  /  31 Decided      │   1 Active  |  4 Overdue/Stale ⚠️   │
│   (Excludes 5 pending offers)     │   Action: Review 4 unclosed offers │
└───────────────────────────────────┴────────────────────────────────────┘
```

### Dashboard Logic Rules:
1. **Primary Headline Number**: Displays **Closed Offer Acceptance Rate** ($26/31 = \mathbf{83.87\%}$).
2. **Mandatory Sub-label**: Shows exact numerator and denominator ($26 \text{ Accepted} / 31 \text{ Decided}$).
3. **Pending Offer Exposure Card**: Displayed immediately adjacent. Shows total unresolved offers (**5**), breaking them down into **Active deliberating** (within 14 days) and **Overdue / Stale** (past decision or $>14$ days).
4. **When Unresolved Offers Exist**:
   - They are **strictly excluded** from the acceptance rate percentage.
   - An amber badge warns: *"4 offers require recruiter status update."*
5. **No Feigned Precision**: If the total decided offers in a filtered view is $<10$ (small sample size), the dashboard renders a statistical caveat: *"Sample size too small ($N < 10$) for reliable trend analysis."*

---

## 10. Example Calculation (Using Acme Production Data)

Using the complete cached production dataset from Acme Corp (`offers.json`, 36 records):

### Step 1: Filter Dataset
- Total Offer Records: **36**
- Records with `Status == 'Accepted'`: **26**
- Records with `Status == 'Declined'`: **5**
- Records with `Status == 'Pending'`: **5**

### Step 2: Calculate Denominators
- **Closed Deliberation Denominator**:
  $$\text{Denominator}_{\text{Closed}} = 26 \text{ Accepted} + 5 \text{ Declined} = \mathbf{31}$$
- **Raw Extended Denominator (VP's Formula)**:
  $$\text{Denominator}_{\text{Raw}} = 26 + 5 + 5 = \mathbf{36}$$

### Step 3: Compute Metrics
1. **Closed Offer Acceptance Rate (COAR — Recommended Metric)**:
   $$\text{COAR} = \frac{26}{31} = \mathbf{83.87\%}$$
2. **Pending Offer Exposure (POE)**:
   $$\text{POE} = \mathbf{5 \text{ offers}} \quad (4 \text{ overdue / stale}, 1 \text{ abandoned})$$
3. **Raw Extended Ratio (VP's Metric)**:
   $$\text{Raw Ratio} = \frac{26}{36} = \mathbf{72.22\%}$$

### Step 4: Candidate-Level Deduplicated View
- Unique candidates receiving offers: **32**
- Unique candidates accepting an offer: **24**
- Unique candidates declining only: **4**
- Unique candidates pending only: **4**
- **Candidate-Level Closed Rate**:
  $$\text{Candidate COAR} = \frac{24}{24 + 4} = \frac{24}{28} = \mathbf{85.71\%}$$

---

## 11. Implementation Rule (SQL / Pseudo-Code)

Two software engineers implementing this specification independently must use the following standard logic:

```sql
-- Standard Closed Offer Acceptance Rate Query
WITH offer_decisions AS (
    SELECT
        id AS offer_id,
        fields->>'Offer ID' AS offer_code,
        fields->>'Status' AS status,
        (fields->>'Offered On')::DATE AS offered_on,
        (fields->>'Decision On')::DATE AS decision_on,
        fields->'Application'->>0 AS application_id
    FROM offers_raw
)
SELECT
    -- Numerator
    COUNT(*) FILTER (WHERE status = 'Accepted') AS accepted_count,
    
    -- Denominator (Closed resolved outcomes only)
    COUNT(*) FILTER (WHERE status IN ('Accepted', 'Declined')) AS closed_decisions_count,
    
    -- Primary Metric: Closed Offer Acceptance Rate
    ROUND(
        COUNT(*) FILTER (WHERE status = 'Accepted')::NUMERIC / 
        NULLIF(COUNT(*) FILTER (WHERE status IN ('Accepted', 'Declined')), 0) * 100, 
        2
    ) AS closed_offer_acceptance_rate,
    
    -- Secondary Diagnostic: Pending Exposure
    COUNT(*) FILTER (WHERE status = 'Pending') AS pending_count,
    
    -- Operational Hygiene Warning: Stale Pending (Past Decision Date or >14d)
    COUNT(*) FILTER (
        WHERE status = 'Pending' 
          AND (decision_on IS NOT NULL OR offered_on < CURRENT_DATE - INTERVAL '14 days')
    ) AS stale_pending_count

FROM offer_decisions
WHERE 
    -- Reporting time window anchored on Decision Date (or Offered On for cohort view)
    (:window_type = 'DECISION' AND decision_on BETWEEN :start_date AND :end_date)
    OR
    (:window_type = 'COHORT' AND offered_on BETWEEN :start_date AND :end_date);
```

---

## 12. Analytical Integrity: Fact, Definition, and Assumption

### FACT
- `offers.json` contains exactly 36 records: 26 Accepted, 5 Declined, 5 Pending.
- $26 / 36 = 72.22\%$; $26 / 31 = 83.87\%$; $24 / 28 = 85.71\%$.
- 4 of 5 pending offers have past decision dates; 1 application explicitly notes candidate withdrawal.

### DEFINITION / PRODUCT DECISION
- **Product Decision 1**: We define the primary executive metric as **Closed Offer Acceptance Rate** ($26/31 = 83.87\%$), excluding pending offers from the rate calculation.
- **Product Decision 2**: We define **Decision Date** as the primary anchor for quarterly reporting to prevent incomplete cohort drag.
- **Product Decision 3**: We mandate displaying **Pending Offer Exposure** as a separate diagnostic tile to prevent hiding unresolved offers.

### ASSUMPTION
- It is assumed that Acme's recruiters intend to mark withdrawn candidates as non-acceptances once a "Withdrawn" status is made available.
- It is assumed that the board of directors will accept the closed metric if shown the transparent 26/31 breakdown alongside pending exposure.

---

## 13. Executive Recommendation on the Existing "72%" Metric

### Recommendation: **REPLACE IT IMMEDIATELY**

The existing "72%" dashboard number should be **replaced**, not retained.

### Rationale:
1. **It is Mathematically False**: Including active deliberations and abandoned records in the denominator treats unclosed workflow tickets as candidate rejections. It is the mathematical equivalent of treating active applicants in the interview stage as rejected.
2. **It Drives Dysfunctional Executive Behavior**: The 72% number created false alarm at the board level, causing the VP of People to demand emergency engineering investments to "move the number." 
3. **The Real Problem is Recruiter Hygiene, Not Candidate Closing**: Replacing the 72.22% raw metric with **83.87% Closed Acceptance** and a **"5 Pending Offers"** operational tile provides executive clarity while spotlighting the true operational fix: requiring recruiters to disposition terminal offer outcomes.
