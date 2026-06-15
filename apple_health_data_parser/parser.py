import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path

RECORD_TYPES = {
    "HKQuantityTypeIdentifierStepCount":             "steps",
    "HKQuantityTypeIdentifierHeartRate":             "heart_rate",
    "HKCategoryTypeIdentifierSleepAnalysis":         "sleep",
    "HKQuantityTypeIdentifierDietaryWater":          "hydration",
    "HKQuantityTypeIdentifierDietaryEnergyConsumed": "nutrition"}


class HealthDataParser:

    def parse(self, filepath:str) -> pd.DataFrame:
        rows = []
        for event, element in ET.iterparse(Path(filepath), events=("end",)):
            if element.tag == "Record":
                row = self._extract_record(element)
                if row:
                    rows.append(row)
            elif element.tag == "Workout":
                rows.append(self._extract_workout(element))
            element.clear()
        return self._convert_types(pd.DataFrame(rows))


    def _convert_types(self, df: pd.DataFrame) -> pd.DataFrame:
        df["startDate"] = pd.to_datetime(df["startDate"], utc=True)
        df["endDate"]   = pd.to_datetime(df["endDate"],   utc=True)
        df["duration"]  = (df["endDate"] - df["startDate"]).dt.total_seconds()
        numeric_types   = {"steps", "heart_rate", "hydration", "nutrition"}
        mask = df["type"].isin(numeric_types)
        df["value"] = df["value"].where(~mask, pd.to_numeric(df["value"], errors="coerce"))
        sleep_mask   = df["type"] == "sleep"
        workout_mask = df["type"] == "workout"
        df.loc[sleep_mask,   "value"] = df.loc[sleep_mask,   "value"].str.replace("HKCategoryValueSleepAnalysis", "").str.lower()
        df.loc[workout_mask, "value"] = df.loc[workout_mask, "value"].str.replace("HKWorkoutActivityType",        "").str.lower()
        df = df.sort_values("startDate").reset_index(drop=True)
        return df


    def _extract_record(self, element:ET.Element) -> dict | None:
        hk_type = element.get("type")
        if hk_type not in RECORD_TYPES:
            return None
        return {
            "type":      RECORD_TYPES[hk_type],
            "startDate": element.get("startDate"),
            "endDate":   element.get("endDate"),
            "value":     element.get("value"),
            "duration":  None}
    

    def _extract_workout(self, element:ET.Element) -> dict:
        return {
            "type":      "workout",
            "startDate": element.get("startDate"),
            "endDate":   element.get("endDate"),
            "value":     element.get("workoutActivityType"),
            "duration":  None}
