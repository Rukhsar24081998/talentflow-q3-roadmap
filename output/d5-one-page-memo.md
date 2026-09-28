# TalentFlow Q3 — Product Decision Memo

**To**: CEO, TalentFlow; VP of People, Acme Corp  
**From**: Product Management, TalentFlow  
**Date**: September 28, 2026  
**Subject**: Q3 Product Roadmap & Resource Allocation (6.0 Engineer-Weeks)

---

## Executive Summary
An audit of Acme Corp’s production recruiting data reveals that the two primary requests proposed for Q3—accelerating job-board integrations and addressing a reported 72% offer acceptance rate—do not align with the verified constraints in the hiring pipeline. Job boards and employee referrals produce identical hiring output (7 hires each), but referrals convert at an 18.1x higher rate (53.85% vs. 2.97%), while true closed offer acceptance stands at 83.87% once unresolved records are properly segmented. We are deploying our 6.0 engineer-weeks to automate requisition lifecycle management, migrate source tracking to the application level to support employee referrals, and instrument offer workflow guardrails.

---

## What We Found
- **Sourcing Output & Efficiency**: Job boards and employee referrals each accounted for 7 of Acme's 26 hires (26.92% each). However, job boards generated 236 applications to yield 7 hires (2.97% conversion), whereas employee referrals yielded 7 hires from 13 applications (53.85% conversion).
- **Requisition & Pipeline Hygiene**: 56.19% of active applications (59 of 105) remain attached to job openings that are already filled (55) or cancelled (4). Furthermore, 55.24% of active applications (58 of 105) have been active for more than 90 days without disposition.
- **Offer Acceptance Metrics**: The reported 72.22% rate reflects 26 accepted offers divided by all 36 extended offers, which includes 5 pending offers. On decided offers, the closed acceptance rate is 83.87% (26 of 31). Four of the five pending offers have decision dates in the past, including one applicant who withdrew.
- **Data Quality & Attribution Context**: Sourcing is stored at the candidate level rather than the application level; 24 applications have an employee recorded in `Referred By` but carry a non-referral candidate source. Additionally, six duplicate candidate pairs share identical names, phones, and employers across separate profile records.

---

## What We're Doing
We are allocating our exact 6.0 engineer-week budget across three high-leverage initiatives:

1. **Requisition Lifecycle Automation & Cascade Dispositioning — 2.5 engineer-weeks**  
   *Objective*: Automatically transitions requisitions to filled when headcount is met and provides recruiters with a bulk-action workflow to disposition remaining applicants, directly addressing the 56.19% of active applications (59 of 105) currently attached to filled or cancelled requisitions.
2. **Application-Level Source Tracking & Referral Capture — 2.0 engineer-weeks**  
   *Objective*: Moves sourcing channel tracking from the candidate entity to the application entity and introduces a structured employee referral intake workflow, addressing attribution ambiguity and supporting the channel with the highest hire conversion rate (53.85% for referrals vs. 2.97% for job boards).
3. **Offer Lifecycle Guardrails & Metric Dashboard — 1.5 engineer-weeks**  
   *Objective*: Implements closed offer acceptance reporting on executive dashboards and adds automated alerts for offers lingering past decision dates, reflecting the verified 83.87% closed acceptance rate (26 of 31) while monitoring the 5 unresolved offers separately.

---

## What We're NOT Doing
- **No Job-Board Commercial Integrations in Q3**: Job boards and referrals are tied in hire count (7 hires each), but job boards show lower observed conversion (2.97% vs. 53.85%). With 56.19% of active applications attached to filled or cancelled requisitions, resolving pipeline hygiene is a higher operational priority in Q3 than adding top-of-funnel integrations.
- **No Candidate Offer-Nudging / E-Sign Acceleration in Q3**: Closed offer acceptance is 83.87% (26 of 31). Candidate declinations (5 total) were attributed to counter-offers (3), compensation (1), and location (1), with zero records indicating workflow, signing, or communication delays.
- **No AI Resume Scoring in Q3**: While 7 of 26 hires (26.92%) had at least one negative interview recommendation, all 7 negative recommendations originated from a single interviewer (28 of 30 interview records had a negative recommendation; 2 had no recommendation). The data does not establish an organizational disregard of interview scorecards; interview evaluation data requires better calibration and consistency before automating candidate evaluation.

---

## Metric Definition
To ensure consistency across leadership and board reporting, Offer Acceptance Rate is formally instrumented as:

$$\text{Closed Offer Acceptance Rate} = \frac{\text{Accepted Offers}}{\text{Accepted Offers} + \text{Declined Offers}}$$

- **Current Dataset Performance**: $\frac{26}{31} = \mathbf{83.87\%}$ (26 Accepted, 5 Declined).
- **Operational Handling**: Pending offers (5 total; 4 with past decision dates) are excluded from the conversion percentage and surfaced on a separate operational diagnostic card to ensure reporting transparency without depressing the closed metric.

---

## What We'll Look At Next
In Q4, we recommend evaluating:
1. **Recruiter Disposition Throughput**: Whether automated cascade dispositioning reduces the share of active applications older than 90 days.
2. **Referral Channel Contribution**: Whether application-level source tracking clarifies multi-application channel attribution and whether referral hire volume increases.
3. **Offer Decision Aging**: Whether automated staleness alerts reduce the number of offers remaining in pending status past their decision dates.

---

### Q3 Capacity
**6.0 engineer-weeks allocated: 2.5 + 2.0 + 1.5**
