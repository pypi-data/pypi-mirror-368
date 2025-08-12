#!/usr/local/bin/python3

# https://www.datacamp.com/courses/machine-learning-with-pyspark

# part 1: introduction

from pyspark.ml import Pipeline
from pyspark.ml.classification import (
    DecisionTreeClassifier,
    GBTClassifier,
    LogisticRegression,
)
from pyspark.ml.evaluation import (
    BinaryClassificationEvaluator,
    MulticlassClassificationEvaluator,
    RegressionEvaluator,
)
from pyspark.ml.feature import (
    IDF,
    Bucketizer,
    HashingTF,
    OneHotEncoderEstimator,
    StopWordsRemover,
    StringIndexer,
    Tokenizer,
    VectorAssembler,
)
from pyspark.ml.regression import LinearRegression
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_replace, round

# setup spark://<ip>:7077 - default port
# local[4] - local using 4 cores

spark = SparkSession.builder.master("local[*]").appName("first_spark_app").getOrCreate()

print(spark.version)
spark.stop()  # close SparkSession


spark.read.csv(file_path, header=True, inferSchema=True, nullValue="NA")  # read csv

# DenseVector
# SparseVector

# part 2: classification

# preprocess data
df = df.drop("flight")
df = df.filter("delay IS NOT NULL")
df = df.dropna()
print(df.count())

df = df.withColumn("km", round(df.mile * 1.60934, 0)).drop("mile")
df = df.withColumn("label", (flights_km.delay >= 15).cast("integer"))

indexer = StringIndexer(inputCol="col", outputCol="col_index")
indexer_model = indexer.fit(df)
df = indexer_model.transform(df)

assembler = VectorAssembler(
    inputCols=[
        "col1",
        "col2",
    ],
    outputCol="features",
)  # create assembler object
df_assembled = assembler.transform(df)
df_assembled.select("features", "delay")

df_train, df_test = df.randomSplit([0.8, 0.2], seed=1)  # split df

# decision tree
model = DecisionTreeClassifier().fit(df_train)  # create object and fit
prediction = model.transform(df_test)  # create predictions
prediction.groupBy("label", "prediction").count().show()

# logistic regression
model = LogisticRegression().fit(df_train)  # create object and fit
prediction = model.transform(df_test)
prediction.groupBy("label", "prediction").count().show()

# evaluation of model
# - accuracy = (TN + TP) / (TN + TP + FN + FP)
# - precision = TP / (TP + FP)
# - recall = TP / (TP + FN)

# weighted precision
multi_eval = MulticlassClassificationEvaluator()
print(
    multi_eval.evaluate(prediction, {multi_evaluator.metricName: "weightedPrecision"})
)

# AUC
binary_eval = BinaryClassificationEvaluator()
print(binary_eval.evaluate(prediction, {binary_evaluator.metricName: "areaUnderROC"}))


# preprocess text
rdd = rdd.withColumn(
    "text", regexp_replace(rdd.text, "[_():;,.!?\\-]", " ")
)  # remove punctuation
rdd = rdd.withColumn("text", regexp_replace(rdd.text, "[0-9]", " "))  # remove numbers
rdd = rdd.withColumn(
    "text", regexp_replace(rdd.text, " +", " ")
)  # remove multiple spaces
rdd = Tokenizer(inputCol="text", outputCol="words").transform(
    rdd
)  # split text into words
rdd = StopWordsRemover(inputCol="words", outputCol="terms").transform(
    rdd
)  # remove stop words
rdd = HashingTF(inputCol="terms", outputCol="hash", numFeatures=1024).transform(
    rdd
)  # hashing trick
rdd = (
    IDF(inputCol="hash", outputCol="features").fit(rdd).transform(rdd)
)  # convert hashed tot TF-IDF
# TF-IDF matrix reflects how important a word is to each document
rdd.select("terms", "features").show(4, truncate=False)


# part 3: regression

onehot = OneHotEncoderEstimator(inputCols=["cat_index"], outputCols=["cat_dummy"])
onehot = onehot.fit(df)
df = onehot.transform(df)
df.select("cat", "cat_idx", "cat_dummy").distinct().sort("cat_idx").show()


# create regression object and fit w/ all features
regression = LinearRegression(labelCol="label").fit(df_train)
predictions = regression.transform(df_test)  # create predictions
predictions.select("label", "prediction").show(5, False)
RegressionEvaluator(labelCol="label").evaluate(predictions)  # calc RMSE
print(regression.intercept)  # print intercepts
print(regression.coefficients)  # print coefficients


# create buckets + onehot encode
buckets = Bucketizer(
    splits=[0, 3, 6, 9, 12, 15, 18, 21, 24], inputCol="col", outputCol="col_bucket"
)
rdd = buckets.transform(rdd)
onehot = OneHotEncoderEstimator(inputCols=["col_bucket"], outputCols=["col_dummy"])
rdd = onehot.fit(rdd).transform(rdd)
rdd.select("col", "col_bucket", "col_dummy").show(5)


