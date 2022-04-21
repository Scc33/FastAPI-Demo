from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
import yaml
from starlette.requests import Request
import requests
import time

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

# Ideally this would be a different database
# A key point of microservices is that they have control of their own data
# Doesn't even have to be Redis could be a whole diff databse type
redis = get_redis_connection(
    host='redis-13781.c91.us-east-1-3.ec2.cloud.redislabs.com',
    port=13781,
    password=redis_password,
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pending, completed, refunded

    class Meta:
        database = redis

@app.get('/orders/{pk}')
def get(pk: str):
    return Order.get(pk)

@app.post("/orders")
async def create(request: Request, background_tasks: BackgroundTasks):
    body = await request.json() # One way of handling async tasks
    req = requests.get('http://localhost:8000/products/' + body['id']) # Handing request to other microservice
    product = req.json()

    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2 * product['price'],
        total=1.2* product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    order.save()

    background_tasks.add_task(order_completed, order)

    return order

# You could do something like handle payment processing here
def order_completed(order: Order):
    time.sleep(5) # Simulate processing time of a payment
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*')


# Redis Stream is a messaging event buses, like Kafka or RabbitMQ
# Messaging bus is a way to communicate between microservices
# They don't know about each other, they communicate via a messaging bus