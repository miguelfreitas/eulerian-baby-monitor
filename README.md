# eulerian-baby-monitor
Scripts for using Eulerian Video Magnification and neural networks as a baby breathing monitor

*Disclaimer: this is a functional set of scripts to implement a baby breathing monitor using IP camera and Linux computer, however it is not intended for end-users. Setting up the whole thing requires some programming skills and possibly retraining the neural network model with your data. I'm just documenting what I've hacked together to use with my newborn baby - I'm not providing support.*

## How it works
1. Video from IP camera is streamed with RTSP protocol
2. ffmpeg convert video into a v4l2 loopback device
3. Forked branch of [Realtime-Video-Magnification](https://github.com/miguelfreitas/Live-Video-Magnification/blob/print-movement-stdout) project performs realtime motion video magnification and outputs a "motion scalar" to stdout
4. Motion data is piped into `pipeInMagPredictAlarm.py` script which runs a previously trained [Keras](https://keras.io/) model to predict either 1 (baby is breathing) or 0 (no baby / no breathing)
5. In case of a sequence of "no breathing" of ~30 seconds an alarm is played (currently mplayer playing a sound)
6. Alarm may be turned on/off from smartphone by acessing a simple web page (quite useful if computer is far away from the sleeping room)

## Random notes

### Video from IP camera
* Set the IP camera for maximum bitrate/quality as possible since compression artifacts may cause false movement detection. I also use GOP size, intra-frame period to 1. Alternatively one may try using MJPEG instead of MPEG4/H264 etc (I couldn't figure out how to get MJPEG from my camera).
* Load kernel module: `sudo modprobe v4l2loopback`
* ffmpeg command: `ffmpeg -i rtsp://user:password@192.168.1.10:8554/profile0/media.smp -f v4l2 /dev/video0` (The actual URL is camera specific)

### Training
The model is trained using `treinaRede.py` script. This script will received a "dataset params" file with first line defining global parameters:

`inputLen (in frames),batchSize,modelNum`

Further lines will add data for training:

`tag(0 or 1),numRandomSlicesForTraining,dataFile`

* Current model uses size 125 (5 seconds of 25 fps) and model 2 (3 levels of "relu" with 0.2 dropout factor and sigmoid activation).
* Current model was trained using a single data value per frame (the "motion" scalar which is the sum of motion of all pixels). Since lighting conditions may affect the general noise level of the image (compression artifacts and stuff) the [Realtime-Video-Magnification](https://github.com/miguelfreitas/Live-Video-Magnification/blob/print-movement-stdout) branch now outputs the standard deviation of pixels' motion as well. Scripts have not yet been updated to make use of this new data.
*  If camera or lightning conditions change the model may need to be retrained to fix false positive/negatives. I have found useful to save data of every night and eventually retrain the model to fix the misdetections.

### Motion detection and alarm

Every night I use the following command:

`./Realtime-Video-Magnification/src/rvm | python3 pipeInMagPredictAlarm.py --outputDate --alarm`

This will execute RVM program (I still need to go through GUI menus to open camera and select Haar Wavelet magnification) and pipe motion data into script. The script will execute the previously trained model, creating a backup of the motion data name as current date and time and call the external alarm if required.

	usage: pipeInMagPredictAlarm.py [-h] [--input INPUT] [--output OUTPUT]
	                                [--outputDate] [--plot] [--alarm]
	                                [--clipPlotVals]

### Sample baby's sleeping motion data

![Whole night baby's movement and breathing](images/data-2019_12_23-night.png)

![Detail of irregular (but normal) newborn's breathing pattern](images/data-2019_11_06-newborn-breathing.png)
