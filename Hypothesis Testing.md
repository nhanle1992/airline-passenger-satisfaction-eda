# Hypothesis Testing Plan

## Status and approval gate

This document defines the proposed statistical analysis. **No hypothesis tests have been performed.** Testing will begin only after this plan is reviewed and approved.

## Common analysis framework

### Analysis dataset

Use `data/processed/airline_passenger_satisfaction_cleaned.csv` as the analysis source.

- Unit of analysis: one passenger survey record
- Available records: 129,880
- Outcome: `is_satisfied`, coded `1` for Satisfied and `0` for Neutral or Dissatisfied
- Significance level: α = 0.05
- Confidence level: 95%
- Statistical tests: two-sided unless a directional contrast is explicitly identified below

The source is observational and cross-sectional. Results will be described as associations or differences, not causal effects.

### Reporting principles

Because the sample is very large, small and operationally unimportant differences may produce small p-values. Every result will therefore include:

- The analysis sample size and exclusions
- The estimated effect and its 95% confidence interval
- The p-value for the prespecified test
- An absolute measure, such as a satisfaction-rate or predicted-probability difference
- A practical interpretation alongside the statistical conclusion
- Unadjusted and adjusted results reported separately

The primary test for each hypothesis will determine the main conclusion. Follow-up comparisons and sensitivity analyses will be clearly labeled and will not replace the primary result without explanation.

### Candidate adjustment variables

Adjusted analyses will consider variables available before or independently of the surveyed service evaluation:

- `age`
- `gender`
- `customer_type`
- `travel_type`
- `travel_class`, except when class is the exposure under Hypothesis 2
- `flight_distance`
- Departure and arrival delay, when they are not the exposure under Hypothesis 3

Service ratings will not automatically be used as control variables for the class or delay hypotheses because they may be part of the pathway through which class or disruption relates to satisfaction. If included, that model will be labeled exploratory rather than the primary adjusted model.

Continuous adjustment variables will be checked for nonlinear relationships with the log-odds of satisfaction. Categories will not be combined merely to produce a preferred result.

### Multiple-comparison control

- Each hypothesis has one prespecified primary global test.
- Holm correction will be used within a hypothesis family when multiple follow-up comparisons are made.
- Hypothesis 3 has two related delay exposures; departure- and arrival-delay primary p-values will be Holm-adjusted as a two-test family.
- Both raw and adjusted p-values will be reported for transparency.


## Hypothesis 1: Service quality and satisfaction

### Problem-definition statement

Passengers who give higher ratings for cleanliness, seat comfort, and onboard service are more likely to report overall satisfaction than passengers who give lower ratings.

- **H0:** Cleanliness, seat-comfort, and onboard-service ratings are not associated with overall passenger satisfaction.
- **H1:** Higher ratings are associated with a higher probability of overall satisfaction.

### 1. Statistical test to be performed

#### Primary test: joint binary logistic-regression likelihood-ratio test

Fit a binary logistic-regression model with:

- Outcome: `is_satisfied`
- Predictors: `cleanliness_rating_clean`, `seat_comfort_rating_clean`, and `onboard_service_rating_clean`

For the primary model, each 1–5 rating will be treated as a categorical variable. This avoids assuming that the change from rating 1 to 2 has the same relationship with satisfaction as the change from rating 4 to 5.

Compare the full three-rating model with an intercept-only model using a likelihood-ratio test. This is the primary global test of whether the service-rating set is associated with satisfaction.

#### Planned follow-up analyses

- Estimate odds ratios for each rating level relative to rating 1, with 95% confidence intervals.
- Calculate model-based satisfaction probabilities at each rating level while holding the other two rating distributions constant through average marginal standardization.
- Test each service variable as a group by comparing the full model with a model omitting that service. Apply Holm correction to the three service-level p-values.
- Fit a prespecified ordered-trend model treating each rating as numeric only after checking whether the observed log-odds pattern is reasonably linear. Positive coefficients would support the stated direction.

#### Adjusted model

Repeat the model while adjusting for age, gender, customer type, travel purpose, travel class, flight distance, departure delay, and arrival delay. Departure and arrival delay will be checked for collinearity and functional form before both are retained together.

The unadjusted joint test remains the primary result; the adjusted model assesses whether the association persists after accounting for observed passenger and travel differences.

### 2. Required data subset

Include records with:

- Nonmissing `is_satisfied`
- Nonmissing `cleanliness_rating_clean`
- Nonmissing `seat_comfort_rating_clean`
- Nonmissing `onboard_service_rating_clean`

