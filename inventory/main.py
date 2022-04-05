from fastapi import FastAPI
from redis_om import get_redis_connection
import yaml

app = FastAPI()
redis_password = ""

with open("../config/secrets-local.yaml", "r") as stream:
    try:
        redis_password = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

redis = get_redis_connection(
    host='redis-13781.c91.us-east-1-3.ec2.cloud.redislabs.com',
    port=13781,
    password=redis_password,
    decode_responses=True
)


@app.get("/")
async def root():
    return {"message": redis_password}