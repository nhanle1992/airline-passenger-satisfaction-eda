# Problem Definition: Airline Passenger Satisfaction

## 1. Business Context

Airlines operate in a highly competitive market where passenger experience can influence customer loyalty, repeat bookings, brand reputation, and revenue. Understanding which aspects of a journey have the strongest relationship with satisfaction can help an airline prioritize service improvements and allocate resources effectively.

This project uses survey responses from more than 120,000 airline passengers. The dataset includes passenger characteristics, flight and travel information, and evaluations of service factors such as cleanliness, comfort, onboard service, and the overall travel experience.

## 2. Project Objective

The objective is to analyze the factors associated with overall passenger satisfaction and identify meaningful differences among passenger and travel segments. The analysis will provide evidence-based insights that help the airline:

- Identify the service attributes most strongly associated with satisfaction.
- Detect passenger or journey segments with comparatively low satisfaction.
- Prioritize improvements that could produce the greatest increase in passenger satisfaction.

This exploratory analysis will identify associations and patterns; it will not establish causation without additional experimental or longitudinal evidence.

## 3. Key Performance Indicators (KPIs)

### KPI 1: Overall Satisfaction Rate

The percentage of surveyed passengers whose overall outcome is classified as satisfied.

**Formula:**

```text
Overall Satisfaction Rate = Satisfied Passengers / Total Surveyed Passengers × 100
```

### KPI 2: Average Service Experience Score

The mean rating across selected service dimensions, such as cleanliness, seat comfort, onboard service, food and drink, and inflight entertainment. Individual dimension scores should also be reported so that weak service areas are not hidden by the combined average.

**Formula:**

```text
Average Service Experience Score = Sum of Valid Service Ratings / Number of Valid Ratings
```

### KPI 3: Satisfaction Gap by Passenger or Travel Segment

The difference in satisfaction rate between relevant segments, such as loyal and disloyal customers, business and personal travelers, or travel classes.

**Formula:**

```text
Satisfaction Gap = Highest Segment Satisfaction Rate − Lowest Segment Satisfaction Rate
```

## 4. Key Hypotheses

### Hypothesis 1: Service Quality and Satisfaction

Passengers who give higher ratings for cleanliness, seat comfort, and onboard service are more likely to report overall satisfaction than passengers who give lower ratings.

- **Null hypothesis (H0):** Service-quality ratings are not associated with overall passenger satisfaction.
- **Alternative hypothesis (H1):** Higher service-quality ratings are associated with higher overall passenger satisfaction.

### Hypothesis 2: Travel Class and Satisfaction

Passengers traveling in business class have a higher satisfaction rate than passengers traveling in economy or economy-plus class.

- **Null hypothesis (H0):** Overall satisfaction does not differ by travel class.
- **Alternative hypothesis (H1):** Overall satisfaction differs by travel class, with business-class passengers showing a higher satisfaction rate.

### Hypothesis 3: Flight Delays and Satisfaction

Passengers experiencing longer departure or arrival delays have a lower satisfaction rate than passengers experiencing short or no delays.

- **Null hypothesis (H0):** Flight delay duration is not associated with overall passenger satisfaction.
- **Alternative hypothesis (H1):** Longer flight delays are associated with lower overall passenger satisfaction.

