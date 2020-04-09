#!/usr/bin/env python3
import keras
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation, Flatten, Conv1D, MaxPooling1D, Reshape, GlobalAveragePooling1D
from keras.constraints import maxnorm
from keras.optimizers import SGD

import numpy as np
import sys

if len(sys.argv) < 2:
    print("%s <dataset.param>" % sys.argv[0])
    print("1a linha:          inputLen,batchSize,modelNum")
    print("demais linhas: label,numDataSamples,dataFile")
    exit(0)
    
fparams = open(sys.argv[1])
lines = fparams.readlines()
line0fields = lines[0].split(',')

inputLen = int(line0fields[0])
batch_size = int(line0fields[1])
modelNum = int(line0fields[2])
inputTuples = int(line0fields[3]) if len(line0fields) >= 4 else 1
inputShape = (inputLen, inputTuples) if inputTuples > 1 else (inputLen,)

#inputLen = 25*5 # 5 segundos de video
#numData = 40000
#batch_size = 128
#modelNum = 2

trainData = []
trainLabels = []
testData = []
testLabels = []

np.random.seed(1000)

for line in lines[1:]:
    if line[0] == '#':
        continue
    line = line.strip()
    lineStrs = line.split(",")
    if len(lineStrs) <= 1:
        continue
    label = float(lineStrs[0])
    numData = int(lineStrs[1])
    datalines = open(lineStrs[2].strip()).readlines()
    
    #lineVals = np.array([float(x) for x in datalines])
    #lineVals = np.array([float((x.split(" "))[0]) for x in datalines])
    if inputTuples == 1:
        lineVals = np.array([float((x.split(" "))[0]) for x in datalines])
    else:
        lineVals = np.array([ [float(y) for y in x.split(" ")] for x in datalines])

    print("Adicionando %d subsets de um total de %d amostras com label %d" % (numData, len(lineVals), label))

    if True:
        # usa primeira metade para treinar, segunda metada para testar
        randIdx = np.random.randint(0,int(len(lineVals)/2)-inputLen,numData)
        for i in randIdx:
            data = lineVals[i:i+inputLen]
            trainData.append( data )
            trainLabels.append( label )

            data = lineVals[i + int(len(lineVals)/2):i+int(len(lineVals)/2)+inputLen]
            testData.append( data )
            testLabels.append( label )
    else:
        # usa sequencia seguinte de inputLen para testar (pode ter overlap com outros treinos)
        randIdx = np.random.randint(0,len(lineVals)-2*inputLen,numData)
        for i in randIdx:
            data = lineVals[i:i+inputLen]
            trainData.append( data )
            trainLabels.append( label )

            data = lineVals[i+inputLen:i+2*inputLen]
            testData.append( data )
            testLabels.append( label )
        
#from pylab import *
#plot(trainData[2])
#plot(trainData[-3])
#show()
    
trainData = np.array(trainData)
trainLabels = np.array(trainLabels)
testData = np.array(testData)
testLabels = np.array(testLabels)


if modelNum == 0:
    model = Sequential()
    model.add(Dense(32, activation='relu', input_shape=inputShape))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='rmsprop',
                loss='binary_crossentropy',
                metrics=['accuracy'])
    
if modelNum == 1:
    model = Sequential()
    # Dense(64) is a fully-connected layer with 64 hidden units.
    # in the first layer, you must specify the expected input data shape:
    # here, inputLen-dimensional vectors.
    model = Sequential()
    model.add(Dense(64, input_shape=inputShape, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy',
                optimizer='rmsprop',
                metrics=['accuracy'])

if modelNum == 2:
    model = Sequential()
    model.add(Dense(128, activation='relu', input_shape=inputShape, kernel_constraint=maxnorm(3)))
    model.add(Dropout(0.2))
    model.add(Dense(128, activation='relu', kernel_constraint=maxnorm(3)))
    model.add(Dropout(0.2))
    model.add(Dense(128, activation='relu', kernel_constraint=maxnorm(3)))
    model.add(Dropout(0.2))
    if inputTuples > 1:
        model.add(GlobalAveragePooling1D())
    model.add(Dense(1, activation='sigmoid'))
    opt=keras.optimizers.rmsprop(lr=0.0001, decay=1e-6)
    model.compile(optimizer=opt,
                loss='binary_crossentropy',
                metrics=['accuracy'])

if modelNum == 3:
    model = Sequential()
    model.add(Dense(64, activation='relu', input_shape=inputShape))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam',
                loss='binary_crossentropy',
                metrics=['accuracy'])

if modelNum == 4:
    model = Sequential()
    model.add(Reshape(inputShape, input_shape=inputShape))
    model.add(Conv1D(100, kernel_size=10, activation='relu'))#, input_shape=inputShape))
    model.add(Conv1D(100, kernel_size=10, activation='relu'))
    #model.add(Dropout(0.2))
    model.add(MaxPooling1D(pool_size=3))
    #model.add(Flatten())
    model.add(Conv1D(160, kernel_size=10, activation='relu'))
    model.add(Conv1D(160, kernel_size=10, activation='relu'))
    model.add(GlobalAveragePooling1D())
    model.add(Dropout(0.2))
    model.add(Dense(128, activation='relu', kernel_constraint=maxnorm(3)))
    model.add(Dropout(0.2))
    #if inputTuples > 1:
    #    model.add(Flatten())
    model.add(Dense(1, activation='sigmoid'))
    opt=keras.optimizers.rmsprop(lr=0.0001, decay=1e-6)
    model.compile(optimizer=opt,
                loss='binary_crossentropy',
                metrics=['accuracy'])


#if modelNum == 4:
#    model = load_model('model_stddev_%d.h5' % (inputLen))

# Train the model, iterating on the data in batches of 32 samples
#model.fit(trainData, trainLabels, epochs=10, batch_size=32)

print(model.summary())
#exit(0)

print("Tranining...")
model.fit(trainData, trainLabels,
          epochs=20,
          batch_size=batch_size)

print("Evaluate...")
score = model.evaluate(testData, testLabels, batch_size=batch_size)

print(model.metrics_names)
print("score:", score)

model.save('model_tst_%d-%d.h5' % (inputLen, inputTuples))
