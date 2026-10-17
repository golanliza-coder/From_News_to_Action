
# Data Dictionary

This document provides a detailed overview of the datasets tracking global health security, demographic trends, health indicators, and technology adoption.

---

## 1. 2021-GHS-Index-April-2022.csv

**Description:** This dataset tracks the Global Health Security (GHS) Index scores and hundreds of specific underlying indicators for countries to measure their capacity to prevent, detect, and respond to health emergencies.,

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| Country | String | Name of the country being assessed. | Afghanistan |
| Year | Integer | The year the index data was recorded. | 2021 |
| OVERALL SCORE | Float | The aggregated health security index score (0-100). | 28.8 |
| 1) PREVENTION... | Float | Score for the Prevention of the emergence or release of pathogens. | 12 |
| 1.1) Antimicrobial resistance (AMR) | Float | Specific score for AMR capacity and regulations. | 16.7 |
| 2) EARLY DETECTION & REPORTING... | Float | Score for capacity in laboratory systems and real-time surveillance. | 20.6 |
| 3) RAPID RESPONSE... | Float | Score for emergency preparedness and risk communication. | 23.3 |
| 4) SUFFICIENT & ROBUST HEALTH SECTOR... | Float | Score for clinical capacity and healthcare workforce. | 24.5 |
| 5) COMMITMENT TO IMPROVING... | Float | Score for international agreements and financing for preparedness. | 25 |
| 6) OVERALL RISK ENVIRONMENT... | Float | Score for political, security, and socio-economic resilience. | 45.1 |
| *[Hundreds of specific sub-indicators]* | Float | Granular binary or numeric scores for specific laws, rates, or capacities (e.g., 1.1.1a, 6.5.1a)., | 50 |

---

## 2. country Index.csv

**Description:** This file serves as a geographic reference table, mapping location keys to country names, subregional divisions, and hierarchical aggregation levels.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| location_key | String | Unique identifier used to join with other health and demographic tables. | AF_BAL |
| country_code | String | Two-letter ISO country code. | AF |
| country_name | String | Full name of the country. | Afghanistan |
| subregion1_code | String | Code for the primary sub-administrative division (e.g., state or province). | BAL |
| subregion1_name | String | Name of the primary sub-administrative division. | Balkh |
| subregion2_code | String | Code for the secondary sub-administrative division (e.g., county or district). | 7 |
| subregion2_name | String | Name of the secondary sub-administrative division. | Anta |
| aggregation_level | Integer | Hierarchical level (0 for country, 1 for subregion1, 2 for subregion2). | 1 |

---

## 3. demographics.csv

**Description:** This dataset provides detailed population statistics, including gender distribution, urban/rural splits, population density, and age-specific breakdowns for global locations.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| location_key | String | Unique identifier linking to the country index. | AE |
| population | Integer | Total resident population for the location. | 9890400 |
| population_male | Integer | Total male population. | 6836349 |
| population_female | Integer | Total female population. | 3054051 |
| population_rural | Integer | Number of people living in rural areas. | 1290785 |
| population_urban | Integer | Number of people living in urban areas. | 8479744 |
| population_density | Float | Number of people per square kilometer. | 118.306 |
| human_development_index | Float | UNDP Human Development Index (HDI) score. | 0.863 |
| population_age_00_09 | Integer | Population count for ages 0 through 9. | 1011713 |
| population_age_80_and_older | Integer | Population count for ages 80 and above. | 12426 |

---

## 4. health.csv

**Description:** This table tracks critical health outcomes and healthcare system metrics, such as life expectancy, disease prevalence, mortality rates, and medical expenditures.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| location_key | String | Unique identifier linking to the country index. | AE |
| life_expectancy | Float | Average number of years a person is expected to live. | 77.814 |
| smoking_prevalence | Float | Percentage of the population that uses tobacco. | 28.9 |
| diabetes_prevalence | Float | Percentage of the population with diabetes. | 16.3 |
| infant_mortality_rate | Float | Number of infant deaths per 1,000 live births. | 6.5 |
| adult_male_mortality_rate | Float | Probability of dying between ages 15 and 60 for males per 1,000. | 69.555 |
| physicians_per_1000 | Float | Number of medical doctors per 1,000 people. | 2.5278 |
| health_expenditure_usd | Float | Total health expenditure per capita in USD. | 1357.017 |
| out_of_pocket_health_expenditure_usd | Float | Direct health payments by individuals per capita in USD. | 256.034 |

