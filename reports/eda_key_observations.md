# Airline Passenger Satisfaction: EDA Key Observations

## The story in brief

The analysis describes 129,880 passenger survey records and reveals an experience that is divided rather than broadly positive. Only 43.4% of passengers are classified as satisfied, while 56.6% are neutral or dissatisfied. Service evaluations, travel class, travel purpose, customer status, and flight delays all help explain where that divide appears in the observed data. At the same time, the multivariable views show that these factors do not operate in isolation: the apparent advantage associated with one variable often changes substantially when the passenger's broader travel context is considered.

These findings are descriptive. They identify patterns and priorities for formal testing, but they do not establish statistical significance or causation.

## A sample dominated by returning and business travelers

The typical passenger in the dataset is middle-aged, with a median age of 40. The recorded gender distribution is nearly balanced: 50.7% Female and 49.3% Male. The largest age group is 35–44, representing 23.2% of passengers, followed by ages 45–54 at 20.7% and ages 25–34 at 19.0%.

The sample is less balanced in its travel characteristics. Returning customers account for 81.7% of all records, and 69.1% of passengers report traveling for business. Business class represents 47.9% of the sample, Economy 44.9%, and Economy Plus only 7.2%. Flight distances are spread reasonably broadly: 31.0% are in the analyst-defined short-distance band, 38.7% are medium distance, and 30.3% are long distance. The median distance is 844 dataset units.

This composition matters throughout the analysis. Because returning customers and business travelers are heavily represented, an overall percentage can conceal very different experiences among smaller groups such as first-time or personal-travel passengers.

## The service experience has clear strengths and weaknesses

Among the cleaned service measures, inflight service receives the highest average rating at 3.64 out of 5, closely followed by baggage handling at 3.63. Seat comfort is also among the stronger measures at 3.44. At the opposite end, inflight Wi-Fi has the lowest clean average at 2.81, followed by online booking at 2.88 and gate location at 2.98. These results point to a contrast between relatively stronger human or operational service and weaker digital-service experiences.

The three services selected for the first hypothesis—cleanliness, seat comfort, and onboard service—show clear descriptive relationships with overall satisfaction. Satisfaction rises from 19.7% at a cleanliness rating of 1 to 61.2% at a rating of 5. For onboard service, it rises from 19.7% at rating 1 to 64.6% at rating 5. Seat comfort has a less even pattern at ratings 1–3, where satisfaction remains around 21%–23%, before increasing to 56.0% at rating 4 and 65.1% at rating 5.

The combined core-service score tells the same broad story. Neutral or dissatisfied passengers have an average core-service score of 3.00 and a median of 3.0, while satisfied passengers average 3.86 with a median of 4.0. In other words, the outcome groups occupy noticeably different parts of the service-quality distribution, although formal testing is still required to determine how robust that separation is.

## Service quality remains relevant within subgroups, but context changes its magnitude

The multivariable analysis shows that higher core-service bands correspond with higher observed satisfaction within every travel class, but the levels and size of the increase differ sharply. Among Business-class passengers, satisfaction increases from 18.5% in the lowest core-service band to 92.6% in the highest. Economy rises from 10.0% to 27.9%, while Economy Plus rises from 8.2% to 40.7%.

Individual service plots reinforce this result. For example, at a cleanliness rating of 5, satisfaction is 89.3% in Business class, compared with 42.2% in Economy Plus and 26.9% in Economy. At an onboard-service rating of 5, the corresponding rates are 88.6%, 34.8%, and 26.0%. Higher service ratings align with better satisfaction across classes, but the same rating does not correspond with the same outcome rate in every class.

Customer status also changes the core-service pattern. In the highest core-service band, 77.5% of returning customers are satisfied, compared with 31.3% of first-time customers. The difference is much smaller in the lower bands. This suggests that passenger history or other characteristics associated with returning status may be important when the service hypothesis is eventually tested.

## Travel class appears important, but it is inseparable from travel context in the descriptive data

The pooled class comparison is striking. Business-class passengers have a satisfaction rate of 69.4%, compared with 24.6% for Economy Plus and 18.8% for Economy. Viewed alone, this makes class look like one of the strongest separators in the dataset.

The multivariable plots show why this result needs careful interpretation. Within Business class, the observed satisfaction rate is 72.0% for business-purpose travelers but only 11.7% for personal travelers. Within Economy, the equivalent rates are 29.9% and 10.2%; within Economy Plus, they are 39.3% and 8.7%. Travel purpose therefore separates satisfaction sharply within every cabin class.

