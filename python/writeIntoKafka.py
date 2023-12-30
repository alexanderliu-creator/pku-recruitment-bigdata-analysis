from kafka import KafkaProducer
import json

producer = KafkaProducer(bootstrap_servers='kafka:9092', api_version=(3, 6, 1))

data = {
    "company": "Google",
    "comment": "I like it!",
    "label": 1,
    "create_time": "2023-12-21 23:01:34"
}

message = json.dumps(data)
topic = 'comment-topic'
producer.send(topic, value=message.encode('utf-8'))
producer.flush()
producer.close()
