
# Data Dictionary

This document provides detailed information about road accident/s and its statistic in Israel. It outlines the structure, field names, data types, inferred descriptions, and sample values across multiple tables tracking monthly time-series metrics, accident severities, road types, temporal distributions, collision classifications, pedestrian involvement, and locality statistics.

---

## 1. `t01_01.xlsx`

The table contains annual road accident statistics in Israel spanning a 10-year period from 2016 to 2025. It categorizes total road accidents across three dimensions: calendar month (`January`–`December`), type of collision or incident (e.g., `Hitting a pedestrian`, `Front to side`, `Head-on`), and time of day (`Day` vs. `Night`).

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Category / Indicator (English)`  | String | English label describing the accident breakdown dimension or category (Month, Type of accident, or Time of accident). | `Hitting a pedestrian` |
| `2025`  | Integer | Total number of recorded road accidents for the given category in 2025. | `7717` |
| `2024`  | Integer | Total number of recorded road accidents for the given category in 2024. | `8315` |
| `2023`  | Integer | Total number of recorded road accidents for the given category in 2023. | `8832` |
| `2022`  | Integer | Total number of recorded road accidents for the given category in 2022. | `10404` |
| `2021`  | Integer | Total number of recorded road accidents for the given category in 2021. | `11554` |
| `2020`  | Integer | Total number of recorded road accidents for the given category in 2020. | `10836` |
| `2019`  | Integer | Total number of recorded road accidents for the given category in 2019. | `12670` |
| `2018`  | Integer | Total number of recorded road accidents for the given category in 2018. | `12596` |
| `2017`  | Integer | Total number of recorded road accidents for the given category in 2017. | `13628` |
| `2016`  | Integer | Total number of recorded road accidents for the given category in 2016. | `12966` |
| `Category / Indicator (Hebrew)`  | String | Hebrew label corresponding to the English accident breakdown dimension or category. | `פגיעה בהולך רגל` |

---

## 2. `t01_02.xlsx`

The table tracks annual road accidents in Israel categorized by road type (urban vs. non-urban, intersections vs. non-intersections) and accident severity (fatal, serious, slight) from 2016 to 2025.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Road Type and Severity (English)`  | String | English label describing the road type and/or accident severity category. | `Urban road` / `Fatal` / `At intersection` |
| `2025`  | Integer | Total number of recorded accidents for the category in 2025. | `4949` |
| `2024`  | Integer | Total number of recorded accidents for the category in 2024. | `5447` |
| `2023`  | Integer | Total number of recorded accidents for the category in 2023. | `5726` |
| `2022`  | Integer | Total number of recorded accidents for the category in 2022. | `6849` |
| `2021`  | Integer | Total number of recorded accidents for the category in 2021. | `7856` |
| `2020`  | Integer | Total number of recorded accidents for the category in 2020. | `7582` |
| `2019`  | Integer | Total number of recorded accidents for the category in 2019. | `8809` |
| `2018`  | Integer | Total number of recorded accidents for the category in 2018. | `8735` |
| `2017`  | Integer | Total number of recorded accidents for the category in 2017. | `9631` |
| `2016`  | Integer | Total number of recorded accidents for the category in 2016. | `9230` |
| `Road Type and Severity (Hebrew)`  | String | Hebrew label corresponding to the road type and severity category. | `דרך עירונית` / `קטלניות` / `בצומת` |

---

## 3. `t01_03.xlsx`

