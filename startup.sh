#!/bin/bash

docker-compose up -d
echo "start frontend and backend"
docker exec spark-master nohup python /python/frontend/web_vis/manage.py runserver 0.0.0.0:8000 > ./frontend.out 2>&1 &
docker exec spark-master nohup spark-submit --master spark://spark-master:7077 /python/backend/integration_app.py > ./backend.out 2>&1 &
docker exec spark-master nohup spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.8 /python/kafkaToSpark.py > ./kafkaToSpark.out 2>&1 &
docker exec spark-master nohup python /python/writeIntoKafka.py > ./writeIntoKafka.out 2>&1 &