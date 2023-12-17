import os
import pika
import json
import pymysql
from datetime import datetime
from decimal import Decimal

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, Decimal):
            return float(o)
        return super(DateTimeEncoder, self).default(o)

#credentials = pika.PlainCredentials('backend', 'password')
#parameters = pika.ConnectionParameters(
#    host='10.147.17.79',
    #host='10.147.17.34',
#    port=5672,
#    credentials=credentials)

primary_host = '10.147.17.79'
secondary_host = '10.147.17.34'
output_file = 'workout_data.txt'  # Specify your desired file name or path here

credentials = pika.PlainCredentials('backend', 'password')

def check_rabbitmq_host(host):
    try:
        parameters = pika.ConnectionParameters(host=host, port=5672, credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        connection.close()
        return True
    except pika.exceptions.AMQPConnectionError:
        return False

if not check_rabbitmq_host(primary_host):
    print(f"Primary host {primary_host} is not running RabbitMQ. Setting secondary host {secondary_host}.")
    parameters = pika.ConnectionParameters(host=secondary_host, port=5672, credentials=credentials)
else:
    parameters = pika.ConnectionParameters(host=primary_host, port=5672, credentials=credentials)

# Create connections and channels
consume1_connection = pika.BlockingConnection(parameters)
consume1_channel = consume1_connection.channel()
consume1_channel.queue_declare(queue='back-workout-request', durable=True)
consume1_channel.queue_bind(exchange='backend-database', queue='back-workout-request', routing_key='workout.back')

def save_to_txt(data):
    with open(output_file, 'w') as file:
        file.write(json.dumps(data) + '\n')

def get_mysql_connection():
    # Modify this with your MySQL connection details
    connection = pymysql.connect(
        host='10.147.17.44',
        user='rp54',
        password='Patel@123',
        database='ShapeShift',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection, connection.cursor()

def get_user_workouts(user_id, cursor):
    workout_sql = "SELECT * FROM workout WHERE user_id = %s"
    cursor.execute(workout_sql, (user_id,))
    workouts = cursor.fetchall()
    return workouts

def get_user_totals(user_id, cursor):
    query = """
        SELECT SUM(calories) as total_calories,
               SUM(protein) as total_protein,
               SUM(carbohydrates) as total_carbohydrates,
               SUM(fat) as total_fat,
               SUM(sugar) as total_sugar
        FROM nutrition_data
        JOIN meals ON nutrition_data.meal_id = meals.meal_id
        WHERE meals.user_id = %s
    """
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    return result

def callback_and_insert(ch, method, properties, body):
    data = json.loads(body.decode('utf-8'))
    print("Received data from backend:", data)

    try:
        email = data.get('email')
        workout = data.get('workout')
        print("Processing Data:", email, workout)

        # Connect to MySQL
        db_connection, cursor = get_mysql_connection()

        try:
            user_sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(user_sql, (email,))
            user = cursor.fetchone()

            if user:
                # Insert workout information into the 'workout' table
                insert_workout_sql = "INSERT INTO workout (user_id, workout_name) VALUES (%s, %s)"
                cursor.execute(insert_workout_sql, (user['user_id'], workout))
                db_connection.commit()
                print(f"Workout '{workout}' added for user {email}")

                # Fetch workouts for the user
                workouts = get_user_workouts(user['user_id'], cursor)

                # Fetch user totals
                user_totals = get_user_totals(user['user_id'], cursor)

                # Send success message back to the queue with user information, workouts, and user totals
                success_message = {
                    'status': 'success',
                    'message': f'Successfully added workout "{workout}" for {email}',
                    'user_data': {
                        'email': user['email'],
                        'password': user['password'],
                        'weight': user['weight'],
                        'height': user['height'],
                        'goal': user['goal'],
                        'first_name': user['first_name'],
                        'last_name': user['last_name'],
                    },
                    'workouts': workouts,
                    'user_totals': user_totals
                }
                ch.basic_publish(
                    exchange='backend-database',
                    routing_key='workout.data',
                    body=json.dumps(success_message, cls=DateTimeEncoder),
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                    )
                )

            else:
                print(f"User with email {email} not found in the database. Skipping workout addition.")

        except Exception as e:
            print(f"Error reading and updating database: {e}")

        finally:
            db_connection.close()

        save_to_txt(data)

    except Exception as e:
        print(f"Error processing message: {e}")

if __name__ == "__main__":
    consume1_channel.basic_consume(queue='back-workout-request', on_message_callback=callback_and_insert, auto_ack=True)

    try:
        print('Workout is [*] Waiting for messages. To exit press CTRL+C')
        consume1_channel.start_consuming()

    except KeyboardInterrupt:
        consume1_channel.stop_consuming()

    consume1_connection.close()