The table tracks road accidents in Israel by calendar month, accident severity (fatal, serious, slight), and day of the month (1st through 31st) for the year 2025.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Month and Severity / Indicator` (Col 1) | String | Description of the month, overall totals, or accident severity level (`All accidents`, `Fatal`, `Serious`, `Slight`, `January`, etc.). | `All accidents` / `January` / `Fatal` |
| `Day 31` | Integer / Float | Number of accidents occurring on the 31st day of the month for the given category. | `132.0` |
| `Day 30` | Integer / Float | Number of accidents occurring on the 30th day of the month for the given category. | `271.0` |
| `Day 29` | Integer / Float | Number of accidents occurring on the 29th day of the month for the given category. | `209.0` |
| `Day 28` | Integer / Float | Number of accidents occurring on the 28th day of the month for the given category. | `266.0` |
| `Day 27` | Integer / Float | Number of accidents occurring on the 27th day of the month for the given category. | `259.0` |
| `Day 26` | Integer / Float | Number of accidents occurring on the 26th day of the month for the given category. | `236.0` |
| `Day 25` | Integer / Float | Number of accidents occurring on the 25th day of the month for the given category. | `239.0` |
| `Day 24` | Integer / Float | Number of accidents occurring on the 24th day of the month for the given category. | `252.0` |
| `Day 23` | Integer / Float | Number of accidents occurring on the 23rd day of the month for the given category. | `250.0` |
| `Day 22` | Integer / Float | Number of accidents occurring on the 22nd day of the month for the given category. | `246.0` |
| `Day 21` | Integer / Float | Number of accidents occurring on the 21st day of the month for the given category. | `260.0` |
| `Day 20` | Integer / Float | Number of accidents occurring on the 20th day of the month for the given category. | `259.0` |
| `Day 19` | Integer / Float | Number of accidents occurring on the 19th day of the month for the given category. | `248.0` |
| `Day 18` | Integer / Float | Number of accidents occurring on the 18th day of the month for the given category. | `228.0` |
| `Day 17` | Integer / Float | Number of accidents occurring on the 17th day of the month for the given category. | `237.0` |
| `Day 16` | Integer / Float | Number of accidents occurring on the 16th day of the month for the given category. | `273.0` |
| `Day 15` | Integer / Float | Number of accidents occurring on the 15th day of the month for the given category. | `241.0` |
| `Day 14` | Integer / Float | Number of accidents occurring on the 14th day of the month for the given category. | `238.0` |
| `Day 13` | Integer / Float | Number of accidents occurring on the 13th day of the month for the given category. | `250.0` |
| `Day 12` | Integer / Float | Number of accidents occurring on the 12th day of the month for the given category. | `263.0` |
| `Day 11` | Integer / Float | Number of accidents occurring on the 11th day of the month for the given category. | `265.0` |
| `Day 10` | Integer / Float | Number of accidents occurring on the 10th day of the month for the given category. | `293.0` |
| `Day 9`  | Integer / Float | Number of accidents occurring on the 9th day of the month for the given category. | `270.0` |
| `Day 8`  | Integer / Float | Number of accidents occurring on the 8th day of the month for the given category. | `231.0` |
| `Day 7`  | Integer / Float | Number of accidents occurring on the 7th day of the month for the given category. | `264.0` |
| `Day 6`  | Integer / Float | Number of accidents occurring on the 6th day of the month for the given category. | `258.0` |
| `Day 5`  | Integer / Float | Number of accidents occurring on the 5th day of the month for the given category. | `233.0` |
| `Day 4`  | Integer / Float | Number of accidents occurring on the 4th day of the month for the given category. | `274.0` |
| `Day 3`  | Integer / Float | Number of accidents occurring on the 3rd day of the month for the given category. | `239.0` |
| `Day 2`  | Integer / Float | Number of accidents occurring on the 2nd day of the month for the given category. | `267.0` |
| `Day 1`  | Integer / Float | Number of accidents occurring on the 1st day of the month for the given category. | `266.0` |
| `Total`  | Integer / Float | Total annual sum of accidents for the category across all days in 2025. | `7717` |
| `Month and Severity` | String | Hebrew translation or equivalent label for the category/month. | `כל התאונות` / `ינואר` |

---

## `t01_04.xlsx`

The table tracks road accidents in Israel for the year 2025 broken down by road type (urban vs. non-urban), accident severity (fatal, serious, slight), and calendar month (December through January in reverse order).

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Road Type and Severity`  | String | Description of the road type and accident severity category (`All accidents`, `Fatal`, `Serious`, `Slight`, `Urban road`, etc.). | `All accidents` / `Urban road` / `Fatal` |
| `December` | Integer | Number of accidents occurring in December 2025 for the given category. | `503` |
| `November` | Integer | Number of accidents occurring in November 2025 for the given category. | `607` |
| `October`  | Integer | Number of accidents occurring in October 2025 for the given category. | `627` |
| `September`| Integer | Number of accidents occurring in September 2025 for the given category. | `655` |
| `August`  | Integer | Number of accidents occurring in August 2025 for the given category. | `636` |
| `July`    | Integer | Number of accidents occurring in July 2025 for the given category. | `662` |
| `June`    | Integer | Number of accidents occurring in June 2025 for the given category. | `602` |
| `May`     | Integer | Number of accidents occurring in May 2025 for the given category. | `742` |
| `April`   | Integer | Number of accidents occurring in April 2025 for the given category. | `670` |
| `March`   | Integer | Number of accidents occurring in March 2025 for the given category. | `761` |
| `February`| Integer | Number of accidents occurring in February 2025 for the given category. | `582` |
| `January` | Integer | Number of accidents occurring in January 2025 for the given category. | `670` |
| `Total`   | Integer | Total annual sum of accidents for the category across all months in 2025. | `7717` |
| `Road Type and Severity`  | String | Hebrew translation or equivalent label for the road type and severity category. | `כל התאונות` / `דרך עירונית` |

