import requests
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import pandas as pd
from scipy.signal import correlate
import ftplib
from netCDF4 import Dataset
import pytz


def convert_time_to_seconds(t):
    if len(t) == 4 and t.isdigit():  # Ensure the string has 4 digits
        return int(t[:2])*3600 + int(t[2:])*60
    else:
        return np.nan  # Return NaN for invalid entries

def format_time_str(time_str):
    # Convert the time string to an integer and ensure it's within the range [0, 86399]
    time_val = int(time_str)
    if time_val < 0 or time_val > 86399:
        return None
    
    # Extract hours and minutes
    hours = time_val // 3600
    minutes = (time_val % 3600) // 60
    
    # Return the formatted time string without the colon
    return f"{hours:02d}{minutes:02d}"

#######################################################################################BLOCK1

start_date = datetime(2014, 10, 29)
end_date = datetime(2014, 10, 31)
date_range = pd.date_range(start_date, end_date)

# Convert dates to the desired format
dates_formatted = date_range.strftime('%Y%m%d')
Dates = dates_formatted.tolist()
# Adjusting for hours off at the beginning and end (in minutes)
hours_off_beg = 240  # 4 hours
hours_off_end = 480  # 8 hours

'''
I coded the sym-h and ae indices in later and because the data store
# was formatted differently (with data for an entire month in one file)
# you have to distinguish which day of the month you want to look at
# (this is individually and not a range of dates). The code for these
# indices also does not pull from the internet so you have to go grab
# the file from OmniWeb and then choose the day from the month you're
# looking at
'''

#######################################################################################BLOCK2

api_base_url = 'https://sohoftp.nascom.nasa.gov/sdb/ace/daily/'
sw_data = []  # Initialize outside the loop if collecting data across all dates

for w, date_str in enumerate(dates_formatted):  # Use enumerate to get index and date string
    sw_file = f'{date_str}_ace_mag_1m.txt'
    url = f'{api_base_url}{sw_file}'
    response = requests.get(url)
    if response.status_code == 200:
        data_lines = response.text.split('\n')[15:]  # Adjust the line number as needed
        
        for line in data_lines:
            parts = line.split()  # Make sure this line is properly indented within the for loop
            if len(parts) > 10:  # Check if 'parts' has more than 10 elements
                try:
                    time_val = parts[5]  # Accessing the 6th element, ensure this index exists in your data
                    bz_val = float(parts[9]) if parts[9] != '-999.9' else np.nan
                    bt_val = float(parts[10]) if parts[10] != '-999.9' else np.nan
                    sw_data.append([date_str, time_val, bz_val, bt_val])  # Append the data to 'sw_data'
                except ValueError:
                    continue  # Skip the line if conversion fails
            else:
                continue


#######################################################################################BLOCK3
#######################################################################################BLOCK4 Merged with 3
# Convert to DataFrame for easier handling

bz_df = pd.DataFrame(sw_data, columns=['Date', 'Time', 'Bz', 'Bt'])  # Adjust columns as needed
bz_df.replace(-999.9, np.nan, inplace=True)
bz_df.dropna(inplace=True)

#######################################################################################BLOCK5
      
for w, date_str in enumerate(dates_formatted):  # Plot for each date if needed
    # Filter data for the current date
    daily_df = bz_df[bz_df['Date'] == date_str]

    # Convert 'Time' to datetime format for plotting
    current_date = datetime.strptime(date_str, "%Y%m%d")
    timesw_datetime = [current_date + timedelta(seconds=int(t)) for t in daily_df['Time']]

    # Plotting


    plt.figure(figsize=(10, 6))
    plt.plot(timesw_datetime, daily_df['Bt'], label='Bt')
    plt.plot(timesw_datetime, daily_df['Bz'], label='Bz')
    plt.axhline(0, color='k', linewidth=1)
    plt.xlim([timesw_datetime[0], timesw_datetime[-1]])
    plt.title(f'{date_str} Bt and Bz', fontsize=14)
    plt.xlabel('Time [hours UT]', fontsize=12)
    plt.ylabel('Magnetic Flux Density [nT]', fontsize=12)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.legend(loc='best')
    plt.gcf().autofmt_xdate()
    plt.savefig(f'{date_str}BzandBt.png', dpi=300)
    plt.show()





#######################################################################################BLOCK6

for w, date_str in enumerate(dates_formatted):  # Iterate over each date
    # Filter data for the current date
    daily_df = bz_df[bz_df['Date'] == date_str]
    
    # Convert 'Time' to datetime format for plotting
    current_date = datetime.strptime(date_str, "%Y%m%d")
    timesw_datetime = [current_date + timedelta(seconds=int(t)) for t in daily_df['Time']]

    # Truncate the last 8 hours from the data
    truncate_hours = 8
    data_end_time = timesw_datetime[-1] - timedelta(hours=truncate_hours)
    timesw_datetime_truncated = [t for t in timesw_datetime if t <= data_end_time]
    Bz_truncated = daily_df['Bz'][:len(timesw_datetime_truncated)]

    # Plotting


    plt.figure(figsize=(10, 6))
    plt.plot(timesw_datetime_truncated, Bz_truncated, label='Bz')

    plt.axhline(0, color='k', linewidth=1)

    plt.xlim([timesw_datetime[0], data_end_time])


    plt.title(f'{date_str} Bz', fontsize=14)
    plt.xlabel('Time [hours UT]', fontsize=12)
    plt.ylabel('Magnetic Flux Density [nT]', fontsize=12)

    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))  # Major ticks every 2 hours
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))  # Display hours only
    plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=1))  # Minor ticks every hour

    plt.gcf().autofmt_xdate()


    plt.savefig(f'{date_str}_Bz.png', dpi=300)

    plt.show()


