"""Add descriptive retention-proxy views to the bivariate notebook."""

from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell


PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks/02_bivariate_analysis.ipnb"
STANDARD_COPY = PROJECT_ROOT / "notebooks/02_bivariate_analysis.ipynb"
SECTION_MARKER = "## 5. Retention proxy across satisfaction and experience levels"


def main() -> None:
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)

    existing_start = next(
        (
            index
            for index, cell in enumerate(notebook.cells)
            if cell.cell_type == "markdown" and SECTION_MARKER in cell.source
        ),
        None,
    )
    if existing_start is not None:
        existing_end = next(
            (
                index
                for index in range(existing_start + 1, len(notebook.cells))
                if notebook.cells[index].cell_type == "markdown"
                and notebook.cells[index].source.startswith("## 6.")
            ),
            len(notebook.cells),
        )
        del notebook.cells[existing_start:existing_end]

    review_index = next(
        index
        for index, cell in enumerate(notebook.cells)
        if cell.cell_type == "markdown"
        and (
            cell.source.startswith("## 5. Review guide")
            or cell.source.startswith("## 6. Review guide")
        )
    )
    notebook.cells[review_index].source = notebook.cells[review_index].source.replace(
        "## 5. Review guide", "## 6. Review guide"
    )

    cells = [
        new_markdown_cell(
            """## 5. Retention proxy across satisfaction and experience levels

**Definition and limitation:** `customer_type = Returning` is used as a retention proxy. The dataset does not track the same customer over time, so the figures below show the **share of surveyed passengers labeled Returning**, not a true cohort-retention rate.

This section descriptively compares the proxy across satisfaction outcomes and within service-rating, travel-class, and delay groups. No statistical tests or causal conclusions are included."""
        ),
        new_code_cell(
            '''retention_data = df.assign(is_returning=df["customer_type"].eq("Returning").astype(int))

retention_by_satisfaction = (
    retention_data.groupby("satisfaction", observed=True)
    .agg(Passengers=("passenger_id", "size"), Returning_customers=("is_returning", "sum"), Returning_share=("is_returning", "mean"))
    .reset_index()
)
display(retention_by_satisfaction.style.hide(axis="index").format({
    "Passengers": "{:,}", "Returning_customers": "{:,}", "Returning_share": "{:.1%}"
}))

fig, ax = plt.subplots(figsize=(9, 5))
sns.barplot(data=retention_by_satisfaction, x="satisfaction", y="Returning_share", hue="satisfaction", palette=SATISFACTION_COLORS, legend=False, ax=ax)
ax.set(title="Returning-customer share by satisfaction outcome", xlabel="", ylabel="Returning-customer share", ylim=(0, 1))
ax.yaxis.set_major_formatter(PercentFormatter(1))
annotate_rates(ax)
plt.tight_layout()
plt.show()'''
        ),
        new_markdown_cell(
            """### 5.1 Service ratings, satisfaction, and the retention proxy

Each line represents one satisfaction outcome. The vertical axis is the share of passengers labeled Returning within each rating-and-satisfaction subgroup. Clean ratings exclude undocumented zero values."""
        ),
        new_code_cell(
            '''service_retention_tables = {}
fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=True)
for ax, (column, label) in zip(axes, service_variables.items()):
    table = (
        retention_data.dropna(subset=[column])
        .groupby([column, "satisfaction"], observed=True)
        .agg(Passengers=("passenger_id", "size"), Returning_customers=("is_returning", "sum"), Returning_share=("is_returning", "mean"))
        .reset_index()
        .rename(columns={column: "Rating"})
    )
    service_retention_tables[label] = table
    sns.lineplot(data=table, x="Rating", y="Returning_share", hue="satisfaction", hue_order=["Satisfied", "Neutral or Dissatisfied"], palette=SATISFACTION_COLORS, marker="o", linewidth=2.3, ax=ax)
    ax.set(title=f"{label}: returning share", xlabel=f"{label} rating", ylabel="Returning-customer share", ylim=(0, 1))
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xticks([1, 2, 3, 4, 5])
    if ax is not axes[0]:
        ax.get_legend().remove()
axes[0].legend(title="Satisfaction")
plt.tight_layout()
plt.show()

service_retention_table = pd.concat(
    [table.assign(Service=label) for label, table in service_retention_tables.items()],
    ignore_index=True,
)[["Service", "Rating", "satisfaction", "Passengers", "Returning_customers", "Returning_share"]]
display(service_retention_table.style.hide(axis="index").format({
    "Rating": "{:.0f}", "Passengers": "{:,}", "Returning_customers": "{:,}", "Returning_share": "{:.1%}"
}))'''
        ),
        new_markdown_cell(
            """### 5.2 Travel class, satisfaction, and the retention proxy

The grouped bars compare returning-customer share between the two satisfaction outcomes within each travel class."""
        ),
        new_code_cell(
            '''class_retention = (
    retention_data.groupby(["travel_class", "satisfaction"], observed=True)
    .agg(Passengers=("passenger_id", "size"), Returning_customers=("is_returning", "sum"), Returning_share=("is_returning", "mean"))
    .reset_index()
)
class_retention["travel_class"] = pd.Categorical(class_retention["travel_class"], categories=class_order, ordered=True)
class_retention = class_retention.sort_values(["travel_class", "satisfaction"])
display(class_retention.style.hide(axis="index").format({
    "Passengers": "{:,}", "Returning_customers": "{:,}", "Returning_share": "{:.1%}"
}))

fig, ax = plt.subplots(figsize=(11, 5))
sns.barplot(data=class_retention, x="travel_class", y="Returning_share", hue="satisfaction", hue_order=["Satisfied", "Neutral or Dissatisfied"], palette=SATISFACTION_COLORS, ax=ax)
ax.set(title="Returning-customer share by travel class and satisfaction", xlabel="Travel class", ylabel="Returning-customer share", ylim=(0, 1))
ax.yaxis.set_major_formatter(PercentFormatter(1))
for container in ax.containers:
    ax.bar_label(container, labels=[f"{bar.get_height():.1%}" for bar in container], padding=3, fontsize=8)
ax.legend(title="Satisfaction")
plt.tight_layout()
plt.show()'''
        ),
        new_markdown_cell(
            """### 5.3 Flight delays, satisfaction, and the retention proxy

The delay-band views retain every record. Missing arrival delay remains a separate category rather than being imputed."""
        ),
        new_code_cell(
            '''def retention_by_delay_band(column, order):
    table = (
        retention_data.groupby([column, "satisfaction"], observed=True)
        .agg(Passengers=("passenger_id", "size"), Returning_customers=("is_returning", "sum"), Returning_share=("is_returning", "mean"))
        .reset_index()
    )
    table[column] = pd.Categorical(table[column], categories=order, ordered=True)
    return table.sort_values([column, "satisfaction"]).reset_index(drop=True)

departure_retention = retention_by_delay_band("departure_delay_band", departure_order)
arrival_retention = retention_by_delay_band("arrival_delay_band", arrival_order)

display(Markdown("**Departure-delay bands**"))
display(departure_retention.style.hide(axis="index").format({
    "Passengers": "{:,}", "Returning_customers": "{:,}", "Returning_share": "{:.1%}"
}))
display(Markdown("**Arrival-delay bands**"))
display(arrival_retention.style.hide(axis="index").format({
    "Passengers": "{:,}", "Returning_customers": "{:,}", "Returning_share": "{:.1%}"
}))

fig, axes = plt.subplots(1, 2, figsize=(17, 5), sharey=True)
for ax, table, category, title in [
    (axes[0], departure_retention, "departure_delay_band", "Departure-delay band"),
    (axes[1], arrival_retention, "arrival_delay_band", "Arrival-delay band"),
]:
    sns.barplot(data=table, x=category, y="Returning_share", hue="satisfaction", hue_order=["Satisfied", "Neutral or Dissatisfied"], palette=SATISFACTION_COLORS, ax=ax)
    ax.set(title=f"Returning share by {title.lower()} and satisfaction", xlabel=title, ylabel="Returning-customer share", ylim=(0, 1))
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.tick_params(axis="x", rotation=18)
    if ax is not axes[0]:
        ax.get_legend().remove()
axes[0].legend(title="Satisfaction")
plt.tight_layout()
plt.show()'''
        ),
        new_code_cell(
            '''overall_proxy = retention_by_satisfaction.set_index("satisfaction")["Returning_share"]
cleanliness_proxy = service_retention_tables["Cleanliness"].pivot(index="Rating", columns="satisfaction", values="Returning_share")
seat_proxy = service_retention_tables["Seat comfort"].pivot(index="Rating", columns="satisfaction", values="Returning_share")
onboard_proxy = service_retention_tables["Onboard service"].pivot(index="Rating", columns="satisfaction", values="Returning_share")
display(Markdown(f"""
**Descriptive interpretation**

- Returning-customer share is **{overall_proxy['Satisfied']:.1%}** among satisfied passengers and **{overall_proxy['Neutral or Dissatisfied']:.1%}** among neutral or dissatisfied passengers.
- For **cleanliness**, satisfied passengers have especially high returning shares at ratings 3–5 ({cleanliness_proxy.loc[3, 'Satisfied']:.1%} to {cleanliness_proxy.loc[5, 'Satisfied']:.1%}). At ratings 1–2, their returning share is slightly below the neutral-or-dissatisfied group.
- For **seat comfort**, the largest separation appears at ratings 4–5: returning share is about {seat_proxy.loc[4, 'Satisfied']:.1%}–{seat_proxy.loc[5, 'Satisfied']:.1%} among satisfied passengers, compared with {seat_proxy.loc[4, 'Neutral or Dissatisfied']:.1%} and {seat_proxy.loc[5, 'Neutral or Dissatisfied']:.1%} among neutral or dissatisfied passengers.
- For **onboard service**, satisfied passengers have a higher returning share at every rating level; however, neither satisfaction group's pattern rises consistently with every rating step.
- The service-rating, class, and delay charts show customer-status composition across observed subgroups, not conversion from first-time to returning status.
- These patterns do not measure how many first-time passengers later returned and do not establish that satisfaction, service ratings, class, or delays caused retention.
"""))'''
        ),
    ]

    notebook.cells[review_index:review_index] = cells
    nbformat.write(notebook, NOTEBOOK_PATH)
    nbformat.write(notebook, STANDARD_COPY)
    print(f"Added retention-proxy section to {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()
