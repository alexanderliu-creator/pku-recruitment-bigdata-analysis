from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, ByteType, TimestampType
from pyspark.sql.functions import from_json, col

topic_name = "comment-topic"
hive_table = "bigdata.comment_table"

# 对每个batch进行处理的函数
def foreach_batch_function(df, epoch_id):
    df.write.insertInto(hive_table, overwrite=False)

# 创建spark对话，连接hive
spark = SparkSession \
    .builder \
    .config("spark.sql.catalogImplementation", "hive") \
    .enableHiveSupport() \
    .getOrCreate()

# # 读取数据到DataFrame
# data = [("a", "b", 0, "2023-12-20 22:00:00")]
# df = spark.createDataFrame(data, ["company", "comment", "label", "create_time"])
# print(df)

# 将DataFrame插入Hive表
# df.write.insertInto(hive_table, overwrite=False)

# 创建流读取 Kafka 主题数据
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", topic_name) \
    .option("startingOffsets", "earliest") \
    .option("group.id", 1) \
    .load()

# # # 跳过第一条消息
# # df = df.filter(col("offset") > 0)

# 使用json_schema将数据解析为json数据
json_schema = StructType([
    StructField("company", StringType()),
    StructField("comment", StringType()),
    StructField("label", ByteType()),
    StructField("create_time", TimestampType())
])
df = df.withColumn("json_data", from_json(
    col("value").cast("string"), json_schema))

# 启动流，持续监测
df.select("json_data.company", "json_data.comment", "json_data.label", "json_data.create_time") \
    .writeStream \
    .foreachBatch(foreach_batch_function) \
    .start() \
    .awaitTermination()

# df.selectExpr("json_data.create_time") \
#     .writeStream \
#     .outputMode("append") \
#     .format("console") \
#     .start() \
#     .awaitTermination()
