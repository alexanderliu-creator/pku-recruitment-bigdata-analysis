docker cp csv hive-server:/csv
docker exec hive-server hive -f /csv/hive.sql