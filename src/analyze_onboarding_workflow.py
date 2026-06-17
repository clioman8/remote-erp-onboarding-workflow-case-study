"""
Analyze reconstructed/anonymized onboarding workflow data.

This script reads the public-safe data files for the
Remote ERP Onboarding Workflow Case Study and exports:

reports/
- analysis_summary.md
- artifact_sensitivity_counts.csv
- case_study_report.md
- complexity_counts.csv
- domain_counts.csv
- failure_severity_counts.csv
- knowledge_gap_counts.csv
- monthly_event_counts.csv
- onboarding_timeline.png
- risk_tag_counts.csv
- role_mode_counts.csv

visuals/
- artifact_fragmentation_map.png
- complexity_counts.png
- cwi_interpretation_diagram.png
- domain_counts.png
- domain_overload_matrix.png
- monthly_event_counts.png
- onboarding_timeline.png
- risk_tag_counts.png
- role_mode_counts.png

This script uses only reconstructed/anonymized summaries and synthetic data.
"""

from __future__ import annotations

from pathlib import Path
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
VISUALS_DIR = BASE_DIR / "visuals"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)
VISUALS_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> dict[str, pd.DataFrame]:
    files = {
        "events": "synthetic_onboarding_event_log.csv",
        "artifacts": "artifact_inventory.csv",
        "taxonomy": "onboarding_failure_taxonomy.csv",
        "roles": "role_expectation_matrix.csv",
        "gaps": "knowledge_transfer_gap_matrix.csv",
    }

    data = {}
    for key, filename in files.items():
        path = DATA_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing required file: {path}")
        data[key] = pd.read_csv(path)

    data["events"]["event_date"] = pd.to_datetime(data["events"]["event_date"], errors="coerce")
    return data


