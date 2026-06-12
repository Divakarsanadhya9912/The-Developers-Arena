```markdown
# Complete Weather Data Pipeline System

## Project Overview

This project is an end-to-end weather data engineering pipeline that extracts real-time weather data from the OpenWeatherMap API, validates and transforms the data, stores it in a MySQL database, and generates reports with automated monitoring.

---

## Features

- OpenWeatherMap API integration
- MySQL database with normalized tables
- ETL (Extract, Transform, Load) pipeline
- Data validation and quality checks
- Automated scheduling
- Logging and error handling
- Pipeline execution monitoring
- Historical weather storage
- Automated reports and alerts

---

## Technologies Used

- Python
- MySQL
- OpenWeatherMap API
- Requests
- Schedule
- Python Dotenv
- Pytest

---

## Project Structure

```

weather-data-pipeline/
│
├── README.md
├── requirements.txt
├── .env.example
├── src/
├── tests/
├── docs/
├── logs/
├── reports/
└── scripts/

````

---

## Database Schema

### cities
Stores city information.

### weather_data
Stores historical weather records.

### pipeline_logs
Stores ETL execution history.

---

## ETL Workflow

Extract → Validate → Transform → Load

1. Fetch weather data from OpenWeatherMap.
2. Validate incoming data.
3. Transform and clean records.
4. Store data in MySQL.
5. Log execution details.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/Divakarsanadhya9912/The-Developers-Arena.git
````

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=weather_pipeline
OPENWEATHER_API_KEY=your_api_key
```

---

## Running the Project

Run the pipeline:

```bash
python src/main.py
```

Run the scheduler:

```bash
python src/scheduler.py
```

Run tests:

```bash
pytest
```

---

## Sample Outputs

* Weather reports generated in `reports/`
* Logs generated in `logs/`
* Pipeline execution records stored in `pipeline_logs`

---

## Future Improvements

* Dashboard visualization
* Cloud deployment
* Multiple weather providers
* Email notifications for alerts

---

## Author

Name: Divakar Sanadhya

ID card Number: EMP20260110-093

```
```
