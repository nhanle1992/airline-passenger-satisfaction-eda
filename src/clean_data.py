"""Create an analysis-ready cleaned dataset without overwriting source data."""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from statistics import mean


RATING_COLUMNS = [
    "time_convenience_rating",
    "online_booking_rating",
    "checkin_service_rating",
    "online_boarding_rating",
    "gate_location_rating",
    "onboard_service_rating",
    "seat_comfort_rating",
    "legroom_rating",
    "cleanliness_rating",
    "food_drink_rating",
    "inflight_service_rating",
    "inflight_wifi_rating",
    "inflight_entertainment_rating",
    "baggage_handling_rating",
]

SCORE_GROUPS = {
    "core_service_score_clean": [
        "cleanliness_rating",
        "seat_comfort_rating",
        "onboard_service_rating",
    ],
    "comfort_score_clean": [
        "seat_comfort_rating",
        "legroom_rating",
        "cleanliness_rating",
    ],
    "digital_experience_score_clean": [
        "online_booking_rating",
        "online_boarding_rating",
        "inflight_wifi_rating",
    ],
    "airport_experience_score_clean": [
        "time_convenience_rating",
        "online_booking_rating",
        "checkin_service_rating",
        "online_boarding_rating",
        "gate_location_rating",
    ],
    "onboard_experience_score_clean": [
        "onboard_service_rating",
        "seat_comfort_rating",
        "legroom_rating",
        "cleanliness_rating",
        "food_drink_rating",
        "inflight_service_rating",
        "inflight_wifi_rating",
        "inflight_entertainment_rating",
    ],
    "overall_service_score_clean": RATING_COLUMNS,
}

NEW_COLUMNS = (
    [f"{column}_clean" for column in RATING_COLUMNS]
    + list(SCORE_GROUPS)
    + [
        "core_service_valid_rating_count",
        "overall_service_valid_rating_count",
        "arrival_delay_missing",
        "extreme_delay_over_180",
        "extreme_delay_over_720",
        "passenger_segment_sample_size",
        "passenger_segment_reporting_eligible",
    ]
)


def clean_score(row: dict[str, str], columns: list[str]) -> str:
    values = [int(row[column]) for column in columns if int(row[column]) != 0]
    return f"{mean(values):.3f}" if values else ""


def segment_counts(input_path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    with input_path.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            counts[row["passenger_segment"]] += 1
    return counts


def clean(input_path: Path, output_path: Path, minimum_segment_size: int = 30) -> int:
    counts = segment_counts(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records = 0

    with input_path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        required = set(RATING_COLUMNS) | {
            "passenger_id",
            "arrival_delay",
            "departure_delay",
            "passenger_segment",
        }
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")

        output_columns = list(reader.fieldnames or []) + NEW_COLUMNS
        with output_path.open("w", newline="", encoding="utf-8") as destination:
            writer = csv.DictWriter(destination, fieldnames=output_columns)
            writer.writeheader()

            for row in reader:
                for column in RATING_COLUMNS:
                    value = int(row[column])
                    row[f"{column}_clean"] = "" if value == 0 else value

                for score_name, columns in SCORE_GROUPS.items():
                    row[score_name] = clean_score(row, columns)

                core_columns = SCORE_GROUPS["core_service_score_clean"]
                row["core_service_valid_rating_count"] = sum(
                    int(row[column]) != 0 for column in core_columns
                )
                row["overall_service_valid_rating_count"] = sum(
                    int(row[column]) != 0 for column in RATING_COLUMNS
                )

                arrival = None if row["arrival_delay"] == "" else int(row["arrival_delay"])
                departure = int(row["departure_delay"])
                available_delays = [departure] + ([] if arrival is None else [arrival])
                row["arrival_delay_missing"] = int(arrival is None)
                row["extreme_delay_over_180"] = int(max(available_delays) > 180)
                row["extreme_delay_over_720"] = int(max(available_delays) > 720)

                segment_size = counts[row["passenger_segment"]]
                row["passenger_segment_sample_size"] = segment_size
                row["passenger_segment_reporting_eligible"] = int(
                    segment_size >= minimum_segment_size
                )

                writer.writerow(row)
                records += 1

    return records


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root
        / "data/processed/airline_passenger_satisfaction_prepared.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root
        / "data/processed/airline_passenger_satisfaction_cleaned.csv",
    )
    parser.add_argument("--minimum-segment-size", type=int, default=30)
    args = parser.parse_args()

    records = clean(args.input, args.output, args.minimum_segment_size)
    print(f"Cleaned {records:,} rows: {args.output}")


if __name__ == "__main__":
    main()

