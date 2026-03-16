# EarthScape Climate Analysis

This repository contains a Django-based foundation for the EarthScape Climate Agency platform. It provides core modules for:

- Role-based authentication and authorization (`administrator`, `analyst`, `viewer`)
- Climate data ingestion metadata and ingestion runs
- Climate data processing jobs (MapReduce/Streaming/Hybrid)
- Machine learning model registry and predictions
- Dashboard summaries, alerts, and support tickets

## Implemented API Areas

- `api/users/*`: register, login, logout, profile
- `api/ingestion/*`: list sources, create/list datasets, trigger ingestion runs
- `api/processing/*`: create/list processing jobs
- `api/ml/*`: register models, create predictions, list models
- `api/dashboard/*`: summary, preferences, alert rules/events, support tickets

## Project Notes

- `ClimateDataset.hdfs_path` stores the HDFS pointer for dataset files.
- Processing and model entities include JSON configuration/metrics for extensibility.
- Dashboard includes support for configurable anomaly alerting and user feedback workflows.

## Run locally

```bash
cd earthscape
python manage.py makemigrations
python manage.py migrate
python manage.py test
python manage.py runserver
```
