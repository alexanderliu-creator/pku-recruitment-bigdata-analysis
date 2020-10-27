[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/big-data-europe/Lobby)

# Docker multi-container environment with Hadoop, Spark and Hive

This is it: a Docker multi-container environment with Hadoop (HDFS), Spark and Hive. But without the large memory requirements of a Cloudera sandbox. (On my Windows 10 laptop (with WSL2) it seems to consume a mere 3 GB.)

The only thing lacking, is that Hive server doesn't start automatically. To be added when I understand how to do that in docker-compose.


## Quick Start

To deploy an the HDFS-Spark-Hive cluster, run:
```
  docker-compose up
```

`docker-compose` creates a docker network that can be found by running `docker network list`, e.g. `docker-hadoop-spark-hive_default`.

Run `docker network inspect` on the network (e.g. `docker-hadoop-spark-hive_default`) to find the IP the hadoop interfaces are published on. Access these interfaces with the following URLs:

* Namenode: http://<dockerhadoop_IP_address>:9870/dfshealth.html#tab-overview
* History server: http://<dockerhadoop_IP_address>:8188/applicationhistory
* Datanode: http://<dockerhadoop_IP_address>:9864/
* Nodemanager: http://<dockerhadoop_IP_address>:8042/node
* Resource manager: http://<dockerhadoop_IP_address>:8088/
* Spark master: http://<dockerhadoop_IP_address>:8080/
* Spark worker: http://<dockerhadoop_IP_address>:8081/
* Hive: http://<dockerhadoop_IP_address>:10000

## Quick Start HDFS

Find the Container ID of the namenode.
```
  docker ps |grep namenode

1df7a57164de        bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8          "/entrypoint.sh /run…"   27 hours ago        Up 12 hours (healthy)      0.0.0.0:9000->9000/tcp, 0.0.0.0:9870->9870/tcp             namenode

```

Copy breweries.csv to the namenode.
```
  docker cp breweries.csv 1df7a57164de:breweries.csv
```

Go to the bash shell on the namenode with that same Container ID of the namenode.
```
  docker exec -it 1df7a57164de bash
```


Create a HDFS directory /data//openbeer/breweries.

```
  hdfs dfs -mkdir /data
  hdfs dfs -mkdir /data/openbeer
  hdfs dfs -mkdir /data/openbeer/breweries
```

Copy breweries.csv to HDFS:
```
  hdfs dfs -put breweries.csv /data/openbeer/breweries/breweries.csv
```


## Quick Start Spark

Go to http://<dockerhadoop_IP_address>:8080 or http://localhost:8080/ on your Docker host (laptop). Here you find the spark:// master address:
```
  Spark Master at spark://452dd59615b0:7077
```

Go to the command line of the Spark master and start spark-shell.
```
  docker ps |grep spark
efef70177b0b        bde2020/spark-worker:3.0.0-hadoop3.2                     "/bin/bash /worker.sh"   27 hours ago        Up 12 hours                0.0.0.0:8081->8081/tcp                                     spark-worker-1
453dd19695b0        bde2020/spark-master:3.0.0-hadoop3.2                     "/bin/bash /master.sh"   27 hours ago        Up 12 hours                0.0.0.0:7077->7077/tcp, 6066/tcp, 0.0.0.0:8080->8080/tcp   spark-master

  docker exec -it 453dd19695b0 bash
  
  spark/bin/spark-shell --master spark://452dd59615b0:7077
```

Load breweries.csv from HDFS.
```
  val df = spark.read.csv("hdfs://namenode:8020/data/openbeer/breweries/breweries.csv")
  
  df.show()
+----+--------------------+-------------+-----+---+
| _c0|                 _c1|          _c2|  _c3|_c4|
+----+--------------------+-------------+-----+---+
|null|                name|         city|state| id|
|   0|  NorthGate Brewing |  Minneapolis|   MN|  0|
|   1|Against the Grain...|   Louisville|   KY|  1|
|   2|Jack's Abby Craft...|   Framingham|   MA|  2|
|   3|Mike Hess Brewing...|    San Diego|   CA|  3|
|   4|Fort Point Beer C...|San Francisco|   CA|  4|
|   5|COAST Brewing Com...|   Charleston|   SC|  5|
|   6|Great Divide Brew...|       Denver|   CO|  6|
|   7|    Tapistry Brewing|     Bridgman|   MI|  7|
|   8|    Big Lake Brewing|      Holland|   MI|  8|
|   9|The Mitten Brewin...| Grand Rapids|   MI|  9|
|  10|      Brewery Vivant| Grand Rapids|   MI| 10|
|  11|    Petoskey Brewing|     Petoskey|   MI| 11|
|  12|  Blackrocks Brewery|    Marquette|   MI| 12|
|  13|Perrin Brewing Co...|Comstock Park|   MI| 13|
|  14|Witch's Hat Brewi...|   South Lyon|   MI| 14|
|  15|Founders Brewing ...| Grand Rapids|   MI| 15|
|  16|   Flat 12 Bierwerks| Indianapolis|   IN| 16|
|  17|Tin Man Brewing C...|   Evansville|   IN| 17|
|  18|Black Acre Brewin...| Indianapolis|   IN| 18|
+----+--------------------+-------------+-----+---+
only showing top 20 rows

```

