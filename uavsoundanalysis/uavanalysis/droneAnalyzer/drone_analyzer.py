import joblib
import librosa
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class DroneAnalyzer:
    """
    Class for analyzing audio file to detect if it contains drone sound.

    Attributes:
        file_path (str): Path to the audio file.

    Methods:
        is_drone: Returns True if the audio file contains drone sound, False otherwise.

    Notes:
        The class uses a pre-trained svm model to analyze the audio file.
        The features used for analysis are mel-frequency cepstral coefficients (mfccs) and their standard deviation.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.features: list = []

    def is_drone(self) -> bool:
        self.__extract_features()
        return bool(self.__predict())

    def __extract_features(self):
        # Load the audio file
        audio, sr = librosa.load(self.file_path, sr=44100)

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

        all_features = np.concatenate(
            (
                mfcc_mean,
                mfcc_std,
                [spectral_rolloff_mean],
                [spectral_rolloff_std],
                [spectral_centroid_mean],
                [spectral_centroid_std],
            )
        )

        # Normalize the features
        scaler = StandardScaler()
        normalized_features = scaler.fit_transform(all_features.reshape(-1, 1))

        self.features.append([*normalized_features.flatten()])

    def __predict(self) -> int:
        if len(self.features) == 0:
            print("no features")
            return 0

        model_path = "uavanalysis/model/svm_model.joblib"
        loaded_model = joblib.load(model_path)
        X = pd.DataFrame(
            self.features,
            columns=[
                [f"mfcc_{i}" for i in range(1, 21)]
                + [f"mfcc_{i}_std" for i in range(1, 21)]
                + [
                    "spectral_rolloff_mean",
                    "spectral_rolloff_std",
                    "spectral_centroid_mean",
                    "spectral_centroid_std",
                ]
            ],
        )
        predict = loaded_model.predict(X)
        print("predict", predict[0])
        return predict[0]
