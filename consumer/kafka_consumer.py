from kafka import KafkaConsumer, KafkaProducer
import json
import os
from datetime import datetime
import pandas as pd
from collections import Counter
import time

def process_message(message):
    # Convert the Unix timestamp in the message to a human-readable datetime format.
    message['timestamp'] = datetime.fromtimestamp(int(message['timestamp'])).isoformat()
    
    # Rename the 'ip' key in the message dictionary to 'ip_address' for clarity and consistency.
    message['ip_address'] = message.pop('ip')
        
    return message

def generate_insights(df):
    # Create a dictionary of insights from the DataFrame including counts and statistical data.
    insights = {
        "batch_size": len(df),  # Total number of messages in the batch.
        "start_time": df['timestamp'].min(),  # Earliest timestamp in the batch.
        "end_time": df['timestamp'].max(),  # Latest timestamp in the batch.
        "device_type_aggregation": df['device_type'].value_counts().to_dict(),  # Count of each device type.
        "top_10_locations": df['locale'].value_counts().nlargest(10).to_dict(),  # Top 10 most frequent locations.
        "bottom_5_locations": df['locale'].value_counts().nsmallest(5).to_dict(),  # Bottom 5 least frequent locations.
        "top_5_users": df['user_id'].value_counts().nlargest(5).to_dict(),  # Top 5 users with most messages.
    }
    return insights

def save_insights(insights, base_path='/app/insights/'):
    # Construct filename from the insights start and end time, and save to the specified path.
    filename = f"{base_path}insights_{insights['start_time']} to {insights['end_time']}.json"
    with open(filename, 'w') as f:
        json.dump(insights, f)  # Serialize insights dictionary to JSON and save.
    print(f"Insights saved to {filename}")

def main():
    # Initialize a KafkaConsumer with environment-specific configurations and JSON deserialization.
    consumer = KafkaConsumer(
        os.environ.get('INPUT_TOPIC', 'user-login'),  # Topic to consume from, default 'user-login'.
        bootstrap_servers=os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092'),  # Kafka cluster addresses.
        auto_offset_reset='earliest',  # Start reading at the earliest message.
        enable_auto_commit=True,  # Automatically commit offsets.
        group_id='my-consumer-group',  # Consumer group id for coordination.
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Deserialize messages from JSON.
    )

    # Initialize a KafkaProducer for sending messages with environment-specific configurations.
    producer = KafkaProducer(
        bootstrap_servers=os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092'),  # Kafka cluster addresses.
        value_serializer=lambda x: json.dumps(x).encode('utf-8')  # Serialize messages to JSON for sending.
    )

    output_topic = os.environ.get('OUTPUT_TOPIC', 'processed-data')  # Topic to send processed messages to.
    
    print("Starting to consume messages...")
    batch = []  # Initialize an empty list to collect a batch of messages.
    batch_size = 100  # Set the number of messages per batch.

    for message in consumer:
        try:
            processed_message = process_message(message.value)  # Process each message.
            if processed_message:
                batch.append(processed_message)  # Add processed message to the batch.
            
            if len(batch) >= batch_size:  # Check if the batch is ready to process.
                df = pd.DataFrame(batch)  # Convert batch to DataFrame for analysis.
                
                insights = generate_insights(df)  # Generate insights from the DataFrame.
                
                producer.send(output_topic, value=insights)  # Send insights to the output topic.
                producer.flush()  # Ensure all pending messages are sent to Kafka.
                
                save_insights(insights)  # Save the insights to a file.
                
                print(f"Processed {len(batch)} messages")
                print(f"Generated insights: {insights}")
                
                batch = []  # Reset batch after processing.
        except Exception as e:
            print(f"Error processing message: {str(e)}")  # Print any errors encountered during processing.

if __name__ == "__main__":
    main()
