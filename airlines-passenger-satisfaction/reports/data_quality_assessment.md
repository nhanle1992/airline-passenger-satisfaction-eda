# Processed Data Quality Assessment and Proposed Cleaning Plan

## Review status

Assessment only. No cleaning has been applied to the processed dataset. The file reviewed was `data/processed/airline_passenger_satisfaction_prepared.csv`.

## Dataset integrity summary

- Records: 129,880
- Columns: 43 (24 standardized source variables and 19 engineered variables)
- Unique passenger IDs: 129,880, spanning 1 through 129,880
- Duplicate full rows: 0
- Duplicate rows after excluding passenger ID: 0
- Malformed CSV rows: 0
- Numeric parsing errors: 0
- Leading or trailing whitespace issues: 0
- Unrecognized missing-value markers such as `NA`, `null`, or `?`: 0
- Invalid category labels or inconsistent capitalization: 0 detected
- Rating values outside the expected 0–5 range: 0
- Negative ages, distances, or delays: 0
- Engineered-feature mismatches: 0

All satisfaction flags, bands, delay calculations, composite scores, zero-rating counts, and passenger segments were recalculated independently and matched the processed dataset.

## Issues requiring treatment or an explicit analysis decision

### 1. Missing arrival-delay information

`arrival_delay` is missing in 393 records, representing approximately 0.30% of the dataset. The following dependent engineered fields are consequently also missing in exactly those records:

- `any_arrival_delay`
- `total_delay`
- `delay_change`

The `arrival_delay_band` field correctly preserves these records under the category `Missing`.

The missing records differ somewhat from complete records:

| Measure | Missing arrival delay | Available arrival delay |
|---|---:|---:|
| Satisfaction rate | 42.24% | 43.45% |
| Mean departure delay | 37.89 | 14.64 |
| No departure delay | 37.40% | 56.54% |
| Business-class passengers | 43.26% | 47.87% |
| Business travel | 63.10% | 69.08% |

Because the missing group has substantially longer departure delays, the arrival-delay values should not automatically be considered missing completely at random.

### 2. Ambiguous zero-valued service ratings

The source documentation does not define whether a rating of zero means the lowest possible rating, not applicable, not used, or missing.

- 10,313 records (7.94%) contain at least one zero service rating.
- There are 20,134 zero-valued rating cells in total.
- Zeros occur mainly in time convenience, online booking, online boarding, and inflight Wi-Fi.
- The three variables used in the core-service hypothesis contain very few zeros: cleanliness has 14, seat comfort has 1, and onboard service has 5.
- Baggage handling contains only ratings from 1 through 5.

The concentration of zeros in optional or digital services suggests that zero may mean “not applicable” or “not used,” but that interpretation cannot be confirmed from the data alone.

### 3. Extreme but internally consistent delays

Delay distributions are strongly right-skewed:

| Threshold | Departure delay count | Arrival delay count |
|---|---:|---:|
| Greater than 180 | 1,290 | 1,317 |
| Greater than 360 | 150 | 157 |
| Greater than 720 | 19 | 15 |
| Greater than 1,440 | 1 | 1 |

The maximum departure and arrival delays are 1,592 and 1,584 respectively. The largest departure and arrival values generally occur together and are close in magnitude, which makes them internally plausible rather than obvious entry errors. Removing them would discard genuine severe-disruption experiences and could bias the delay hypothesis.

### 4. Very small combined passenger segments

The engineered `passenger_segment` variable produces a few very small groups:

- First-time, personal, Economy Plus: 4 records
- First-time, personal, Business: 13 records
- First-time, personal, Economy: 184 records

These are not invalid records. However, percentages for very small groups will be unstable and should not be presented as reliable segment-level findings.

### 5. Unverified measurement definitions

- The measurement unit for `flight_distance` is not documented.
- Delay units appear likely to be minutes, but this is not explicitly documented.
- The exact wording and anchors for the 0–5 rating scales are unavailable.
- The current distance and delay bands are analytically useful but remain provisional until the units and business definitions are confirmed.

### 6. Structural limitations that cleaning cannot resolve

- `satisfaction` combines neutral and dissatisfied passengers into one category; these outcomes cannot be separated.
- Gender contains only Female and Male, reflecting the source data's available categories.
- The data is observational, so cleaning will not make causal conclusions possible.

## Proposed cleaning plan — pending approval

### Step 1: Preserve lineage

- Keep the current raw and processed files unchanged.
- Write cleaning results to a new file named `data/processed/airline_passenger_satisfaction_cleaned.csv`.
- Add explicit cleaning flags rather than silently deleting or overwriting questionable values.

### Step 2: Handle missing arrival delays without general-purpose imputation

- Retain all 393 records.
- Add `arrival_delay_missing` as a binary flag.
- Keep `arrival_delay`, `total_delay`, and `delay_change` missing where the source arrival delay is unavailable.
- Use all records for analyses that do not require arrival delay.
- Use complete cases for primary arrival-delay analyses and report the excluded count.
- Compare results with a sensitivity analysis that includes the existing `Missing` band. Do not mean- or median-impute arrival delay because the missing group has a different departure-delay profile and simple imputation could distort the hypothesis test.

### Step 3: Treat zero ratings transparently

- Preserve every original rating column unchanged.
- Create analysis versions of rating fields in which zero is treated as missing, with clear `_clean` or `_nonzero` suffixes.
- Use zero-excluded values for primary service averages if no official codebook can be obtained.
- Retain zero-inclusive composites for sensitivity checks.
- Report how many observations contribute to each composite score.

This approach is preferable to recoding zero directly because its meaning is uncertain. The service-quality hypothesis should be largely unaffected because its three core fields contain only 20 zero values in total.

### Step 4: Retain and flag extreme delays

- Do not delete or replace high delays automatically.
- Add severity flags such as `extreme_delay_over_180` and `extreme_delay_over_720`.
- Use medians, interquartile ranges, percentiles, and log-scaled plots for descriptive analysis.
- For future regression, compare the raw-delay model with a capped or transformed sensitivity model. Any cap should affect only the sensitivity feature, not the original delays.

### Step 5: Manage sparse passenger segments at reporting time

- Retain all underlying passenger records and base categories.
- Do not report or statistically compare combined segments below a stated minimum sample size, recommended as 30 records.
- Prefer separate comparisons by customer type, travel type, and travel class when combined segments are sparse.

### Step 6: Confirm or clearly label assumptions

- Seek the original codebook to verify distance units, delay units, rating anchors, and the meaning of zero.
- If documentation remains unavailable, label distance and delay values as “dataset units” in reports and state all rating assumptions.
- Keep the current bands but mark them as analyst-defined, not official airline categories.

### Step 7: Recalculate and validate cleaned features

- Recalculate all affected composites and delay features from the preserved source columns.
- Confirm row count and unique IDs remain 129,880.
- Confirm categorical domains, numeric ranges, missing-value propagation, and engineered-feature formulas.
- Produce a before-and-after quality summary and log every transformation.

## Recommendation

Proceed with the plan above. The dataset is already structurally sound; cleaning should focus on transparent handling of missing arrival delays, ambiguous zero ratings, extreme delays, and sparse reporting groups rather than deleting records. This preserves maximum information for descriptive analysis and future hypothesis testing.

