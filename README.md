# GBD compact

This dataset is based on [GBD 2023](http://ghdx.healthdata.org/gbd-results-tool). We filtered
the datapoints required by the [SG dataset](https://github.com/open-numbers/ddf--gapminder--systema_globalis).

Age standardised Death rates, death numbers, age standardised incidence rates, and incidence numbers for following
causes, disaggregated by sex, are included in this dataset:

- Stomach cancer
- Liver cancer
- Tracheal, bronchus, and lung cancer
- Breast cancer
- Prostate cancer
- Colon and rectum cancer
- Motorcyclist road injuries (only death rates for both sexes)
- Motor vehicle road injuries (only death rates for both sexes)
- Falls (only death rates for both sexes)
- Drowning (only death rates for both sexes)
- Fire, heat, and hot substances (only death rates for both sexes)
- Poisonings (only death rates for both sexes)
 

## Notes on ETL and source files

Source files are not included in the dataset, and manual downloading of the source files are required in order to run
the etl script.

The ETL script, written with flexibility in mind, is able to proceed with any number of source files downloaded from the
GBD result tool.
