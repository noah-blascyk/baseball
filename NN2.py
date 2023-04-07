# expanded 3-layer (1 hidden layer) neural network from
# https://iamtrask.github.io/2015/07/12/basic-python-network/

from re import L
import numpy as np
import matplotlib.pyplot as plt
from neuralnet import getInputData, getOutputData
from scipy.special import expit

# sigmoid function
def activation_sigmoid(x,deriv=False):
    if(deriv==True):
        return x*(1-x)
    else:
        return expit(x)

def activation_tanh(x,deriv=False):
    if (deriv==True):
        return 1-(np.tanh(x)**2)
    else:
        return np.tanh(x)

def activation_relu(x,deriv=False):
    if deriv == True:
        y = (x > 0) * 1
    return np.maximum(0, x)

# input data
X = np.array(getInputData([2010,2012,2014,2016,2018]))
                
# output data
y = np.array(getOutputData([2010,2012,2014,2016,2018]))

# seed random numbers to make calculation deterministic (a good practice)
np.random.seed(1)

# randomly initialize the weights with mean 0
syn0 = 2*np.random.random((36,12)) - 1
syn1 = 2*np.random.random((12,12)) - 1
syn2 = 2*np.random.random((12,1)) - 1
epoch_list = []
error_history = []

# run multiple epochs, where epoch = one forward pass and one backward 
# pass of all the training examples.
for j in range(60000):

    # Feed forward through layers 0, 1, and 2
    l0 = X     # input
    l1 = activation_tanh(np.dot(l0,syn0))
    l2 = activation_tanh(np.dot(l1,syn1))
    l3 = activation_sigmoid(np.dot(l2,syn2))

    # how much did we miss the target value?
    l3_error = y - l3
    error_history.append(np.mean(np.abs(l3_error)))
    epoch_list.append(j)
    
    if (j% 10) == 0:
        print ("epoch "+ str(j) + " Error: " + str(np.mean(np.abs(l3_error))))

    diff = l3_error.T[0]
        
    # in what direction is the target value?
    # were we really sure? if so, don't change too much.
    l3_delta = l3_error*activation_sigmoid(l2,deriv=True)

    # how much did each l1 value contribute to the l2 error (according to the weights)?
    l2_error = l3_delta.dot(syn1.T)
    
    # in what direction is the target l1?
    # were we really sure? if so, don't change too much.
    l2_delta = l2_error * activation_tanh(l1,deriv=True)

    l1_error = l2_delta.dot(syn0.T)
    l1_delta = l1_error * activation_tanh(l1,deriv=True)


    syn2 += l2.T.dot(l3_delta)
    syn1 += l1.T.dot(l2_delta)
    syn0 += l0.T.dot(l1_delta)

plt.figure(figsize=(15,5))
plt.plot(epoch_list, error_history)
plt.xlabel('Epoch')
plt.ylabel('Error')
plt.show()