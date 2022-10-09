# -*- coding: utf-8 -*-
"""fcc_sms_text_classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/freeCodeCamp/boilerplate-neural-network-sms-text-classifier/blob/master/fcc_sms_text_classification.ipynb
"""

# Importing of libraries
try:
  # %tensorflow_version only exists in Colab.
  !pip install tf-nightly
except Exception:
  pass
import tensorflow as tf
import pandas as pd
from tensorflow import keras
!pip install tensorflow-datasets
import tensorflow_datasets as tfds
import numpy as np
import matplotlib.pyplot as plt

print(tf.__version__)

# Getting the data files
!wget https://cdn.freecodecamp.org/project-data/sms/train-data.tsv
!wget https://cdn.freecodecamp.org/project-data/sms/valid-data.tsv

train_file_path = "train-data.tsv"
test_file_path = "valid-data.tsv"

# Transforming the files in pd.DataFrame
train_df=pd.read_csv('train-data.tsv',sep='\t',header=None,names=['target', 'input'])
train_df

val_df=pd.read_csv('valid-data.tsv',sep='\t',header=None,names=['target', 'input'])
val_df

# Plotting the number of ham and spam messages
bar = train_df['target'].value_counts()

plt.bar(bar.index, bar)
plt.xlabel('Labels')
plt.title('Number of ham and spam messages')

# Changing the order of the columns
train_df = train_df[['input', 'target']]
val_df = val_df[['input', 'target']]

#Identigying the target (labels) columns
y_train = train_df['target'].astype('category').cat.codes
y_test  = val_df['target'].astype('category').cat.codes
y_train

#OneHot Encoding in targets column
train_df['target']=train_df['target'].apply({'ham':0,'spam':1}.get)
y_train=train_df['target']

val_df['target']=val_df['target'].apply({'ham':0,'spam':1}.get)

y_train

#Cleaning the texts in the training set using the dedicated nltk and re libraries
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# We start with the training set
corpus_train = []
for i in range(0, 4179):
    review = re.sub('[^a-zA-Z0-9]', ' ', train_df['input'][i])
    review = review.lower()
    review = review.split()
    ps = PorterStemmer()
    review = [ps.stem(word) for word in review if not word in set(stopwords.words('english'))]
    review = ' '.join(review)
    corpus_train.append(review)

# Next, the test set
corpus_val = []
for i in range(0, 1392):
    review = re.sub('[^a-zA-Z0-9]', ' ', val_df['input'][i])
    review = review.lower()
    review = review.split()
    ps = PorterStemmer()
    review = [ps.stem(word) for word in review if not word in set(stopwords.words('english'))]
    review = ' '.join(review)
    corpus_val.append(review)

from keras.preprocessing.text import Tokenizer

tokenizer = Tokenizer(num_words=5000)
tokenizer.fit_on_texts(corpus_train) # Updates internal vocabulary based on a list of texts.

X_train = tokenizer.texts_to_sequences(corpus_train) #transform its text into a sequence of squence
X_test = tokenizer.texts_to_sequences(corpus_val)

vocab_size = len(tokenizer.word_index) + 1  # Adding 1 because of reserved 0 index

from keras_preprocessing.sequence import pad_sequences

# Padding of the sequence in a specific length
maxlen = 150

X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)

print(X_train[0, :])

# Training the model
from keras.models import Sequential
from keras import layers

embedding_dim = 50
model = Sequential()
model.add(layers.Embedding(input_dim=vocab_size, 
                           output_dim=embedding_dim, 
                           input_length=maxlen))
model.add(layers.Conv1D(128, 5, activation='relu'))
model.add(layers.GlobalMaxPool1D())
model.add(layers.Dense(10, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

# Compiling the model
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])
model.summary()

history = model.fit(X_train, y_train,
                    epochs=10,
                    verbose=True,
                    validation_data=(X_test, y_test),
                    batch_size=10)

# Function to predict messages based on model
# (should return list containing prediction and label, ex. [0.008318834938108921, 'ham'])
def predict_message(predict_text):
  predict_text = [predict_text]
  pred_df = pd.DataFrame(predict_text)
  pred_df = pred_df.rename(columns={0:'input'})
  # Cleaning the texts in the test set
  import re
  import nltk
  nltk.download('stopwords')
  from nltk.corpus import stopwords
  from nltk.stem.porter import PorterStemmer
  corpus_pred = []
  for i in range(0, len(predict_text)):
    review = re.sub('[^a-zA-Z0-9]', ' ', pred_df['input'][i])
    review = review.lower()
    review = review.split()
    ps = PorterStemmer()
    review = [ps.stem(word) for word in review if not word in set(stopwords.words('english'))]
    review = ' '.join(review)
    corpus_pred.append(review)

    sequence = tokenizer.texts_to_sequences(corpus_pred)
    # pad the sequence
    sequence = pad_sequences(sequence, maxlen=maxlen)
    # get the prediction
    prediction = model.predict(sequence)

  if prediction >= 0.5:
    prediction = ([prediction, 'spam'])
  else:
    prediction = ([prediction, 'ham'])

  return (prediction)

predict_text = "how are you doing today?"

prediction = predict_message(predict_text)
print(prediction)

# Run this cell to test your function and model. Do not modify contents.
def test_predictions():
  test_messages = ["how are you doing today",
                   "sale today! to stop texts call 98912460324",
                   "i dont want to go. can we try it a different day? available sat",
                   "our new mobile video service is live. just install on your phone to start watching.",
                   "you have won £1000 cash! call to claim your prize.",
                   "i'll bring it tomorrow. don't forget the milk.",
                   "wow, is your arm alright. that happened to me one time too"
                  ]

  test_answers = ["ham", "spam", "ham", "spam", "spam", "ham", "ham"]
  passed = True

  for msg, ans in zip(test_messages, test_answers):
    prediction = predict_message(msg)
    if prediction[1] != ans:
      passed = False

  if passed:
    print("You passed the challenge. Great job!")
  else:
    print("You haven't passed yet. Keep trying.")



