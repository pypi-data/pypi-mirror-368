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

class NN(object):

  """Minimal feedforward neural network using CuPy.

    This class implements batched SGD with configurable activation,
    classifier, and loss functions. Inputs/targets are kept on device
    to avoid host↔device copies.

    Args:
        input (cupy.ndarray | numpy.ndarray): Training inputs of shape
            (n_samples, n_features). If NumPy, it will be moved to device.
        output (cupy.ndarray | numpy.ndarray): Training targets of shape
            (n_samples, n_outputs). If NumPy, it will be moved to device.
        architecture (list[int]): Units per layer, including output layer.
        activation (Callable[[cupy.ndarray], cupy.ndarray]): Hidden-layer
            activation function.
        derivative1 (Callable[[cupy.ndarray], cupy.ndarray]): Derivative of
            ``activation`` evaluated at pre-activations.
        classifier (Callable[[cupy.ndarray], cupy.ndarray]): Output-layer
            transfer function (e.g., identity, sigmoid, softmax).
        derivative2 (Callable[[cupy.ndarray], cupy.ndarray]): Derivative of
            ``classifier`` evaluated at pre-activations.
        loss (Callable[..., cupy.ndarray]): Loss function that accepts
            named arguments (e.g., ``yhat``, ``y``) and returns per-sample
            losses or their average.
        derivative3 (Callable[..., cupy.ndarray]): Derivative of ``loss``
            with respect to predictions (same signature as ``loss``).
        learning_rate (float): SGD step size.
        dtype (cupy.dtype, optional): Floating dtype for parameters and data.
            Defaults to ``cupy.float32``.

    Attributes:
        X (cupy.ndarray): Training inputs with a prepended bias column,
            shape (n_samples, n_features + 1).
        Y (cupy.ndarray): Training targets on device.
        W (list[cupy.ndarray]): Layer weight matrices; ``W[i]`` has shape
            (in_features_i, out_features_i).
        architecture (list[int]): Layer sizes as provided.
        learning_rate (float): SGD step size (cast to ``dtype``).
  """

  def __init__(self, input, output, architecture, activation, derivative1,
               classifier, derivative2, loss, derivative3, learning_rate,
               dtype=cp.float32):
    # keep data on device and in a consistent dtype
    self.X = cp.asarray(input, dtype=dtype)
    self.Y = cp.asarray(output, dtype=dtype)

    # device-side bias column (avoid NumPy)
    bias = cp.ones((self.X.shape[0], 1), dtype=dtype)
    self.X = cp.concatenate((bias, self.X), axis=1)

    self.architecture = architecture
    self.activation = activation
    self.activation_derivative = derivative1
    self.classifier = classifier
    self.classifier_derivative = derivative2
    self.loss = loss
    self.loss_derivative = derivative3
    self.learning_rate = learning_rate #dtype.type(learning_rate)  # keep scalar dtype consistent

    # weights initialized from [-1, 1] (kept your scheme; could swap to Xavier/He later)
    self.W = []
    features = self.X.shape[1]
    for i in range(len(self.architecture)):
      nodes = self.architecture[i]
      w = 2 * cp.random.random((features, nodes), dtype=dtype) - 1
      self.W.append(w)
      features = nodes

  def train(self, epochs=1, batch=0):
    """Train the model using simple SGD.

        Args:
            epochs: Number of SGD steps to run.
            batch: One of:
                - ``1``: sample a single example per step (pure SGD)
                - ``0``: use all samples per step (full batch)
                - ``>1`` and ``< len(Y)``: use that mini-batch size per step

        Raises:
            SystemExit: If ``batch`` is invalid.
    """
    n = self.X.shape[0]
    if batch == 1:
      for _ in range(epochs):
        index = random.randint(0, n - 1)
        self.batch(self.X[index], self.Y[index])
    elif batch == 0:
      for _ in range(epochs):
        self.batch(self.X, self.Y)
    elif 1 < batch < n:
      for _ in range(epochs):
        index = random.randint(0, n - batch)
        x = self.X[index:index + batch]
        y = self.Y[index:index + batch]
        self.batch(x, y)
    else:
      sys.exit(f"improper batch size {batch}")

  def batch(self, x, y):
    """Run a single forward/backward/update step.

        Args:
            x (cupy.ndarray | numpy.ndarray): Inputs, shape (B, D) or (D,).
            y (cupy.ndarray | numpy.ndarray): Targets, shape (B, K) or (K,).

        Notes:
            Ensures inputs/targets reside on device and are at least 2D.
    """
    # ensure inputs live on device & 2D
    x = cp.atleast_2d(cp.asarray(x))
    y = cp.asarray(y)

    inputs = []
    raw_outputs = []

    # forward
    h = x
    for i in range(len(self.architecture)):
      inputs.append(h)
      z = cp.atleast_2d(h @ self.W[i])
      raw_outputs.append(z)
      if i == len(self.architecture) - 1:
        h = self.classifier(z)
      else:
        h = self.activation(z)

    # backward
    prev_grad = None
    for i in range(len(self.architecture) - 1, -1, -1):
      if i == len(self.architecture) - 1:
        loss_grad = self.loss_derivative(yhat=h, y=y)
        grad = cp.atleast_2d(loss_grad * self.classifier_derivative(raw_outputs[i]))
      else:
        grad = (prev_grad @ self.W[i + 1].T) * self.activation_derivative(raw_outputs[i])

      # in-place weight update
      self.W[i] -= self.learning_rate * (inputs[i].T @ grad)
      prev_grad = grad

  def predict(self, input):
    """Run a forward pass to produce predictions.

        Args:
            input (cupy.ndarray | numpy.ndarray): Inputs of shape
                (n_samples, n_features). If NumPy, it will be moved to device.

        Returns:
            cupy.ndarray: Model outputs of shape (n_samples, n_outputs).
    """
    x = cp.asarray(input)
    bias = cp.ones((x.shape[0], 1), dtype=x.dtype)
    x = cp.concatenate((bias, x), axis=1)

    h = x
    for i in range(len(self.architecture)):
      z = cp.atleast_2d(h @ self.W[i])
      if i == len(self.architecture) - 1:
        h = self.classifier(z)
      else:
        h = self.activation(z)
    return h

  def summary(self):
    """Print layer shapes and total parameter count."""
    total = 0
    for idx, w in enumerate(self.W):
      params = w.shape[0] * w.shape[1]
      total += params
      print(f"layer {idx} weights {tuple(w.shape)} parameters {params}")
    print(f"total parameters {total}")

