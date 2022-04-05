from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
import yaml

app = FastAPI()
redis_password = ""

# Runs on different ports, fixes that issue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis

@app.get("/products")
def all():
    return [format(pk) for pk in Product.all_pks()]

def format(pk: str):
    product = Product.get(pk)

    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }

@app.post("/products")
def create(product: Product):
    product.save()
    return product

@app.get("/products/{pk}")
def get(pk: str):
    return Product.get(pk)

@app.delete("/products/{pk}")
def delete(pk: str):
    product = Product.delete(pk)
    return product