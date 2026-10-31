
"""
RecruitFlow AI — Streamlit Recruiter Dashboard
Day 3, Task 2

Run:
    python -m streamlit run app.py
"""

import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

from src.database import (
    initialize_database,
    save_job,
    save_review,
    get_review,
    list_reviews,
    update_human_review,
    get_review_audit,
    ProtectedReviewError,
)
from src.document_parser import (
    DocumentExtractionError,
    extract_document,
)
from src.analytics import summarize_reviews
from src.matching_engine import screen_candidate
from src.schemas import JobDescription


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "recruitflow.db"

DEFAULT_REQUIRED = (
    "Python, Machine Learning, Scikit-learn, Pandas, SQL"
)
DEFAULT_PREFERRED = (
    "TensorFlow, PyTorch, FastAPI, Docker, Git"
)


st.set_page_config(
    page_title="RecruitFlow AI",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.07);
        padding: 14px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def split_skills(value):
    """Convert comma/newline-separated skills to a unique list."""
    result = []
    seen = set()

    for part in re.split(r"[,;\n]+", value or ""):
        skill = part.strip()
        key = skill.casefold()

        if skill and key not in seen:
            result.append(skill)
            seen.add(key)

    return result


def build_job(
    job_id,
    title,
    required_text,
    preferred_text,
    min_experience,
):
    return JobDescription(
        job_id=job_id.strip(),
        title=title.strip(),
        required_skills=split_skills(required_text),
        preferred_skills=split_skills(preferred_text),
        min_experience_years=float(min_experience),
    )


def candidate_id_from_filename(filename):
    """
    Match existing synthetic candidate IDs:
    candidate_01.txt -> C01
    """
    stem = Path(filename).stem.strip()

    if stem.lower().startswith("candidate_"):
        suffix = stem[len("candidate_"):]

        if suffix.isdigit():
            return "C" + suffix

    return stem.upper()


def process_uploads(job, uploaded_files):
    """
    Screen uploaded files independently.

    Invalid documents are reported without stopping
    other candidates.
    """
    results = []
    errors = []
    seen_ids = set()

    for uploaded in uploaded_files:
        try:
            candidate_id = candidate_id_from_filename(
                uploaded.name
            )

            if candidate_id in seen_ids:
                raise ValueError(
                    f"Duplicate candidate ID: {candidate_id}"
                )

            extraction = extract_document(
                uploaded.name,
                uploaded.getvalue(),
            )

            review = screen_candidate(
                job=job,
                candidate_id=candidate_id,
                resume_text=extraction.text,
            )

            # Reserve ID only after successful processing.
            seen_ids.add(candidate_id)

            results.append({
                "filename": uploaded.name,
                "review": review,
                "document": extraction,
            })

        except (
            DocumentExtractionError,
            ValueError,
            OSError,
        ) as exc:
            errors.append({
                "filename": uploaded.name,
                "error": str(exc),
            })

    return results, errors


def results_dataframe(results):
    rows = []

    for item in results:
        review = item["review"]

        rows.append({
            "Candidate ID": review.candidate_id,
            "Review Status": review.review_status,
            "Experience": review.experience_status,
            "Matched Skills": ", ".join(
                review.matched_skills
            ),
            "Missing Skills": ", ".join(
                review.missing_required_skills
            ),
            "Approval": review.approval_status,
        })

    return pd.DataFrame(rows)


def show_review(review, document=None):
    st.markdown(f"### Candidate {review.candidate_id}")

    a, b, c = st.columns(3)

    a.metric("Review Status", review.review_status)
    b.metric("Experience", review.experience_status)
    c.metric("Approval", review.approval_status)

    left, right = st.columns(2)

    with left:
        st.markdown("**Matched skills**")

        if review.matched_skills:
            for skill in review.matched_skills:
                st.success(skill)
        else:
            st.info("No required skills matched.")

    with right:
        st.markdown("**Missing required skills**")

        if review.missing_required_skills:
            for skill in review.missing_required_skills:
                st.warning(skill)
        else:
            st.success("No required skills missing.")

    st.markdown("**Evidence notes**")
    st.write(review.evidence_notes)

    if review.warnings:
        st.markdown("**Warnings**")

        for warning in review.warnings:
            st.warning(warning)

    if document is not None:
        with st.expander("Document extraction details"):
            st.write("Filename:", document.filename)
            st.write("File type:", document.file_type)
            st.write(
                "Characters:", document.character_count
            )
            st.write("Pages:", document.page_count)

            for warning in document.warnings:
                st.warning(warning)


