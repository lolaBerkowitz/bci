# import packages and modules
# data wrangling
import numpy as np
import pandas as pd

# data visualization
import matplotlib.pyplot as plt
import seaborn as sns

#io 
import os
import io
import glob
import scipy as sp
import scipy.io as sio
import skimage.io as skio

# image processing
import cv2
from PIL import Image

# loading functions for bioluminescence images

def load_metadata(folder):
    """
    Input:
    folder: string specifying the relative path to a folder containing metadata in '.mat' format
    
    Output:
    df: pandas DataFrame object containing the loaded metadata
    Description: This function loads metadata from a .mat file located in the specified subfolder
    and creates a pandas DataFrame object to store the metadata. 

    The resulting DataFrame object contains columns corresponding to the variables in the 
    loaded metadata file, as well as additional columns for the experiment name, 
    source directory, and start time of the experiment.

    Dependencies: 
        scipy.io
        pandas 
    Example Usage:

    example: 
    df = load_metadata('Y:\\Laurie\\4.23.23\\5aeq_WT\\2023-04-23 4x_test_inj3\\')
    
    Note: This function assumes that the metadata file is stored in a .mat 
    format and that the directory containing the metadata file is structured 
    in a particular way.

    """
    # find name of matfile in subfolder
    matfile = glob.glob(folder + "*.mat")

    # load metadata
    meta_data = sio.loadmat(os.path.join(folder, matfile[0]), simplify_cells=True)
    # upack data
    data = meta_data["vs"]["data"]
    vars = meta_data["vs"]["datanames"]

    # put in dataframe
    df = pd.DataFrame(data, columns=vars)
    # add additional columns
    df["time_sec"] = (df["time"] - df["time"].min()) / 10000
    df["experiment_name"] = meta_data["vs"]["expname"]
    df["source_dir"] = meta_data["vs"]["directory"]
    df["start_time"] = meta_data["vs"]["starttime_str"]

    return df