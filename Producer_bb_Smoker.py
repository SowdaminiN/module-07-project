"""
The project is to create a producer that reads sensor data from the CSV file 
The CSV file contains readings related to each patient.

Modified By : Sowdamini Nandigama
Original Source : Denise Case
Date: 10/05/2023
"""

import pika
import sys
import webbrowser
import csv
import socket

def offer_rabbitmq_admin_site():
    """Offer to open the RabbitMQ Admin website"""
    ans = input("Would you like to monitor RabbitMQ queues? y or n ")
    print()
    if ans.lower() == "y":
        webbrowser.open_new("http://localhost:15672/#/queues")
        print()

def send_patient_details(host: str, queue_name: str, queue_name1: str, queue_name2: str, queue_name3: str):
    """
    Creates and sends a message to queue each execution.

    """
    host = "localhost"
    port = 9999
    address = (host, port)

    # use the socket constructor to create a socket object we'll call sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

     # read from a file to get smoker data
    input_file = open("Health_Dataset.csv", "r")

     # create a csv reader 
    reader = csv.reader(input_file, delimiter=",")


    for row in reader:
        # read a row from the file
        PatientID, FirstName, LastName, DateOfBirth, Gender, AdmissionDate, VitalSignsID, HeartRatePerMin, BloodPressureMMHG, SPO2, Temperature, TimeStamp = row

        try:
            # create a blocking connection to the RabbitMQ server
            conn = pika.BlockingConnection(pika.ConnectionParameters(host))
            # use the connection to create a communication channel
            ch = conn.channel()

            ch.queue_declare(queue=queue_name, durable=True)    
            ch.queue_declare(queue=queue_name1, durable=True)
            ch.queue_declare(queue=queue_name2, durable=True)
            ch.queue_declare(queue=queue_name3, durable=True)    

            try:
                HeartRatePerMin= int(HeartRatePerMin)
                Patient_Name = f"{FirstName} {LastName}"
                PatientID= int(PatientID)
                # create a message from our data
                Patient_details = f"PatientID:{PatientID},Name:{Patient_Name},Heart_Rate:{HeartRatePerMin}"
                # prepare a binary (1s and 0s) message to stream
                MESSAGE = Patient_details.encode()
                # use the socket sendto() method to send the message
                sock.sendto(MESSAGE, address)
                ch.basic_publish(exchange="", routing_key=queue_name, body=MESSAGE)
                # print a message to the console for the user
                print(f" [x] Sent {MESSAGE} for Patient with ID {PatientID}")
            except ValueError:
                pass

            try:
                Patient_Name = f"{FirstName} {LastName}"
                PatientID= int(PatientID)
                # create a message from our data
                Patient_details = f"PatientID:{PatientID},Name:{Patient_Name},BP:{BloodPressureMMHG}"
                # prepare a binary (1s and 0s) message to stream
                MESSAGE = Patient_details.encode()
                # use the socket sendto() method to send the message
                sock.sendto(MESSAGE, address)
                ch.basic_publish(exchange="", routing_key=queue_name1, body=MESSAGE)
                # print a message to the console for the user
                print(f" [x] Sent {MESSAGE} for Patient with ID {PatientID}")
            except ValueError:
                pass

            try:
                Temp1= round(float(Temperature),1)
                Patient_Name = f"{FirstName} {LastName}"
                PatientID= int(PatientID)
                # create a message from our data
                Patient_details = f"PatientID:{PatientID},Name:{Patient_Name},Temp:{Temp1}"
                # prepare a binary (1s and 0s) message to stream
                MESSAGE = Patient_details.encode()
                # use the socket sendto() method to send the message
                sock.sendto(MESSAGE, address)
                ch.basic_publish(exchange="", routing_key=queue_name2, body=MESSAGE)
                # print a message to the console for the user
                print(f" [x] Sent {MESSAGE} for Patient with ID {PatientID}")
            except ValueError:
                pass

            try:
                spo2= int(SPO2)
                Patient_Name = f"{FirstName} {LastName}"
                PatientID= int(PatientID)
                # create a message from our data
                Patient_details = f"PatientID:{PatientID},Name:{Patient_Name},SPO2:{spo2}"
                # prepare a binary (1s and 0s) message to stream
                MESSAGE = Patient_details.encode()
                # use the socket sendto() method to send the message
                sock.sendto(MESSAGE, address)
                ch.basic_publish(exchange="", routing_key=queue_name3, body=MESSAGE)
                # print a message to the console for the user
                print(f" [x] Sent {MESSAGE} for Patient with ID {PatientID}")
            except ValueError:
                pass

        except pika.exceptions.AMQPConnectionError as e:
                print(f"Error: Connection to RabbitMQ server failed: {e}")
                sys.exit(1)

        finally:
            # close the connection to the server
            conn.close()

if __name__ == "__main__":  
    # ask the user if they'd like to open the RabbitMQ Admin site
    offer_rabbitmq_admin_site()
 
    # send the message to the queue
    send_patient_details("localhost","heartbeat_alert","bloodpressure_alert","temp_alert","sp02_alert")