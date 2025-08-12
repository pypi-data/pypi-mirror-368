import cupy as cp
import numpy as np
import os
import math
import random
import re
import pickle
import sys

cp.random.seed()
cp.set_printoptions(precision=2,floatmode='fixed',suppress=True)

class Distributions(object):
  """Random training distributions for test modules.
  """

  def __init__(self):
    pass

  def linear_distribution(self,depth):
    """linear regression
    predict y from x for x-values on a random line with slope and intercept
    """
    # random input values
    x = cp.random.random((depth,1)).astype(cp.float64)
    # target weight, bias
    z = cp.random.random((2,1)).astype(cp.float64)
    # y = wx + b
    y = [ z[0] * x[j] + z[1] for j in range(0,len(x)) ]
    y = cp.array(y).astype(cp.float64)
    return x,y
  def logical_distribution(self,depth,mode):
    """boolean logic
    predict binary result for two binary inputs [0,1]
    choice of four boolean operations: and, or, xor, xnor
    """
    x = cp.round(cp.random.random((depth,2))).astype(cp.float64)
    y = cp.zeros([depth,1]).astype(cp.float64).flatten()
    if mode=="and":
      y = cp.array([x[j,0] * x[j,1] for j in range(0,len(x))])
    elif mode=="or":
      y = cp.array( [ cp.max(x[j]) for j in range(0,len(x)) ] )
    elif mode=="xor":
      y = cp.array([abs(x[j,0] - x[j,1]) for j in range(0,len(x))])
    elif mode=="xnor":
      y = cp.array([1 if x[j,0]==x[j,1] else 0 for j in range(0,len(x))])
    else:
      return None,None
    return x,y
  def arithmetic_distribution(self,depth,mode):
    """arithmetic operations
    predict arithmetic result for two input values
    select from five arithmetic operations: add, subtract, multiply, divide, zero (always predict 0)
    """
    x = cp.random.random((depth,2)).astype(cp.float64)
    y = cp.zeros([depth,1]).astype(cp.float64)
    if mode=="add":
      y = cp.array([x[j,0] + x[j,1] for j in range(0,len(x))]) # weights = 1
    elif mode=="subtract":
      y = cp.array([x[j,0] - x[j,1] for j in range(0,len(x))]) # w1 = 1, w2 = -1
    elif mode=="multiply":
      y = cp.array([x[j,0] * x[j,1] for j in range(0,len(x))])
    elif mode=="divide":
      y = cp.array([x[j,0] / x[j,1] for j in range(0,len(x))])
    elif mode=="zero": # weights = 0
      y = y.flatten()
    else:
      return None,None
    return x,y
  def summation(self,rows,cols,mode="summation"):
    """sum numbers in each row
    generates a matrix of zeros and ones
    mode=summation or one_hot
    for one hot mode, pass in one hot vectors and sum the number of ones in each row
    must declare NN model with particular number of output columns
    if mode=summation then declare NN model with one output column
    if mode=onehot then declare NN model with cols+1 output columns (for values from zero to # cols)
    """
    x = cp.array([random.randrange(2) for i in range(rows * cols)]).reshape(rows,cols)
    if mode=="summation":
      # y = a scalar for the number of ones in each x vector
      y = cp.array([[cp.sum(x[i])] for i in range(0,len(x))])
    elif mode=="one_hot":
      # y = one hot vector with a 1 in the place of the number of ones in x vector
      y = cp.array([[0] * (cols + 1) for i in range(rows)]) # Initialize y with the correct shape
      for i in range(rows):
        y[i,cp.sum(x[i])] = 1
    else:
      sys.exit("mode must be summation or one_hot")
    return x,y
  def sort(self,rows,cols):
    """numerical sort
    generates a matrix of any size
    sorts each row into order from smallest to largest
    """
    x = cp.random.random((rows,cols))
    y = cp.array([sorted(x[i]) for i in range(0,len(x))])
    return x,y