---

## 5. `t01_05.xlsx` 

The table tracks road accidents in Israel for the year 2025 broken down by road type, accident severity, and day of the week (including Saturday and holiday vs. weekdays), along with daily accident averages and yearly day counts.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Road Type and Severity`  | String | Description of the category (`All accidents`, `Fatal`, `Serious`, `Slight`, `Urban road`, `Average number of accidents per day`, etc.). | `All accidents` / `Urban road` / `Fatal` |
| `Saturday and Holiday`   | Integer / Float | Number of accidents or days for Saturday and holidays. | `810` |
| `Friday and Holiday Eve` | Integer / Float | Number of accidents or days for Friday and holiday eves. | `1127` |
| `Thursday`  | Integer / Float | Number of accidents or days for Thursdays. | `1143` |
| `Wednesday` | Integer / Float | Number of accidents or days for Wednesdays. | `1169` |
| `Tuesday`   | Integer / Float | Number of accidents or days for Tuesdays. | `1128` |
| `Monday`    | Integer / Float | Number of accidents or days for Mondays. | `1104` |
| `Sunday`    | Integer / Float | Number of accidents or days for Sundays. | `1236` |
| `Total`     | Integer / Float | Total annual sum across all days of the week in 2025. | `7717` |
| `Road Type and Severity` | String | Hebrew translation or equivalent label for the day of the week and category. | `כל התאונות` / `דרך עירונית` |

---

## 6. `t01_06.xlsx`

The table tracks road accidents in Israel for the year 2025 broken down by month, accident severity (fatal, serious, slight), and detailed type of accident (including pedestrian collisions, various collision sub-types, single vehicle accidents, and other types).

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Month and Severity`  | String | Description of the month or aggregate category and severity level (`All accidents`, `Fatal`, `Serious`, `Slight`, `January`, etc.). | `All accidents` / `January` / `Fatal` |
| `Other and not known` | Integer | Number of accidents classified as other or unknown type. | `117` |
| `Single vehicle - Falling from moving vehicle`   | Integer | Number of single vehicle accidents due to falling from a moving vehicle. | `41` |
| `Single vehicle - Injury to passenger in vehicle` | Integer | Number of single vehicle accidents involving injury to a passenger. | `69` |
| `Single vehicle - Skidding`    | Integer | Number of single vehicle accidents caused by skidding. | `260` |
| `Single vehicle - Overturning` | Integer | Number of single vehicle accidents involving overturning. | `197` |
| `Single vehicle - Running off road` | Integer | Number of single vehicle accidents caused by running off the road. | `44` |
| `Single vehicle - Total` | Integer | Total number of single vehicle accidents. | `611` |
| `Collisions - With fixed object`   | Integer | Number of collisions with a fixed object. | `264` |
| `Collisions - With parked vehicle` | Integer | Number of collisions with a parked vehicle. | `195` |
| `Collisions - Rear end to side/front` | Integer | Number of rear-end collisions with side or front. | `56` |
| `Collisions - Head-on`   | Integer | Number of head-on collisions. | `554` |
| `Collisions - Sideswipe` | Integer | Number of sideswipe collisions. | `544` |
| `Collisions - Front to rear end` | Integer | Number of front-to-rear-end collisions. | `742` |
| `Collisions - Front to side`     | Integer | Number of front-to-side collisions. | `2651` |
| `Collisions - Total sub-total`   | Integer | Subtotal of collisions with moving vehicles / general collisions. | `4547` |
| `Collisions - Grand Total`   | Integer | Total collision accidents. | `5006` |
| `Hitting a pedestrian`       | Integer | Number of accidents involving hitting a pedestrian. | `1983` |
| `Grand Total`                | Integer | Total number of road accidents for the category/month. | `7717` |
| `Month and Severity`               | String | Hebrew translation or equivalent label for the month and severity. | `כל התאונות` / `ינואר` |

