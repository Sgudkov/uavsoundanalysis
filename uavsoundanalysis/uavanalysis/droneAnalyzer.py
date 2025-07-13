import os

import joblib
import librosa
import numpy as np
from sklearn.preprocessing import StandardScaler
import pandas as pd


class DroneAnalyzer:

    def __init__(self, dir_audio: str):
        self.dir = dir_audio
        self.features = []

    def is_drone(self) -> bool:
        print('is_drone')
        self.__extract_features()
        return bool(self.__predict())

    def __analyze(self):
        pass

    def __extract_features(self):
        dir_name = self.dir
        for file in os.listdir(dir_name):
            print('file', file)
            if not file.endswith('.wav'):
                continue
            # Load the audio file
            audio, sr = librosa.load(os.path.join(dir_name, file), sr=44100)

            # Normalize the loudness
            normalized_audio = librosa.util.normalize(audio)

            # Preprocess the audio data
            normalized_audio, _ = librosa.effects.trim(normalized_audio, top_db=20)

            # Extract MFCCs
            mfccs = librosa.feature.mfcc(y=normalized_audio, sr=sr)

            # Calculate the mean and standard deviation of the MFCCs
            mfcc_mean = mfccs.mean(axis=1)
            mfcc_std = mfccs.std(axis=1)

            # Extract spectral features
            spectral_rolloff = librosa.feature.spectral_rolloff(y=normalized_audio, sr=sr)
            spectral_centroid = librosa.feature.spectral_centroid(y=normalized_audio, sr=sr)

            # Calculate the mean and standard deviation of the spectral features
            spectral_rolloff_mean = spectral_rolloff.mean()
            spectral_rolloff_std = spectral_rolloff.std()
            spectral_centroid_mean = spectral_centroid.mean()
            spectral_centroid_std = spectral_centroid.std()

            all_features = np.concatenate((mfcc_mean, mfcc_std, [spectral_rolloff_mean], [spectral_rolloff_std],
                                           [spectral_centroid_mean], [spectral_centroid_std]))

            # Normalize the features
            scaler = StandardScaler()
            normalized_features = scaler.fit_transform(all_features.reshape(-1, 1))

            self.features.append(
                [*normalized_features.flatten()])

    def __predict(self) -> int:
        if len(self.features) == 0:
            print('no features')
            return 0
        loaded_model = joblib.load('uavanalysis/model/svm_model.joblib')
        X = pd.DataFrame(self.features,
                         columns=[[f'mfcc_{i}' for i in range(1, 21)] + [f'mfcc_{i}_std' for i in range(1, 21)] + [
                             'spectral_rolloff_mean',
                             'spectral_rolloff_std',
                             'spectral_centroid_mean',
                             'spectral_centroid_std']])
        predict = loaded_model.predict(X)
        predict_prob = loaded_model.predict_proba(X)
        print('predict', predict)
        print('predict_prob', predict_prob)
        return predict[0]
