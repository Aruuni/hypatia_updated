import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scienceplots
from matplotlib.ticker import FormatStrFormatter

plt.style.use('science')
import matplotlib as mpl

FROM = 1668
TO = 1593
BW = 50
PROTOCOLS = ['TcpCubic', 'TcpBbr', 'TcpBbr3']
PROTOCOLS_PRINT = ['Cubic', 'BBR', 'BBRv3']
FLOWS = 6
RUNS = [1]
PATH_CHANGE_BEFORE = 140
PATH_CHANGE_AFTER = 184
EXPERIMENT_START_TIME = 120
EXPERIMENT_END_TIME = 200

pd.set_option('display.max_rows', None)
plt.rcParams['text.usetex'] = False

def calculate_rfair(flow_data, window_size=5):
    n = len(flow_data)
    print(n)
    # Calculate the average throughput of the i-th flow over the last w seconds
    avg_thri = flow_data.rolling(window=window_size).mean().iloc[-1]

    print (flow_data.rolling(window=window_size).mean().iloc[-1])
    # Calculate numerator and denominator for R-FAIR
    numerator = np.sqrt(np.sum((flow_data - avg_thri) ** 2))
    denominator = len(flow_data) * np.sqrt(np.sum(flow_data ** 2))
    
    # Calculate R-FAIR
    rfair = numerator / denominator
    
    return 1 - rfair
    

def jains_fairness_index(x):
    return (np.sum(x) ** 2) / (len(x) * np.sum(x ** 2))

FAIRNESS_FUNCTION = jains_fairness_index






def plot_cwnd_data(data, fairness_data, filename):
    COLOR = {'BLUE': '#0C5DA5',
             'GREEN': '#00B945',
             'ORANGE': '#FF9500'
             }
    fig, axes = plt.subplots(nrows=len(PROTOCOLS), ncols=2, figsize=(18, 6), sharex=True, sharey=False)

    for i, protocol in enumerate(PROTOCOLS):
        ax = axes[i, 0]
        fig.suptitle('Cross path experiment (NY to SYD and Lagos to NY)', fontsize=16)
        for n in range(FLOWS):
            ax.plot(data[protocol][n + 1].index, data[protocol][n + 1]['mean'],
                    linewidth=1, label=protocol)
        if i == len(PROTOCOLS) - 1:
            ax.set(xlabel='time (s)')

        ax.set(xlim=[EXPERIMENT_START_TIME,EXPERIMENT_END_TIME])
        ax.set(title=PROTOCOLS_PRINT[i])
        ax.set(ylabel='Goodput (mbps)')
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        ax.grid()

        ax = axes[i, 1]
        ax.plot(fairness_data[protocol]['fairness_set1'].index, fairness_data[protocol]['fairness_set1'],
                linewidth=1, color=COLOR['BLUE'], label='Fairness flows 1,2,3')
        ax.plot(fairness_data[protocol]['fairness_set2'].index, fairness_data[protocol]['fairness_set2'],
                linewidth=1, color=COLOR['GREEN'], label='Fairness flows 4,5,6')
        ax.plot(fairness_data[protocol]['fairness_all_sharing'].index, fairness_data[protocol]['fairness_all_sharing'],
                linewidth=1, color=COLOR['ORANGE'], label='Fairness combined')
        if i == len(PROTOCOLS) - 1:
            ax.set(xlabel='Time (seconds)')

        ax.set(xlim=[EXPERIMENT_START_TIME,EXPERIMENT_END_TIME])  
        ax.set(title=PROTOCOLS_PRINT[i])
        ax.set(ylabel='Jain\'s Fairness Index' if FAIRNESS_FUNCTION == jains_fairness_index else 'R-fair Metric')
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax.grid()
        ax.legend(fontsize='small', loc='lower right')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to make room for the title
    plt.show()
    plt.savefig(filename, dpi=1080)

