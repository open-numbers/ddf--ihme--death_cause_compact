#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ETL script for IHME GBD 2023 data
Converts GBD result tool CSV exports into DDF format with meaningful indicator names
"""

import os
import os.path as osp
import pandas as pd
import numpy as np
from zipfile import ZipFile
from ddf_utils.str import to_concept_id, format_float_digits
from functools import partial


# Configuration
SOURCE_DIR = "../source/"
OUTPUT_DIR = "../../"

# Number formatter
formatter = partial(format_float_digits, digits=2)


def load_source_data_from_zip(zip_path):
    """Load the source CSV file directly from a zip file."""
    print(f"Loading data from {zip_path}")

    with ZipFile(zip_path, "r") as zf:
        # Find the CSV file in the zip
        csv_files = [f for f in zf.namelist() if f.endswith(".csv")]

        if not csv_files:
            print(f"  WARNING: No CSV files found in {zip_path}")
            return None

        if len(csv_files) > 1:
            print(f"  WARNING: Multiple CSV files found, using first: {csv_files[0]}")

        csv_file = csv_files[0]
        print(f"  Reading {csv_file} from zip")

        # Read CSV directly from zip
        with zf.open(csv_file) as f:
            df = pd.read_csv(f)

    print(f"  Loaded {len(df)} rows")
    return df


def load_all_source_data(source_dir):
    """Load and concatenate all zip files in the source directory."""
    print(f"\nScanning for zip files in {source_dir}")

    zip_files = [f for f in os.listdir(source_dir) if f.endswith(".zip")]

    if not zip_files:
        print("ERROR: No zip files found in source directory!")
        return None

    print(f"Found {len(zip_files)} zip file(s)")

    all_dataframes = []

    for zip_file in zip_files:
        zip_path = osp.join(source_dir, zip_file)
        df = load_source_data_from_zip(zip_path)

        if df is not None:
            all_dataframes.append(df)

    if not all_dataframes:
        print("ERROR: No data loaded from any zip files!")
        return None

    # Concatenate all dataframes
    print(f"\nConcatenating {len(all_dataframes)} dataframe(s)")
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    print(f"Combined total: {len(combined_df)} rows")

    # Remove duplicates
    original_count = len(combined_df)
    combined_df = combined_df.drop_duplicates()
    duplicates_removed = original_count - len(combined_df)

    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} duplicate rows")
    else:
        print("No duplicate rows found")

    print(f"Final dataset: {len(combined_df)} rows")

    return combined_df


def create_indicator_name(row):
    """
    Create meaningful indicator name from cause, measure, metric, and age.
    Example: Breast cancer + Deaths + Number + All ages -> breast_cancer_deaths_number_all_ages
    """
    cause = row["cause_name"]
    measure = row["measure_name"]
    metric = row["metric_name"]
    age = row["age_name"]

    # Create a readable name
    name = f"{cause} {measure} {metric} {age}"
    # Convert to concept_id format (lowercase, underscores)
    concept = to_concept_id(name)

    return concept, name


def extract_entities(df):
    """Extract entity domains from the source data."""

    entities = {}

    # Extract locations
    location_cols = ["location_id", "location_name"]
    locations = df[location_cols].drop_duplicates().sort_values("location_id")
    locations.columns = ["location", "name"]
    entities["location"] = locations

    # Extract sex
    sex_cols = ["sex_id", "sex_name"]
    sexes = df[sex_cols].drop_duplicates().sort_values("sex_id")
    sexes.columns = ["sex", "name"]
    entities["sex"] = sexes

    # Age is now flattened into indicator names, not an entity dimension

    # Extract cause
    cause_cols = ["cause_id", "cause_name"]
    causes = df[cause_cols].drop_duplicates().sort_values("cause_id")
    causes.columns = ["cause", "name"]
    entities["cause"] = causes

    # Extract measure
    measure_cols = ["measure_id", "measure_name"]
    measures = df[measure_cols].drop_duplicates().sort_values("measure_id")
    measures.columns = ["measure", "name"]
    entities["measure"] = measures

    # Extract metric
    metric_cols = ["metric_id", "metric_name"]
    metrics = df[metric_cols].drop_duplicates().sort_values("metric_id")
    metrics.columns = ["metric", "name"]
    entities["metric"] = metrics

    return entities


def serve_entities(entities):
    """Write entity files in DDF format."""

    print("Creating entity files...")

    for entity_type, entity_df in entities.items():
        filepath = osp.join(OUTPUT_DIR, f"ddf--entities--{entity_type}.csv")
        entity_df.to_csv(filepath, index=False)
        print(f"  Written: {filepath} ({len(entity_df)} entities)")


def get_all_indicators(df):
    """Get all unique indicator combinations from the data."""

    # Get unique combinations of measure, cause, metric, and age
    indicator_cols = ["measure_name", "cause_name", "metric_name", "age_name"]
    unique_combos = df[indicator_cols].drop_duplicates()

    indicators = []
    for _, row in unique_combos.iterrows():
        concept, name = create_indicator_name(row)
        indicators.append(
            {
                "concept": concept,
                "name": name,
                "measure_name": row["measure_name"],
                "cause_name": row["cause_name"],
                "metric_name": row["metric_name"],
                "age_name": row["age_name"],
            }
        )

    return indicators


def serve_datapoints(df, indicators):
    """Create datapoint files for each indicator."""

    print("\nCreating datapoint files...")

    for indicator in indicators:
        concept = indicator["concept"]
        measure = indicator["measure_name"]
        cause = indicator["cause_name"]
        metric = indicator["metric_name"]
        age = indicator["age_name"]

        print(f"  Processing: {concept}")

        # Filter data for this indicator (including age filter)
        mask = (
            (df["measure_name"] == measure)
            & (df["cause_name"] == cause)
            & (df["metric_name"] == metric)
            & (df["age_name"] == age)
        )
        df_indicator = df[mask].copy()

        if df_indicator.empty:
            print(f"    WARNING: No data found for {concept}")
            continue

        # Select and rename columns for DDF format (age_id removed from dimensions)
        df_out = df_indicator[
            ["location_id", "sex_id", "cause_id", "year", "val"]
        ].copy()

        df_out.columns = ["location", "sex", "cause", "year", concept]

        # Format the value column
        df_out[concept] = df_out[concept].map(formatter)

        # Sort by dimensions (age removed)
        df_out = df_out.sort_values(by=["location", "sex", "cause", "year"])

        # Create filename following DDF naming convention (age removed from dimensions)
        by_dims = ["location", "sex", "cause", "year"]
        filename = f"ddf--datapoints--{concept}--by--{'--'.join(by_dims)}.csv"
        filepath = osp.join(OUTPUT_DIR, filename)

        # Write to file
        df_out.to_csv(filepath, index=False)
        print(f"    Written: {filename} ({len(df_out)} rows)")


def serve_concepts(indicators, entities):
    """Create concept files in DDF format."""

    print("\nCreating concept files...")

    # Continuous concepts (measures/indicators)
    continuous_concepts = pd.DataFrame(
        [
            {"concept": ind["concept"], "name": ind["name"], "concept_type": "measure"}
            for ind in indicators
        ]
    )

    continuous_path = osp.join(OUTPUT_DIR, "ddf--concepts--continuous.csv")
    continuous_concepts.to_csv(continuous_path, index=False)
    print(f"  Written: {continuous_path} ({len(continuous_concepts)} concepts)")

    # Discrete concepts (entity domains and other dimensions)
    # Note: age is not included as it's flattened into indicator names
    discrete_concepts = pd.DataFrame(
        [
            ["name", "Name", "string"],
            ["location", "Location", "entity_domain"],
            ["sex", "Sex", "entity_domain"],
            ["cause", "Cause", "entity_domain"],
            ["measure", "Measure", "entity_domain"],
            ["metric", "Metric", "entity_domain"],
            ["year", "Year", "time"],
        ],
        columns=["concept", "name", "concept_type"],
    )

    discrete_path = osp.join(OUTPUT_DIR, "ddf--concepts--discrete.csv")
    discrete_concepts.sort_values(by="concept").to_csv(discrete_path, index=False)
    print(f"  Written: {discrete_path} ({len(discrete_concepts)} concepts)")


def main():
    """Main ETL process."""

    print("=" * 60)
    print("IHME GBD 2023 ETL Process")
    print("=" * 60)

    # Load and concatenate all zip files from source directory
    df = load_all_source_data(SOURCE_DIR)

    if df is None:
        print("ERROR: Failed to load data!")
        return

    # Extract entities
    print("\n" + "=" * 60)
    entities = extract_entities(df)
    serve_entities(entities)

    # Get all indicators
    print("\n" + "=" * 60)
    indicators = get_all_indicators(df)
    print(f"Found {len(indicators)} unique indicators:")
    for ind in indicators:
        print(f"  - {ind['concept']}: {ind['name']}")

    # Create datapoint files
    serve_datapoints(df, indicators)

    # Create concept files
    serve_concepts(indicators, entities)

    print("\n" + "=" * 60)
    print("ETL Process Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
