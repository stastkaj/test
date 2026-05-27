import subprocess
import datetime
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates

def get_LNB_parameters():
    """
    Parse LNB parameters and return dictionary of these parameters.
    """
    LNB_par={}
    output_show_satellite_plain = subprocess.check_output("{ echo 'show satellite'; echo 'exit'; } | /home/stastka/./cmcs -ip 192.168.0.112", shell=True)
    for line in output_show_satellite_plain.decode('utf-8').split('\n'):
        if (":" in line):
            line_parts=line.split(':')
            if line_parts[1]:
                LNB_par[line_parts[0].strip()]=line_parts[1].strip()
    return LNB_par

def log_values(filename, date, CN, SS):
    with open(filename, "a") as f:
        f.write(f"{date},{CN},{SS}\n")

def read_logged_values(filename):
    dates, CNs, SSs = [], [], []
    if not os.path.exists(filename):
        return dates, CNs, SSs
    with open(filename, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) == 3:
                dates.append(parts[0])
                CNs.append(float(parts[1]))
                SSs.append(float(parts[2]))
    return dates, CNs, SSs

def save_plot(dates, CNs, SSs, plot_filename):
    # Convert string dates to datetime objects
    date_objs = [datetime.datetime.strptime(d, "%H:%M:%S") for d in dates]

    fig, ax1 = plt.subplots(figsize=(10,5))
    ax1.plot(date_objs, CNs, 'b-', label="C/N")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("C/N", color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # Set major ticks every hour
    ax1.xaxis.set_major_locator(mdates.HourLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    ax2 = ax1.twinx()
    ax2.plot(date_objs, SSs, 'r-', label="Signal Strength")
    ax2.set_ylabel("Signal Strength", color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    plt.title("C/N and Signal Strength Over Time")
    fig.tight_layout()
    plt.savefig(plot_filename)
    plt.close()

data_dir = "/mnt/data/received/MTG/FCI/FDHSI"    

LNB_parameters = get_LNB_parameters()
CN = float(LNB_parameters['Carrier to Noise C/N'][:-2])
SS = float(LNB_parameters['Signal Strength'].split()[0])
date_now = datetime.datetime.now().strftime("%H:%M:%S")
date_day = datetime.datetime.now().strftime("%Y%m%d")

log_file = os.path.join(data_dir, f"lnb_log_{date_day}.txt")
plot_file = os.path.join(data_dir, f"lnb_plot_{date_day}.png")

log_values(log_file, date_now, CN, SS)

dates, CNs, SSs = read_logged_values(log_file)
if dates:
    save_plot(dates, CNs, SSs, plot_file)
