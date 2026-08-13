"""Add a retention/cohort availability and proxy section to the EDA notebook."""

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks/01_univariate_analysis.ipynb"
SECTION_MARKER = "## 8. Retention and customer-cohort proxy"


def main() -> None:
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)

    # Make the update idempotent when the script is run more than once.
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
                and notebook.cells[index].source.startswith("## 9.")
            ),
            len(notebook.cells),
        )
        del notebook.cells[section_start:section_end]

    findings_index = next(
        index
        for index, cell in enumerate(notebook.cells)
        if cell.cell_type == "markdown" and "## 8. Univariate findings" in cell.source
    )
    notebook.cells[findings_index].source = notebook.cells[findings_index].source.replace(
        "## 8. Univariate findings", "## 9. Univariate findings"
    )

    new_cells = [
        new_markdown_cell(
            """## 8. Retention and customer-cohort proxy

**Important limitation:** This dataset cannot measure true retention by tenure cohort (for example, first-month versus later-month users). It has no customer signup date, survey date, booking history, tenure, or repeated observations for the same customer.

The closest available proxy is `customer_type`:

- `First-time` indicates a passenger identified as a first-time customer.
- `Returning` indicates a passenger identified as a returning customer.

The tables and plots below therefore describe **customer-status composition**, not a retention rate. A returning-customer share should not be interpreted as the percentage of first-time customers who later returned, because the records are not linked longitudinally."""
        ),
        new_code_cell(
            """retention_availability = pd.DataFrame({
    "Requested measure": [
        "First-month vs later-month retention",
        "Returning-customer share",
        "Returning-customer share by available travel cohort",
    ],
    "Can calculate?": ["No", "Yes — proxy only", "Yes — descriptive proxy only"],
    "Reason / required field": [
        "Requires customer ID plus signup/first-use date and later activity dates",
        "Available from customer_type, but it is not a longitudinal retention rate",
        "Can group customer_type by travel type or class, but cohorts are not tenure cohorts",
    ],
})
display(retention_availability.style.hide(axis="index"))"""
        ),
        new_code_cell(
            """customer_status = (
    df["customer_type"]
    .value_counts()
    .rename_axis("Customer status")
    .to_frame("Passengers")
)
customer_status["Share"] = customer_status["Passengers"] / len(df)
display(customer_status.style.format({"Passengers": "{:,}", "Share": "{:.1%}"}))

fig, ax = plt.subplots(figsize=(8, 4.5))
status_order = ["Returning", "First-time"]
status_counts = df["customer_type"].value_counts().reindex(status_order)
sns.barplot(
    x=status_counts.index,
    y=status_counts.values,
    hue=status_counts.index,
    palette=[COLORS[0], COLORS[4]],
    legend=False,
    ax=ax,
)
ax.set(title="Customer-status composition (retention proxy)", xlabel="", ylabel="Passengers")
annotate_bars(ax)
plt.tight_layout()
plt.show()"""
        ),
        new_markdown_cell(
            """### Returning-customer share across available cohorts

These cohort views describe how common returning customers are within travel-purpose and travel-class groups. They do not track customers over time and should not be labeled as cohort retention curves."""
        ),
        new_code_cell(
            """def returning_share_table(column, label):
    result = (
        df.assign(is_returning=df["customer_type"].eq("Returning"))
        .groupby(column, observed=True)
        .agg(Passengers=("passenger_id", "size"), Returning_customers=("is_returning", "sum"), Returning_share=("is_returning", "mean"))
        .reset_index()
        .rename(columns={column: label})
    )
    return result

travel_retention_proxy = returning_share_table("travel_type", "Travel purpose")
class_retention_proxy = returning_share_table("travel_class", "Travel class")

display(Markdown("**By travel purpose**"))
display(travel_retention_proxy.style.hide(axis="index").format({"Passengers": "{:,}", "Returning_customers": "{:,}", "Returning_share": "{:.1%}"}))
display(Markdown("**By travel class**"))
display(class_retention_proxy.style.hide(axis="index").format({"Passengers": "{:,}", "Returning_customers": "{:,}", "Returning_share": "{:.1%}"}))

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
for ax, table, category, title in [
    (axes[0], travel_retention_proxy, "Travel purpose", "Returning-customer share by travel purpose"),
    (axes[1], class_retention_proxy, "Travel class", "Returning-customer share by travel class"),
]:
    sns.barplot(data=table, x=category, y="Returning_share", color=COLORS[0], ax=ax)
    ax.set(title=title, xlabel="", ylabel="Returning-customer share", ylim=(0, 1))
    ax.yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(1))
    for patch in ax.patches:
        ax.text(
            patch.get_x() + patch.get_width() / 2,
            patch.get_height(),
            f"{patch.get_height():.1%}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
plt.tight_layout()
plt.show()"""
        ),
        new_code_cell(
            '''returning_share = df["customer_type"].eq("Returning").mean()
highest_class = class_retention_proxy.loc[class_retention_proxy["Returning_share"].idxmax()]
lowest_class = class_retention_proxy.loc[class_retention_proxy["Returning_share"].idxmin()]
display(Markdown(f"""
**Proxy interpretation**

- Returning customers make up **{returning_share:.1%}** of the surveyed sample.
- The highest returning-customer share among travel classes is **{highest_class['Travel class']} ({highest_class['Returning_share']:.1%})**; the lowest is **{lowest_class['Travel class']} ({lowest_class['Returning_share']:.1%})**.
- These differences describe the sample's composition. They do **not** estimate whether new customers were retained.

To calculate true month-based retention, collect a stable customer identifier, first-use or signup month, and subsequent booking/activity dates. Then define retention as the share of each starting cohort active again in month 1, month 2, and later periods.
"""))'''
        ),
    ]

    notebook.cells[findings_index:findings_index] = new_cells
    nbformat.write(notebook, NOTEBOOK_PATH)
    print(f"Added retention proxy section to {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