if __name__ == "__main__":
    goodput_data = {
        'TcpCubic': {i: pd.DataFrame([], columns=['time', 'mean', 'std']) for i in range(1, FLOWS + 1)},
        'TcpBbr': {i: pd.DataFrame([], columns=['time', 'mean', 'std']) for i in range(1, FLOWS + 1)},
        'TcpBbr3': {i: pd.DataFrame([], columns=['time', 'mean', 'std']) for i in range(1, FLOWS + 1)}
    }
    fairness_data = {protocol: {'fairness_set1': pd.Series(dtype='float64'),
                                'fairness_set2': pd.Series(dtype='float64'),
                                'fairness_all_sharing': pd.Series(dtype='float64')}
                     for protocol in PROTOCOLS}

    for PROTOCOL in PROTOCOLS:
        receivers = {i: [] for i in range(1, FLOWS + 1)}
        for RUN in RUNS:
            PATH = 'data/starlink_550_isls_%s_to_%s_with_%s_at_%s_Mbps_%s_run/' % (FROM, TO, PROTOCOL, BW, RUN)
            for n in range(FLOWS):
                if os.path.exists(PATH + 'tcp_flow_%s_rate_in_intervals.csv' % n):
                    receiver_total = pd.read_csv(PATH + 'tcp_flow_%s_rate_in_intervals.csv' % (n), header=None).reset_index(drop=True)
                    receiver_total.columns = ['Flowid', 'time', 'goodput']
                    receiver_total['time'] = receiver_total['time'].apply(lambda x: int(float(x)))
                    receiver_total['time'] = receiver_total['time'] / 1e9
                    receiver_total = receiver_total[receiver_total['time'] >= EXPERIMENT_START_TIME]
                    receiver_total = receiver_total.drop_duplicates('time')
                    receiver_total = receiver_total.set_index('time')
                    receivers[n + 1].append(receiver_total)
                else:
                    print("Folder %s not found" % PATH)
            for n in range(FLOWS):
                goodput_data[PROTOCOL][n + 1]['mean'] = pd.concat(receivers[n + 1], axis=1).mean(axis=1)
                goodput_data[PROTOCOL][n + 1]['std'] = pd.concat(receivers[n + 1], axis=1).std(axis=1)
                goodput_data[PROTOCOL][n + 1].index = pd.concat(receivers[n + 1], axis=1).index

        combined_goodput = pd.DataFrame({n: goodput_data[PROTOCOL][n]['mean'] for n in range(1, FLOWS + 1)})

        # Calculate Jain's Fairness Index for different time segments
        fairness_before_path_change = combined_goodput[combined_goodput.index <= PATH_CHANGE_BEFORE].copy()
        fairness_between_140_185 = combined_goodput[(combined_goodput.index >= PATH_CHANGE_BEFORE) & (combined_goodput.index <= PATH_CHANGE_AFTER)].copy()
        fairness_after_path_change = combined_goodput[combined_goodput.index >= PATH_CHANGE_AFTER].copy()

        # Before 140 seconds: groups of flows
        fairness_before_path_change['fairness_set1'] = fairness_before_path_change.apply(lambda row: FAIRNESS_FUNCTION(row[[1, 2, 3]]), axis=1)
        fairness_before_path_change['fairness_set2'] = fairness_before_path_change.apply(lambda row: FAIRNESS_FUNCTION(row[[4, 5, 6]]), axis=1)
        
        # Between 140 and 185 seconds: all flows
        fairness_between_140_185['fairness_all_sharing'] = fairness_between_140_185.apply(FAIRNESS_FUNCTION, axis=1)

        # After 185 seconds: groups of flows again
        fairness_after_path_change['fairness_set1'] = fairness_after_path_change.apply(lambda row: FAIRNESS_FUNCTION(row[[1, 2, 3]]), axis=1)
        fairness_after_path_change['fairness_set2'] = fairness_after_path_change.apply(lambda row: FAIRNESS_FUNCTION(row[[4, 5, 6]]), axis=1)

        # Concatenate all fairness data
        fairness_combined = pd.concat([fairness_before_path_change[['fairness_set1', 'fairness_set2']],
                                       fairness_between_140_185[['fairness_all_sharing']],
                                       fairness_after_path_change[['fairness_set1', 'fairness_set2']]])

        fairness_data[PROTOCOL]['fairness_set1'] = fairness_combined['fairness_set1']
        fairness_data[PROTOCOL]['fairness_set2'] = fairness_combined['fairness_set2']
        fairness_data[PROTOCOL]['fairness_all_sharing'] = fairness_combined['fairness_all_sharing']
    
    plot_cwnd_data(goodput_data, fairness_data, 'cross_path_hypatia.pdf')