---

## 7. `t01_07.xlsx`

The table tracks road accidents in Israel for the year 2025 broken down by road type, day of the week, and detailed accident/collision types.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Road Type and Day of the Week`  | String | Description of the road type, aggregate level, or day of the week (`All accidents`, `Sunday`, `Monday`, `Urban road`, etc.). | `All accidents` / `Sunday` |
| `Other and not known`  | Integer | Number of accidents classified as other or unknown type for the day/category. | `117` |
| `Single vehicle - Falling from moving vehicle`    | Integer | Number of single vehicle accidents due to falling from moving vehicle. | `41` |
| `Single vehicle - Injury to passenger in vehicle` | Integer | Number of single vehicle accidents involving injury to passenger. | `69` |
| `Single vehicle - Skidding`    | Integer | Number of single vehicle accidents caused by skidding. | `260` |
| `Single vehicle - Overturning` | Integer | Number of single vehicle accidents involving overturning. | `197` |
| `Single vehicle - Running off road` | Integer | Number of single vehicle accidents caused by running off road. | `44` |
| `Single vehicle - Total`  | Integer | Total number of single vehicle accidents for the category. | `611` |
| `Collisions - With fixed object`   | Integer | Number of collisions with a fixed object. | `264` |
| `Collisions - With parked vehicle` | Integer | Number of collisions with a parked vehicle. | `195` |
| `Collisions - Rear end to side/front` | Integer | Number of rear-end collisions with side or front. | `56` |
| `Collisions - Head-on`   | Integer | Number of head-on collisions. | `554` |
| `Collisions - Sideswipe` | Integer | Number of sideswipe collisions. | `544` |
| `Collisions - Front to rear end` | Integer | Number of front-to-rear-end collisions. | `742` |
| `Collisions - Front to side`     | Integer | Number of front-to-side collisions. | `2651` |
| `Collisions - Total sub-total`   | Integer | Subtotal of collisions with moving vehicles / general collisions. | `4547` |
| `Collisions - Grand Total`       | Integer | Total collision accidents. | `5006` |
| `Hitting a pedestrian`           | Integer | Number of accidents involving hitting a pedestrian. | `1983` |
| `Grand Total`  | Integer | Total number of road accidents for the category/day. | `7717` |
| `Road Type & Day of week` | String | Hebrew translation or equivalent label for the day of the week and category. | `כל התאונות` / `ראשון` |

---

## 8. `t01_08.xlsx`

The table tracks road accidents in Israel for the year 2025 broken down by road type, hour of the day (0–23), and detailed accident/collision type.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Road Type and Hour of the Day`  | String / Integer | Description of the road type, aggregate level, or hour of the day (`All accidents`, `6`, `7`, `Urban road`, etc.). | `All accidents` / `6` |
| `Other and not known`  | Integer | Number of accidents classified as other or unknown type for the hour/category. | `117` |
| `Single vehicle - Falling from moving vehicle`    | Integer | Number of single vehicle accidents due to falling from moving vehicle. | `41` |
| `Single vehicle - Injury to passenger in vehicle` | Integer | Number of single vehicle accidents involving injury to passenger. | `69` |
| `Single vehicle - Skidding`    | Integer | Number of single vehicle accidents caused by skidding. | `260` |
| `Single vehicle - Overturning` | Integer | Number of single vehicle accidents involving overturning. | `197` |
| `Single vehicle - Running off road` | Integer | Number of single vehicle accidents caused by running off road. | `44` |
| `Single vehicle - Total` | Integer | Total number of single vehicle accidents for the hour/category. | `611` |
| `Collisions - With fixed object` | Integer | Number of collisions with a fixed object. | `264` |
| `Collisions - With parked vehicle` | Integer | Number of collisions with a parked vehicle. | `195` |
| `Collisions - Rear end to side/front` | Integer | Number of rear-end collisions with side or front. | `56` |
| `Collisions - Head-on` | Integer | Number of head-on collisions. | `554` |
| `Collisions - Sideswipe` | Integer | Number of sideswipe collisions. | `544` |
| `Collisions - Front to rear end` | Integer | Number of front-to-rear-end collisions. | `742` |
| `Collisions - Front to side`     | Integer | Number of front-to-side collisions. | `2651` |
| `Collisions - Total sub-total`   | Integer | Subtotal of collisions with moving vehicles / general collisions. | `4547` |
| `Collisions - Grand Total`       | Integer | Total collision accidents. | `5006` |
| `Hitting a pedestrian`           | Integer | Number of accidents involving hitting a pedestrian. | `1983` |
| `Grand Total`  | Integer | Total number of road accidents for the category/hour. | `7717` |
| `Road Type & Hour of the day` | String | Hebrew translation or equivalent label for the hour of the day and category. | `כל התאונות` / `6` |

