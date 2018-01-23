# -*- coding: utf-8 -*-

## test_attack.py -- sample code to test attack procedure
##
## Copyright (C) 2016, Nicholas Carlini <nicholas@carlini.com>.
##
## This program is licenced under the BSD 2-Clause licence,
## contained in the LICENCE file in this directory.

import tensorflow as tf
import numpy as np
import time

from setup_cifar import CIFAR, CIFARModel
from setup_mnist import MNIST, MNISTModel
#from setup_inception import ImageNet, InceptionModel

from l2_attack import CarliniL2
from l0_attack import CarliniL0
from li_attack import CarliniLi

import random
import matplotlib.pyplot as plt




def show(img):
    """
    Show MNSIT digits in the console.
    """
    remap = "  .*#"+"#"*100
    img = (img.flatten()+.5)*3
    if len(img) != 784: return
    print("START")
    for i in range(28):
        print("".join([remap[int(round(x))] for x in img[i*28:i*28+28]]))


def generate_data(data, samples, targeted=True, start=0, inception=False):
    """
    Generate the input data to the attack algorithm.
    data: the images to attack
    samples: number of samples to use
    targeted: if true, construct targeted attacks, otherwise untargeted attacks
    start: offset into data to use
    inception: if targeted and inception, randomly sample 100 targets intead of 1000
    """
    inputs = []
    targets = []
    for i in range(samples):
        if targeted:
            if inception:
                seq = random.sample(range(1,1001), 10)
            else:
                seq = range(data.test_labels.shape[1])

            for j in seq:
                if (j == np.argmax(data.test_labels[start+i])) and (inception == False):
                    continue
                inputs.append(data.test_data[start+i])
                targets.append(np.eye(data.test_labels.shape[1])[j])
        else:
            inputs.append(data.test_data[start+i])
            targets.append(data.test_labels[start+i])

    inputs = np.array(inputs)
    targets = np.array(targets)
    
    return inputs, targets


if __name__ == "__main__":
    with tf.Session() as sess:
        data, model =  MNIST(), MNISTModel("models/mnist", sess)
        attack = CarliniL2(sess, model, batch_size=9, max_iterations=1000,confidence=0)

        inputs, targets = generate_data(data, samples=1, targeted=True,
                                        start=0, inception=False)
        timestart = time.time()

         #ran=random.uniform(1,2)
         #ran= np.random.normal(loc=0, scale=1, size=None)
        adv = attack.attack(inputs, targets)
        timeend = time.time()
    
        print("Took",timeend-timestart,"seconds to run",len(inputs),"samples.")
        r = []
        s = []
        for i in range(len(adv)):
            print("Valid:")
            show(inputs[i])
            print("Adversarial:")
            show(adv[i])
            
            print(model.model.predict(adv[i:i+1]),end="")       
            print(np.sum((adv[i]-inputs[i])**2)**.5,np.argmax(model.model.predict(adv[i:i+1])))
            
            #difference array
            r.append(np.sort(model.model.predict(adv[i:i+1]))[0,-1]-np.sort(model.model.predict(adv[i:i+1]))[0,-2])
            print(r[i])
            
            #the probability that the second largest value is correct classification
            index=np.where((model.model.predict(adv[i:i+1]))==(np.sort(model.model.predict(adv[i:i+1]))[0,-2]))
            s.append(index[1][0] == 7)
            print("the probability that the second largest value is correct classification:",np.mean(s))
        
        #draw Scatter plot
        x=[0,1,2,3,4,5,6,8,9]
        y=r
        
        plt.xlabel("target classification")
        plt.ylabel("difference between max and the second")
        plt.title("source classification=7")
        plt.scatter(x,y,marker='o')
        plt.show()
        
'''
        for i in range(len(adv)):
#            print("Valid:")
#            show(inputs[i])
#            print("Adversarial:")
#            show(adv[i])
            
            print("classification",model.model.predict(adv[i:i+1]))
 #            r=np.mean(model.model.predict(adv[i:i+1]))
             
            print("total distortion",np.sum((adv[i]-inputs[i])**2)**.5)
 #            print(np.mean(model.model.predict(adv[i:i+1])))
             
            print(np.argmax(model.model.predict(adv[i:i+1])))
            print(np.argmax(model.model.predict(inputs[i:i+1])))
             
#             print(np.where(model.model.predict(adv[i:i+1])>r))
'''             
     
    
 
        
    


