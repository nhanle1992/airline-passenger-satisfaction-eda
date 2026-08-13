# Airline Passenger Satisfaction Analysis

An end-to-end exploratory and statistical analysis of passenger satisfaction using survey responses from **129,880 airline passengers**. The project examines how service quality, travel class, passenger characteristics, and flight delays relate to overall satisfaction.

## Final report

The complete findings, charts, hypothesis results, and recommendations are presented in a self-contained HTML report:

### [View the final Airline Passenger Satisfaction report](reports/airline_passenger_satisfaction_report.html)

Download the HTML file and open it in a browser for the fully styled and interactive reading experience.

## Business problem

Airlines operate in a competitive market where the passenger experience can influence loyalty, repeat bookings, brand perception, and revenue. The purpose of this project is to identify the aspects of the journey most closely associated with satisfaction so that improvement efforts can be focused on the areas with the greatest potential value.

The analysis addresses three questions:

1. Are cleanliness, seat comfort, and onboard service associated with passenger satisfaction?
2. Do Business-class passengers report higher satisfaction than Economy and Economy Plus passengers?
3. Are longer departure and arrival delays associated with lower satisfaction?

## Dataset

The source contains 129,880 passenger-level survey records and 24 original variables covering:

- Passenger age and recorded gender
- First-time or returning customer status
- Business or personal travel
- Business, Economy Plus, or Economy class
- Flight distance
- Departure and arrival delays
- Fourteen service ratings
- Overall satisfaction

The raw dataset is intentionally excluded from this repository. Place a local copy at:

```text
data/raw/airline_passenger_satisfaction.csv
```

## Project workflow

```text
Problem definition
       ↓
Data dictionary and quality assessment
       ↓
Feature engineering and cleaning
       ↓
Univariate analysis
       ↓
Bivariate analysis
       ↓
Multivariable analysis
       ↓
Hypothesis testing
       ↓
Final HTML report and recommendations
```

## Key findings

- Only **43.4%** of surveyed passengers were classified as satisfied.
- Inflight service received the highest clean average service rating at **3.64 out of 5**.
- Inflight Wi-Fi received the lowest clean average rating at **2.81 out of 5**.
- Business-class satisfaction was **69.4%**, compared with **24.6%** for Economy Plus and **18.8%** for Economy.
- Higher cleanliness, seat-comfort, and onboard-service ratings were associated with higher satisfaction.
- Onboard service showed the largest adjusted association among the three core service measures.
- Satisfaction declined as departure and arrival delays moved from no delay to moderate and long delay bands.
- Delay effects were nonlinear: the sharpest decline appeared at lower-to-moderate delays before flattening at longer durations.
- Returning customers represented **89.9%** of satisfied passengers and **75.4%** of neutral or dissatisfied passengers. This is a customer-status composition measure, not true longitudinal retention.

## Hypothesis-testing results

| Hypothesis | Primary method | Decision | Interpretation |
|---|---|---|---|
| Service quality and satisfaction | Logistic-regression likelihood-ratio test | Reject H0 | Cleanliness, seat comfort, and onboard service are jointly associated with satisfaction. |
| Travel class and satisfaction | Pearson chi-square test with planned class contrasts | Reject H0 | Business class has a substantially higher satisfaction rate than both comparison classes. |
| Flight delays and satisfaction | Separate nonlinear logistic models for departure and arrival delay | Reject H0 | Both delay measures are associated with satisfaction, but the relationships are nonlinear. |

The dataset is observational. These results demonstrate association, not causation.

## Recommendations

1. **Prioritize onboard-service consistency.** Use targeted coaching, service monitoring, and recovery playbooks to strengthen the service area with the largest adjusted association.
2. **Improve digital touchpoints.** Investigate inflight Wi-Fi reliability and online-booking friction, which received the weakest average ratings.
3. **Use class-specific improvement plans.** Protect the Business-class experience while addressing comfort and core service gaps in Economy and Economy Plus.
4. **Intervene early during disruptions.** Use operational triggers and proactive communication before short delays develop into moderate delays.
5. **Expand future data collection.** Add stable customer IDs, dates, route, fare, loyalty tier, aircraft, delay cause, compensation, city, and device information.

## Analysis notebooks

| Notebook | Purpose |
|---|---|
| [`01_univariate_analysis.ipynb`](notebooks/01_univariate_analysis.ipynb) | Individual distributions, missingness, service ratings, and passenger composition |
| [`02_bivariate_analysis.ipynb`](notebooks/02_bivariate_analysis.ipynb) | Satisfaction relationships for the three hypotheses and returning-customer proxy analysis |
| [`03_multivariable_analysis.ipynb`](notebooks/03_multivariable_analysis.ipynb) | Stratified patterns involving service quality, class, travel purpose, customer type, and delays |
| [`04_hypothesis_testing.ipynb`](notebooks/04_hypothesis_testing.ipynb) | Primary tests, adjusted models, diagnostics, effect sizes, and sensitivity analyses |

## Repository structure

```text
airlines-passenger-satisfaction/
├── data/
│   ├── raw/                 # Original data (excluded from Git)
│   └── processed/           # Prepared and cleaned data (excluded from Git)
├── notebooks/               # Executed analysis notebooks
├── reports/
│   ├── airline_passenger_satisfaction_report.html
│   ├── eda_key_observations.md
│   ├── hypothesis_testing_results.md
│   └── data quality and validation reports
├── src/                     # Reproducible preparation, cleaning, and report scripts
├── problem_definition.md
├── data_dictionary_and_gap_analysis.txt
├── Hypothesis Testing.md
├── requirements.txt
└── README.md
```

## Reproducing the project

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install the dependencies

```bash
pip install -r requirements.txt
```

### 3. Add the dataset

Place the source CSV at:

```text
data/raw/airline_passenger_satisfaction.csv
```

### 4. Prepare and clean the data

```bash
python3 src/prepare_data.py
python3 src/clean_data.py
```

### 5. Open the notebooks

```bash
jupyter notebook
```

Run the notebooks in numerical order.

### 6. Regenerate the final HTML report

```bash
python3 src/generate_html_report.py
```

## Data-quality decisions

- The 393 missing arrival-delay values were retained and flagged rather than imputed.
- Extreme but plausible delays were preserved and analyzed through robust summaries and sensitivity checks.
- Undocumented zero service ratings were preserved in original fields and treated as missing only in dedicated clean fields.
- Sparse combined passenger segments were retained but excluded from independent reporting when their sample size was below 30.
- Raw and processed datasets are excluded from Git to protect repository size and preserve data lineage.

## Limitations

- Neutral and dissatisfied passengers are combined into one outcome.
- The units for flight distance and delay are not documented in the source.
- The exact meaning of a zero service rating is unknown.
- The data does not include route, fare, aircraft, loyalty tier, delay cause, compensation, city, or device.
- There are no repeated customer records or dates, so true retention cannot be calculated.
- Observational analysis cannot establish causal effects.

## Tools used

- Python
- pandas and NumPy
- Matplotlib and Seaborn
- SciPy and statsmodels
- Jupyter Notebook
- HTML and CSS

## Author

Created as an end-to-end data analysis project focused on airline passenger experience and satisfaction.