---

## 9. `t01_09.xlsx` 

The table tracks road accidents in Israel for the year 2025, broken down by road type (intersections vs. non-intersections), hour of the day (0–23), accident severity (slight, serious, fatal), and day of the week.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Road Type and Hour of the Day`  | String / Integer | Description of the road type, aggregate level, or hour of the day (`All accidents`, `6`, `7`, `Urban road`, etc.). | `All accidents` / `6` |
| `Not at intersection - Saturday and holiday`   | Integer | Accidents not at an intersection on Saturdays/holidays. | `431` |
| `Not at intersection - Friday and holiday eve` | Integer | Accidents not at an intersection on Fridays/holiday eves. | `609` |
| `Not at intersection - Thursday`  | Integer | Accidents not at an intersection on Thursdays. | `598` |
| `Not at intersection - Wednesday` | Integer | Accidents not at an intersection on Wednesdays. | `580` |
| `Not at intersection - Tuesday`   | Integer | Accidents not at an intersection on Tuesdays. | `581` |
| `Not at intersection - Monday`    | Integer | Accidents not at an intersection on Mondays. | `579` |
| `Not at intersection - Sunday`    | Integer | Accidents not at an intersection on Sundays. | `643` |
| `Not at intersection - Total`     | Integer | Total accidents not at an intersection for the hour/category. | `4021` |
| `At intersection - Saturday and holiday`  | Integer | Accidents at an intersection on Saturdays/holidays. | `379` |
| `At intersection - Friday and holiday eve`| Integer | Accidents at an intersection on Fridays/holiday eves. | `518` |
| `At intersection - Thursday`  | Integer | Accidents at an intersection on Thursdays. | `545` |
| `At intersection - Wednesday` | Integer | Accidents at an intersection on Wednesdays. | `589` |
| `At intersection - Tuesday`   | Integer | Accidents at an intersection on Tuesdays. | `547` |
| `At intersection - Monday`    | Integer | Accidents at an intersection on Mondays. | `525` |
| `At intersection - Sunday`    | Integer | Accidents at an intersection on Sundays. | `593` |
| `At intersection - Total`     | Integer | Total accidents at an intersection for the hour/category. | `3696` |
| `Severity - Slight`   | Integer | Number of slight injury accidents. | `4801` |
| `Severity - Serious`  | Integer | Number of serious injury accidents. | `2478` |
| `Severity - Fatal`    | Integer | Number of fatal accidents. | `438` |
| `Grand Total`   | Integer | Total number of road accidents for the hour/category. | `7717` |
| `Road Type and Hour of the Day`  | String | Hebrew translation or equivalent label for the hour of the day and category. | `כל התאונות` / `6` |

---

## 10. `t01_10.xlsx`

The table tracks road accidents in Israel for the year 2025, broken down by visibility conditions (day vs. night), specific road/lighting conditions, accident severity, and detailed accident/collision types.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Visibility and Road Condition`  | String | Description of visibility conditions, lighting, or aggregate level (`All accidents`, `Daytime accidents`, `Ordinary daylight`, `Night accidents`, `Lighting in order`, etc.). | `All accidents` / `Ordinary daylight` |
| `Other and not known`  | Integer | Number of accidents classified as other or unknown type for the condition. | `117` |
| `Single vehicle - Falling from moving vehicle`     | Integer | Number of single vehicle accidents due to falling from moving vehicle. | `41` |
| `Single vehicle - Injury to passenger in vehicle`  | Integer | Number of single vehicle accidents involving injury to passenger. | `69` |
| `Single vehicle - Skidding`      | Integer | Number of single vehicle accidents caused by skidding. | `260` |
| `Single vehicle - Overturning`   | Integer | Number of single vehicle accidents involving overturning. | `197` |
| `Single vehicle - Running off road`    | Integer | Number of single vehicle accidents caused by running off road. | `44` |
| `Collisions - With fixed object`       | Integer | Number of collisions with a fixed object. | `264` |
| `Collisions - With parked vehicle`     | Integer | Number of collisions with a parked vehicle. | `195` |
| `Collisions - Rear end to side/front`  | Integer | Number of rear-end collisions with side or front. | `56` |
| `Collisions - Head-on`            | Integer | Number of head-on collisions. | `554` |
| `Collisions - Sideswipe`          | Integer | Number of sideswipe collisions. | `544` |
| `Collisions - Front to rear end`  | Integer | Number of front-to-rear-end collisions. | `742` |
| `Collisions - Front to side`  | Integer | Number of front-to-side collisions. | `2651` |
| `Hitting a pedestrian` | Integer | Number of accidents involving hitting a pedestrian. | `1983` |
| `Severity - Slight` | Integer | Number of slight injury accidents. | `4801` |
| `Severity - Serious`| Integer | Number of serious injury accidents. | `2478` |
| `Severity - Fatal`  | Integer | Number of fatal accidents. | `438` |
| `Grand Total`   | Integer | Total number of road accidents for the visibility/condition category. | `7717` |
| `Visibility and Road Condition`  | String | Hebrew translation or equivalent label for the visibility and road condition. | `כל התאונות` / `אור יום רגיל` |