#######################################################################################BLOCK7
#Spectrograph not used
#######################################################################################BLOCK8
#######################################################################################BLOCK9
#######################################################################################BLOCK10
#######################################################################################BLOCK11
#######################################################################################BLOCK12
#######################################################################################BLOCK13
#######################################################################################BLOCK14
#######################################################################################BLOCK15


start_date = datetime(2014, 10, 29)
end_date = datetime(2014, 10, 31)
dates_formatted = pd.date_range(start_date, end_date).strftime('%Y%m%d')

# Initialize an empty list to store solar wind data
sw_data = []

# Base URL for data retrieval
api_base_url = 'https://sohoftp.nascom.nasa.gov/sdb/ace/daily/'

# Fetch solar wind speed data for each date
for date_str in dates_formatted:
    sw_file = f'{date_str}_ace_swepam_1m.txt'
    url = f'{api_base_url}{sw_file}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data_lines = response.text.split('\n')[15:]  # Skip header lines
        
        for line in data_lines:
            parts = line.split()
            if len(parts) >= 9 and parts[8].replace('.', '', 1).isdigit() and parts[8] != '-9999.9':
                time_val = parts[5]  # Time in HHMM format
                sw_speed = float(parts[8])  # Solar wind speed
                sw_data.append([date_str, time_val, sw_speed])

# Convert the list to a DataFrame
sw_df = pd.DataFrame(sw_data, columns=['Date', 'Time', 'Speed'])

########################################################################################BLOCK16
                
# Analysis and Plotting
for w, date_str in enumerate(dates_formatted):
    daily_sw_df = sw_df[sw_df['Date'] == date_str].copy()
    
    
    # Apply the formatting function to the 'Time' column
    daily_sw_df['Time'] = daily_sw_df['Time'].apply(format_time_str)
 
    
    # Now convert to 'DateTime' using the corrected 'Time' values
    daily_sw_df['DateTime'] = pd.to_datetime(daily_sw_df['Date'] + daily_sw_df['Time'], format='%Y%m%d%H%M').dt.tz_localize(pytz.utc)
    
    # Your plotting code follows...
    plt.figure(figsize=(10, 6))
    plt.plot(daily_sw_df['DateTime'], daily_sw_df['Speed'], label='Solar Wind Speed')
    plt.title(f'Solar Wind Speed on {date_str}')
    plt.xlabel('Time [UTC]')
    plt.ylabel('Solar Wind Speed [km/s]')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
#######################################################################################BLOCK17



for date_str in dates_formatted:

    bz_df['Date'] = pd.to_datetime(bz_df['Date'], format='%Y%m%d')

    bz_df['Time'] = pd.to_timedelta(bz_df['Time'])

# Convert 'Time' column to total minutes
    bz_df['Time'] = bz_df['Time'].dt.total_seconds() / 60

    # Now you can convert the 'Time' column to integer
    bz_df['Time'] = bz_df['Time'].astype(int)

# Convert 'Time' column to timedeltas without specifying the unit
    bz_df['Time'] = pd.to_timedelta(bz_df['Time'], errors='coerce')

    # Check if there are any missing values after conversion
    if bz_df['Time'].isnull().any():
    # Handle missing or invalid values if necessary
        pass

    # Combine 'Date' and 'Time' columns to get the datetime representation for bz_df
    bz_df['DateTime'] = bz_df['Date'] + bz_df['Time']

for date_str in dates_formatted:
    daily_sw_df = sw_df[sw_df['Date'] == date_str].copy()
    
    # Apply the formatting function to the 'Time' column
    daily_sw_df['Time'] = daily_sw_df['Time'].apply(format_time_str)
    
    # Convert 'Date' and 'Time' columns to appropriate datetime objects for daily_sw_df
    daily_sw_df['DateTime'] = pd.to_datetime(daily_sw_df['Date'] + daily_sw_df['Time'], format='mixed').dt.tz_localize(pytz.utc)
    
    # Plotting Bz vs Velocity
    plt.clf()
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot Bz on the left y-axis
    ax1.plot(bz_df['DateTime'], bz_df['Bz'], 'b', label='Bz')
    ax1.set_xlabel('Time [hours UTC]')
    ax1.set_ylabel('Magnetic Flux Density [nT]', color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # Create a horizontal line at y=0
    ax1.axhline(0, color='k')

    # Create a secondary y-axis for the solar wind speed
    ax2 = ax1.twinx()
    ax2.plot(daily_sw_df['DateTime'], daily_sw_df['Speed'], 'r', label='Speed')
    ax2.set_ylabel('Speed [km/s]', color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    # Set x-axis ticks and labels
    ax1.set_xticks([0, 3600, 7200, 10800, 14400, 18000, 21600, 25200, 28800, 32400, 36000, 39600, 43200, 46800, 50400, 54000, 57600, 61200, 64800, 68400, 72000, 75600, 79200, 82800, 86400])
    ax1.set_xticklabels(['0', ' ', '02', ' ', '04', ' ', '06', ' ', '08', ' ', '10', ' ', '12', ' ', '14', ' ', '16', ' ', '18', ' ', '20', ' ', '22', ' ', '24'])

    # Title and legend
    plt.title(f"{date_str} Bz and Solar Wind Speed")
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='best')

    # Saving the plot
    plt.tight_layout()
    plt.savefig(f"{date_str}BzandSWSpeed.png")
    plt.show()
    



#######################################################################################BLOCK18
#######################################################################################BLOCK19
#######################################################################################BLOCK20
#######################################################################################BLOCK21
#######################################################################################BLOCK22
#######################################################################################BLOCK23
#######################################################################################BLOCK24
#######################################################################################BLOCK25
#######################################################################################BLOCK26 FINAL

