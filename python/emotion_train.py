import os
import sys
from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, HashingTF, IDF, StringIndexer, StopWordsRemover
from pyspark.ml.classification import NaiveBayes
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml import PipelineModel
import joblib

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("TextClassificationModelTraining") \
    .config("spark.driver.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .config("spark.executor.extraJavaOptions", "-Dfile.encoding=UTF-8") \
    .getOrCreate()

# 获取SparkContext对象
sc = spark.sparkContext

# 设置日志级别为ERROR
sc.setLogLevel("ERROR")

# Load dataset
weibo_senti_df = spark.read.csv("/python/data/weibo_senti_100k.csv", header=True, inferSchema=True)

# Split dataset
train_df, test_df = weibo_senti_df.randomSplit([0.7, 0.3], seed=42)

# Data preprocessing pipeline
tokenizer = Tokenizer(inputCol="review", outputCol="words")
remover = StopWordsRemover(inputCol="words", outputCol="filtered")
hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures")
idf = IDF(inputCol="rawFeatures", outputCol="features")
label_stringIdx = StringIndexer(inputCol="label", outputCol="labelIndex")
nb = NaiveBayes(featuresCol="features", labelCol="labelIndex")
pipeline = Pipeline(stages=[tokenizer, remover, hashingTF, idf, label_stringIdx, nb])


# Train model and save model
model = pipeline.fit(train_df)


# Evaluate model
test_predictions = model.transform(test_df)
evaluator = MulticlassClassificationEvaluator(labelCol="labelIndex", predictionCol="prediction", metricName="accuracy")
test_accuracy = evaluator.evaluate(test_predictions)
print(f"Test Dataset Accuracy: {test_accuracy}")

# 切记model_path不能改成python，会清空里面所有内容
model_path = "hdfs://namenode:9000/model/classfication"
model.write().overwrite().save(model_path)
# Stop Spark session
spark.stop()
