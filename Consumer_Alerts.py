"""
    This program will continuously look for the messages from Producer of Health and it's parameters
    and listens messages from mentioned queue, alerts are raised. 
"""

# Import project libraries
import pika
import sys

def heartrate_callback(ch, method, properties, body):
    """
    heartrate_callback looks if the heart rate increases more than 100 or decreases less than 80 .
    """
    try:
        data = body.decode().split(",")
        heart_rate = int(data[2].split(":")[1].strip())

        if heart_rate > 100:
            print(f"!!! Critical !!! Heart Rate Elevated Alert !! {data}")
        elif heart_rate < 80:
            print(f"!!! Critical !!! Heart Rate Deprecating Alert !! {data}")
        else:
            print(f"[x] Heart Rate Vitals are Good for {data}")
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except ValueError:
        pass
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def bp_callback(ch, method, properties, body):
    """
    bp_callback checks the blodpressure and then gives alert or warning.
    """
    try:
        data = body.decode().split(",")
        systolic_bp = int(data[2].split('/')[0].strip())
        diastolic_bp = int(data[2].split('/')[1].strip())

        if systolic_bp > 120 or systolic_bp <= 90:
            print(f"!! Warning !! Blood Pressure Alert !! for {data[1]}")
        elif diastolic_bp < 80 or diastolic_bp > 95:
            print(f"!! Warning !! Blood Pressure Alert !! for {data[1]}")
        else:
            print(f"[x] Blood Pressure vitals are Good for {data}")

        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except ValueError:
        pass
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def temp_callback(ch, method, properties, body):
    """
    temp_callback looks for a potential changes in patients body temparature
    """
    try:
        data = body.decode().split(",")
        temp = float(data[2].split(":")[1].strip())

        if temp > 99.0:
            print(f"!! Warning !! Body Temparature Alert !! for {data}")
        else:
            print(f"[x] Body Temparature vitals are Good for {data}")

    # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except ValueError:
        pass
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def spo2_callback(ch, method, properties, body):
    """
    spo2_callback looks for a potential difference in the patients O2 levels and raise alert.
    """
    try:
        data = body.decode().split(",")
        spo2 = int(data[2].split(":")[1].strip())

        if spo2 <= 95 :
            print(f"!! Critical !! Low SPO2 levels for {data}")
        else:
            print(f"[x] SPO2 vitals are Good for {data}")

    # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except ValueError:
        pass
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)    


def main(hn: str,queue_name: str, queue_name1: str,queue_name2: str,queue_name3: str):
    """
    Continuously listen for a message across 4 queues and processes message using the
    appropriate callback functions.
    """
    try:
        # Create a connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
    except Exception as e:
        print()
        print("ERROR: connection to RabbitMQ server failed.")
        print(f"Verify the server is running on host={hn}.")
        print(f"The error says: {e}")
        print()
        sys.exit(1)

    try:    

        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_declare(queue=queue_name1, durable=True)
        channel.queue_declare(queue=queue_name2, durable=True)
        channel.queue_declare(queue=queue_name3, durable=True)

        # Set up the consumers for each queue
        channel.basic_consume(queue=queue_name, on_message_callback=heartrate_callback, auto_ack=False)
        channel.basic_consume(queue=queue_name1, on_message_callback=bp_callback, auto_ack=False)
        channel.basic_consume(queue=queue_name2, on_message_callback=temp_callback, auto_ack=False)
        channel.basic_consume(queue=queue_name3, on_message_callback=spo2_callback, auto_ack=False)

        # Inform the user that the consumer is ready to begin
        print(' [*] Waiting for messages. To exit press CTRL+C')
        
        # Start the consumers
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        print("Error connecting to RabbitMQ server: ", e)
    except KeyboardInterrupt:
        print("User has stopped the process.")
    except Exception as e:
        print("An unexpected error occurred: ", e)
    finally:
        try:
            connection.close()
        except ValueError: 
            pass

if __name__ == "__main__":
    main("localhost","heartbeat_alert","bloodpressure_alert","temp_alert","sp02_alert")