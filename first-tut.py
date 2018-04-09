#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 20:30:09 2018

@author: MichaelAbdelmalek
"""

import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from tensorflow.examples.tutorials.mnist import input_data

data = input_data.read_data_sets("data/MNIST", one_hot = True)

print("The Sizes are :")
print("- Training data:\t{}".format(len(data.train.labels)))
print("- Test data:\t\t{}".format(len(data.test.labels)))
print("- Validation data:\t{}".format(len(data.validation.labels)))

data.test.cls = np.array([label.argmax() for label in data.test.labels])

num_classes = 10

img_size = 28
img_size_flat = img_size * img_size
img_shape = (img_size, img_size)

def plot_images(images, cls_true, cls_pred = None):
    assert len(images) == len(cls_true) == 9
    
    fig, axes = plt.subplots(3,3)
    fig.subplots_adjust(hspace = 0.3, wspace = 0.3)
    
    for i, ax in enumerate(axes.flat):
        ax.imshow(images[i].reshape(img_shape), cmap = 'binary')
        
        if cls_pred is None:
            xlabel = 'True: {0}'.format(cls_true[i])
        else:
            xlabel = 'True: {0}, Pred: {1}'.format(cls_true[i],cls_pred[i])
            
        ax.set_xlabel(xlabel)
        ax.set_xticks([])
        ax.set_yticks([])
    plt.show()

plot_images(images = data.test.images[0:9], cls_true = data.test.cls[0:9])

x = tf.placeholder(tf.float32,[None, img_size_flat])
y_true = tf.placeholder(tf.float32,[None, num_classes])
y_true_cls = tf.placeholder(tf.int64, [None])

weights = tf.Variable(tf.zeros([img_size_flat, num_classes]))
biases = tf.Variable(tf.zeros([num_classes]))

logits = tf.matmul(x,weights) + biases

y_pred = tf.nn.softmax(logits)
y_pred_cls = tf.argmax(y_pred, axis = 1)

cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits = logits, labels = y_true)

cost = tf.reduce_mean(cross_entropy)

optimizer =tf.train.GradientDescentOptimizer(learning_rate=0.5).minimize(cost)

correct = tf.equal(y_pred_cls, y_true_cls)
accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))

session = tf.Session()
session.run(tf.global_variables_initializer())

batch_size = 100

def optimize(num_iterations):
    for i in range(num_iterations):
        x_batch, y_batch = data.train.next_batch(batch_size)
        feed_dict_train = {x:x_batch, y_true:y_batch}
        session.run(optimizer, feed_dict = feed_dict_train)

feed_dict_test = {x:data.test.images, y_true:data.test.labels, y_true_cls:data.test.cls}

def print_accuracy():
    acc = session.run(accuracy, feed_dict=feed_dict_test)
    print("Accuracy on test-set: {0:.1%}".format(acc))
    
def print_confusion_matrix():
    # Get the true classifications for the test-set.
    cls_true = data.test.cls
    
    # Get the predicted classifications for the test-set.
    cls_pred = session.run(y_pred_cls, feed_dict=feed_dict_test)

    # Get the confusion matrix using sklearn.
    cm = confusion_matrix(y_true=cls_true,
                          y_pred=cls_pred)

    # Print the confusion matrix as text.
    print(cm)

    # Plot the confusion matrix as an image.
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)

    # Make various adjustments to the plot.
    plt.tight_layout()
    plt.colorbar()
    tick_marks = np.arange(num_classes)
    plt.xticks(tick_marks, range(num_classes))
    plt.yticks(tick_marks, range(num_classes))
    plt.xlabel('Predicted')
    plt.ylabel('True')
    
    # Ensure the plot is shown correctly with multiple plots
    # in a single Notebook cell.
    plt.show()
    
def plot_example_errors():
    # Use TensorFlow to get a list of boolean values
    # whether each test-image has been correctly classified,
    # and a list for the predicted class of each image.
    ct, cls_pred = session.run([correct, y_pred_cls],
                                    feed_dict=feed_dict_test)

    # Negate the boolean array.
    incorrect = (ct == False)
    
    # Get the images from the test-set that have been
    # incorrectly classified.
    images = data.test.images[incorrect]
    
    # Get the predicted classes for those images.
    cls_pred = cls_pred[incorrect]

    # Get the true classes for those images.
    cls_true = data.test.cls[incorrect]
    
    # Plot the first 9 images.
    plot_images(images=images[0:9],
                cls_true=cls_true[0:9],
                cls_pred=cls_pred[0:9])

def plot_weights():
    # Get the values for the weights from the TensorFlow variable.
    w = session.run(weights)
    
    # Get the lowest and highest values for the weights.
    # This is used to correct the colour intensity across
    # the images so they can be compared with each other.
    w_min = np.min(w)
    w_max = np.max(w)

    # Create figure with 3x4 sub-plots,
    # where the last 2 sub-plots are unused.
    fig, axes = plt.subplots(3, 4)
    fig.subplots_adjust(hspace=0.3, wspace=0.3)

    for i, ax in enumerate(axes.flat):
        # Only use the weights for the first 10 sub-plots.
        if i<10:
            # Get the weights for the i'th digit and reshape it.
            # Note that w.shape == (img_size_flat, 10)
            image = w[:, i].reshape(img_shape)

            # Set the label for the sub-plot.
            ax.set_xlabel("Weights: {0}".format(i))

            # Plot the image.
            ax.imshow(image, vmin=w_min, vmax=w_max, cmap='seismic')

        # Remove ticks from each sub-plot.
        ax.set_xticks([])
        ax.set_yticks([])
        
    # Ensure the plot is shown correctly with multiple plots
    # in a single Notebook cell.
    plt.show()
    
print_accuracy()
plot_example_errors()
optimize(num_iterations=1)
print_accuracy()
plot_example_errors()
plot_weights()
optimize(num_iterations=9)
print_accuracy()
plot_example_errors()
plot_weights()
optimize(num_iterations=990)
print_accuracy()
plot_example_errors()
plot_weights()
print_confusion_matrix()