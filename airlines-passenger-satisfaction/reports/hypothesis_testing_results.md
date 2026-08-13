# Airline Passenger Satisfaction: Hypothesis-Testing Results

## Executive conclusion

At α = 0.05, the null hypothesis was rejected for all three planned areas:

- Cleanliness, seat comfort, and onboard service are jointly associated with overall satisfaction.
- Satisfaction differs by travel class, with Business class showing a substantially higher observed rate than Economy and Economy Plus.
- Departure and arrival delay are each associated with satisfaction, but the relationship is nonlinear rather than a constant decline at every additional unit of delay.

These are statistical associations in cross-sectional survey data. They do not establish that service ratings, class, or delays caused the reported outcome.

## Analysis safeguards

- Outcome: `is_satisfied`, where 1 = Satisfied and 0 = Neutral or Dissatisfied
- Significance level: 0.05
- Confidence level: 95%
- Departure and arrival delay correlation: 0.965
- Because the two delay measures are highly correlated, they were tested separately and were not entered together in the primary adjusted models.
- Holm correction was applied to planned comparison families.
- All reported models converged, showed no fitted probabilities indicative of complete separation, and produced acceptable deviance-to-residual-degree-of-freedom summaries.
- Effect sizes and predicted probabilities are emphasized because the large sample can make small associations statistically significant.

## Hypothesis 1: Service quality and satisfaction

### Primary result

The primary categorical logistic model included cleanliness, seat comfort, and onboard-service ratings and used 129,861 records. Nineteen records were excluded because a zero rating in at least one of these fields was treated as missing in the clean analysis variables.

The joint likelihood-ratio test rejected the null hypothesis:

- Likelihood-ratio statistic: 33,591.61
- Degrees of freedom: 12
- p-value: < 1 × 10⁻³⁰⁰
- Decision: Reject H0

Holm-adjusted service-level likelihood-ratio tests also rejected the separate null hypothesis for each service. The contribution was largest for onboard service, followed by seat comfort and cleanliness:

| Service | LR statistic | df | Holm-adjusted p-value |
|---|---:|---:|---:|
| Cleanliness | 1,887.33 | 4 | < 1 × 10⁻³⁰⁰ |
| Seat comfort | 7,327.84 | 4 | < 1 × 10⁻³⁰⁰ |
| Onboard service | 10,713.00 | 4 | < 1 × 10⁻³⁰⁰ |

### Effect sizes and direction

In the adjusted ordered-trend model, each one-point increase in rating was associated with:

| Service | Adjusted odds ratio | 95% CI |
|---|---:|---:|
| Cleanliness | 1.44 | 1.42–1.46 |
| Seat comfort | 1.32 | 1.29–1.34 |
| Onboard service | 1.82 | 1.79–1.84 |

Holding the other two service-rating distributions constant in the unadjusted categorical model, standardized satisfaction probability increased from 23.0% at onboard-service rating 1 to 59.9% at rating 5. For seat comfort it increased from 32.1% at rating 1 to 57.3% at rating 5, with a dip at rating 3. Cleanliness increased overall from 30.2% at rating 1 to 47.9% at rating 5, although the adjusted categorical pattern was not strictly monotonic at every step.

The adjusted joint service test remained highly significant after accounting for age, gender, customer type, travel purpose, travel class, flight distance, and departure delay:

- Adjusted LR statistic: 23,777.72
- Degrees of freedom: 12
- p-value: < 1 × 10⁻³⁰⁰

### Sensitivity checks

The conclusion was unchanged when:

- Original zero-inclusive ratings were used.
- The clean core-service composite score was used.
- Arrival delay replaced departure delay in the adjusted model.

### Interpretation

The evidence supports an association between better service evaluations and greater odds of satisfaction. Onboard service has the largest adjusted one-point association among the three measures. The categorical results also show that the relationship is not perfectly linear, so individual rating levels should remain visible alongside the summarized trend.

## Hypothesis 2: Travel class and satisfaction

### Primary result

The Pearson chi-square test used all 129,880 records. The minimum expected cell count was 4,088.7, comfortably satisfying the large-sample count assumption.

- Chi-square statistic: 32,906.17
- Degrees of freedom: 2
- p-value: < 1 × 10⁻³⁰⁰
- Cramér's V: 0.503
- Decision: Reject H0

Cramér's V of 0.503 indicates a substantial association between class and satisfaction in this sample.

### Planned class contrasts

| Comparison | Business rate | Comparison rate | Absolute difference | 95% CI for difference | Holm-adjusted p-value |
|---|---:|---:|---:|---:|---:|
| Business vs Economy | 69.4% | 18.8% | 50.7 points | 50.2–51.2 points | < 1 × 10⁻³⁰⁰ |
| Business vs Economy Plus | 69.4% | 24.6% | 44.8 points | 43.8–45.7 points | < 1 × 10⁻³⁰⁰ |

Both planned contrasts reject their null hypotheses after Holm correction.

### Adjusted result

After adjustment for age, gender, customer type, travel purpose, flight distance, and departure delay, the global class term remained associated with satisfaction:

- Adjusted LR statistic: 6,023.56
- Degrees of freedom: 2
- p-value: < 1 × 10⁻³⁰⁰

Relative to Business class, adjusted satisfaction odds were lower for:

- Economy: OR 0.28, 95% CI 0.27–0.29
- Economy Plus: OR 0.24, 95% CI 0.23–0.26

