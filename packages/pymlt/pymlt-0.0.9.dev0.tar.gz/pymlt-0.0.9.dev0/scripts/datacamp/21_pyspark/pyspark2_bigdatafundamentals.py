#!/usr/local/bin/python3

# https://www.datacamp.com/courses/big-data-fundamentals-with-pyspark

# part 1: introduction to big data analysis with spark

# 3 v's: volume, variety, velocity

# clustered computing
# parallel computing
# distributed computing
# batch processing
# real time processing

# hadoop/mapreduce framework, writen in Java
# spark framework for parallel and real time processing w/ clusters

# spark components:
# - spark core (rdd api)
# -- spark sql (this courses)
# -- spark ml lib (this course)
# -- graphx
# -- spark streaming

# local mode - on your laptop
# cluster mode - for production

# spark shell - command line interface for python

# SparkContext = entry point into world of spark
# connection to spark cluster

# libs for part 4
import pandas as pd
from pyspark.mllib.classification import LogisticRegressionWithLBFGS
from pyspark.mllib.clustering import KMeans
from pyspark.mllib.recommendation import ALS

sc.version  # spark version
sc.pythonVer  # python version used by spark
sc.master  # url of cluster

rdd = sc.parrallellize([1, 2, 3, 4, 5])  # load data
rdd = sc.textFile("test.txt")  # load text

sdf = sc.parrallellize(range(1, 101))  # load data

# lambda functions are anonymous functions, efficient w/ map() and filter()
# lambda similar to def
# lambda argument: expression
# lambda functions can have many argument, but only one expression

items = [1, 2, 3, 4]
print(items)
print(list(items))
print(list(map(lambda x: x * 2, items)))  # map(function, list)

# part 2: programming in pyspark rdd's

# rdd = resilient distributed dataset
# resilient bc broken partitions can be fixed

sdf = sc.parrallellize(range(10), minPartitions=6)
print(sdf.getNumPartitions())

# spark operations
# - transformations = returns a new rdd
# -- map()
# -- filter()
# -- flatMap() = multiple outputs, e.g. split sentence in words
# -- union() = combine rdd's
# - actions = conputation on rdd
# -- collect() = return array
# -- take() = head()
# -- count()

# map, filter and collect
rdd = sc.parrallellize([1, 2, 3, 4, 5])
print(rdd.map(lambda x: x**3).collect())
print(rdd.filter(lambda x: x > 2).collect())

# pair rdd, key-value pairs
t = [("sam", 23), ("sam", 34)]  # create tuple
rdd = sc.parallelize(t)

# rdd transformations on key-value pairs
# - reduceByKey(func)
# - groupByKey()
# - sortByKey()
# - join()

rdd.reduceByKey(lambda x, y: x + y)
rdd.sortByKey(ascending=False)

# advanced functions
rdd.saveAsTextFile()  # save rdd as text file
rdd.coalesce(1).saveAsTextFile()  # bring partitions back to one file
rdd.countByKey().collect()  # count values per key

# analyse large text
rdd = sc.textFile(file_path)
rdd = rdd.flatMap(lambda x: x.split())  # split lines to words
rdd.count()
rdd = rdd.filter(lambda x: x.lower() not in stop_words)  # remove stop words
rdd = rdd.map(lambda w: (w, 1))  # create tuplev
rdd = rdd.filter(lambda x: x.lower() not in stop_words)
rdd = rdd.reduceByKey(lambda x, y: x + y)  # count word occurences

# part 3: pyspark sql & dataframes

l = [("Mona", 20), ("Jennifer", 34), ("John", 20), ("Jim", 26)]  # create list of tuples
rdd = sc.parallelize(l)  # create rdd
df = spark.createDataFrame(rdd, schema=["Name", "Age"])  # create pyspark df

df = spark.read.csv(file_path, header=True, inferSchema=True)  # read from csv

# subsetting and cleaning
df.show(10)  # df = .show()
rdd.take(10)  # rdd = .take()
df.count()  # count rows
df.columns
df.select("col1", "col2", "col3")
df.dropDuplicates()
df.filter(df.sex == "f")

