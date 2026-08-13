# Data Cleaning Validation Report

## Result

The approved cleaning plan was applied to a new file: `data/processed/airline_passenger_satisfaction_cleaned.csv`. The prepared dataset remains unchanged.

## Preservation checks

| Validation | Result |
|---|---:|
| Input records | 129,880 |
| Output records | 129,880 |
| Unique output passenger IDs | 129,880 |
| Prepared columns preserved | 43 of 43 |
| Original field values changed | 0 |
| New cleaning and quality fields | 27 |
| Total output columns | 70 |

No records were deleted, duplicated, or imputed.

## Missing arrival delays

- All 393 missing `arrival_delay` values were retained.
- `arrival_delay_missing` equals 1 for exactly those 393 records.
- `any_arrival_delay`, `total_delay`, and `delay_change` remain missing for those same records.
- No synthetic arrival-delay values were created.

## Zero-rating treatment

Original rating fields were preserved. Each new `_clean` rating field treats an original zero as missing. The resulting missing counts exactly match the original zero counts:

| Clean rating field | Values treated as missing |
|---|---:|
| `time_convenience_rating_clean` | 6,681 |
| `online_booking_rating_clean` | 5,682 |
| `online_boarding_rating_clean` | 3,080 |
| `inflight_wifi_rating_clean` | 3,916 |
| `legroom_rating_clean` | 598 |
| `food_drink_rating_clean` | 132 |
| `inflight_entertainment_rating_clean` | 18 |
| `cleanliness_rating_clean` | 14 |
| `onboard_service_rating_clean` | 5 |
| `inflight_service_rating_clean` | 5 |
| `checkin_service_rating_clean` | 1 |
| `seat_comfort_rating_clean` | 1 |
| `gate_location_rating_clean` | 1 |
| `baggage_handling_rating_clean` | 0 |

Of the 129,880 records:

- 119,567 have all 14 valid nonzero ratings.
- 4,548 have 13 valid ratings.
- 2,452 have 12 valid ratings.
- 2,570 have 11 valid ratings.
- 743 have 10 valid ratings.

All clean composite scores fall within 1–5. The clean digital-experience score is missing for 1,603 records because all three contributing digital ratings are zero; this is intentional and is preferable to inventing a score.

## Delay flags

The original delay values were retained without capping:

- 1,457 records have a departure or arrival delay greater than 180.
- 19 records have a departure or arrival delay greater than 720.

These records can now be isolated for descriptive reporting and sensitivity analysis without removing them from the dataset.

## Sparse passenger segments

- 129,863 records belong to combined passenger segments containing at least 30 records.
- 17 records belong to two segments below the reporting threshold.
- The underlying records and categories were retained; `passenger_segment_reporting_eligible` controls only whether the combined segment should be reported independently.

## Recommended analysis fields

- Satisfaction outcome: `is_satisfied`
- Service-quality hypothesis: individual `_clean` ratings and `core_service_score_clean`
- Travel-class hypothesis: `travel_class` and `is_satisfied`
- Delay hypothesis: original delay fields, `arrival_delay_missing`, delay bands, and extreme-delay flags
- Overall descriptive service analysis: `overall_service_score_clean` with `overall_service_valid_rating_count`
- Sensitivity checks: compare clean scores with the original zero-inclusive scores

## Reproducibility

Run the following commands from the project directory to regenerate both datasets:

```bash
python3 src/prepare_data.py
python3 src/clean_data.py
```

