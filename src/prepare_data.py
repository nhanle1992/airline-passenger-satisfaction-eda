"""Prepare the airline passenger survey for EDA and hypothesis testing.

This script uses only Python's standard library so the preparation step can be
run before optional analysis packages are installed.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean


RAW_TO_CLEAN = {
    "ID": "passenger_id",
    "Gender": "gender",
    "Age": "age",
    "Customer Type": "customer_type",
    "Type of Travel": "travel_type",
    "Class": "travel_class",
    "Flight Distance": "flight_distance",
    "Departure Delay": "departure_delay",
    "Arrival Delay": "arrival_delay",
    "Departure and Arrival Time Convenience": "time_convenience_rating",
    "Ease of Online Booking": "online_booking_rating",
    "Check-in Service": "checkin_service_rating",
    "Online Boarding": "online_boarding_rating",
    "Gate Location": "gate_location_rating",
    "On-board Service": "onboard_service_rating",
    "Seat Comfort": "seat_comfort_rating",
    "Leg Room Service": "legroom_rating",
    "Cleanliness": "cleanliness_rating",
    "Food and Drink": "food_drink_rating",
    "In-flight Service": "inflight_service_rating",
    "In-flight Wifi Service": "inflight_wifi_rating",
    "In-flight Entertainment": "inflight_entertainment_rating",
    "Baggage Handling": "baggage_handling_rating",
    "Satisfaction": "satisfaction",
}

INTEGER_COLUMNS = {
    "passenger_id",
    "age",
    "flight_distance",
    "departure_delay",
    "arrival_delay",
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
}

SERVICE_RATINGS = [
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

CORE_SERVICE_RATINGS = [
    "cleanliness_rating",
    "seat_comfort_rating",
    "onboard_service_rating",
]

COMFORT_RATINGS = [
    "seat_comfort_rating",
    "legroom_rating",
    "cleanliness_rating",
]

DIGITAL_RATINGS = [
    "online_booking_rating",
    "online_boarding_rating",
    "inflight_wifi_rating",
]

AIRPORT_RATINGS = [
    "time_convenience_rating",
    "online_booking_rating",
    "checkin_service_rating",
    "online_boarding_rating",
    "gate_location_rating",
]

ONBOARD_RATINGS = [
    "onboard_service_rating",
    "seat_comfort_rating",
    "legroom_rating",
    "cleanliness_rating",
    "food_drink_rating",
    "inflight_service_rating",
    "inflight_wifi_rating",
    "inflight_entertainment_rating",
]

ENGINEERED_COLUMNS = [
    "is_satisfied",
    "age_group",
    "flight_distance_band",
    "departure_delay_band",
    "arrival_delay_band",
    "any_departure_delay",
    "any_arrival_delay",
    "total_delay",
    "delay_change",
    "core_service_score",
    "core_service_score_nonzero",
    "comfort_score",
    "digital_experience_score",
    "airport_experience_score",
    "onboard_experience_score",
    "overall_service_score",
    "overall_service_score_nonzero",
    "zero_service_rating_count",
    "passenger_segment",
]


def parse_integer(value: str, column: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Invalid integer in {column}: {value!r}") from exc


def age_group(age: int) -> str:
    if age < 18:
        return "Under 18"
    if age <= 24:
        return "18-24"
    if age <= 34:
        return "25-34"
    if age <= 44:
        return "35-44"
    if age <= 54:
        return "45-54"
    if age <= 64:
        return "55-64"
    return "65+"


def distance_band(distance: int) -> str:
    if distance <= 500:
        return "Short (<=500)"
    if distance <= 1500:
        return "Medium (501-1500)"
    return "Long (>1500)"


def delay_band(delay: int | None) -> str:
    if delay is None:
        return "Missing"
    if delay == 0:
        return "No delay"
    if delay <= 15:
        return "Short (1-15)"
    if delay <= 60:
        return "Moderate (16-60)"
    return "Long (>60)"


def score(row: dict[str, object], columns: list[str], exclude_zero: bool = False) -> str:
    values = [row[column] for column in columns]
    numeric = [value for value in values if isinstance(value, int)]
    if exclude_zero:
        numeric = [value for value in numeric if value != 0]
    return f"{mean(numeric):.3f}" if numeric else ""


def prepare_row(raw_row: dict[str, str]) -> dict[str, object]:
    row: dict[str, object] = {}
    for raw_name, clean_name in RAW_TO_CLEAN.items():
        value = raw_row[raw_name].strip()
        row[clean_name] = parse_integer(value, clean_name) if clean_name in INTEGER_COLUMNS else value

    satisfaction = row["satisfaction"]
    if satisfaction not in {"Satisfied", "Neutral or Dissatisfied"}:
        raise ValueError(f"Unexpected satisfaction value: {satisfaction!r}")

    for column in SERVICE_RATINGS:
        value = row[column]
        if not isinstance(value, int) or not 0 <= value <= 5:
            raise ValueError(f"Rating outside 0-5 in {column}: {value!r}")

    age = row["age"]
    distance = row["flight_distance"]
    departure = row["departure_delay"]
    arrival = row["arrival_delay"]
    assert isinstance(age, int)
    assert isinstance(distance, int)
    assert isinstance(departure, int)
    assert arrival is None or isinstance(arrival, int)

    row["is_satisfied"] = 1 if satisfaction == "Satisfied" else 0
    row["age_group"] = age_group(age)
    row["flight_distance_band"] = distance_band(distance)
    row["departure_delay_band"] = delay_band(departure)
    row["arrival_delay_band"] = delay_band(arrival)
    row["any_departure_delay"] = 1 if departure > 0 else 0
    row["any_arrival_delay"] = "" if arrival is None else (1 if arrival > 0 else 0)
    row["total_delay"] = "" if arrival is None else departure + arrival
    row["delay_change"] = "" if arrival is None else arrival - departure
    row["core_service_score"] = score(row, CORE_SERVICE_RATINGS)
    row["core_service_score_nonzero"] = score(row, CORE_SERVICE_RATINGS, exclude_zero=True)
    row["comfort_score"] = score(row, COMFORT_RATINGS)
    row["digital_experience_score"] = score(row, DIGITAL_RATINGS)
    row["airport_experience_score"] = score(row, AIRPORT_RATINGS)
    row["onboard_experience_score"] = score(row, ONBOARD_RATINGS)
    row["overall_service_score"] = score(row, SERVICE_RATINGS)
    row["overall_service_score_nonzero"] = score(row, SERVICE_RATINGS, exclude_zero=True)
    row["zero_service_rating_count"] = sum(row[column] == 0 for column in SERVICE_RATINGS)
    row["passenger_segment"] = " | ".join(
        [str(row["customer_type"]), str(row["travel_type"]), str(row["travel_class"])]
    )

    # CSV represents missing values as empty strings rather than the word None.
    return {column: "" if value is None else value for column, value in row.items()}


def prepare(input_path: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    seen_ids: set[int] = set()

    with input_path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        missing_columns = set(RAW_TO_CLEAN) - set(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

        output_columns = list(RAW_TO_CLEAN.values()) + ENGINEERED_COLUMNS
        with output_path.open("w", newline="", encoding="utf-8") as destination:
            writer = csv.DictWriter(destination, fieldnames=output_columns)
            writer.writeheader()
            for raw_row in reader:
                prepared = prepare_row(raw_row)
                passenger_id = int(prepared["passenger_id"])
                if passenger_id in seen_ids:
                    raise ValueError(f"Duplicate passenger_id: {passenger_id}")
                seen_ids.add(passenger_id)
                writer.writerow(prepared)
                count += 1

    return count


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root / "data/raw/airline_passenger_satisfaction.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "data/processed/airline_passenger_satisfaction_prepared.csv",
    )
    args = parser.parse_args()
    count = prepare(args.input, args.output)
    print(f"Prepared {count:,} rows: {args.output}")


if __name__ == "__main__":
    main()

