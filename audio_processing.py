# -*- coding: utf-8 -*-
import os
import wave
import time
import pickle
import pyaudio
import numpy as np
from sklearn import preprocessing
from scipy.io.wavfile import read
import python_speech_features as mfcc
from sklearn.mixture import GaussianMixture
from sklearn import preprocessing
from python_speech_features import mfcc
from python_speech_features import delta
import re
import warnings
import pymongo
warnings.filterwarnings("ignore")

def record(user_name, nbr_samples, time_limit,flag):
     #creation du data set par l administrateur ou teste
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = time_limit
    if flag=='train': # enregistrement pour enrichir le data set  (repertorier de nouvelle personnes )
        #nbr_samples : nombre d'échantillion enregistré
        #chaque personne fourni  un  certain nombre d'échantillion 
        l=list()
        for count in range(nbr_samples):
            audio = pyaudio.PyAudio()
            # commencer l'enregistrement
            stream = audio.open(format=FORMAT, channels=CHANNELS,rate=RATE, input=True,frames_per_buffer=CHUNK)
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            # fin d'enregistrement
            stream.stop_stream()
            stream.close()
            audio.terminate()

            FILENAME = user_name + str(count) + ".wav"
            # le fichier wav généré va etre déplacé dans le repertoire data_set
            WAVE_FILE=os.path.join("data_set", FILENAME)

            l.append(FILENAME)
            waveFile = wave.open(WAVE_FILE, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(frames))
            waveFile.close()
        # ajouter  le fichier de sortie dans la liste des trained files 
        # inserer dans MongoDB  username  et la liste des fichiers audio 
        add_to_train_set(user_name,l)

    if flag=='test': # enregistrer la voix pour le test
        audio = pyaudio.PyAudio()    
        # commencer l'enregistrement
        stream = audio.open(format=FORMAT, channels=CHANNELS,rate=RATE, input=True,frames_per_buffer=CHUNK)    
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        # fin d'enregistrement
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        FILENAME="test.wav"
        WAVE_FILE=os.path.join("test_folder",FILENAME)
        waveFile = wave.open(WAVE_FILE, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()

# extraction des features 
def extract_features(audio, rate):
        #Extraire les caractéristiques vocales, y compris le coefficient cepstral mel fréquence (MFCC)
        #à partir d’un audio utilisant le module python_speech_features, effectue Cepstral Mean
        #normalisation (CMS) et le combiner avec les deltas MFCC et le double MFCC
        #Deltas
        
        mfcc_feature = mfcc(audio,rate, 0.025, 0.01,20,nfft = 1200, appendEnergy = True) 
        mfcc_feature  = preprocessing.scale(mfcc_feature)
        deltas        = delta(mfcc_feature, 2)
        double_deltas = delta(deltas, 2)
        combined      = np.hstack((mfcc_feature, deltas, double_deltas))
        return combined


def start_training(user_n,permission):

    src   = "data_set/"   
    dest = "trained_folder/"        
    count = 1
    features = np.asarray(())
    pattern = r'[0-9]'
    
    file_train=get_samples(user_n)
    nbr_samples=len(file_train)
    
    for path in file_train:
    
        path = path.strip()
        sr,audio = read(src+path)
        v= extract_features(audio,sr)
    
        if features.size == 0:
            features = v
        else:
            features = np.vstack((features, v))
        #creation du model pour chaque groupe d echantillon fourni par la personne 
        # chaque personne possede un model    
        if count == nbr_samples:    
            gmm = GaussianMixture(n_components = nbr_samples+1, max_iter = 200, covariance_type='diag',n_init = 3)
            gmm.fit(features)
            name= re.sub(pattern, '',path.split(".")[0])
            picklefile = name+".gmm"
            pickle.dump(gmm,open(dest + picklefile,'wb'))
            features = np.asarray(())
            count = 0
    
        count = count + 1
    
    add_user_to_bdd(user_n,permission)

def add_user_to_bdd(user_name,permission): # inserer user_name et permission (yes or no ) dans la base mongodb
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["BDD"]
    mycol = mydb["EMPLOYEE"]
    mydict = { "USER_NAME": str(user_name), "PERMISSION": str(permission) }
    mycol.insert_one(mydict)
    


def start_testing():
    allowed=True
    res=None
    src   = "test_folder/"  
    model = "trained_folder/"
    test_file = "test.wav"       
    user_name=None
    gmm_files = [os.path.join(model,fname) for fname in os.listdir(model) if fname.endswith('.gmm')]

    models    = [pickle.load(open(fname,'rb')) for fname in gmm_files]
    speakers   = [fname.split("\\")[-1].split(".gmm")[0] for fname in gmm_files]
	 
	# tester les fichiers audio
    sr,audio = read(src+test_file)
    v = extract_features(audio,sr)     
    l = np.zeros(len(models)) 
	    
    for i in range(len(models)):
        gmm    = models[i]  # verification avec chaque model
        scores = np.array(gmm.score(v)) #calcule des scores
        l[i] = scores.sum()

    winner = np.argmax(l) #prendre le meilleur score donc le plus simillair 
    res=speakers[winner]
    res=res.split("/")[-1] 
    answer=get_user_perm(res)
    if answer==None:
        answer='no'
    return(answer,res) # retourne la permission 


def get_user_perm(user_n): #recuperer la permission de user_n
    allowed=None
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["BDD"]
    mycol = mydb["EMPLOYEE"]
    for t in mycol.find({"USER_NAME":str(user_n)},{ "_id": 0,"USER_NAME": 1, "PERMISSION": 1 }):
        allowed=t['PERMISSION']
    return allowed

def add_to_train_set(user_n,audio_file):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["BDD"]
    mycol = mydb["Training_Set"]
    train_dict = { "USER_NAME":user_n,"FILE_NAME":audio_file }
    x = mycol.insert_one(train_dict)

def get_samples(user_n):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["BDD"]
    mycol = mydb["Training_Set"]
    for t in mycol.find({"USER_NAME":str(user_n)},{ "_id": 0,"FILE_NAME": 1 }):
        samples=t['FILE_NAME']
    return samples


