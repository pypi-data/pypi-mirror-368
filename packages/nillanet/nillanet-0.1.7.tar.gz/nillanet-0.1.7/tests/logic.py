from nillanet.model import NN
from nillanet.activations import Activations
from nillanet.loss import Loss
from nillanet.distributions import Distributions

d = Distributions()
x,y = d.logical_distribution(10,"xor")
print(x.shape)
print(y.shape)
print(x)
print(y)

a = Activations()
activation = a.sigmoid
derivative1 = a.sigmoid_derivative
classifier = a.sigmoid
derivative2 = a.sigmoid_derivative

l = Loss()
loss = l.mse
derivative3 = l.mse_derivative

input = x
output = y
architecture = [4,8,1]
learning_rate = 0.1

model = NN(input,output,architecture,activation,derivative1,classifier,derivative2,loss,derivative3,learning_rate)
model.train(10000,0)
prediction = model.predict(x)

print("prediction")
print(prediction)
print("expected")
print(y)