---

## 11. `t01_11.xlsx` 

The table tracks road accidents in Israel for the year 2025, broken down by the main cause of the accident (e.g., driver's offence, pedestrian's action), accident severity (fatal, serious, slight), and detailed accident/collision types.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Main Cause and Severity`  | String | Description of the main cause category or severity level (`All accidents`, `Driver's offence`, `Fatal`, `Serious`, `Slight`, etc.). | `All accidents` / `Driver's offence` |
| `Other and not known`  | Integer | Number of accidents classified as other or unknown type for the main cause category. | `117` |
| `Single vehicle - Falling from moving vehicle`     | Integer | Number of single vehicle accidents due to falling from moving vehicle. | `41` |
| `Single vehicle - Injury to passenger in vehicle`  | Integer | Number of single vehicle accidents involving injury to passenger. | `69` |
| `Single vehicle - Skidding`            | Integer | Number of single vehicle accidents caused by skidding. | `260` |
| `Single vehicle - Overturning`         | Integer | Number of single vehicle accidents involving overturning. | `197` |
| `Single vehicle - Running off road`    | Integer | Number of single vehicle accidents caused by running off road. | `44` |
| `Single vehicle - Total`               | Integer | Total number of single vehicle accidents for the main cause category. | `611` |
| `Collisions - With fixed object`       | Integer | Number of collisions with a fixed object. | `264` |
| `Collisions - With parked vehicle`     | Integer | Number of collisions with a parked vehicle. | `195` |
| `Collisions - Rear end to side/front`  | Integer | Number of rear-end collisions with side or front. | `56` |
| `Collisions - Head-on`            | Integer | Number of head-on collisions. | `554` |
| `Collisions - Sideswipe`          | Integer | Number of sideswipe collisions. | `544` |
| `Collisions - Front to rear end`  | Integer | Number of front-to-rear-end collisions. | `742` |
| `Collisions - Front to side`    | Integer | Number of front-to-side collisions. | `2651` |
| `Collisions - Total sub-total`  | Integer | Subtotal of collisions with moving vehicles / general collisions. | `4547` |
| `Collisions - Grand Total`      | Integer | Total collision accidents. | `5006` |
| `Hitting a pedestrian`          | Integer | Number of accidents involving hitting a pedestrian. | `1983` |
| `Grand Total`  | Integer | Total number of road accidents for the main cause category. | `7717` |
| `Main Cause and Severity`  | String | Hebrew translation or equivalent label for the main cause and severity. | `כל התאונות` / `עבירה של נהג` |

---

## 12. `t01_12.xlsx` 

The table tracks road accidents in Israel for the year 2025, broken down by road type (urban vs. non-urban, intersections vs. non-intersections), accident severity (fatal, serious, slight), and detailed accident/collision types.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Road Type and Severity`  | String | Description of the road type category or severity level (`All accidents`, `Urban road`, `At intersection`, `Fatal`, `Serious`, `Slight`, etc.). | `All accidents` / `Urban road` |
| `Other and not known`  | Integer | Number of accidents classified as other or unknown type for the road/severity category. | `117` |
| `Single vehicle - Falling from moving vehicle`    | Integer | Number of single vehicle accidents due to falling from moving vehicle. | `41` |
| `Single vehicle - Injury to passenger in vehicle` | Integer | Number of single vehicle accidents involving injury to passenger. | `69` |
| `Single vehicle - Skidding`           | Integer | Number of single vehicle accidents caused by skidding. | `260` |
| `Single vehicle - Overturning`        | Integer | Number of single vehicle accidents involving overturning. | `197` |
| `Single vehicle - Running off road`   | Integer | Number of single vehicle accidents caused by running off road. | `44` |
| `Single vehicle - Total`    | Integer | Total number of single vehicle accidents for the road/severity category. | `611` |
| `Collisions - With fixed object`       | Integer | Number of collisions with a fixed object. | `264` |
| `Collisions - With parked vehicle`     | Integer | Number of collisions with a parked vehicle. | `195` |
| `Collisions - Rear end to side/front`  | Integer | Number of rear-end collisions with side or front. | `56` |
| `Collisions - Head-on`            | Integer | Number of head-on collisions. | `554` |
| `Collisions - Sideswipe`          | Integer | Number of sideswipe collisions. | `544` |
| `Collisions - Front to rear end`  | Integer | Number of front-to-rear-end collisions. | `742` |
| `Collisions - Front to side`  | Integer | Number of front-to-side collisions. | `2651` |
| `Collisions - Total sub-total`  | Integer | Subtotal of collisions with moving vehicles / general collisions. | `4547` |
| `Collisions - Grand Total`  | Integer | Total collision accidents. | `5006` |
| `Hitting a pedestrian`  | Integer | Number of accidents involving hitting a pedestrian. | `1983` |
| `Grand Total`  | Integer | Total number of road accidents for the road/severity category. | `7717` |
| `Road Type and Severity`  | String | Hebrew translation or equivalent label for the road type and severity. | `כל התאונות` / `דרך עירונית` |

