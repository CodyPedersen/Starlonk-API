# Starlonk API

Interface to pull Starlink satellite metadata and predictions. Supports GraphQL and REST.
Utilizes Starlonk-Airflow as a data backend.

__Note: changes to pull recent predicitons has not been implemented, currently calculating predictions in realtime (slow)__

## Prerequisite steps
1. Requires NORAD satellite data ingested via [Starlonk Airflow](https://github.com/CodyPedersen/Starlonk-Airflow) (not great, but functional)
2. `pip3 install requirements.txt` (TODO: migrate to pipenv)

## FastAPI/GraphQL local testing setup
```python
python3 .
```

## FastAPI/GraphQL Docker or Kubernetes setup
see `deployment/README.md`

## Architecture diagram (next iteration)
![Architecture](https://github.com/CodyPedersen/Starlonk-API/blob/main/architecture.png?raw=true)
