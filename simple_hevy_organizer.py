#!/usr/bin/env python3
import csv
import os
import re
from dotenv import load_dotenv
import datetime
from pathlib import Path

load_dotenv()

import requests


def fetch_hevy_workouts_page(api_key, page=1, page_size=5):
    """Fetch workout data from the Hevy API."""
    url = f"https://api.hevyapp.com/v1/workouts?page={page}&pageSize={page_size}"
    headers = {"accept": "application/json", "api-key": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def convert_start_time_to_date(start_time):
    """Extract the date part from an ISO format timestamp."""
    return start_time.split("T")[0]


def calculate_workout_duration_minutes(start_time, end_time):
    """Calculate the duration in minutes between two timestamps."""
    if not start_time or not end_time:
        return None
    
    # Parse ISO format timestamps
    start = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    # Calculate duration in minutes
    duration = (end - start).total_seconds() / 60
    return round(duration, 1)


def sanitize_filename(name):
    """Convert a string to a valid filename by removing invalid characters."""
    # Replace invalid filename characters with underscores
    return re.sub(r'[\\/*?:"<>|]', "_", name)


def organize_workouts_by_date(workouts, output_dir="output", debug=False):
    """
    Organize workouts into folders by date and title, with CSV files for each workout.
    """
    # Create the output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Process each workout
    for workout in workouts.get("workouts", []):
        # Get workout date and title
        workout_date = convert_start_time_to_date(workout.get("start_time"))
        workout_title = workout.get("title", "Unnamed Workout")
        
        # Create a sanitized folder name with date and title
        folder_name = f"{workout_date}_{sanitize_filename(workout_title)}"
        workout_folder = output_path / folder_name
        
        # Create or recreate the workout folder
        if workout_folder.exists():
            import shutil
            shutil.rmtree(workout_folder)
            if debug:
                print(f"Removing existing workout folder: {workout_folder}")
        
        # Create the workout folder
        workout_folder.mkdir(exist_ok=True)
        
        # Get workout details
        start_time = workout.get("start_time")
        end_time = workout.get("end_time")
        description = workout.get("description", "")
        duration_minutes = calculate_workout_duration_minutes(start_time, end_time)
        
        # Create summary file for this workout
        summary_filename = workout_folder / "workout_summary.txt"
        
        with open(summary_filename, "w") as summary_file:
            summary_file.write(f"Workout: {workout_title}\n")
            summary_file.write(f"Date: {workout_date}\n")
            summary_file.write(f"Start Time: {start_time}\n")
            summary_file.write(f"End Time: {end_time}\n")
            summary_file.write(f"Total Duration: {duration_minutes} minutes\n\n")
            
            if description:
                summary_file.write(f"Description: {description}\n\n")
            
            summary_file.write("Exercise Summary:\n")
            exercise_counts = {}
            for exercise in workout.get("exercises", []):
                title = exercise.get("title")
                # Count the actual number of sets in this exercise
                set_count = len(exercise.get("sets", []))
                if title in exercise_counts:
                    exercise_counts[title] += set_count
                else:
                    exercise_counts[title] = set_count
            
            for exercise, count in exercise_counts.items():
                summary_file.write(f"- {exercise}: {count} sets\n")
            
            summary_file.write("\n")
            summary_file.write("General Notes:\n")
            summary_file.write("[Add your general notes about this workout here]\n")
        
        if debug:
            print(f"Created {summary_filename}")
        
        # Create CSV file for this workout
        csv_filename = workout_folder / "exercises.csv"
        
        # Define column headers with human-readable names
        headers = [
            "Exercise", 
            "Exercise Notes", 
            "Set Number", 
            "Repetitions", 
            "Weight (kg)", 
            "Duration (seconds)", 
            "Superset Group", 
            "Coach Feedback"
        ]
        
        with open(csv_filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            # Write exercise data
            for exercise in workout.get("exercises", []):
                exercise_name = exercise.get("title", "")
                exercise_notes = exercise.get("notes", "")
                
                for s in exercise.get("sets", []):
                    set_number = s.get("index")
                    reps = s.get("reps")
                    weight_kg = s.get("weight_kg")
                    duration_seconds = s.get("duration_seconds")
                    superset_id = exercise.get("superset_id")
                    
                    row = [
                        exercise_name,
                        exercise_notes,
                        set_number,
                        reps,
                        weight_kg,
                        duration_seconds,
                        superset_id,
                        ""  # Empty feedback column for the coach
                    ]
                    
                    if debug:
                        print(f"[{folder_name}] {row}")
                    
                    writer.writerow(row)
        
        if debug:
            print(f"Created {csv_filename}")
    
    return output_path


if __name__ == "__main__":
    api_key = os.environ.get("HEVY_API_KEY")
    if not api_key:
        raise RuntimeError("Please set the HEVY_API_KEY environment variable.")
    
    try:
        print("Fetching workouts from Hevy API...")
        workouts_json = fetch_hevy_workouts_page(api_key, page=1, page_size=5)
        
        # Print the structure of the first workout to understand the data
        if workouts_json.get("workouts") and len(workouts_json.get("workouts")) > 0:
            first_workout = workouts_json.get("workouts")[0]
            print("\nWorkout structure:")
            for key, value in first_workout.items():
                print(f"{key}: {type(value).__name__}")
        
        # Organize workouts into folders by date and title
        print("\nOrganizing workouts into folders...")
        output_path = organize_workouts_by_date(workouts_json, debug=True)
        print(f"\nWorkouts organized in: {output_path}")
        
    except Exception as e:
        print(f"Error processing workouts: {e}")
