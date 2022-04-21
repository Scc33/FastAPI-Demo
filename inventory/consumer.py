from main import redis, Product
import time

key = 'order_completed'
group = 'inventory-group'

try:
    redis.xgroup_create(key, group)
except:
    print('Group already exists')

# get event from Redis stream
while True:
    try: 
        results = redis.xreadgroup(group, key, {key: '>'}, None) # get all th events
        if result != []:
            for result in results:
                obj = result[1][0][1]
                product = Product.get(obj['product_id'])
                print(product)
                product.quantity -= int(obj['quantity'])
                product.save()
    except Exception as e:
        print(e)
    time.sleep(1)