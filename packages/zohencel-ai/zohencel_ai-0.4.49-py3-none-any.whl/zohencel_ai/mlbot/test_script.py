import pandas as pd
import pickle
import os
import numpy as np
from train import *

current_dir = os.path.dirname(os.path.abspath(__file__))
pickle_file_path = os.path.join(current_dir, "pipeline_model.pkl")

with open(pickle_file_path, "rb") as f:
    pipeline = pickle.load(f)

def get_batch_predictions(test_df):
    test_df = test_df.dropna()
    test_df = test_df.drop_duplicates()
    predictions = pipeline.predict(test_df)
    test_df['predictions'] = list(predictions)
    return test_df