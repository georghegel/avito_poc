import psycopg2

# postgresql connect
db_connection = psycopg.Connection.connect("")
def add_to_order(
  user_id: int,
  order_id:int,
  item_id: int,
  quantity: int,
  price: int):
    if not all(isinstance(p, int) for p in [user_id, order_id, item_id, quantity, price]):
        return {"error": "wrong type"}

    cursor = db_connection.execute(
        'select from "Items" where id = %s', (item_id,)
    )

    current_price = cursor.fetchone()[0] # fetchone might not return accessible data, so [0] can raise an exception

    if current_price != price:
        return {'error': 'Price has been changed. Try again'}

    cursor = db_connection.execute(
        'insert into "Orders" values (%s, %s, %s, %s, %s)', # we don't sanitize those parameters
        (user_id, order_id, item_id, quantity, price)
    )
    return {'result' : cursor.fetchone()[0]}

def show_order(order_id: int, user_id: int):
    try:
        cursor = db_connection.execute(
            'select from "Orders" where id = {}'.format(order_id) # SQLi
        )
        order_info = cursor.fetchone()[0]
        return f'<html><body><p>{order_info}</p></body></html>' # possible HTML injection vector attack
    except Exception as e:
        return (
           f'<html><body><p>Error was happend for {order_id}'
           '</p></body></html>')