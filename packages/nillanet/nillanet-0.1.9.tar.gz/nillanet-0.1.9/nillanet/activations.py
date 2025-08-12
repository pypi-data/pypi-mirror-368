import cupy as cp

class Activations(object):
  """Helper functions for NN class.
  """

  def __init__(self):
    pass

  def sigmoid(self,x):
    return 1 / (1 + cp.exp(-x))

  def sigmoid_derivative(self,x):
    return self.sigmoid(x) * (1 - self.sigmoid(x))

  def tanh(self,x):
    return cp.tanh(x) # return (1 - cp.exp(-2 * x)) / (1 + cp.exp(-2 * x))

  def tanh_derivative(self,x):
    return 1 - (x ** 2)

  def linear(self,x):
    return x

  def linear_derivative(self,x):
    if isinstance(x,cp.ndarray) or isinstance(x,list):
      return cp.atleast_2d(cp.ones(x.shape)).astype(cp.float64)
    return 1

  def relu(self,x):
    return cp.maximum(0,x)

  def relu_derivative(self,x):
    if isinstance(x,list) or isinstance(x,cp.ndarray):
      x[x > 0] = 1
      return x
    else:
      return 1 if x > 0 else 0

  def softmax_matrix(self,yhat):
    if not isinstance(yhat,cp.ndarray):
      sys.exit("error - only cp arrays allowed")
    y = cp.copy(yhat)
    minimum = cp.min(y)
    y += abs(minimum)
    maximum = cp.max(y)
    if maximum > 0:
      y /= maximum
    else:
      print("warning - zero matrix")
    results = []
    for row in y:
      summation = cp.sum([math.exp(x) for x in row])
      result = [math.exp(x) / summation for x in row]
      result = cp.array(result)
      results.append(result)
    results = cp.array(results)
    return results

  def softmax_matrix_derivative(self,yhat):
    gradient = cp.zeros(yhat.shape)
    for row in range(0,yhat.shape[0]):
      for i in range(0,len(yhat[row])):
        for j in range(0,len(yhat[row])):
          if i == j:
            gradient[row,i] = yhat[row,i] * (1-yhat[row,i])
          else:
            gradient[row,i] = -yhat[row,i]*yhat[row,j]
    return gradient

  def softmax_vector(self,yhat):
    y = None
    if isinstance(yhat,cp.ndarray):
      y = cp.copy(yhat)
      y = cp.array(list(y.flatten()))
    elif isinstance(yhat,list):
      y = cp.array(y)
    minimum = cp.min(y)
    y += abs(minimum)
    maximum = cp.max(y)
    if maximum > 0:
      y /= maximum
      summation = cp.sum([math.exp(x) for x in y])
      result = [math.exp(x) / summation for x in y]
      result = cp.array(result)
    else:
      result = cp.zeros(yhat.shape)
    return result

  def softmax_vector_derivative(self,yhat):
    gradient = []
    for i in range(0,len(yhat)):
      for j in range(0,len(yhat)):
        if i == j:
          gradient[i] = yhat[i] * (1-yhat[i])
        else:
          gradient[i] = -yhat[i]*yhat[j]
    return cp.array(gradient)

  def sum_to_one(self,yhat):
    y = cp.copy(yhat)
    y = cp.array(y)
    minimum = min(y)
    y += abs(minimum)
    maximum = max(y)
    y /= maximum
    summation = cp.sum(y)
    result = y / summation
    return result