---

## 13. `t01_13.xlsx` 

The table tracks road accidents in Israel for the year 2025, broken down by the specific locality where the accident occurred (including major cities with 10,000+ residents, non-urban roads, and urban road aggregates), accident severity, and detailed accident/collision types.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Locality`  | String | Name of the locality or aggregate category (`Total`, `On non-urban roads`, `On urban roads`, `Tel Aviv-Yafo`, `Jerusalem`, etc.). | `Tel Aviv-Yafo` / `On urban roads` |
| `Other and not known`  | Integer / Float | Number of accidents classified as other or unknown type for the locality. | `117` |
| `Single vehicle - Falling from moving vehicle`  | Integer / Float | Number of single vehicle accidents due to falling from moving vehicle. | `41` |
| `Single vehicle - Injury to passenger in vehicle`  | Integer / Float | Number of single vehicle accidents involving injury to passenger. | `69` |
| `Single vehicle - Running off road, overturning, skidding`  | Integer / Float | Number of single vehicle accidents caused by running off road, overturning, or skidding. | `501` |
| `Collisions - Other`  | Integer / Float | Number of other collision types. | `515` |
| `Collisions - Head-on`  | Integer / Float | Number of head-on collisions. | `554` |
| `Collisions - Sideswipe`  | Integer / Float | Number of sideswipe collisions. | `544` |
| `Collisions - Front to rear end`  | Integer / Float | Number of front-to-rear-end collisions. | `742` |
| `Collisions - Front to side`  | Integer / Float | Number of front-to-side collisions. | `2651` |
| `Hitting a pedestrian`  | Integer / Float | Number of accidents involving hitting a pedestrian. | `1983` |
| `Severity - Slight`  | Integer / Float | Number of slight injury accidents in the locality. | `4801` |
| `Severity - Serious`  | Integer / Float | Number of serious injury accidents in the locality. | `2478` |
| `Severity - Fatal`  | Integer / Float | Number of fatal accidents in the locality. | `438` |
| `Grand Total`  | Integer / Float | Total number of road accidents in the locality. | `7717` |
| `Locality`  | String | Hebrew translation or equivalent label for the locality name. | `תל אביב-יפו` / `בדרכים עירוניות` |

---

## 14. `t01_14.xlsx`

This file tracks road accidents involving pedestrians in Israel for the year 2025, broken down by road type, accident severity, and the pedestrian's action prior to or during the accident (e.g., crossing at a crosswalk with/without traffic lights, walking on sidewalk or road, standing on road, etc.).

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Road Type and Severity`  | String | Description of the road type and severity category (`All accidents`, `Fatal`, `Serious`, `Slight`, `Urban road`, etc.). | `All accidents` / `Fatal` |
| `Crossed road - Not known / Other`  | Integer | Pedestrian crossing road, specific details unknown. | `108` |
| `Crossed road - Not in crosswalk, not near intersection` | Integer | Pedestrian crossing not at a crosswalk or near an intersection. | `58` |
| `Crossed road - Not in crosswalk, near intersection` | Integer | Pedestrian crossing not at a crosswalk but near an intersection. | `229` |
| `Crossed road - In crosswalk without traffic light` | Integer | Pedestrian crossing in a crosswalk without a traffic light. | `51` |
| `Crossed road - In crosswalk with traffic light` | Integer | Pedestrian crossing in a crosswalk with a traffic light. | `1073` |
| `Crossed road - Sub-total`    | Integer | Sub-total for pedestrian crossing road. | `187` |
| `Did not cross road - Other`  | Integer | Pedestrian not crossing road, other actions. | `1598` |
| `Did not cross road - Was on sidewalk`         | Integer | Pedestrian standing or walking on sidewalk. | `198` |
| `Did not cross road - Was on separation area`  | Integer | Pedestrian on separation area/island. | `41` |
| `Did not cross road - Stood on road`    | Integer | Pedestrian standing on the roadway. | `4` |
| `Did not cross road - Played on road`   | Integer | Pedestrian playing on the roadway. | `25` |
| `Did not cross road - Walked opposite to traffic` | Integer | Pedestrian walking opposite to traffic direction. | `3` |
| `Did not cross road - Walked with traffic`  | Integer | Pedestrian walking with traffic direction. | `6` |
| `Did not cross road - Sub-total`  | Integer | Sub-total for pedestrian not crossing road. | `277` |
| `Grand Total`   | Integer | Total number of pedestrian accidents for the category/severity. | `1983` |
| `Road Type & Severity`  | String | Hebrew translation or equivalent label for the road type and severity. | `כל התאונות` / `קטלניות` |

