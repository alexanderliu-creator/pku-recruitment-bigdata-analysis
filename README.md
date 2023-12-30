# 企业招聘与就业市场大数据分析



## 运行流程





## 说明

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