# running sql
df_temp.createOrReplaceTempView("df")  # create temp table
spark.sql("select col1 from df limit 10")
spark.sql("select col1 from df where sex == 'f'")

# visualization
pdf = df.toPandas()
pdf.plot(kind="barh", x="col1", y="col2", colormap="winter_r")  # horizontal bar chart
# pdf.plot(kind='density') # density plot
plt.show()

df.printSchema()  # print schema
df.describe().show()  # print basic statistics

# part 4: machine learning w/ pyspark mllib

# ml algorithms that can be processed in parallel
# 1.) collaborative filtering
# 2.) classification; binary and multi-class classification
# 3.) clustering

# mllib only works with rdd's

# 1.) collaborative filtering
# - user-user approch
# - item-item approach

rdd = sc.textFile(file_path)  # load ratings data
rdd = df.map(lambda l: l.split(","))  # split values
rdd = rdd.map(lambda line: rdd(int(line[0]), int(line[1]), float(line[2])))  # transform
rdd_train, rdd_test = rdd.randomSplit([0.8, 0.2])  # split into train/test

model = ALS.train(
    rdd_train, rank=10, iterations=10
)  # create model, rank = n latent factors
rdd_test = rdd_test.map(lambda p: (p[0], p[1]))  # drop rating column
rdd_pred = model.predictAll(rdd_test)  # create predictions
rdd_pred.take(5)  # print first 5 rows

rdd_test = rdd_test.map(lambda r: ((r[0], r[1]), r[2]))  # ((user, product), rating)
rdd_pred = rdd_pred.map(lambda r: ((r[0], r[1]), r[2]))  # ((user, product), rating)
rdd_join = rdd_test.join(rdd_pred)  # join
print(rdd_join.map(lambda r: (r[1][0] - r[1][1]) ** 2).mean())  # calc MSE

# 2.) classification

rdd_spam_t = sc.textFile(file_path_spam)  # load data w/ true/false
rdd_spam_f = sc.textFile(file_path_non_spam)

rdd_spam_words_t = rdd_spam_t.flatMap(
    lambda email: email.split(" ")
)  # split into words
rdd_spam_words_f = rdd_spam_f.flatMap(lambda email: email.split(" "))
print(rdd_spam_words_t.first())  # print first element

tf = HashingTF(numFeatures=200)  # create a HashingTf instance
features_t = tf.transform(rdd_spam_words_t)  # map words to features
features_f = tf.transform(rdd_spam_words_f)

samples_t = features_t.map(
    lambda features: LabeledPoint(1, features)
)  # label the features
samples_f = features_f.map(lambda features: LabeledPoint(0, features))

samples = samples_t.union(samples_f)  # combine two sets

samples_train, samples_test = samples.randomSplit([0.8, 0.2])  # split
model = LogisticRegressionWithLBFGS.train(samples_train)  # train model
predictions = model.predict(
    samples_test.map(lambda x: x.features)
)  # create predictions
samples_test = samples_test.map(lambda x: x.label).zip(
    predictions
)  # combine test w/ predictions
print(
    samples_test.filter(lambda x: x[0] == x[1]).count() / float(samples_test.count())
)  # print accuracy


# 3.) clustering

rdd = sc.textFile(file_path)
rdd = rdd.map(lambda x: x.split("\t"))
rdd = rdd.map(lambda x: [int(x[0]), int(x[1])])

# check a range of clusters to find the best fit
for clusters in range(13, 17):
    model = KMeans.train(rdd, clusters, seed=1)
    # calc WSSSE: within set sum of squared errors
    print(rdd.map(lambda point: error(point)).reduce(lambda x, y: x + y))

model = KMeans.train(rdd_split_int, k=15, seed=1)  # use k=15
df_centers = model.clusterCenters

# visualizing clusters
pdf = spark.createDataFrame(rdd, schema=["col1", "col2"]).toPandas()  # create pandas df
pdf_centers = pd.DataFrame(
    df_centers, columns=["col1", "col2"]
)  # creaet pandas df w/ centers
# Create an overlaid scatter plot
plt.scatter(pdf["col1"], pdf["col2"])
plt.scatter(pdf_centers["col1"], pdf_centers["col2"], color="red", marker="x")
plt.show()
