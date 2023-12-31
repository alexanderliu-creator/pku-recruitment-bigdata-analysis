# 企业招聘与就业市场大数据分析


## 运行流程

**相关依赖安装**

pip install -r requirements.txt

**启动项目**

cd docker-hadoop-hive-spark

bash startup.sh

**检查服务**

- 数据分析看板：http://127.0.0.1:8000/
- Namenode: http://127.0.0.1:9870/dfshealth.html#tab-overview
- Datanode: http://127.0.0.1:9864/
- Spark master: http://127.0.0.1:8080/
- Spark worker: http://127.0.0.1:8081/
- ResourceManager: http://localhost:8088/cluster
- NodeManager: http://localhost:8042/node
- HistoryServer: http://localhost:8188/applicationhistory
- HiveServer2: http://localhost:10002/
- Spark Master: http://localhost:8080/
- Spark Worker: http://localhost:8081/
- Spark Job WebUI: http://localhost:4040/ (当 Spark 任务在 spark-master 运行时才可访问)
- hue: http://localhost:8889/


## 说明
### 模型服务
调用前端预测功能后，请稍等片刻，spark集群运行模型需要一定的时间

### 可视化前端

为了前端内容的顺畅显示，前期我们将数据一次性从hive中导出为csv，而不需每次启动前端调用spark集群。

以导出“公司常见福利词”为例，从hive中导出hql命令如下：

```sql
set hive.exec.mode.local.auto=true;
set hive.exec.mode.local.auto.inputbytes.max=52428800;
set hive.exec.mode.local.auto.input.files.max=10;

INSERT OVERWRITE DIRECTORY 'welfare.csv'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
SELECT fl, count(1)
FROM (
    SELECT b.fl
    FROM job
    LATERAL VIEW explode(split(welfare, '、')) b AS fl
) AS a
WHERE fl <> '其他'
GROUP BY fl;

```



