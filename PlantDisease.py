# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YHjUzMnqtIYsR012gwXqwuj4EhxwQOTy

Seeding for reproducibility
"""

#set seeds for reproducibility
import random
random.seed(0)
import numpy as np
np.random.seed(0)
import tensorflow as tf
tf.random.set_seed(0)

"""Importing the dependencies"""

import os
import json
from zipfile import ZipFile
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models

"""Data curation"""

#uploading the kaggle.json file

!pip install kaggle

kaggle_credentails=json.load(open("kaggle.json"))

#setup kaggle api as environmental variables

os.environ['KAGGLE_USERNAME']= kaggle_credentails['username']
os.environ['KAGGLE_KEY']= kaggle_credentails['key']

!kaggle datasets download -d abdallahalidev/plantvillage-dataset

!ls

#unzip the downloaded dataset

with ZipFile('plantvillage-dataset.zip','r') as zip_ref:
  zip_ref.extractall()

print(os.listdir("plantvillage dataset"))

print(len(os.listdir("plantvillage dataset/segmented")))
print(os.listdir("plantvillage dataset/segmented")[:5])

print(len(os.listdir("plantvillage dataset/color")))
print(os.listdir("plantvillage dataset/color")[:5])

print(len(os.listdir("plantvillage dataset/grayscale")))
print(os.listdir("plantvillage dataset/grayscale")[:5])

#dataset path
base_dir='plantvillage dataset/color'

image_path='/content/plantvillage dataset/color/Apple___Apple_scab/00075aa8-d81a-4184-8541-b692b78d398a___FREC_Scab 3335.JPG'
#read the image
img=mpimg.imread(image_path)
print(img.shape)
#display the image
plt.imshow(img)
plt.axis('off')
plt.show()

#image parameters
img_size= 224
batch_size=32

"""Train Test Split"""

#Image data generators
data_gen=ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2 #use 20% of data for validation
)

#train generator
train_generator=data_gen.flow_from_directory(
    base_dir,
    target_size=(img_size, img_size),
    batch_size=batch_size,
    subset='training',
    class_mode='categorical'
)

#validation generator
validation_generator=data_gen.flow_from_directory(
    base_dir,
    target_size=(img_size, img_size),
    batch_size=batch_size,
    subset='validation',
    class_mode='categorical'
)

#model definition
model=models.Sequential()

model.add(layers.Conv2D(32,(3,3), activation='relu', input_shape=(img_size, img_size,3)))
model.add(layers.MaxPooling2D(2,2))

model.add(layers.Conv2D(64, (3,3), activation='relu'))
model.add(layers.MaxPooling2D(2,2))

model.add(layers.Flatten())
model.add(layers.Dense(256, activation='relu'))
model.add(layers.Dense(train_generator.num_classes,activation='softmax'))

#model summary
model.summary()

#compiling the model

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

"""model training"""

#training the model
history=model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    epochs=5, #number of epochs
    validation_data= validation_generator,
    validation_steps=validation_generator.samples // batch_size #Validation steps
)

"""Model Evaluation"""

#model evaluation
print("evaluation model...")
val_loss, val_accuracy= model.evaluate(validation_generator, steps=validation_generator.samples // batch_size)
print(f"Validation Accuracy: {val_accuracy * 100:.2f}%")

#plot training & validation accuracy values
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train','test'], loc='upper left')
plt.show()

"""Building a predictive system"""

#function to load and preprocess the image using pillow
def load_and_preprocess_image(image_path, target_size=(224,224)):
  #load the image
  img=Image.open(image_path)
  #resize the image
  img=img.resize(target_size)
  #convert the image to a numpy array
  img_array=np.array(img)
  #add batch dimension
  img_array=np.expand_dims(img_array,axis=0)
  #scale the image values to {0,1}
  img_array= img_array.astype('float32')/255.
  return img_array

  #function to predict the class of an image
  def predict_image_class(model, image_path, class_indices):
    preprocessed_img=load_and_preprocess_image(image_path)
    predictions=model.predict(preprocessed_img)
    predicted_class_index=np.argmax(prediction, axis=1)[0]
    predicted_class_name=class_indices[predicted_class_index]
    return predicted_class_name

