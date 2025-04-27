# Hevy Workout Organizer

This project helps you organize your Hevy workout data into a structured folder system for sharing with your coach.

## Features

- Fetches workout data from the Hevy API
- Organizes workouts into folders by date and title
- Creates CSV files with exercise details and a column for coach feedback

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Hevy API key:

```
HEVY_API_KEY=your_api_key_here
```

## Usage

```bash
python simple_hevy_organizer.py
```

This will:
- Fetch your latest workouts from Hevy
- Create folders for each workout (named with date and title)
- Generate CSV files with exercise details

## Workflow

1. Run `simple_hevy_organizer.py` to fetch new workouts
2. Manually upload the workout folders to your preferred cloud storage
3. Add workout videos to the folders from your phone
4. Your coach can add feedback in the "Coach Feedback" column of the CSV files

## Files

- `simple_hevy_organizer.py`: Fetches workout data and organizes it into folders
- `requirements.txt`: List of required Python packages
- `.env`: Contains your Hevy API key (not tracked in git)
