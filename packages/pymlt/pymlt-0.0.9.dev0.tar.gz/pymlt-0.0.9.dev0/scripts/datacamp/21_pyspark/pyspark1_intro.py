#!/usr/local/bin/python3

# https://www.datacamp.com/courses/introduction-to-pyspark

# part 1: getting to know pyspark

import pyspark.ml.evaluation as evals
import pyspark.ml.tuning as tune
import pyspark.sql.functions as F
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.sql import SparkSession

print(sc)  # verify SparkContext, ie connection to cluster
print(sc.version)  # print spark version

spark = SparkSession.builder.getOrCreate()  # get existing one or creates one

print(spark)
print(spark.catalog.listTables())  # print the tables in the catalog
# catalog = attribute, listTables() = method

# get data
flights10 = spark.sql("select * from flights limit 10")
flights10.show()

# convert to pd
flight_counts = spark.sql(
    "select origin, dest, count(*) as cnt from flights group by origin, dest"
)
flight_counts = flight_counts.toPandas()
print(pd_counts.head())

# put a pd df into spark
df = pd.DataFrame(np.random.random(10))  # create df
sdf = spark.createDataFrame(df)  # local spark df
sdf.createOrReplaceTempView("sdf")  # create or replace temp
print(spark.catalog.listTables())  # sdf in catalog

# put a csv into spark
airports = spark.read.csv("/usr/local/share/datasets/airports.csv", header=True)
airports.show()

# part 2: manipulating data

flights = spark.table("flights")  # create df
flights.show()

# filter and select
flights.filter("distance > 1000")
flights.filter(flights.distance > 1000)
flights.filter(flights.origin == "SEA").filter(flights.dest == "PDX")

flights.select("tailnum", "origin", "dest")
flights.select(flights.tailnum, flights.origin, flights.dest)

# rename column
flights.withColumnRenamed("old", "new")

# create new column
flights.withColumn("duration_hrs", flights.air_time / 60)

avg_speed = (flights.distance / (flights.air_time / 60)).alias("avg_speed")
flights.select("origin", "dest", "tailnum", avg_speed)

flights.selectExpr("origin", "dest", "tailnum", "distance/(air_time/60) as avg_speed")

# aggregate
flights.filter(flights.origin == "PDX").groupBy().min("distance").show()
flights.filter(flights.origin == "SEA").groupBy().max("air_time").show()
flights.filter(flights.carrier == "DL" & flights.origin == "SEA").groupBy().avg(
    "air_time"
).show()
flights.withColumn("duration_hrs", flights.air_time / 60).groupBy().sum(
    "duration_hrs"
).show()

# Group by
flights.groupBy("tailnum").count().show()
flights.groupBy("origin").avg("air_time").show()

flights.groupBy("month", "dest").avg("dep_delay").show()
flights.groupBy("month", "dest").agg(F.stddev("dep_delay")).show

# joins
flights.join(airports, on="key", how="leftouter")

# part 3: getting started w/ ml pipelines

# pyspark.ml module w/ Transformer and Estimator classes

flights = flights.withColumn(
    "column", flights.column.cast("integer")
)  # cast to integer
flights = flights.withColumn(
    "plane_age", flights.year - flights.plane_year
)  # create new var

flights = flights.withColumn("is_late", flights.arr_delay > 0)  # create bolean
flights = flights.withColumn("label", flights.is_late.cast("integer"))  # rename en cast
flights = flights.filter(
    "arr_delay is not NULL and dep_delay is not NULL and air_time is not NULL and plane_year is not NULL"
)

# StringIndexer and OneHotEncoder
carr_indexer = StringIndexer(inputCol="carrier", outputCol="carrier_index")
carr_encoder = OneHotEncoder(
    inputCol="carrier_index", outputCol="carrier_fact"
)  # Create a OneHotEncoder

# VectorAssembler
vec_assembler = VectorAssembler(
    inputCols=["month", "air_time", "carrier_fact", "dest_fact", "plane_age"],
    outputCol="features",
)

# create pipeline
flights_pipe = Pipeline(
    stages=[dest_indexer, dest_encoder, carr_indexer, carr_encoder, vec_assembler]
)

# Fit and transform the data
piped_data = flights_pipe.fit(flights).transform(flights)

# Split the data into training and test sets
training, test = piped_data.randomSplit([0.6, 0.4])

# part 4: model tuning and selection

lr = LogisticRegression()  # create encstimator
evaluator = evals.BinaryClassificationEvaluator(
    metricName="areaUnderROC"
)  # create evaluator

grid = tune.ParamGridBuilder()  # create parameter grid, this is a class
grid = grid.addGrid(lr.regParam, np.arange(0, 0.1, 0.01))  # add hyperparameter
grid = grid.addGrid(lr.elasticNetParam, [0, 1])  # add hyperparameter
grid = grid.build()  # build the grid

cv = tune.CrossValidator(
    estimator=lr, estimatorParamMaps=grid, evaluator=evaluator
)  # create the CrossValidator, k-fold


best_lr = lr.fit(training)  # fit
models = cv.fit(training)  # fit cross validation models
best_lr = models.bestModel  # extract the best model
print(best_lr)

test_results = best_lr.transform(test)  # predict
print(evaluator.evaluate(test_results))  # evaluate performance