# regularization
# goal = use just enough features to get robust predictions, not use too many predictions
# - penalized regression, penalty for n predictors
# - lasso uses absolute value of the coefficinets
# - ridge uses square of the coefficients

# normal regression
regression = LinearRegression(labelCol="label").fit(
    df_train
)  # features are in the SparseVector column
predictions = regression.transform(df_test)
print(RegressionEvaluator(labelCol="label").evaluate(predictions))  # print RMSE
print(regression.coefficients)  # check if any are zero?

# use lasso regression (regularized with a L1 penalty) to create a more parsimonious model
regression = LinearRegression(labelCol="label", regParam=1, elasticNetParam=1).fit(
    df_train
)
predictions = regression.transform(df_test)
print(RegressionEvaluator(labelCol="label").evaluate(predictions))  # print RMSE
print(regression.coefficients)  # check if any are zerod / some reduced to 0


# part 4: ensembles & pipelines

# apply .fit() to df_test is called leakage, a pipeline will help to avoid this

# create pipeline stages
indexer = StringIndexer(inputCol="col", outputCol="col_idx")
onehot = OneHotEncoderEstimator(
    inputCols=["col_idx", "cat"], outputCols=["col_dummy", "cat_dummy"]
)
assembler = VectorAssembler(
    inputCols=["col_extra", "col_dummy", "cat_dummy"], outputCol="features"
)
regression = LinearRegression(labelCol="label")

# construct a pipeline, fit and transform
pipeline = Pipeline(stages=[indexer, onehot, assembler, regression])
pipeline = pipeline.fit(df_train)
predictions = pipeline.transform(df_test)

# construct a text pipeline, fit and transform
tokenizer = Tokenizer(inputCol="text", outputCol="words")
remover = StopWordsRemover(inputCol=tokenizer.getOutputCol(), outputCol="terms")
hasher = HashingTF(inputCol=remover.getOutputCol(), outputCol="hash")
idf = IDF(inputCol=hasher.getOutputCol(), outputCol="features")
logistic = LogisticRegression()
pipeline = Pipeline(stages=[tokenizer, remover, hasher, idf, logistic])


# create cross validatator
# - use each fold as test data and evaluate model performance
regression = LinearRegression(labelCol="label")
params = ParamGridBuilder().build()
evaluator = RegressionEvaluator(labelCol="label")
cv = CrossValidator(
    estimator=regression, estimatorParamMaps=params, evaluator=evaluator, numFolds=5
)

cv = cv.fit(df_train)


# create cross validator w/ pipeline and cv
indexer = StringIndexer(inputCol="col", outputCol="col_idx")
onehot = OneHotEncoderEstimator(
    inputCols=["col_idx", "cat"], outputCols=["col_dummy", "cat_dummy"]
)
assembler = VectorAssembler(
    inputCols=["col_extra", "col_dummy", "cat_dummy"], outputCol="features"
)
regression = LinearRegression(labelCol="label")
pipeline = Pipeline(stages=[indexer, onehot, assembler, regression])

cv = CrossValidator(
    estimator=pipeline, estimatorParamMaps=params, evaluator=evaluator, numFolds=5
)

cv = cv.fit(df_train)


# create cross validator w/ pipeline, gridsearch and cv
params = (
    ParamGridBuilder()
    .addGrid(regression.regParam, [0.01, 0.1, 1.0, 10.0])
    .addGrid(regression.elasticNetParam, [0.0, 0.5, 1.0])
    .build()
)

print(len(params))  # number of models

cv = CrossValidator(
    estimator=pipeline, estimatorParamMaps=params, evaluator=evaluator, numFolds=5
)

best_model = cv.bestModel  # get the best model
print(best_model.stages)  # see stages
print(best_model.stages[3].extractParamMap())  # get parameters
predictions = best_model.transform(df_test)  # create model
evaluator.evaluate(predictions)  # evaluate best model


# ensemble models

# - collection of models
# - wisdom of the crowd / models - you need diverse and independent models
# e.g. randomForest or GBT

tree = DecisionTreeClassifier().fit(df_train)
gbt = GBTClassifier().fit(flights_train)

# Compare AUC on testing data
evaluator = BinaryClassificationEvaluator()
evaluator.evaluate(tree.transform(df_test))
evaluator.evaluate(gbt.transform(df_test))
print(gbt.getNumTrees)
print(gbt.featureImportances)


# randomForest
forest = RandomForestClassifier()
params = (
    ParamGridBuilder()
    .addGrid(forest.featureSubsetStrategy, ["all", "onethird", "sqrt", "log2"])
    .addGrid(forest.maxDepth, [2, 5, 10])
    .build()
)
evaluator = BinaryClassificationEvaluator()

cv = CrossValidator(
    estimator=forest, estimatorParamMaps=params, evaluator=evaluator, numFolds=5
)

print(cv.avgMetrics)  # average auc for each cell in grid
print(max(cv.avgMetrics))  # auc of best model
print(cv.bestModel.explainParam("maxDepth"))
print(cv.bestModel.explainParam("featureSubsetStrategy"))

print(evaluator.evaluate(cv.transform(df_test)))  # best auc on df_test