---

## 15. `sep 2026.xlsx`

The table contains official Israeli Central Bureau of Statistics (CBS) data tracking road accidents with casualties ("Expanded R.A." files) across Israel, including the Judea and Samaria area, published in September 2026. It provides annual totals (2022–2025) and monthly time-series metrics (August 2023–August 2026) broken down by accident and casualty severity, alongside seasonally adjusted and trend figures.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `Year`  | String / Integer | The calendar year of the recorded data (rows with `*` indicate provisional data). | `2022` / `*2026` |
| `Month` | String (Roman Numeral) | The calendar month of the observation (`I`–`XII`); null for annual aggregate rows. | `VIII` |
| `Accidents - Total - Original data` | Integer | Raw total count of road accidents involving casualties during the period. | `10404` |
| `Accidents - Total - Seasonally adjusted` | Integer | Total count of casualty road accidents adjusted for seasonal fluctuations. | `10404` |
| `Accidents - Total - Trend`  | Integer | Smoothed underlying trend estimate for total casualty road accidents. | `10367` |
| `Accidents - Fatal`          | Integer | Number of road accidents resulting in at least one fatality. | `319` |
| `Accidents - Serious`        | Integer | Number of road accidents where the most severe outcome was serious injury. | `2320` |
| `Casualties - Total - Original data`  | Integer | Raw total count of individuals injured or killed in road accidents. | `18458` |
| `Casualties - Total - Seasonally adjusted` | Integer | Total count of road accident casualties adjusted for seasonal fluctuations. | `18501` |
| `Casualties - Total - Trend`  | Integer | Smoothed underlying trend estimate for total road accident casualties. | `18428` |
| `Casualties - Killed`         | Integer | Total number of individuals killed in road accidents during the period. | `351` |
| `Casualties - Seriously injured` | Integer | Total number of individuals seriously injured in road accidents during the period. | `2607` |