def explode_risk_tags(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in events.iterrows():
        raw_tags = str(row.get("onboarding_risk_tags", ""))
        tags = [tag.strip() for tag in raw_tags.split(";") if tag.strip()]
        for tag in tags:
            rows.append({
                "event_date": row.get("event_date"),
                "phase_month": row.get("phase_month"),
                "domain": row.get("domain"),
                "role_mode": row.get("role_mode"),
                "risk_tag": tag,
            })
    return pd.DataFrame(rows)


def summarize(data: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    events = data["events"]
    artifacts = data["artifacts"]
    taxonomy = data["taxonomy"]
    gaps = data["gaps"]

    risk_tags = explode_risk_tags(events)

    monthly_event_counts = (
        events["phase_month"]
        .value_counts()
        .rename_axis("phase_month")
        .reset_index(name="event_count")
    )

    # Preserve rough chronological order when possible.
    order = ["January", "February", "March", "April", "May", "June", "July", "August", "August/September"]
    monthly_event_counts["order"] = monthly_event_counts["phase_month"].apply(
        lambda x: order.index(x) if x in order else 999
    )
    monthly_event_counts = monthly_event_counts.sort_values("order").drop(columns=["order"])

    domain_counts = (
        events["domain"]
        .value_counts()
        .rename_axis("domain")
        .reset_index(name="event_count")
    )

    role_mode_counts = (
        events["role_mode"]
        .value_counts()
        .rename_axis("role_mode")
        .reset_index(name="event_count")
    )

    complexity_counts = (
        events["complexity_level"]
        .value_counts()
        .rename_axis("complexity_level")
        .reset_index(name="event_count")
    )

    risk_tag_counts = (
        risk_tags["risk_tag"]
        .value_counts()
        .rename_axis("risk_tag")
        .reset_index(name="count")
    )

    failure_severity_counts = (
        taxonomy["severity"]
        .value_counts()
        .rename_axis("severity")
        .reset_index(name="failure_type_count")
    )

    knowledge_gap_counts = (
        gaps["gap_type"]
        .value_counts()
        .rename_axis("gap_type")
        .reset_index(name="knowledge_area_count")
    )

    artifact_sensitivity_counts = (
        artifacts["sensitivity_level"]
        .value_counts()
        .rename_axis("sensitivity_level")
        .reset_index(name="artifact_count")
    )

    summaries = {
        "monthly_event_counts": monthly_event_counts,
        "domain_counts": domain_counts,
        "role_mode_counts": role_mode_counts,
        "complexity_counts": complexity_counts,
        "risk_tag_counts": risk_tag_counts,
        "failure_severity_counts": failure_severity_counts,
        "knowledge_gap_counts": knowledge_gap_counts,
        "artifact_sensitivity_counts": artifact_sensitivity_counts,
    }

    for name, df in summaries.items():
        df.to_csv(REPORTS_DIR / f"{name}.csv", index=False)

    return summaries


def plot_bar(df: pd.DataFrame, x: str, y: str, title: str, output: Path, rotation: int = 30) -> None:
    plt.figure(figsize=(10, 5))
    plt.bar(df[x].astype(str), df[y])
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.xticks(rotation=rotation, ha="right")
    plt.tight_layout()
    plt.savefig(output, dpi=200)
    plt.close()


def generate_visuals(summaries: dict[str, pd.DataFrame]) -> None:
    plot_bar(
        summaries["monthly_event_counts"],
        "phase_month",
        "event_count",
        "Onboarding Events by Phase",
        VISUALS_DIR / "monthly_event_counts.png",
        rotation=20,
    )

    plot_bar(
        summaries["risk_tag_counts"].head(12),
        "risk_tag",
        "count",
        "Top Onboarding Risk Tags",
        VISUALS_DIR / "risk_tag_counts.png",
        rotation=35,
    )

    plot_bar(
        summaries["domain_counts"].head(12),
        "domain",
        "event_count",
        "Top ERP Domains in Onboarding Events",
        VISUALS_DIR / "domain_counts.png",
        rotation=35,
    )

    plot_bar(
        summaries["role_mode_counts"].head(12),
        "role_mode",
        "event_count",
        "Role Modes Observed in Onboarding",
        VISUALS_DIR / "role_mode_counts.png",
        rotation=35,
    )

    plot_bar(
        summaries["complexity_counts"],
        "complexity_level",
        "event_count",
        "Complexity Level Distribution",
        VISUALS_DIR / "complexity_counts.png",
        rotation=20,
    )


def write_markdown_summary(data: dict[str, pd.DataFrame], summaries: dict[str, pd.DataFrame]) -> None:
    events = data["events"]
    artifacts = data["artifacts"]
    taxonomy = data["taxonomy"]
    gaps = data["gaps"]

    total_events = len(events)
    total_artifacts = len(artifacts)
    total_failure_types = len(taxonomy)
    total_knowledge_gaps = len(gaps)

    most_common_risk = (
        summaries["risk_tag_counts"].iloc[0].to_dict()
        if not summaries["risk_tag_counts"].empty
        else {"risk_tag": "N/A", "count": 0}
    )
    most_common_domain = (
        summaries["domain_counts"].iloc[0].to_dict()
        if not summaries["domain_counts"].empty
        else {"domain": "N/A", "event_count": 0}
    )
    top_role_mode = (
        summaries["role_mode_counts"].iloc[0].to_dict()
        if not summaries["role_mode_counts"].empty
        else {"role_mode": "N/A", "event_count": 0}
    )

    lines = [
        "# Onboarding Workflow Analysis Summary",
        "",
        "## Dataset scope",
        f"- Reconstructed onboarding events: {total_events}",
        f"- Anonymized artifact inventory rows: {total_artifacts}",
        f"- Failure taxonomy entries: {total_failure_types}",
        f"- Knowledge-transfer gap entries: {total_knowledge_gaps}",
        "",
        "## Key signals",
        f"- Most frequent risk tag: **{most_common_risk['risk_tag']}** ({most_common_risk['count']} occurrences).",
        f"- Most frequent domain: **{most_common_domain['domain']}** ({most_common_domain['event_count']} events).",
        f"- Most frequent role mode: **{top_role_mode['role_mode']}** ({top_role_mode['event_count']} events).",
        "",
        "## Interpretation",
        "",
        "The reconstructed data suggests that the onboarding experience was not simply a matter of difficult ERP content.",
        "The stronger pattern is the compression of live project exposure, formal training, artifact fragmentation, manufacturing ERP complexity, data reconciliation, and shifting role expectations into one remote onboarding environment.",
        "",
        "From a CWI perspective, the case can be interpreted as a workflow scaffolding failure.",
        "The employee was exposed to many artifacts and domains, but the relationships among learning stage, role boundary, artifact status, feedback loop, and operational responsibility were not sufficiently staged.",
        "",
        "## Generated output files",
        "",
        "Reports:",
        "- reports/monthly_event_counts.csv",
        "- reports/domain_counts.csv",
        "- reports/role_mode_counts.csv",
        "- reports/complexity_counts.csv",
        "- reports/risk_tag_counts.csv",
        "- reports/failure_severity_counts.csv",
        "- reports/knowledge_gap_counts.csv",
        "- reports/artifact_sensitivity_counts.csv",
        "",
        "Visuals:",
        "- visuals/monthly_event_counts.png",
        "- visuals/risk_tag_counts.png",
        "- visuals/domain_counts.png",
        "- visuals/role_mode_counts.png",
        "- visuals/complexity_counts.png",
    ]

    (REPORTS_DIR / "analysis_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = load_data()
    summaries = summarize(data)
    generate_visuals(summaries)
    write_markdown_summary(data, summaries)

    print("Analysis complete.")
    print(f"Reports written to: {REPORTS_DIR}")
    print(f"Visuals written to: {VISUALS_DIR}")


if __name__ == "__main__":
    main()