Standardized adjusted satisfaction probabilities were:

- Business: 54.4% (95% CI 54.0%–54.9%)
- Economy: 30.9% (95% CI 30.4%–31.3%)
- Economy Plus: 28.4% (95% CI 27.5%–29.3%)

The adjusted class ordering differs slightly from the unadjusted Economy and Economy Plus ordering, demonstrating that passenger and travel composition affects the raw comparison. Business remains clearly higher in both analyses.

### Sensitivity and subgroup checks

- Replacing departure delay with arrival delay did not change the class conclusion.
- Global class differences remained significant within Business travel, Personal travel, Returning customers, and First-time customers.
- The Personal-travel subgroup had the smallest—but still statistically significant—global class association (χ² = 17.07, df = 2, p = 0.000196).

### Interpretation

Business-class passengers have a materially higher satisfaction rate than both comparison classes. The difference remains after observed passenger and travel characteristics are considered. Nevertheless, class is not randomly assigned, and unmeasured differences such as fare, route, aircraft, loyalty tier, or upgrade status may still explain part of the association.

## Hypothesis 3: Flight delays and satisfaction

### Functional-form check

The nonlinear spline form fit better than a single linear-delay term for both exposures:

| Exposure | Nonlinearity LR | df | p-value |
|---|---:|---:|---:|
| Departure delay | 365.28 | 3 | 7.32 × 10⁻⁷⁹ |
| Arrival delay | 910.52 | 3 | 4.63 × 10⁻¹⁹⁷ |

Natural cubic splines were therefore retained. This means a single odds ratio per delay unit would be an inadequate primary summary.

### Primary results

| Exposure | Analysis N | LR statistic | df | Holm-adjusted p-value | Decision |
|---|---:|---:|---:|---:|---|
| Departure delay | 129,880 | 721.82 | 4 | 6.58 × 10⁻¹⁵⁵ | Reject H0 |
| Arrival delay | 129,487 | 1,384.49 | 4 | 3.18 × 10⁻²⁹⁸ | Reject H0 |

The arrival-delay analysis excludes the 393 records with missing arrival delay; no values were imputed.

### Predicted-probability effects

Unadjusted spline estimates show:

| Delay | Departure satisfaction | Difference from 0 | Arrival satisfaction | Difference from 0 |
|---:|---:|---:|---:|---:|
| 0 | 45.9% | — | 47.2% | — |
| 15 | 40.4% | −5.5 points | 37.7% | −9.5 points |
| 30 | 37.3% | −8.6 points | 33.5% | −13.6 points |
| 60 | 35.8% | −10.1 points | 34.7% | −12.5 points |
| 120 | 35.8% | −10.2 points | 37.7% | −9.5 points |

Adjusted results were similar. Compared with zero delay, standardized satisfaction probability was approximately 9.7 percentage points lower at 60 units of departure delay and 11.6 points lower at 60 units of arrival delay.

The estimated relationship drops sharply at lower-to-moderate delays and then flattens or rebounds somewhat at longer values. Therefore, the evidence supports lower satisfaction among delayed passengers, but it does **not** support the stronger claim that every additional delay unit always produces a further decline.

### Delay-band effect sizes

Relative to no delay, unadjusted satisfaction odds were:

| Delay band | Departure OR (95% CI) | Arrival OR (95% CI) |
|---|---:|---:|
| Short (1–15) | 0.91 (0.88–0.93) | 0.78 (0.76–0.80) |
| Moderate (16–60) | 0.71 (0.68–0.73) | 0.62 (0.60–0.64) |
| Long (>60) | 0.66 (0.63–0.69) | 0.61 (0.59–0.64) |

### Sensitivity checks

The delay conclusion remained statistically significant when:

- Delay was represented using `log1p(delay)`.
- Values above the 99th percentile were winsorized in a separate sensitivity feature.
- Passenger and travel characteristics were added to adjusted spline models.

The missing-arrival-delay category had lower odds of satisfaction than the no-delay group (OR 0.81, 95% CI 0.66–0.99, p = 0.041), reinforcing the decision not to assume that those records were missing completely at random.

### Interpretation

Both departure and arrival delays are associated with satisfaction, and passengers with delays generally have lower predicted satisfaction than those with no delay. Arrival delay shows a larger probability difference at common operational thresholds. The nonlinearity suggests that preventing or quickly resolving early delay accumulation may matter more than assuming a constant effect per minute or dataset unit.

## Final decision table

| Hypothesis | Decision | Practical conclusion |
|---|---|---|
| H1: Service quality | Reject H0 | Better cleanliness, seat comfort, and especially onboard-service ratings are associated with higher satisfaction. |
| H2: Travel class | Reject H0 | Business class has a substantially higher satisfaction rate than Economy and Economy Plus, before and after observed adjustment. |
| H3: Flight delays | Reject H0 for departure and arrival delay | Delays are associated with lower satisfaction, but the relationship is nonlinear and should not be summarized as a constant decline per unit. |

## Limitations

- The analysis is observational and cannot establish causation.
- Neutral and dissatisfied outcomes are combined.
- Route, fare, aircraft, airline, loyalty tier, upgrade status, delay cause, and compensation are unavailable.
- Ratings and overall satisfaction come from the same survey and may share response bias.
- Distance and delay units are undocumented in the source.
- Adjusted models address observed variables only and cannot remove unmeasured confounding.