Ratings of zero are excluded through the `_clean` fields because their meaning is undocumented. Only 20 zero values exist across these three source fields, so the primary service subset should remain close to the full sample. The exact complete-case count and reason for every exclusion will be reported before testing.

For the adjusted complete-case model, records also need nonmissing values for all included adjustment variables. Arrival delay has 393 missing values; those observations will remain in the unadjusted service analysis and will be excluded only from an adjusted model that requires arrival delay.

### 3. Assumptions, diagnostics, and metrics

#### Assumptions and diagnostics

- Each row represents an independent passenger response.
- The binary outcome is coded correctly.
- Rating categories have adequate observations and outcome variation.
- The logistic model has no complete or quasi-complete separation.
- Predictors do not exhibit problematic multicollinearity; inspect correlations, variance inflation factors, and condition indices.
- Numeric trend versions satisfy approximate linearity in the logit; otherwise categorical or spline representations will be retained.
- Examine influential observations using standardized residuals, leverage, and Cook's distance or an equivalent diagnostic.

#### Effect-size and model metrics

- Odds ratios and 95% confidence intervals
- Adjusted and unadjusted predicted satisfaction probabilities
- Absolute probability differences between meaningful rating levels, especially ratings 1 and 5
- Likelihood-ratio statistic and degrees of freedom
- McFadden pseudo-R² and calibration summary as model-description measures

Model discrimination may be reported descriptively using ROC AUC, but it will not determine whether the hypothesis is supported.

#### Sensitivity analyses

- Repeat using the original zero-inclusive rating fields.
- Repeat with `core_service_score_clean` as a summarized exposure.
- Compare categorical-rating results with the ordered numeric trend model.
- Repeat the adjusted model without arrival delay so the 393 missing arrival-delay records remain included.


## Hypothesis 2: Travel class and satisfaction

### Problem-definition statement

Passengers traveling in Business class have a higher satisfaction rate than passengers traveling in Economy or Economy Plus.

- **H0:** Overall satisfaction does not differ by travel class.
- **H1:** Satisfaction differs by travel class, with Business-class passengers having a higher rate.

### 1. Statistical test to be performed

#### Primary test: Pearson chi-square test of independence

Construct a 3 × 2 contingency table using:

- Rows: Business, Economy, and Economy Plus
- Columns: Satisfied and Neutral or Dissatisfied

Use Pearson's chi-square test to determine whether satisfaction outcome and travel class are associated. This global test addresses whether any class difference exists.

#### Prespecified directional contrasts

If the global test is significant, perform two planned comparisons:

1. Business versus Economy
2. Business versus Economy Plus

Use two-sample tests of proportions and apply Holm correction to these two comparisons. Report one-sided directional p-values only as supplementary evidence because the global primary test is two-sided; two-sided confidence intervals will always be reported.

No Economy-versus-Economy-Plus comparison is required for the stated hypothesis. If shown, it will be labeled exploratory.

#### Adjusted model

Fit a binary logistic-regression model with travel class as a categorical predictor and Business as the reference category, adjusting for age, gender, customer type, travel purpose, flight distance, departure delay, and arrival delay.

Use a global likelihood-ratio test for the class terms and report standardized adjusted satisfaction probabilities for each class. The adjusted model is important because the EDA showed that travel purpose and customer type are distributed differently across classes.

### 2. Required data subset

For the primary chi-square test, include all records with:

- A valid `travel_class` value: Business, Economy, or Economy Plus
- Nonmissing `is_satisfied`

The cleaned dataset contains both variables for all 129,880 records, so the full dataset is expected to be used.

The adjusted complete-case model will additionally require nonmissing adjustment variables. Arrival-delay missingness affects 393 records if arrival delay is included.

### 3. Assumptions, diagnostics, and metrics

#### Assumptions and diagnostics

- Passenger observations are independent.
- Travel-class categories are mutually exclusive.
- Outcome categories are mutually exclusive.
- Expected counts in the contingency table are at least 5. Given the observed sample sizes, this is expected to be satisfied but will be verified.
- For the adjusted logistic model, check separation, multicollinearity, functional form, residuals, leverage, and influential observations.
- Inspect class-by-travel-purpose and class-by-customer-type cell sizes before considering interaction terms. Sparse combined cells will not support stable estimates.

#### Effect-size metrics

- Satisfaction rate and 95% confidence interval for each class
- Absolute percentage-point differences for Business versus each comparison class
- Risk ratios and odds ratios with 95% confidence intervals
- Cramér's V for the global class-by-satisfaction association
- Adjusted predicted probabilities and average marginal contrasts from the secondary logistic model

#### Sensitivity and subgroup analyses

