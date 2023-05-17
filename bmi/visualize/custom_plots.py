from ripple_heterogeneity.utils import functions

import matplotlib.pyplot as plt
import scipy as sp


def plot_average_angle(df):
    """
    input: dataframe with the following columns:
        data_normed: normalized data (zscored)
        data: raw data
        channel: channel number
        frame: frame number
        ts: timestamp (generated in seconds)
        angle: angle of the stimulus
    output:
        fig: figure handle
        axs: axis handle
    
    Uses pandas pivot to average across trials for each angle. 
    
    
    """
    # setup figure 
    fig, axs = plt.subplots(1, len(df.angle.unique()), figsize=functions.set_size('thesis',1, subplots=(1,2)),sharey=True)
    axs = axs.ravel()

    # for each angle, plot data as a function of time averaged over trials 
    for angle,ax in zip(df.angle.unique(),axs):
        # get data for each angle
        temp_df = df.loc[df.angle == angle,df.columns != 'file']
        temp_df = temp_df.groupby(['channel', 'frame']).mean()
        temp_df = temp_df.reset_index()
        # use pivot to get mean over tirals
        temp_df = temp_df.pivot(index=['ts'], columns='channel', values='data')
        # for each column in temp_df, zscore    
        temp_df = temp_df.apply(sp.stats.zscore)
        # plot data 
        temp_df.plot(ax = ax)
        ax.set_title(angle)
        # add vertical shaded regions to indicate stimulus between 2 and 4 seconds
        ax.axvspan(2, 4, color='red', alpha=0.25)
        
        ax.set_xlabel('time (s)')
        # remove figure 
        ax.legend().remove()


    axs[0].set_ylabel('average intensity (zscore)')
    # add label to legend 
    
    axs[-1].legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0., title='channel')

    return fig, axs
