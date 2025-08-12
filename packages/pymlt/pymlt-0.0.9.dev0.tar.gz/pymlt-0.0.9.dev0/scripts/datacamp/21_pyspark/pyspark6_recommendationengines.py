#!/usr/local/bin/python3

# https://www.datacamp.com/courses/recommendation-engines-in-pyspark

# part 1: recommendations are everywhere

# - content-based filtering vs collaborative filtering
# - explicit vs implicit ratings

# ALS creates latent features
# rank = n latent features, i.e. group created from paterns
# values in cell indicates how much the product or item falls into these groups


# matrix multiplication

import numpy as np

a = np.array([[10, 12], [15, 18]])
b = np.array([[10, 12], [15, 18]])
c = np.dot(a, b)
print(c)  # matrix multiplication
# n rows of first and n cols of second must be similar to do matrix multiplication

# matrix factorization = opposite to multiplication
# - split matrix and approximate the values in two matrices, i.e. reverse multiplication
# - in case of CF-ALS, only non-negative values

# when not all values are known, using matrix factorization, the values can be inferred
# see: https://campus.datacamp.com/courses/recommendation-engines-in-pyspark/how-does-als-work?ex=4


# ALS works well with sparse matrices, i.e. a lot of NA's
# - r = rating, u = user, p = product
# step 1: create two matrices with n latent factors
# step 2: na's in p matrix are filled with random number - RMSE is calculated w/ known r
# step 3: na's in u matrix are ajusted
# step 4: etc, etc, -- each iteration the RMSE goes down
# step 5: final iteration, both matrices are multiplied and na's are filled with predictions
# -- with a least one rating in every row and a least one user in every column, predictions can be made

# estimate recommendations
UP = np.matmul(U, P)
print(pd.DataFrame(UP, columns=P.columns, index=U.index))

# get RMSE
getRMSE(pred_matrix, actual_matrix)
getRMSEs(listOfPredMatrices, actualValues)

# data preparation
# - long, row-based df is needed
# - use wide_to_long function if needed

# progress: https://campus.datacamp.com/courses/recommendation-engines-in-pyspark/how-does-als-work?ex=10