Customer status produces another divide. Returning Business-class passengers have a satisfaction rate of 74.6%, compared with 39.7% among first-time Business-class passengers. Returning passengers also have higher observed satisfaction in Economy—20.1% versus 14.4%—and in Economy Plus—26.4% versus 8.0%.

The cohesive message is not simply that Business class performs better. Business class is heavily associated with business travel and returning customers, both of which have their own distinct satisfaction profiles. Any later hypothesis test should therefore distinguish the unadjusted class difference from a comparison that accounts for these observed contextual variables.

## Delays correspond with a weaker passenger experience

More than half of passengers—56.5%—have no recorded departure delay. Delay distributions are strongly right-skewed: most values are small, but 1,457 records have a departure or arrival delay above 180 dataset units, and 19 exceed 720. These severe disruptions were retained because their paired departure and arrival values appear internally plausible rather than obviously erroneous.

The descriptive relationship between delay and satisfaction is consistent in the broad bands. Passengers with no departure delay have a satisfaction rate of 45.9%, compared with 43.5% for short delays, 37.5% for moderate delays, and 35.9% for long delays. The arrival-delay pattern is similar: satisfaction is 47.4% with no delay, 41.2% with a short delay, 35.9% with a moderate delay, and 35.6% with a long delay. Satisfied passengers also have lower average departure and arrival delays—12.51 and 12.53—than neutral or dissatisfied passengers, whose averages are 16.41 and 17.06.

The multivariable views indicate that the delay pattern is present within travel classes, although baseline satisfaction remains very different between classes. In Business class, satisfaction falls from 71.5% with no departure delay to 61.7% with a long delay. Economy falls from 21.6% to 13.8%, while Economy Plus falls from 29.1% to 17.0%. Arrival delays produce a comparable pattern.

Travel purpose again separates the groups. With no departure delay, business-purpose travelers have a satisfaction rate of 61.1%, compared with 12.2% for personal travelers. Under a long delay, the rates fall to 49.4% and 4.5%. Thus, delays align with lower satisfaction within both purposes, but they do not erase the much larger baseline difference between business and personal travel.

## Returning-customer status provides a useful proxy, not a true retention measure

Because the dataset contains no customer history, dates, or repeated customer identifiers, it cannot calculate cohort retention such as the percentage of first-month passengers who return later. The closest available indicator is the source field distinguishing Returning from First-time customers.

Using that proxy, returning customers make up 89.9% of satisfied passengers and 75.4% of neutral or dissatisfied passengers, a descriptive gap of 14.5 percentage points. Service-level plots add nuance. Satisfied passengers with cleanliness ratings of 3–5 have returning-customer shares above 91%. For seat comfort ratings of 4–5, the returning share is approximately 94.7% among satisfied passengers, compared with 79.0% and 69.1% among neutral or dissatisfied passengers. For onboard service, satisfied passengers have a higher returning share at every rating level, although neither group's share increases consistently at every step.

These figures describe the composition of the surveyed groups. They do not show that satisfaction or service quality caused a customer to return, nor do they measure conversion from first-time to returning status.

## Data-quality context

The cleaned data is structurally strong: all 129,880 passenger IDs are unique, no complete duplicate rows were found, categorical labels are consistent, and all engineered features reproduce their source values correctly. Only 393 arrival delays—0.30% of the sample—are missing. These records were retained and flagged rather than imputed.

The original data also contains undocumented zero service ratings. Clean analysis fields treat those zeros as missing while preserving the original values for sensitivity checks. This issue has little direct effect on the first service hypothesis because cleanliness, seat comfort, and onboard service contain only 20 zero values combined. It is more important for optional and digital services such as Wi-Fi, online booking, and time convenience.

The source does not document the units for distance and delay or the precise meaning of rating zero. City and device information are also unavailable. These limitations should remain visible in any final report.

## What the full analysis suggests

Taken together, the exploratory analyses point to three central observations. First, service quality—particularly stronger cleanliness, seat comfort, and onboard service evaluations—aligns with higher satisfaction, but the strength of that pattern varies across travel classes and customer types. Second, Business class has a much higher overall satisfaction rate, yet much of the descriptive landscape also depends on travel purpose and whether the passenger is returning or first-time. Third, longer delays align with lower satisfaction across classes and travel purposes, even though the underlying satisfaction level remains strongly shaped by passenger context.

The practical implication is that the airline should avoid treating satisfaction as the product of a single service feature. Digital-service weaknesses, cabin experience, travel purpose, customer history, and disruption all form part of the observed story. The next stage of formal hypothesis testing should evaluate the three proposed relationships while accounting for these overlapping factors, checking nonlinear delay effects, preserving transparent treatment of missing and zero values, and reporting adjusted results separately from the descriptive comparisons presented here.