---

## 5. ict adoption by 100 people.csv

**Description:** This dataset monitors the evolution of technology adoption, tracking fixed-line, mobile, broadband, and internet usage rates per 100 people over time.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| Entity | String | Name of the country or regional group. | Afghanistan |
| Code | String | Three-letter ISO country code. | AFG |
| Year | Integer | The year of the observation. | 2021 |
| Fixed telephone subscriptions (per 100 people) | Float | Number of landline subscriptions per 100 inhabitants. | 0.364 |
| Fixed broadband subscriptions (per 100 people) | Float | Number of high-speed internet subscriptions per 100 inhabitants. | 0.0664 |
| Mobile cellular subscriptions (per 100 people) | Float | Number of mobile phone subscriptions per 100 inhabitants. | 56.6945 |
| Internet users (per 100 people) | Float | Percentage of the population using the internet. | 16.5143 |

## 6. WHO-COVID-19-global-daily-data.csv

**Description:** This dataset provides a daily time-series of confirmed COVID-19 cases and deaths as reported by various countries and territories to the World Health Organization (WHO).

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| Date_reported | Date | The date on which the daily COVID-19 statistics were recorded. | 04/01/2020 |
| Country_code | String | Two-letter ISO country code identifying the reporting nation. | AF |
| Country | String | Full name of the reporting country or territory. | Afghanistan |
| WHO_region | String | The WHO regional office responsible for the reporting area (e.g., EMR, AFR, EUR). | EMR |
| New_cases | Integer | The number of new confirmed COVID-19 cases reported for that specific day. | 0 |
| Cumulative_cases | Integer | The total running count of confirmed COVID-19 cases reported to date. | 0 |
| New_deaths | Integer | The number of new confirmed COVID-19 deaths reported for that specific day. | 0 |
| Cumulative_deaths | Integer | The total running count of confirmed COVID-19 deaths reported to date. | 0 |

## 7. vaccinations.csv

