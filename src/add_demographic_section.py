"""Add requested demographic distributions and an availability check."""

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks/01_univariate_analysis.ipynb"
SECTION_MARKER = "## 9. Demographic distributions and field availability"


def main() -> None:
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)

    # Remove an earlier copy of this generated section, if present.
    section_start = next(
        (
            index
            for index, cell in enumerate(notebook.cells)
            if cell.cell_type == "markdown" and SECTION_MARKER in cell.source
        ),
        None,
    )
    if section_start is not None:
        section_end = next(
            (
                index
                for index in range(section_start + 1, len(notebook.cells))
                if notebook.cells[index].cell_type == "markdown"
                and notebook.cells[index].source.startswith("## 10.")
            ),
            len(notebook.cells),
        )
        del notebook.cells[section_start:section_end]

    findings_index = next(
        index
        for index, cell in enumerate(notebook.cells)
        if cell.cell_type == "markdown"
        and (
            "## 9. Univariate findings" in cell.source
            or "## 10. Univariate findings" in cell.source
        )
    )
    notebook.cells[findings_index].source = "## 10. Univariate findings"

    cells = [
        new_markdown_cell(
            """## 9. Demographic distributions and field availability

The requested fields were checked against the cleaned dataset before plotting. `age` and the engineered `age_group` are available. `city` and `device` are not collected in this dataset, so their distributions cannot be calculated. Recorded `gender` is included as the only other available demographic variable.

Each chart below is univariate: it displays one demographic variable independently."""
        ),
        new_code_cell(
            """requested_demographics = pd.DataFrame({
    "Requested variable": ["City", "Age group", "Device"],
    "Dataset field": ["Not available", "age_group (derived from age)", "Not available"],
    "Status": ["Cannot analyze", "Available", "Cannot analyze"],
    "What would be needed": [
        "Passenger residence or origin city",
        "Already available; analyst-defined bands are used",
        "Device type used for booking, check-in, or survey",
    ],
})
display(requested_demographics.style.hide(axis="index"))"""
        ),
        new_code_cell(
            """age_order = ["Under 18", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
age_group_frequency = (
    df["age_group"]
    .value_counts()
    .reindex(age_order)
    .rename_axis("Age group")
    .to_frame("Passengers")
)
age_group_frequency["Share"] = age_group_frequency["Passengers"] / len(df)
display(age_group_frequency.style.format({"Passengers": "{:,}", "Share": "{:.1%}"}))

fig, ax = plt.subplots(figsize=(10, 5))
age_counts = age_group_frequency["Passengers"]
sns.barplot(x=age_counts.index, y=age_counts.values, color=COLORS[0], ax=ax)
ax.set(title="Frequency distribution of passenger age groups", xlabel="Age group", ylabel="Passengers")
annotate_bars(ax)
plt.tight_layout()
plt.show()"""
        ),
        new_code_cell(
            """age_frequency = (
    df["age"]
    .value_counts()
    .sort_index()
    .rename_axis("Age")
    .to_frame("Passengers")
)
age_frequency["Share"] = age_frequency["Passengers"] / len(df)
display(age_frequency.style.format({"Passengers": "{:,}", "Share": "{:.2%}"}))

fig, ax = plt.subplots(figsize=(12, 5))
sns.histplot(df["age"], bins=range(df["age"].min(), df["age"].max() + 2), color=COLORS[2], ax=ax)
ax.axvline(df["age"].median(), color=COLORS[3], linestyle="--", label=f"Median: {df['age'].median():.0f}")
ax.set(title="Frequency distribution of passenger age", xlabel="Age", ylabel="Passengers")
ax.legend()
plt.tight_layout()
plt.show()"""
        ),
        new_code_cell(
            """gender_order = ["Female", "Male"]
gender_frequency = (
    df["gender"]
    .value_counts()
    .reindex(gender_order)
    .rename_axis("Recorded gender")
    .to_frame("Passengers")
)
gender_frequency["Share"] = gender_frequency["Passengers"] / len(df)
display(gender_frequency.style.format({"Passengers": "{:,}", "Share": "{:.1%}"}))

fig, ax = plt.subplots(figsize=(8, 5))
gender_counts = gender_frequency["Passengers"]
sns.barplot(
    x=gender_counts.index,
    y=gender_counts.values,
    hue=gender_counts.index,
    palette=[COLORS[4], COLORS[0]],
    legend=False,
    ax=ax,
)
ax.set(title="Frequency distribution of recorded gender", xlabel="", ylabel="Passengers")
annotate_bars(ax)
plt.tight_layout()
plt.show()"""
        ),
        new_markdown_cell(
            """**Interpretation note:** The age bands are analyst-defined and not official airline cohorts. The source contains only `Female` and `Male` gender labels. City and device distributions should be added only if those fields are obtained from another source with a valid passenger- or survey-level join key."""
        ),
    ]

    notebook.cells[findings_index:findings_index] = cells
    nbformat.write(notebook, NOTEBOOK_PATH)
    print(f"Added demographic distribution section to {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()

