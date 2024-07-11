from kafka import KafkaConsumer, KafkaProducer
import json
import os
from datetime import datetime
import pandas as pd
from collections import Counter
import time

def process_message(message):
    # Convert Unix timestamp to datetime
    message['timestamp'] = datetime.fromtimestamp(int(message['timestamp'])).isoformat()
    
    # Rename 'ip' to 'ip_address' for consistency
    message['ip_address'] = message.pop('ip')
        
    return message

def generate_insights(df):
    insights = {
        "batch_size": len(df),
        "start_time": df['timestamp'].min(),
        "end_time": df['timestamp'].max(),
        "device_type_aggregation": df['device_type'].value_counts().to_dict(),
        "top_10_locations": df['locale'].value_counts().nlargest(10).to_dict(),
        "bottom_5_locations": df['locale'].value_counts().nsmallest(5).to_dict(),
        "top_5_users": df['user_id'].value_counts().nlargest(5).to_dict(),
    }
    return insights

def save_insights(insights, base_path='/app/insights/'):
    filename = f"{base_path}insights_{insights['start_time']} to {insights['end_time']}.json"
    with open(filename, 'w') as f:
        json.dump(insights, f)
    print(f"Insights saved to {filename}")

def main():
    consumer = KafkaConsumer(
        os.environ.get('INPUT_TOPIC', 'user-login'),
        bootstrap_servers=os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092'),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='my-consumer-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    producer = KafkaProducer(
        bootstrap_servers=os.environ.get('BOOTSTRAP_SERVERS', 'localhost:9092'),
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    output_topic = os.environ.get('OUTPUT_TOPIC', 'processed-data')
    
    print("Starting to consume messages...")
    batch = []
    batch_size = 100  # Process in batches of 100 messages

    for message in consumer:
        try:
            processed_message = process_message(message.value)
            if processed_message:
                batch.append(processed_message)
            
            if len(batch) >= batch_size:
                df = pd.DataFrame(batch)
                
                insights = generate_insights(df)
                
                # Send aggregated data to output topic
                producer.send(output_topic, value=insights)
                producer.flush()  # Ensure all messages are sent
                
                save_insights(insights)
                
                print(f"Processed {len(batch)} messages")
                print(f"Generated insights: {insights}")
                
                batch = []  # Clear the batch
        except Exception as e:
            print(f"Error processing message: {str(e)}")

if __name__ == "__main__":
    main()