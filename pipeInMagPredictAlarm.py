# rodar com:
# conda activate base
# ./Realtime-Video-Magnification/src/rvm | python3 pipeInMagPredictAlarm.py --outputDate --alarm

import datetime

import sys, os
import numpy as np

import keras
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import SGD

from pylab import *

import argparse

parser = argparse.ArgumentParser(description='Processa dados de Motion Magnitude (metodo 2) e alarma.')
#parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                    help='an integer for the accumulator')
parser.add_argument('--input', dest='input', action='store',
                    default=None, help='arquivo de entrada (stdin se nao usado)')
parser.add_argument('--output', dest='output', action='store',
                    default=None, help='arquivo de saida')
parser.add_argument('--outputDate', action='store_true', default=False,
                    dest='outputDate', help='arquivo de saida como "date-yy-mm-dd_hh:mm:ss"')
parser.add_argument('--plot', action='store_true', default=False,
                    dest='plot', help='Plot ')
parser.add_argument('--alarm', action='store_true', default=False,
                    dest='alarm', help='Alarm ')
parser.add_argument('--clipPlotVals', action='store_true', default=False,
                    dest='clipPlotVals', help='Clipa vals para plotar')
args = parser.parse_args()

inputFile = open(args.input) if args.input else sys.stdin
outputFilename = None
if args.outputDate:
    outputFilename = 'data-{date:%Y-%m-%d_%H:%M:%S}.txt'.format( date=datetime.datetime.now() )
if args.output:
    outputFilename = args.output
outputFile = open(outputFilename,"w") if outputFilename else None

fps = 25.
inputLen = fps*5 # 5 segundos de video
avgLen = 5 # quantas predicoes de inputLen seguidas (x5s = 25seg total)
alarmDelay = 2 # quantas medias regidas abaixo de 0.5 para alarmar (da um delay de confirmacao: 25+10=35)
model = load_model('model_tst_%d.h5' % (inputLen))

inputBuffer = []
avgPredBuffer = []
delayCounter = 0
sampleCounter = 0

plotVals = []
plotPred = []
plotAvgPred = []
plotMedPred = []
plotAlarm = [(0,0)]

def addVal(val):
    global inputBuffer, avgPredBuffer,  delayCounter, sampleCounter
    global plotVals, plotPred, plotAvgPred, plotMedPred, plotAlarm
    
    if val:
        #print( "addVal", val)
        if args.plot:
            plotVals.append( (sampleCounter, val) )
        inputBuffer.append(val)
        if len(inputBuffer) == inputLen:
            data = np.array([inputBuffer])
            pred = model.predict(array(data))[0,0]
            inputBuffer = []
            print( "%d pred: %.2f" % (sampleCounter,pred))
            if args.plot:
                plotPred.append( (sampleCounter, pred) )
            
            avgPredBuffer.append(pred)
            if len(avgPredBuffer) == avgLen + 1:
                avgPredBuffer = avgPredBuffer[1:]
                avgPred = np.average(avgPredBuffer)
                medPred = np.median(avgPredBuffer)
                medPred = np.max(avgPredBuffer)
                #print(avgPredBuffer)
                print( "%d medPred: %.2f" % (sampleCounter,medPred))
                if args.plot:
                    plotAvgPred.append( (sampleCounter, avgPred) )
                    plotMedPred.append( (sampleCounter, medPred) )

                if medPred > 0.5:
                    if delayCounter >= alarmDelay:
                        print( "%d alarm-stop!" % (sampleCounter))
                        if args.alarm:
                            os.system("./alarm-stop.sh")
                        if args.plot:
                            plotAlarm.append( (sampleCounter, 0.) )
                    delayCounter = 0
                else:
                    delayCounter += 1
                    if delayCounter >= alarmDelay:
                        print( "%d alarm-start!" % (sampleCounter))
                        if args.alarm:
                            os.system("./alarm-start.sh")
                        if args.plot:
                            plotAlarm.append( (sampleCounter, 1.) )
        sampleCounter += 1
    sys.stdout.flush()

for line in inputFile:
    val = None
    try:
        vals = [float(x) for x in line.split(" ")]
        val = vals[0]
        
        #teste com stdev
        '''
        if len(vals) > 1:
            if vals[1] < 0.010:
                val = 0.1
        '''
        if outputFile:
            outputFile.write(line)
    except:
        pass
    addVal(val)

if args.plot:
    plotVals = array(plotVals)
    plotPred = array(plotPred)
    plotAvgPred = array(plotAvgPred)
    plotMedPred = array(plotMedPred)
    plotAlarm.append((sampleCounter,0))
    plotAlarm = array(plotAlarm)
    
    if args.clipPlotVals:
        stdVals = np.std(plotVals[:,1])
        limitVals = 100 * stdVals
        plotVals[ plotVals[:,1] > limitVals ,1] = limitVals
    
    plot( plotVals[:,0]/fps, plotVals[:,1] / max(plotVals[:,1]), color='b', label = "vals" )
    plot( plotPred[:,0]/fps, plotPred[:,1], color='g', label = "pred" )
    plot( plotAvgPred[:,0]/fps, plotAvgPred[:,1], 'o', color='y', label = "avgPred" )
    plot( plotMedPred[:,0]/fps, plotMedPred[:,1], 'o', color='m', label = "medPred" )
    plot( plotAlarm[:,0]/fps, plotAlarm[:,1], 'o', color='r', label = "alarm" )
    legend(loc = 'upper right')
    if args.input:
        title(args.input)
    show()
