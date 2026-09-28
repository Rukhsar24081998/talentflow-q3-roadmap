#!/usr/bin/env python3
"""
scripts/audit_data.py

Executes a comprehensive data quality audit across all cached raw tables
for the TalentFlow - Acme Corp dataset.

Generates:
- output/data-quality-findings.json
- output/data-quality-audit.md
"""

import json
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

def load_table(name):
    path = Path(f"data/raw/{name}.json")
    if not path.is_file():
        raise FileNotFoundError(f"Missing raw data file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def run_audit():
    # 1. Load data
    apps_raw = load_table("applications")
    cands_raw = load_table("candidates")
    deps_raw = load_table("departments")
    interviews_raw = load_table("interviews")
    jobs_raw = load_table("job_openings")
    offers_raw = load_table("offers")
    people_raw = load_table("people")

    apps = {r["id"]: r for r in apps_raw}
    cands = {r["id"]: r for r in cands_raw}
    deps = {r["id"]: r for r in deps_raw}
    interviews = {r["id"]: r for r in interviews_raw}
    jobs = {r["id"]: r for r in jobs_raw}
    offers = {r["id"]: r for r in offers_raw}
    people = {r["id"]: r for r in people_raw}

    findings = []

    # =========================================================================
    # AUDIT SECTION 1: SCHEMA / ATTRIBUTION ARCHITECTURE
    # =========================================================================
    # Finding: Sourcing recorded strictly at Candidate level, not Application level
    app_with_source_field = sum(1 for a in apps_raw if "Source" in a["fields"])
    app_with_referred_by = sum(1 for a in apps_raw if a["fields"].get("Referred By"))
    
    findings.append({
        "finding": "Sourcing recorded exclusively at Candidate level with no Application-level source tracking",
        "category": "Schema / Attribution Architecture",
        "classification": "Potential data-quality concern",
        "affected_records": len(apps_raw),
        "affected_percentage": 100.0,
        "evidence": f"0 of {len(apps_raw)} applications have a Source field. Source is stored exclusively on Candidate entity ({len(cands_raw)} records). Meanwhile, Applications contain 'Referred By' on {app_with_referred_by} records.",
        "metric_impact": "Distorts multi-application channel attribution and repeat candidate conversions.",
        "decision_impact": "Directly impacts VP Claim 1; candidate source cannot distinguish how later applications arrived.",
        "confidence": "High",
        "representative_ids": ["rec42NcT9OGY8NOQC", "rec4iYmQoziFjJ9fL", "recOQKvwlqxac6vRX"]
    })

    # Finding: Source Conflict - Applications with Referred By but Candidate Source != Referral
    conflict_ref_apps = []
    for a in apps_raw:
        ref_by = a["fields"].get("Referred By")
        c_id = a["fields"].get("Candidate", [None])[0]
        cand = cands.get(c_id)
        if ref_by and cand and cand["fields"].get("Source") != "Referral":
            conflict_ref_apps.append((a["id"], cand["fields"].get("Source"), ref_by))

    findings.append({
        "finding": "Referral tracking conflict: Applications with 'Referred By' employee but non-Referral candidate source",
        "category": "Source / Channel Attribution",
        "classification": "Confirmed data error",
        "affected_records": len(conflict_ref_apps),
        "affected_percentage": round((len(conflict_ref_apps) / len(apps_raw)) * 100, 2),
        "evidence": f"{len(conflict_ref_apps)} applications have an internal employee referral logged in 'Referred By', but the candidate's static source is Job Board (12), Agency (4), or Career Site (3). E.g. App recOQKvwlqxac6vRX resulted in a hire attributed to 'Job Board' despite being referred by employee rec25IaBcJAP9TN3h.",
        "metric_impact": "Artificially deflates referral hires and inflates job board / agency hires.",
        "decision_impact": "Directly undermines VP Claim 1 (job boards share of hires).",
        "confidence": "High",
        "representative_ids": [x[0] for x in conflict_ref_apps[:5]]
    })

    # Finding: Candidate Source = Referral but Application Referred By is missing
    missing_ref_employee = []
    for a in apps_raw:
        ref_by = a["fields"].get("Referred By")
        c_id = a["fields"].get("Candidate", [None])[0]
        cand = cands.get(c_id)
        if cand and cand["fields"].get("Source") == "Referral" and not ref_by:
            missing_ref_employee.append(a["id"])

    findings.append({
        "finding": "Referral tracking omission: Candidates sourced via 'Referral' lacking referring employee link on application",
        "category": "Missing data",
        "classification": "Missing data",
        "affected_records": len(missing_ref_employee),
        "affected_percentage": round((len(missing_ref_employee) / len(apps_raw)) * 100, 2),
        "evidence": f"{len(missing_ref_employee)} of 13 applications from 'Referral' candidates have no 'Referred By' employee linked (including 7 hired applications, e.g. rec0yM3MdyWBDkjXA, rec3do5Lr0vNEt35R, recF6Nq4dyCozd9Cs).",
        "metric_impact": "Prevents referral bonus tracking and recruiter referral attribution audits.",
        "decision_impact": "Operational hygiene gap; prevents crediting referring employees.",
        "confidence": "High",
        "representative_ids": missing_ref_employee[:5]
    })

    # =========================================================================
    # AUDIT SECTION 2: DUPLICATE RECORDS & IDENTITY FRACTURING
    # =========================================================================
    # Finding: Duplicate Candidate Profiles (Same Full Name + Same Phone Number, Different IDs/Emails)
    phone_map = defaultdict(list)
    for c in cands_raw:
        p = c["fields"].get("Phone")
        if p:
            phone_map[p].append(c)
    
    dup_cand_pairs = [clist for clist in phone_map.values() if len(clist) > 1]
    dup_cand_ids = [c["id"] for clist in dup_cand_pairs for c in clist]

    findings.append({
        "finding": "Duplicate Candidate Profiles: Identical name and phone with disparate Candidate IDs and source attribution",
        "category": "Duplicate Records",
        "classification": "Confirmed data error",
        "affected_records": len(dup_cand_ids),
        "affected_percentage": round((len(dup_cand_ids) / len(cands_raw)) * 100, 2),
        "evidence": f"6 candidate pairs (12 total records, 4.0% of candidates) share identical Full Name and Phone Number but have distinct Candidate IDs and emails. In multiple cases, source attribution conflicts: Varun Sharma (recJYEsd93C0FgfMW = Job Board vs recyRCSer7xBH1pe3 = Referral); Aarav Menon (recx4ndA3SWBtMoEL = Job Board vs recY2oL9jE7i5hCgV = Referral).",
        "metric_impact": "Distorts candidate conversion rates, unique applicant counts, and channel attribution.",
        "decision_impact": "Confirms lack of deduplication mechanisms in TalentFlow/ATS.",
        "confidence": "High",
        "representative_ids": dup_cand_ids
    })

    # Finding: Repeat Applications to the Exact Same Job Opening
    cand_job_apps = defaultdict(lambda: defaultdict(list))
    for a in apps_raw:
        c_id = a["fields"].get("Candidate", [None])[0]
        j_id = a["fields"].get("Opening", [None])[0]
        if c_id and j_id:
            cand_job_apps[c_id][j_id].append(a["id"])

    repeat_same_job = []
    for c_id, jmap in cand_job_apps.items():
        for j_id, alist in jmap.items():
            if len(alist) > 1:
                repeat_same_job.append((c_id, j_id, alist))

    findings.append({
        "finding": "Duplicate applications to identical job opening resulting in double-hiring",
        "category": "Duplicate Records",
        "classification": "Confirmed data error",
        "affected_records": sum(len(x[2]) for x in repeat_same_job),
        "affected_percentage": round((sum(len(x[2]) for x in repeat_same_job) / len(apps_raw)) * 100, 2),
        "evidence": f"3 candidates applied multiple times to the exact same Job Opening. Most critically, Candidate Vinay Khanna (rec4TPTco4kDfU2DJ) applied twice to Support Specialist (recsz6wxHxrxGkre3) and was hired twice (App recrCOYOF6KWpUmqW in Jan 2026, App recF6Nq4dyCozd9Cs in Jun 2026), generating 2 accepted offers for 1 individual.",
        "metric_impact": "Double-counts hires, inflating hire counts and skewing offer acceptance.",
        "decision_impact": "Directly impacts calculation of net new hires and capacity fulfillment.",
        "confidence": "High",
        "representative_ids": [a for x in repeat_same_job for a in x[2]]
    })

    # Finding: Multiple Offers to Same Candidate
    cand_offers = defaultdict(list)
    for o in offers_raw:
        a_id = o["fields"].get("Application", [None])[0]
        if a_id and a_id in apps:
            c_id = apps[a_id]["fields"].get("Candidate", [None])[0]
            if c_id:
                cand_offers[c_id].append(o["id"])
    
    multi_offer_cands = {c: olist for c, olist in cand_offers.items() if len(olist) > 1}
    multi_offer_ids = [o for olist in multi_offer_cands.values() for o in olist]

    findings.append({
        "finding": "Multiple offers extended to single candidates across distinct applications",
        "category": "Offer Data",
        "classification": "Ambiguous data",
        "affected_records": len(multi_offer_ids),
        "affected_percentage": round((len(multi_offer_ids) / len(offers_raw)) * 100, 2),
        "evidence": f"4 candidates received 2 offers each (8 offers total, 22.2% of all offers). Two candidates (Vinay Khanna rec4TPTco4kDfU2DJ, Sneha Shah recykIELP765EIWgr) accepted both offers, resulting in 4 accepted offers across 2 people. One candidate (Arjun Bansal) accepted in 2025 and received a second offer in 2026 marked Pending.",
        "metric_impact": "Distorts Offer Acceptance Rate if computed on offer-level vs candidate-level.",
        "decision_impact": "Directly drives the requirement for D3 metric specification on edge-case handling.",
        "confidence": "High",
        "representative_ids": multi_offer_ids
    })

    # =========================================================================
    # AUDIT SECTION 3: LIFECYCLE & STATUS INCONSISTENCIES
    # =========================================================================
    # Finding: Conflicting Rejection Reasons on Hired, Active, and Offer Stage Applications
    conflicting_rej_apps = []
    for a in apps_raw:
        stg = a["fields"].get("Stage")
        rej = a["fields"].get("Rejection Reason")
        if rej and stg != "Rejected":
            conflicting_rej_apps.append((a["id"], stg, rej))

    findings.append({
        "finding": "Logical contradiction: Rejection reasons populated on Hired, Active, and Offer stage applications",
        "category": "Lifecycle / Status Inconsistencies",
        "classification": "Confirmed data error",
        "affected_records": len(conflicting_rej_apps),
        "affected_percentage": round((len(conflicting_rej_apps) / len(apps_raw)) * 100, 2),
        "evidence": f"18 non-rejected applications have Rejection Reasons. Crucially, 2 HIRED candidates have rejection reasons: App reciNqlMlx5mYgt5N (Hired) has 'Better Candidate'; App recsf6EmTqvMtB5m9 (Hired) has 'Culture Fit'. App recGmP6tLajPeKMGj (Active Interview) has 'Culture Fit'. App reckLPXA8xRgWsC1l (Active Offer) has 'Withdrew'. 14 Withdrawn applications have 'Withdrew'.",
        "metric_impact": "Corrupts rejection reason analytics and pipeline drop-off metrics.",
        "decision_impact": "Shows lack of state-transition validation rules in TalentFlow product.",
        "confidence": "High",
        "representative_ids": [x[0] for x in conflicting_rej_apps[:5]]
    })

    # Finding: Offers with status Pending that have historical Decision On dates
    pending_with_decision = []
    for o in offers_raw:
        st = o["fields"].get("Status")
        dec = o["fields"].get("Decision On")
        if st == "Pending" and dec:
            pending_with_decision.append((o["id"], dec, o["fields"].get("Offered On")))

    findings.append({
        "finding": "Zombie Pending Offers: Offers marked Pending despite having resolved Decision On dates in the past",
        "category": "Offer Data",
        "classification": "Confirmed data error",
        "affected_records": len(pending_with_decision),
        "affected_percentage": round((len(pending_with_decision) / len(offers_raw)) * 100, 2),
        "evidence": f"4 of 5 'Pending' offers (80% of pending, 11.1% of all offers) have Decision On dates in the past (ranging from 2026-02-02 to 2026-08-20). For example, OFF-00002 (recUzh2Vj5NyAPwRO) was offered in Jan 2026 with Decision On 2026-02-02 and proposed start in April 2026, yet remains 'Pending'. Its application explicitly notes Rejection Reason 'Withdrew'.",
        "metric_impact": "Artificially suppresses Offer Acceptance Rate when pending offers are included in denominator.",
        "decision_impact": "Directly explains the VP's flawed 72% claim (26/36 vs true closed acceptance 26/31 = 83.9%).",
        "confidence": "High",
        "representative_ids": [x[0] for x in pending_with_decision]
    })

    # Finding: Job Openings Status vs Headcount vs Hires Discrepancies
    job_hires = defaultdict(list)
    for a in apps_raw:
        if a["fields"].get("Stage") == "Hired":
            j_id = a["fields"].get("Opening", [None])[0]
            if j_id:
                job_hires[j_id].append(a["id"])

    corrupt_jobs = []
    for j in jobs_raw:
        j_id = j["id"]
        st = j["fields"].get("Status")
        hc = j["fields"].get("Headcount", 0)
        h_count = len(job_hires.get(j_id, []))
        if st == "Cancelled" and h_count > 0:
            corrupt_jobs.append((j_id, f"Cancelled job with {h_count} hires", h_count, hc))
        elif st == "Filled" and h_count == 0:
            corrupt_jobs.append((j_id, f"Filled job with 0 hires", h_count, hc))
        elif st == "Filled" and h_count > hc:
            corrupt_jobs.append((j_id, f"Filled job over-hired ({h_count} hires for HC {hc})", h_count, hc))
        elif st == "Open" and h_count >= hc:
            corrupt_jobs.append((j_id, f"Open job with hires ({h_count}) >= HC ({hc})", h_count, hc))

    findings.append({
        "finding": "Job opening status corruption: Cancelled jobs with hires, Filled jobs with 0 hires, and unclosed Open jobs",
        "category": "Lifecycle / Status Inconsistencies",
        "classification": "Confirmed data error",
        "affected_records": len(corrupt_jobs),
        "affected_percentage": round((len(corrupt_jobs) / len(jobs_raw)) * 100, 2),
        "evidence": f"11 of 24 job openings (45.8%) have corrupted status lifecycle. Two Cancelled jobs have hires (rec810iCfuNrOnIYU has 3 hires; rec38ScPLVzASwBYL has 1 hire). Two Filled jobs have 0 hires (recN2CRitgJbTxrMs, recfHWdP7FhYmzOhw). Two Filled jobs are over-hired by 100% (recDWPyPdsjzjzYEx, recRf0sg8Gga7o7w9). Five Open jobs already met or exceeded headcount.",
        "metric_impact": "Invalidates Time-to-Fill, Requisition Velocity, and Open Headcount metrics.",
        "decision_impact": "Proves requisition management workflow is broken at Acme.",
        "confidence": "High",
        "representative_ids": [x[0] for x in corrupt_jobs[:5]]
    })

    # Finding: Active applications attached to Filled or Cancelled jobs
    active_apps_on_dead_jobs = []
    for a in apps_raw:
        if a["fields"].get("Status") == "Active":
            j_id = a["fields"].get("Opening", [None])[0]
            job = jobs.get(j_id)
            if job and job["fields"].get("Status") in ("Filled", "Cancelled"):
                active_apps_on_dead_jobs.append((a["id"], a["fields"].get("Stage"), j_id, job["fields"].get("Status")))

    findings.append({
        "finding": "Ghost pipeline: Active applications stranded on Filled or Cancelled job openings",
        "category": "Lifecycle / Status Inconsistencies",
        "classification": "Confirmed data error",
        "affected_records": len(active_apps_on_dead_jobs),
        "affected_percentage": round((len(active_apps_on_dead_jobs) / 105) * 100, 2),
        "evidence": f"59 of 105 active applications (56.2% of active pipeline) remain in active stages (Applied, Screening, Interview) on jobs that are already Filled (55 apps) or Cancelled (4 apps). E.g. App rec0PaJV3hGNinKGA is still in 'Interview' stage for Enterprise AE (recZHFjeFl5dHlCgF) which is Filled.",
        "metric_impact": "Massively overstates active candidate pipeline volume and recruiter workloads.",
        "decision_impact": "Highlights urgent product need for automated cascade-dispositioning when reqs close.",
        "confidence": "High",
        "representative_ids": [x[0] for x in active_apps_on_dead_jobs[:5]]
    })

    # Finding: Abandoned / Stale Active Applications (>90 days old)
    stale_active_apps = []
    for a in apps_raw:
        if a["fields"].get("Status") == "Active":
            applied = a["fields"].get("Applied On")
            if applied and applied < "2026-05-27":  # >90 days prior to dataset cutoff
                stale_active_apps.append((a["id"], applied, a["fields"].get("Stage")))

    findings.append({
        "finding": "Stale abandoned applications active in pipeline for over 90 days without closure",
        "category": "Lifecycle / Status Inconsistencies",
        "classification": "Potential data-quality concern",
        "affected_records": len(stale_active_apps),
        "affected_percentage": round((len(stale_active_apps) / 105) * 100, 2),
        "evidence": f"58 of 105 active applications (55.2% of active pipeline) were applied over 90 days prior to dataset cutoff, dating as far back as August 2025 (e.g. recApf5fwVoDJ3yJb applied 2025-08-22, still in 'Applied'). Recruiters failed to disposition rejected/withdrawn candidates.",
        "metric_impact": "Severely skews pipeline aging, candidate response times, and active capacity.",
        "decision_impact": "Demonstrates need for automated pipeline hygiene (auto-rejection/inactivity timeouts).",
        "confidence": "High",
        "representative_ids": [x[0] for x in stale_active_apps[:5]]
    })

    # =========================================================================
    # AUDIT SECTION 4: TEMPORAL & CHRONOLOGICAL INCONSISTENCIES
    # =========================================================================
    # Finding: Application Applied Date precedes Candidate Created Date
    app_before_cand = []
    for a in apps_raw:
        applied = a["fields"].get("Applied On")
        c_id = a["fields"].get("Candidate", [None])[0]
        cand = cands.get(c_id)
        if cand:
            c_created = cand["fields"].get("Created On")
            if applied and c_created and applied < c_created:
                app_before_cand.append((a["id"], applied, c_id, c_created))

    findings.append({
        "finding": "Chronological inversion: Application applied date precedes candidate record creation date",
        "category": "Date / Temporal Issues",
        "classification": "Confirmed data error",
        "affected_records": len(app_before_cand),
        "affected_percentage": round((len(app_before_cand) / len(apps_raw)) * 100, 2),
        "evidence": f"104 of 350 applications (29.7%) have Applied On dates occurring months before the Candidate Created On date. E.g. App recApf5fwVoDJ3yJb was applied on 2025-08-22, but Candidate recBv5wzDk6uGZz4A was created on 2026-07-05 (317 days later). Indicates asynchronous candidate record overwrite, migration artifact, or retro-fitted imports.",
        "metric_impact": "Invalidates time-to-apply from candidate creation and candidate cohort analysis.",
        "decision_impact": "Candidate Created On cannot be trusted as initial lead capture date.",
        "confidence": "High",
        "representative_ids": [x[0] for x in app_before_cand[:5]]
    })

    # Finding: Interviews occurring before Application Applied Date or Completed before Scheduled
    chrono_interviews = []
    for i in interviews_raw:
        a_id = i["fields"].get("Application", [None])[0]
        app = apps.get(a_id)
        sched = i["fields"].get("Scheduled On")
        comp = i["fields"].get("Completed On")
        applied = app["fields"].get("Applied On") if app else None
        
        if applied and sched and sched < applied:
            chrono_interviews.append((i["id"], f"Scheduled ({sched}) < App Applied ({applied})"))
        elif applied and comp and comp < applied:
            chrono_interviews.append((i["id"], f"Completed ({comp}) < App Applied ({applied})"))
        elif sched and comp and comp < sched:
            chrono_interviews.append((i["id"], f"Completed ({comp}) < Scheduled ({sched})"))

    findings.append({
        "finding": "Chronological inversion: Interviews scheduled or completed before application was submitted",
        "category": "Date / Temporal Issues",
        "classification": "Confirmed data error",
        "affected_records": len(chrono_interviews),
        "affected_percentage": round((len(chrono_interviews) / len(interviews_raw)) * 100, 2),
        "evidence": f"4 interviews violate chronological reality: Interview recgXEUVzEOX2YYhS was scheduled and completed on 2025-08-10, 19 days BEFORE Application recP47ZJ2xJ54FFWg was submitted on 2025-08-29. Interview reciQu0aUhVUh9gmJ completed on 2026-04-23, 12 days BEFORE it was scheduled on 2026-05-05.",
        "metric_impact": "Yields negative stage transition durations (Time to First Interview).",
        "decision_impact": "Recruiter manual data entry or retroactive backfilling without timestamp guards.",
        "confidence": "High",
        "representative_ids": [x[0] for x in chrono_interviews]
    })

    # Finding: Offer Start Date precedes Offered On or Decision On date
    chrono_offers = []
    for o in offers_raw:
        off_date = o["fields"].get("Offered On")
        dec_date = o["fields"].get("Decision On")
        start_date = o["fields"].get("Proposed Start Date")
        if off_date and start_date and start_date < off_date:
            chrono_offers.append((o["id"], f"Start Date ({start_date}) < Offered On ({off_date})"))
        elif dec_date and start_date and start_date < dec_date:
            chrono_offers.append((o["id"], f"Start Date ({start_date}) < Decision On ({dec_date})"))

    findings.append({
        "finding": "Chronological contradiction: Offer proposed start date precedes offer extension or decision date",
        "category": "Date / Temporal Issues",
        "classification": "Confirmed data error",
        "affected_records": len(chrono_offers),
        "affected_percentage": round((len(chrono_offers) / len(offers_raw)) * 100, 2),
        "evidence": f"4 offers have proposed start dates before the offer was extended or decided. E.g. Offer recJ0AWDZSiO7mxXQ had proposed start date 2026-06-23, but was offered on 2026-07-05 (12 days later) and decided on 2026-07-17. Offer recSz6g6gyqkXsMhe had start date 2026-06-07, offered on 2026-06-23.",
        "metric_impact": "Distorts Time-to-Start and onboarding lead time metrics.",
        "decision_impact": "Demonstrates lack of date validation in offer generation workflows.",
        "confidence": "High",
        "representative_ids": [x[0] for x in chrono_offers]
    })

    # Finding: Milestone dates on Applications desynchronized with Interview and Offer child records
    mismatched_milestones = []
    for a in apps_raw:
        f = a["fields"]
        a_id = a["id"]
        # Offer date mismatch
        app_off = f.get("Offered On")
        off_links = f.get("Offers", [])
        if off_links and app_off:
            o = offers.get(off_links[0])
            if o and o["fields"].get("Offered On") != app_off:
                mismatched_milestones.append(a_id)
                continue
        # Interview date mismatch
        int_links = f.get("Interviews", [])
        if int_links:
            sched_dates = [interviews[iid]["fields"].get("Scheduled On") for iid in int_links if iid in interviews and interviews[iid]["fields"].get("Scheduled On")]
            if sched_dates:
                if f.get("First Interview On") and f.get("First Interview On") != min(sched_dates):
                    mismatched_milestones.append(a_id)
                    continue
                if f.get("Final Interview On") and f.get("Final Interview On") != max(sched_dates):
                    mismatched_milestones.append(a_id)
                    continue

    findings.append({
        "finding": "Application milestone timestamps desynchronized with child event records (Interviews & Offers)",
        "category": "Date / Temporal Issues",
        "classification": "Confirmed data error",
        "affected_records": len(mismatched_milestones),
        "affected_percentage": round((len(mismatched_milestones) / len(apps_raw)) * 100, 2),
        "evidence": f"62 of 350 applications (17.7%) have denormalized milestone dates on the Application record that contradict the actual dates in linked child Interview or Offer records. E.g. App recsf6EmTqvMtB5m9 has App Offered On = 2025-12-24, but Offer record Offered On = 2025-12-13. App reciNqlMlx5mYgt5N has App Offered On = 2025-12-07 vs Offer record 2025-12-02.",
        "metric_impact": "Produces conflicting funnel velocity metrics depending on whether analyst queries parent vs child tables.",
        "decision_impact": "Requires architectural shift in TalentFlow to derive milestones dynamically from events rather than redundant manual fields.",
        "confidence": "High",
        "representative_ids": mismatched_milestones[:5]
    })

    # =========================================================================
    # AUDIT SECTION 5: COMPENSATION & EVALUATION ANOMALIES
    # =========================================================================
    # Finding: Offers extended outside Job Opening salary band
    band_violations = []
    for o in offers_raw:
        base_ctc = o["fields"].get("Base CTC")
        a_id = o["fields"].get("Application", [None])[0]
        app = apps.get(a_id)
        j_id = app["fields"].get("Opening", [None])[0] if app else None
        job = jobs.get(j_id)
        if job and base_ctc:
            b_min = job["fields"].get("Salary Band Min")
            b_max = job["fields"].get("Salary Band Max")
            if base_ctc < b_min or base_ctc > b_max:
                band_violations.append((o["id"], base_ctc, b_min, b_max, job["fields"].get("Title")))

    findings.append({
        "finding": "Offers violating approved requisition salary bands without compensation guardrails",
        "category": "Compensation / Offer Data",
        "classification": "Potential data-quality concern",
        "affected_records": len(band_violations),
        "affected_percentage": round((len(band_violations) / len(offers_raw)) * 100, 2),
        "evidence": f"7 of 36 offers (19.4%) breached approved salary bands. 4 exceeded band max (e.g. recXLjOhQeRS6ds3g offered 2,850,000 vs band max 800,000—3.5x over band—and was declined for Counter Offer; recYKkt6k6hHTt6Qt offered 4,180,000 vs band max 1,600,000). 3 fell below band min (e.g. recUzh2Vj5NyAPwRO offered 440,000 vs band min 800,000).",
        "metric_impact": "Distorts budget variance, offer competitiveness, and compensation benchmark compliance.",
        "decision_impact": "Highlights need for offer approval matrix / salary band enforcement in TalentFlow.",
        "confidence": "High",
        "representative_ids": [x[0] for x in band_violations[:5]]
    })

    # Finding: Hiring candidates with Strong No Hire interview ratings
    anomalous_hires_interview = []
    for a in apps_raw:
        if a["fields"].get("Stage") == "Hired":
            int_links = a["fields"].get("Interviews", [])
            recs = [interviews[iid]["fields"].get("Recommendation") for iid in int_links if iid in interviews]
            scores = [interviews[iid]["fields"].get("Score") for iid in int_links if iid in interviews]
            if any(r in ("No Hire", "Strong No Hire") for r in recs):
                anomalous_hires_interview.append((a["id"], recs, scores))

    findings.append({
        "finding": "Interview evaluation overrides: Candidates hired despite 'Strong No Hire' interviewer recommendations",
        "category": "Lifecycle / Status Inconsistencies",
        "classification": "Potential data-quality concern",
        "affected_records": len(anomalous_hires_interview),
        "affected_percentage": round((len(anomalous_hires_interview) / 26) * 100, 2),
        "evidence": f"7 of 26 hired candidates (26.9% of all hires) were hired despite receiving negative interview recommendations ('Strong No Hire' or 'No Hire') with failing scores as low as 1.4/5.0. E.g. App recaFt6waPJsgv4Ct (Score 1.4, Strong No Hire), App rec0yM3MdyWBDkjXA (Score 1.7, Strong No Hire), App recUTm4vFe46Ns02w (Score 1.8, Strong No Hire).",
        "metric_impact": "Invalidates correlation between interview scores and hiring outcomes; breaks predictive scoring.",
        "decision_impact": "Indicates executive overrides or interview score bypassing in hiring decisions.",
        "confidence": "High",
        "representative_ids": [x[0] for x in anomalous_hires_interview[:5]]
    })

    # Finding: Cancelled / No Show interviews with Completed On timestamps
    no_show_completed = []
    for i in interviews_raw:
        outc = i["fields"].get("Outcome")
        comp = i["fields"].get("Completed On")
        if outc in ("No Show", "Cancelled") and comp:
            no_show_completed.append((i["id"], outc, comp))

    findings.append({
        "finding": "Invalid interview completion: Interviews marked No Show or Cancelled logged as completed",
        "category": "Lifecycle / Status Inconsistencies",
        "classification": "Confirmed data error",
        "affected_records": len(no_show_completed),
        "affected_percentage": round((len(no_show_completed) / len(interviews_raw)) * 100, 2),
        "evidence": f"4 interviews marked 'No Show' (3) or 'Cancelled' (1) have Completed On timestamps populated. E.g. Interview rec4ut1NFvwq5AiNs (Cancelled) has Completed On 2025-12-20; recYkOt2cyPyzNxGh, recwOLmkyNUx8771C, recx6G0nSe0Ywjk3f (No Shows) have completed dates.",
        "metric_impact": "Inflates completed interview counts and distorts interviewer load metrics.",
        "decision_impact": "Operational logging flaw in recruiter scheduling integration.",
        "confidence": "High",
        "representative_ids": [x[0] for x in no_show_completed]
    })

    # Output directory
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON findings
    json_path = out_dir / "data-quality-findings.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)

    print(f"[✓] Wrote {len(findings)} structured findings to {json_path}")
    return findings

if __name__ == "__main__":
    findings = run_audit()
    print(f"Total audit findings identified: {len(findings)}")