- Repeat class comparisons within Business and Personal travel groups.
- Repeat within Returning and First-time customer groups.
- Fit class-by-travel-purpose and class-by-customer-type interaction models only as prespecified secondary analyses and only if cell sizes are adequate.
- Compare adjusted results with and without arrival delay.


## Hypothesis 3: Flight delays and satisfaction

### Problem-definition statement

Passengers experiencing longer departure or arrival delays have a lower satisfaction rate than passengers experiencing short or no delays.

- **H0:** Flight-delay duration is not associated with overall passenger satisfaction.
- **H1:** Longer delay duration is associated with a lower probability of overall satisfaction.

### 1. Statistical test to be performed

#### Primary tests: separate binary logistic-regression likelihood-ratio tests

Analyze departure delay and arrival delay in separate primary models to avoid combining two highly related measures into one coefficient set.

For each delay variable:

- Outcome: `is_satisfied`
- Exposure: continuous delay duration
- Model: binary logistic regression

Delay has many zeros, strong right skew, and extreme but plausible values. The functional form will therefore be selected using a prespecified diagnostic sequence:

1. Fit a linear-delay model.
2. Compare its shape with a restricted cubic-spline representation using fixed, documented knots based on the delay distribution.
3. Retain the simpler linear representation if it describes the logit adequately; otherwise use the spline representation as the primary form.

Use a likelihood-ratio test of the full delay term or spline-term set against an intercept-only model. Apply Holm correction across the two primary exposure tests: departure delay and arrival delay.

#### Adjusted models

Repeat each delay model while adjusting for age, gender, customer type, travel purpose, travel class, and flight distance. Do not automatically adjust for service ratings in the primary adjusted model because service evaluations may occur after the disruption and may mediate part of its relationship with overall satisfaction.

Departure and arrival delays will not be placed together in the main adjusted model. A joint model may be shown as a sensitivity analysis after checking their correlation and variance inflation.

#### Secondary descriptive-form test

Use the prespecified delay bands—No delay, Short (1–15), Moderate (16–60), and Long (>60)—in a categorical logistic model. Compare each band with No delay and report adjusted probabilities. This is easier to interpret but loses continuous information, so it is secondary.

### 2. Required data subsets

#### Departure-delay analysis

Include records with:

- Nonmissing `departure_delay`
- Nonmissing `is_satisfied`

All 129,880 records are expected to qualify.

#### Arrival-delay analysis

Include records with:

- Nonmissing `arrival_delay`
- Nonmissing `is_satisfied`

The primary arrival-delay analysis will use complete cases. The dataset contains 393 missing arrival delays, leaving an expected maximum of 129,487 records before any additional adjusted-model exclusions. Arrival delay will not be mean- or median-imputed.

### 3. Assumptions, diagnostics, and metrics

#### Assumptions and diagnostics

- Passenger observations are independent.
- Delay and satisfaction fields are measured correctly.
- Logistic-model functional form is adequate; inspect binned empirical logits and compare linear and spline shapes.
- There is no complete separation.
- Adjusted predictors do not have problematic multicollinearity.
- Examine residuals, leverage, and influential records.
- Retain extreme delays in the primary analysis, but assess whether they have disproportionate influence.
- Examine whether missing arrival delay is associated with observed variables and satisfaction; the EDA already indicates a different departure-delay profile among missing records.

#### Effect-size and model metrics

- Predicted satisfaction probabilities at meaningful delay values such as 0, 15, 30, 60, and 120 dataset units
- Absolute predicted-probability differences relative to no delay
- Odds ratio per meaningful delay increment if a linear form is adequate
- Global likelihood-ratio statistic for nonlinear spline terms when used
- Adjusted and unadjusted effects with 95% confidence intervals
- McFadden pseudo-R² and calibration summary as descriptive model metrics

#### Sensitivity analyses

- Repeat using categorical delay bands.
- Repeat after winsorizing delay only in a separate sensitivity feature at a prespecified percentile; never overwrite the original delay.
- Compare raw-delay, `log1p(delay)`, and spline shapes.
- For arrival delay, include a Missing category in the banded model and compare it with complete-case results.
- Run a joint departure-and-arrival model only after checking their correlation and multicollinearity.
- Repeat adjusted analyses within travel class or travel purpose if subgroup sizes are adequate.


## Planned outputs after approval

For each hypothesis, the analysis notebook or report will include:

1. Final analysis sample and exclusion flow
2. Required assumption and diagnostic checks
3. Primary test result
4. Effect sizes with 95% confidence intervals
5. Adjusted analysis
6. Prespecified sensitivity analyses
7. Plain-language decision about the null hypothesis
8. Practical interpretation and limitations

No test will be run until this plan is approved.

