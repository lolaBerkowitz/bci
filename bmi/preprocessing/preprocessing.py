# data wrangling and preprocessing functions
import numpy as np  
import pandas as pd
#i/0
import os
import glob
import skimage.io as skio

# custom functions
from bmi.utils import loading

# signal processing
import scipy as sp




def process_tiff(imstack1,method = 'mean', fs=3.41):
    """ 
    Process tiff stack into a dataframe

    input: 
        imstack1: tiff stack of data (frames, rows, columns, channels)
        method: method for collapsing across rows (default = mean)
        fs: sampling rate (default = 3.41 Hz)
    output: 
        df: dataframe with the following columns:
            data_normed: normalized data (zscored)
            data: raw data
            channel: channel number
            frame: frame number
            ts: timestamp (generated in seconds)

    Pandas is not ideal for large datasets, so currently averaging across rows of each frame. May switch to xarray in the future.
    Xarray accomodates multidimensional data and has a pandas-like API.

    
    """
    image_data = []
    channel_vec = []
    frame_vec = []
    temp_ts = []
    ts = []
    ts_offset = []
    data = []

    for frame in np.arange(imstack1.shape[0]):
        # create timestamp for each pixel in the frame
        temp_ts = np.cumsum([(1/fs/imstack1.shape[1]/imstack1.shape[2])]*(imstack1.shape[1]*imstack1.shape[2])) # time for each pixel * total pizels 
        if frame > 0:
            # add the timestamp of the last pixel in the previous frame to the current frame
            temp_ts = temp_ts + ts_offset[-1]    
        ts_offset.append(temp_ts[-1]) # keep the timetamp of the last pixel in the frame will add to the timestamp of the next frame

        # extract data from each channel in the frame
        for channel in np.arange(imstack1[frame,:,:,:].shape[2]):
        
        # average across rows in each channel
            if method == 'mean':
                rate_vec = np.nanmean(imstack1[frame,:,:,channel], axis=0)
            elif method == 'rate':
                rate_vec = np.sum(imstack1[frame,:,:,channel], axis=0)/((1/fs/imstack1.shape[1]/imstack1.shape[2])*imstack1.shape[1])

            #smooth data (NOT IN USE LB 5/17)
            # smooth_vec = sp.signal.savgol_filter(rate_vec, 10, 3)

            # zscore data
            zscore_vec = sp.stats.zscore(rate_vec)

            # append to list 
            image_data.append(zscore_vec)
            data.append(rate_vec)
            channel_vec.append([channel]*zscore_vec.shape[0])
            frame_vec.append([frame]*zscore_vec.shape[0])
            ts.append(temp_ts)
  
    # flatten lists
    ts = np.array(ts).flatten()
    ts = np.array(ts[::imstack1.shape[1]])  #subsample temp ts so it matches rate_vec 
    image_data = np.array(image_data).flatten()
    data = np.array(data).flatten()
    channel_vec = np.array(channel_vec).flatten()
    frame_vec = np.array(frame_vec).flatten()

    # add to dataframe 
    df = pd.DataFrame(columns=["data_normed",'data', 'channel', 'frame', 'ts'])
    df['data_normed'] = np.squeeze(image_data)
    df['data'] = np.squeeze(data)
    df['channel'] = channel_vec
    df['frame'] = frame_vec
    df['ts'] = ts

    return df

def load_experiment(basepath, fs=3.41):
    tiff_files = glob.glob(os.path.join(basepath,'**\*.tif'))

    # load metadata 
    meta = loading.load_metadata(basepath)

    # meta should be same length as tiff, but in some cases there is an extra metadata row 
    if len(meta) > len(tiff_files):
        Warning('metadata is longer than tiff files, truncating metadata')
        meta = meta[:len(tiff_files)]

    # create empty dataframe
    df = pd.DataFrame()

    # loop through tiff files
    for idx in meta.angle.index:
        imstack1 = skio.imread(tiff_files[idx])
        imstack1 = correct_bidirectional_scan(imstack1)
        temp_df = process_tiff(imstack1,'mean', fs)
        basename = os.path.basename(tiff_files[idx])
        # add metadata to dataframe
        temp_df['file'] = basename  
        temp_df['angle'] = meta.loc[idx, 'angle']
        temp_df['trial'] = meta.loc[idx, 'trial']
        temp_df['repetition'] = meta.loc[idx, 'repetition']

        #concatenate to df
        df = pd.concat([df, temp_df], axis=0)

    return df

def correct_bidirectional_scan(imstack1):
    """
    Correct for bidirectional scan by reversing every other frame
    
    """
    # reverse every other frame
    imstack1[:, 1::2, ::-1, :] = imstack1[:, 1::2, :, :]
    return imstack1