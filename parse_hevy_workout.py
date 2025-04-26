import csv
import os
from dotenv import load_dotenv

load_dotenv()

import requests


def fetch_hevy_workouts_page(api_key, page=1, page_size=5):
    url = f"https://api.hevyapp.com/v1/workouts?page={page}&pageSize={page_size}"
    headers = {"accept": "application/json", "api-key": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def parse_hevy_workout_json(workout_json):
    workout = {}
    workout["title"] = workout_json.get("name")
    workout["duration"] = workout_json.get("duration")
    workout["volume"] = workout_json.get("volume")
    return workout


def write_exercises_to_csv(workouts, filename="exercises.csv"):
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "workout_id",
                "workout_title",
                "exercise_title",
                "set_index",
                "reps",
                "weight_kg",
                "duration_seconds",
                "notes",
                "superset_id",
            ]
        )
        for workout in workouts.get("workouts", []):
            workout_id = workout.get("id")
            workout_title = workout.get("title")
            for exercise in workout.get("exercises", []):
                exercise_title = exercise.get("title")
                notes = exercise.get("notes", "")
                superset_id = exercise.get("superset_id")
                for s in exercise.get("sets", []):
                    writer.writerow(
                        [
                            workout_id,
                            workout_title,
                            exercise_title,
                            s.get("index"),
                            s.get("reps"),
                            s.get("weight_kg"),
                            s.get("duration_seconds"),
                            notes,
                            superset_id,
                        ]
                    )


if __name__ == "__main__":
    api_key = os.environ.get("HEVY_API_KEY")
    if not api_key:
        raise RuntimeError("Please set the HEVY_API_KEY environment variable.")
    try:
        workouts = fetch_hevy_workouts_page(api_key, page=1, page_size=5)
        from pprint import pprint

        pprint(workouts)
        write_exercises_to_csv(workouts, filename="exercises.csv")
        print("Exercises written to exercises.csv")
    except Exception as e:
        print(f"Error fetching workouts: {e}")