def show_saved_review(data):
    if data is None:
        st.warning("Review not found.")
        return

    st.markdown(
        f"### Candidate {data['candidate_id']}"
    )

    a, b, c = st.columns(3)

    a.metric("Review Status", data["review_status"])
    b.metric(
        "Experience Status",
        data["experience_status"],
    )
    c.metric(
        "Approval Status",
        data["approval_status"],
    )

    st.markdown("**Matched skills**")
    st.write(
        ", ".join(data["matched_skills"]) or "None"
    )

    st.markdown("**Missing required skills**")
    st.write(
        ", ".join(data["missing_required_skills"])
        or "None"
    )

    st.markdown("**Evidence notes**")
    st.write(data["evidence_notes"])

    for warning in data["warnings"]:
        st.warning(warning)

    st.caption(
        f"Processed: {data['processing_timestamp']}"
    )


def screening_page():
    st.header("Resume Screening")
    st.caption(
        "Upload candidate resumes and generate "
        "evidence-based draft reviews."
    )

    with st.form("screening_form"):
        st.subheader("Job Requirements")

        col1, col2 = st.columns(2)

        with col1:
            job_id = st.text_input(
                "Job ID",
                value="JOB001",
            )

            title = st.text_input(
                "Job Title",
                value="Junior AI/ML Engineer",
            )

            min_experience = st.number_input(
                "Minimum experience (years)",
                min_value=0.0,
                max_value=50.0,
                value=1.0,
                step=0.5,
            )

        with col2:
            required_text = st.text_area(
                "Required Skills",
                value=DEFAULT_REQUIRED,
                height=105,
                help="Separate skills with commas.",
            )

            preferred_text = st.text_area(
                "Preferred Skills",
                value=DEFAULT_PREFERRED,
                height=105,
            )

        st.subheader("Upload Resumes")

        uploaded_files = st.file_uploader(
            "Choose TXT, PDF or DOCX resumes",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
        )

        submitted = st.form_submit_button(
            "Run Screening",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not uploaded_files:
            st.error("Please upload at least one resume.")
            return

        try:
            job = build_job(
                job_id,
                title,
                required_text,
                preferred_text,
                min_experience,
            )

            results, errors = process_uploads(
                job, uploaded_files
            )

            st.session_state["current_job"] = job
            st.session_state["current_results"] = results
            st.session_state["current_errors"] = errors

        except (TypeError, ValueError) as exc:
            st.error(f"Invalid job requirements: {exc}")
            return

    results = st.session_state.get(
        "current_results", []
    )
    errors = st.session_state.get(
        "current_errors", []
    )
    job = st.session_state.get("current_job")

    if not results and not errors:
        return

    st.divider()
    st.subheader("Screening Results")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Processed", len(results))
    m2.metric("Errors", len(errors))

    m3.metric(
        "Meets Requirements",
        sum(
            item["review"].review_status
            == "Meets requirements"
            for item in results
        ),
    )

    m4.metric(
        "Needs Clarification",
        sum(
            item["review"].review_status
            == "Needs clarification"
            for item in results
        ),
    )

    if results:
        st.dataframe(
            results_dataframe(results),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Candidate Details")

        candidate_ids = [
            item["review"].candidate_id
            for item in results
        ]

        selected_id = st.selectbox(
            "Select candidate",
            candidate_ids,
        )

        selected = next(
            item
            for item in results
            if item["review"].candidate_id
            == selected_id
        )

        show_review(
            selected["review"],
            selected["document"],
        )

        st.divider()

        st.info(
            "Saving stores draft reviews only. "
            "It does not approve or reject candidates."
        )

        
        
        if st.button(
            "Save All Reviews to Database",
            type="primary",
        ):
            saved_count = 0
            protected_count = 0
            failed_count = 0

            try:
                save_job(job, DB_PATH)
            except Exception as exc:
                st.error(f"Unable to save job: {exc}")
            else:
                for item in results:
                    candidate_id = item["review"].candidate_id

                    try:
                        save_review(item["review"], DB_PATH)
                        saved_count += 1

                    except ProtectedReviewError as exc:
                        protected_count += 1
                        st.warning(str(exc))

                    except Exception as exc:
                        failed_count += 1
                        st.error(
                            f"Failed to save {candidate_id}: {exc}"
                        )

                if saved_count:
                    st.success(
                        f"{saved_count} draft reviews saved."
                    )

                if protected_count:
                    st.info(
                        f"{protected_count} human-reviewed "
                        "records protected."
                    )

                if failed_count == 0:
                    st.success(
                        "Database save operation completed "
                        "without unexpected errors."
                    )
                else:
                    st.error(
                        f"{failed_count} unexpected save errors."
                    )

        export_rows = [
            item["review"].to_dict()
            for item in results
        ]

        st.download_button(
            "Download Reviews as JSON",
            data=json.dumps(
                export_rows,
                indent=2,
                ensure_ascii=False,
            ),
            file_name="recruitflow_reviews.json",
            mime="application/json",
        )

        st.download_button(
            "Download Reviews as CSV",
            data=results_dataframe(
                results
            ).to_csv(index=False),
            file_name="recruitflow_reviews.csv",
            mime="text/csv",
        )

    if errors:
        st.subheader("Processing Errors")

        for error in errors:
            st.error(
                f"{error['filename']}: "
                f"{error['error']}"
            )


def human_review_editor(data):
    """Edit a saved review and record a human decision."""
    from src.schemas import (
        ReviewStatus,
        ExperienceStatus,
        ApprovalStatus,
    )

    st.divider()
    st.subheader("Human Review & Approval")

    st.info(
        "Approval means the recruiter has verified "
        "the screening review. It is not a hiring decision."
    )

    review_options = [
        item.value for item in ReviewStatus
    ]
    experience_options = [
        item.value for item in ExperienceStatus
    ]
    approval_options = [
        item.value for item in ApprovalStatus
    ]

    with st.form(
        f"human_review_{data['job_id']}_"
        f"{data['candidate_id']}"
    ):
        reviewer = st.text_input(
            "Reviewer Name",
            placeholder="Enter your name",
        )

        col1, col2 = st.columns(2)

        with col1:
            review_status = st.selectbox(
                "Review Status",
                review_options,
                index=review_options.index(
                    data["review_status"]
                ),
            )

            experience_status = st.selectbox(
                "Experience Status",
                experience_options,
                index=experience_options.index(
                    data["experience_status"]
                ),
            )

        with col2:
            approval_status = st.selectbox(
                "Approval Decision",
                approval_options,
                index=approval_options.index(
                    data["approval_status"]
                ),
            )

        matched_text = st.text_area(
            "Matched Skills (comma-separated)",
            value=", ".join(
                data["matched_skills"]
            ),
        )

        missing_text = st.text_area(
            "Missing Required Skills",
            value=", ".join(
                data["missing_required_skills"]
            ),
        )

        evidence_notes = st.text_area(
            "Evidence Notes",
            value=data["evidence_notes"],
            height=150,
        )

        reason = st.text_area(
            "Reason / Verification Note",
            placeholder=(
                "Describe the evidence checked "
                "and why the decision was made."
            ),
            height=100,
        )

        submitted = st.form_submit_button(
            "Save Human Review",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        try:
            updated = update_human_review(
                candidate_id=data["candidate_id"],
                job_id=data["job_id"],
                reviewer=reviewer,
                review_status=review_status,
                experience_status=experience_status,
                matched_skills=split_skills(
                    matched_text
                ),
                missing_required_skills=split_skills(
                    missing_text
                ),
                evidence_notes=evidence_notes,
                approval_status=approval_status,
                correction_reason=reason,
                db_path=DB_PATH,
            )

            st.success(
                "Human review saved successfully. "
                f"Current status: "
                f"{updated['approval_status']}"
            )

            st.rerun()

        except (ValueError, TypeError) as exc:
            st.error(str(exc))

    with st.expander("Human Review Audit History"):
        history = get_review_audit(
            data["candidate_id"],
            data["job_id"],
            DB_PATH,
        )

        if not history:
            st.info("No human review actions yet.")
        else:
            for event in history:
                st.markdown(
                    f"**{event['action']}** — "
                    f"{event['reviewer']}"
                )
                st.caption(event["created_at"])

                previous = event["previous_review"]
                updated = event["updated_review"]

                st.write(
                    "Previous approval:",
                    previous["approval_status"],
                )
                st.write(
                    "New approval:",
                    updated["approval_status"],
                )

                with st.expander(
                    f"Audit event #{event['audit_id']}"
                ):
                    st.json(event)

                st.divider()

def saved_reviews_page():
    st.header("Saved Candidate Reviews")
    st.caption(
        "Browse reviews previously stored in SQLite."
    )

    reviews = list_reviews(db_path=DB_PATH)

    if not reviews:
        st.info(
            "No saved reviews yet. "
            "Run screening and save the results."
        )
        return

    st.metric("Saved Reviews", len(reviews))

    frame = pd.DataFrame(reviews)

    st.dataframe(
        frame,
        use_container_width=True,
        hide_index=True,
    )

    job_ids = sorted({
        item["job_id"]
        for item in reviews
    })

    selected_job = st.selectbox(
        "Select Job",
        job_ids,
    )

    job_reviews = [
        item for item in reviews
        if item["job_id"] == selected_job
    ]

    selected_candidate = st.selectbox(
        "Select Candidate",
        [
            item["candidate_id"]
            for item in job_reviews
        ],
    )

    data = get_review(
        selected_candidate,
        selected_job,
        DB_PATH,
    )

    st.divider()
    show_saved_review(data)
    if data is not None:
        human_review_editor(data)

def analytics_page():
    st.header("Recruitment Analytics")
    st.caption("Live summaries of saved screening reviews, not hiring decisions.")

    all_reviews = list_reviews(db_path=DB_PATH)
    if not all_reviews:
        st.info("No saved reviews yet. Screen resumes and save draft reviews first.")
        return

    job_ids = sorted({item["job_id"] for item in all_reviews})
    selected_job = st.selectbox("Filter by job", ["All jobs"] + job_ids)
    reviews = (all_reviews if selected_job == "All jobs"
               else [item for item in all_reviews if item["job_id"] == selected_job])
    summary = summarize_reviews(reviews)

    a, b, c, d = st.columns(4)
    a.metric("Saved candidate reviews", summary["total"])
    b.metric("Meets requirements", summary["review_counts"]["Meets requirements"])
    c.metric("Human-approved reviews", summary["approval_counts"]["Approved"])
    d.metric("Needs attention", summary["attention_count"])

    left, right = st.columns(2)
    with left:
        st.subheader("Screening outcomes")
        st.bar_chart(pd.DataFrame({"Count": summary["review_counts"]}))
        st.subheader("Experience assessments")
        st.bar_chart(pd.DataFrame({"Count": summary["experience_counts"]}))
    with right:
        st.subheader("Human approval statuses")
        st.bar_chart(pd.DataFrame({"Count": summary["approval_counts"]}))
        st.info("Approved means a human verified the screening review; it does not mean hired.")

    st.subheader("Candidates requiring attention")
    if summary["attention_rows"]:
        st.dataframe(pd.DataFrame(summary["attention_rows"]),
                     use_container_width=True, hide_index=True)
    else:
        st.success("No clarification or correction flags in the selected reviews.")

    st.subheader("Saved review inventory")
    st.dataframe(pd.DataFrame(reviews), use_container_width=True, hide_index=True)
    st.caption("Processing errors are not included: the current database stores successful reviews, not a historical error log.")


def main():
    initialize_database(DB_PATH)

    with st.sidebar:
        st.title("RecruitFlow AI")
        st.caption(
            "Evidence-based recruitment screening"
        )

        page = st.radio(
            "Navigation",
            [
                "Resume Screening",
                "Saved Reviews",
                "Recruitment Analytics",
            ],
        )

        st.divider()

        st.markdown("**System Status**")
        st.success("Backend connected")
        st.success("SQLite connected")

        st.caption(
            "Human approval is required "
            "for all candidate reviews."
        )

    st.title("RecruitFlow AI")
    st.write(
        "Automated resume screening with "
        "structured evidence and human oversight."
    )

    if page == "Resume Screening":
        screening_page()
    elif page == "Saved Reviews":
        saved_reviews_page()
    else:
        analytics_page()


if __name__ == "__main__":
    main()