How cool is that? Your own Spark cluster to play with.


## Quick Start Hive

Find the Container ID of the Hive Server.

```
  docker ps |grep hive-server

60f2c3b5eb32        bde2020/hive:2.3.2-postgresql-metastore                  "entrypoint.sh /bin/…"   27 hours ago        Up 12 hours                       0.0.0.0:10000->10000/tcp, 10002/tcp                        hive-server

```

Go to the command line of the Hive server and start hiveserver2

```
  docker exec -it 60f2c3b5eb32 bash

  hiveserver2
```

Maybe a little check that something is listening on port 10000 now
```
  netstat -anp | grep 10000
tcp        0      0 0.0.0.0:10000           0.0.0.0:*               LISTEN      446/java

```

Okay. Beeline is the command line interface with Hive. Let's connect to hiveserver2 now.

```
  beeline
  
  !connect jdbc:hive2://127.0.0.1:10000 scott tiger
```

Didn't expect to encounter scott/tiger again after my Oracle days. But there you have it. Definitely not a good idea to keep that user on production.

Not a lot of databases here yet.
```
  show databases;
  
+----------------+
| database_name  |
+----------------+
| default        |
+----------------+
1 row selected (0.335 seconds)
```

Let's change that.

```
  create database openbeer;
  use openbeer;
```

And let's create a table.

```
CREATE EXTERNAL TABLE IF NOT EXISTS breweries(
    NUM INT,
    NAME CHAR(100),
    CITY CHAR(100),
    STATE CHAR(100),
    ID INT )
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
location '/data/openbeer/breweries';
```

And have a little select statement going.

```
  select name from breweries limit 10;
+----------------------------------------------------+
|                        name                        |
+----------------------------------------------------+
| name                                                                                                 |
| NorthGate Brewing                                                                                    |
| Against the Grain Brewery                                                                            |
| Jack's Abby Craft Lagers                                                                             |
| Mike Hess Brewing Company                                                                            |
| Fort Point Beer Company                                                                              |
| COAST Brewing Company                                                                                |
| Great Divide Brewing Company                                                                         |
| Tapistry Brewing                                                                                     |
| Big Lake Brewing                                                                                     |
+----------------------------------------------------+
10 rows selected (0.113 seconds)
```

There you go: your private Hive server to play with.


## Configure Environment Variables

The configuration parameters can be specified in the hadoop.env file or as environmental variables for specific services (e.g. namenode, datanode etc.):
```
  CORE_CONF_fs_defaultFS=hdfs://namenode:8020
```

CORE_CONF corresponds to core-site.xml. fs_defaultFS=hdfs://namenode:8020 will be transformed into:
```
  <property><name>fs.defaultFS</name><value>hdfs://namenode:8020</value></property>
```
To define dash inside a configuration parameter, use triple underscore, such as YARN_CONF_yarn_log___aggregation___enable=true (yarn-site.xml):
```
  <property><name>yarn.log-aggregation-enable</name><value>true</value></property>
```

The available configurations are:
* /etc/hadoop/core-site.xml CORE_CONF
* /etc/hadoop/hdfs-site.xml HDFS_CONF
* /etc/hadoop/yarn-site.xml YARN_CONF
* /etc/hadoop/httpfs-site.xml HTTPFS_CONF
* /etc/hadoop/kms-site.xml KMS_CONF
* /etc/hadoop/mapred-site.xml  MAPRED_CONF

If you need to extend some other configuration file, refer to base/entrypoint.sh bash script.