**Description:** This dataset tracks COVID-19 vaccination progress at a granular level, providing daily and cumulative metrics for persons vaccinated, fully vaccinated, and total doses administered, including brand-specific data for Pfizer, Moderna, Janssen, and Sinovac.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| date | Date | The date on which the vaccination data was recorded. | 2021-01-25 |
| location_key | String | Unique identifier used to link demographic and health data tables. | AD |
| new_persons_vaccinated | Integer | The number of people who received their first vaccine dose on this date. | 460 |
| cumulative_persons_vaccinated | Integer | The total number of people who have received at least one vaccine dose to date. | 576 |
| new_persons_fully_vaccinated | Integer | The number of people who completed their primary vaccination series on this date. | 92 |
| cumulative_persons_fully_vaccinated | Integer | The total number of people who have completed their primary vaccination series to date. | 1172 |
| new_vaccine_doses_administered | Integer | The total number of vaccine doses administered on this specific date. | 460 |
| cumulative_vaccine_doses_administered | Integer | The total number of vaccine doses administered to date. | 1036 |
| new_persons_vaccinated_pfizer | Integer | Daily count of individuals receiving their first Pfizer dose. | 0 |
| cumulative_persons_vaccinated_pfizer | Integer | Total count of individuals who have received at least one Pfizer dose. | 0 |
| new_persons_fully_vaccinated_pfizer | Integer | Daily count of individuals completing the Pfizer series. | 0 |
| cumulative_persons_fully_vaccinated_pfizer | Integer | Total count of individuals fully vaccinated with Pfizer. | 0 |
| new_vaccine_doses_administered_pfizer | Integer | Total Pfizer doses administered on this date. | 0 |
| cumulative_vaccine_doses_administered_pfizer | Integer | Total Pfizer doses administered to date. | 0 |
| new_persons_vaccinated_moderna | Integer | Daily count of individuals receiving their first Moderna dose. | 0 |
| cumulative_persons_vaccinated_moderna | Integer | Total count of individuals who have received at least one Moderna dose. | 0 |
| new_persons_fully_vaccinated_moderna | Integer | Daily count of individuals completing the Moderna series. | 0 |
| cumulative_persons_fully_vaccinated_moderna | Integer | Total count of individuals fully vaccinated with Moderna. | 0 |
| new_vaccine_doses_administered_moderna | Integer | Total Moderna doses administered on this date. | 0 |
| cumulative_vaccine_doses_administered_moderna | Integer | Total Moderna doses administered to date. | 0 |
| new_persons_vaccinated_janssen | Integer | Daily count of individuals receiving the single-dose Janssen vaccine. | 0 |
| cumulative_persons_vaccinated_janssen | Integer | Total count of individuals who have received the Janssen vaccine. | 0 |
| new_persons_fully_vaccinated_janssen | Integer | Daily count of individuals fully vaccinated with Janssen. | 0 |
| cumulative_persons_fully_vaccinated_janssen | Integer | Total count of individuals fully vaccinated with Janssen. | 0 |
| new_vaccine_doses_administered_janssen | Integer | Total Janssen doses administered on this date. | 0 |
| cumulative_vaccine_doses_administered_janssen | Integer | Total Janssen doses administered to date. | 0 |
| new_persons_vaccinated_sinovac | Integer | Daily count of individuals receiving their first Sinovac dose. | 0 |
| total_persons_vaccinated_sinovac | Integer | Total count of individuals who have received at least one Sinovac dose. | 0 |
| new_persons_fully_vaccinated_sinovac | Integer | Daily count of individuals completing the Sinovac series. | 0 |
| total_persons_fully_vaccinated_sinovac | Integer | Total count of individuals fully vaccinated with Sinovac. | 0 |
| new_vaccine_doses_administered_sinovac | Integer | Total Sinovac doses administered on this date. | 0 |
| total_vaccine_doses_administered_sinovac | Integer | Total Sinovac doses administered to date. | 0 |

**Comment:** Due to its huge size and size limitation in GitHub, data file is locatedin following share drive location
'/content/drive/MyDrive/DS_IsTheWorldReadyForTheNextPandemic/DATASET TO USE/'


---

## 8. epidemiology.csv

**Description:** This dataset tracks the daily and cumulative spread of COVID-19 by location, recording confirmed cases, deaths, recoveries, and testing activity.

| Field Name | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| date | Date | The date on which the epidemiological statistics were recorded. | 2020-01-01 |
| location_key | String | Unique identifier used to link data across various country and health tables. | AD |
| new_confirmed | Integer | Number of new confirmed COVID-19 cases reported on this date. | 0 |
| new_deceased | Integer | Number of new COVID-19 related deaths reported on this date. | 0 |
| new_recovered | Integer | Number of new COVID-19 recoveries reported on this date. | 0 |
| new_tested | Integer | Number of new COVID-19 tests performed on this date. | 0 |
| cumulative_confirmed | Integer | Total number of confirmed COVID-19 cases reported to date. | 0 |
| cumulative_deceased | Integer | Total number of COVID-19 related deaths reported to date. | 0 |
| cumulative_recovered | Integer | Total number of COVID-19 recoveries reported to date. | 0 |
| cumulative_tested | Integer | Total number of COVID-19 tests performed to date. | 0 |

**Comment:** Due to its huge size and size limitation in GitHub, data file is locatedin following share drive location
'/content/drive/MyDrive/DS_IsTheWorldReadyForTheNextPandemic/DATASET TO USE/'


---

