# GBD compact

This dataset is based on [GBD 2021](http://ghdx.healthdata.org/gbd-results-tool). We filtered
the datapoints required by the [SG dataset](https://github.com/open-numbers/ddf--gapminder--systema_globalis).

## Data Source

We run 2 queries in the GBD Results Tool and download the result files as source data.

### Query 1: Deaths (Number and Rate)

**Parameters:**
- **Years:** All years (1990-2019)
- **Locations:** All countries
- **Measure:** Deaths
- **Metrics:** Number, Age-standardized rate
- **Sex:** Male, Female, Both
- **Ages:** 
  - All ages
  - Age-standardized
  - <5 years
  - 5-9 years
  - 10-14 years
  - 15-19 years
  - 20-24 years
  - 25-29 years
  - 30-34 years
  - 35-39 years
  - 40-44 years
  - 45-49 years
  - 50-54 years
  - 55-59 years
  - 60-64 years
  - 65-69 years
  - 70-74 years
  - 75-79 years
  - 80+ years
  - 85-89 years
  - 90-94 years
  - 95+ years
  - 5-14 years
- **Causes:**
  - Breast cancer
  - Cervical cancer
  - Colon and rectum cancer
  - Falls
  - HIV/AIDS
  - Injuries
  - Liver cancer
  - Tracheal, bronchus, and lung cancer
  - Malaria
  - Motorcyclist road injuries
  - Interpersonal violence
  - Non-communicable diseases
  - Poisonings
  - Prostate cancer
  - Stomach cancer
  - Self-harm
  - Road injuries
  - Measles
  - Meningitis
  - Fire, heat, and hot substances

### Query 2: Incidence (Number and Rate)

**Parameters:**
- **Years:** All years (1990-2019)
- **Locations:** All countries
- **Measure:** Incidence
- **Metrics:** Number, Age-standardized rate
- **Sex:** Male, Female, Both
- **Ages:**
  - All ages
  - Age-standardized
- **Causes:** (Same as Query 1)
  - Breast cancer
  - Cervical cancer
  - Colon and rectum cancer
  - Falls
  - HIV/AIDS
  - Injuries
  - Liver cancer
  - Tracheal, bronchus, and lung cancer
  - Malaria
  - Motorcyclist road injuries
  - Interpersonal violence
  - Non-communicable diseases
  - Poisonings
  - Prostate cancer
  - Stomach cancer
  - Self-harm
  - Road injuries
  - Measles
  - Meningitis
  - Fire, heat, and hot substances
