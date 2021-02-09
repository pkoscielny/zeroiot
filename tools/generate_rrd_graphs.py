import re
import rrdtool
import sqlite3
from os import popen, getenv
from configparser import ConfigParser


'''
 Configuration.
'''
config = ConfigParser()
config.read('configs/config.ini')

latitude = getenv('IOT_LATITUDE') or config['GEO']['LATITUDE']
longitude = getenv('IOT_LONGITUDE') or config['GEO']['LONGITUDE']
sqlite_db = config['DATABASE']['SQLITE_DB']
insolations_rrd_db = config['DATABASE']['INSOLATIONS_RRD_DB']


'''
 Fetch unique list of locations.
 It is independent locations list of fresh data.
 When I had one script for updating rrd databases and generating graphs based on fresh data from sensors
 I had a problem with disappearing of some random metrics from graphs. Some sensor may has been delaying
 and his metrics did not appear.
'''
try:
    print('Connecting to SQLite DB')
    dbh = sqlite3.connect(sqlite_db)
except sqlite3.Error as error:
    print('Error while connecting to sqlite: ', error)
    exit()

print("Locations fetching")
sql_locations = "SELECT DISTINCT(location) AS loc FROM air_states WHERE created > DATE('now', '-1 year') ORDER BY loc;"
locations = [re.sub('(\s+)', '_', row[0].strip()) for row in dbh.execute(sql_locations)]
if dbh:
    dbh.close()
    print("Closed connection to SQLite DB")

'''
 Get sunrise and sunset time.
'''
print('Fetching sunrise and sunset data')
stream = popen('sunwait report '+ latitude +' '+ longitude +' | grep \'Daylight\' | awk \'{ printf "%s,%s", $4, $6 }\'')
sunrise_time, sunset_time = stream.read().strip().split(',')

# Extract sunrise and sunset time (hh:mm).
sunrise_hour, sunrise_minute = map(lambda i: int(i), sunrise_time.split(':'))
sunset_hour, sunset_minute = map(lambda i: int(i), sunset_time.split(':'))

# Seconds of end and begin of night.
sunset_sec = sunset_hour * 3600 + sunset_minute * 60
sunrise_sec = sunrise_hour * 3600 + sunrise_minute * 60


'''
 Generate graphs.
'''
periods = ['6h', '1d', '1w', '1m', '1y']
time_map = {
    '6h': '6h',
    '1d': '24h',
    '1w': 'week',
    '1m': 'month',
    '1y': 'year',
}
print("Generating insolation graphs")
for time in periods:
    rrdtool.graph(
        f'rrdtool/insolations_{time}.png',
        '--start', f'-{time}', '--end', 'now',
        '--full-size-mode', '--slope-mode', '--width=700', '--height=400',
        '--vertical-label=Ins', f'--title=Insolation diagram - last {time_map[time]}',
        '--color=SHADEB#8899CC', '--watermark=IoT - insolation',
        '--font=LEGEND:8:Courier New',
        f"DEF:insolation={insolations_rrd_db}:ins:AVERAGE",
        f'CDEF:nightpos=LTIME,86400,%,{sunrise_sec},LT,INF,LTIME,86400,%,{sunset_sec},GT,INF,UNKN,insolation,+,IF,IF',
        'AREA:nightpos#CCCCCC',
        'COMMENT:Sunrise\: '+ sunrise_time.replace(':','\:') +'\l',
        'COMMENT:Sunset\:  '+ sunset_time.replace(':','\:') +'\l',
        'COMMENT:               Last   Avg   Min   Max\l',
        'AREA:insolation#1598C3:insolation',
        'GPRINT:insolation:LAST:%4.0lf',
        'GPRINT:insolation:AVERAGE:%4.0lf',
        'GPRINT:insolation:MIN:%4.0lf',
        'GPRINT:insolation:MAX:%4.0lf\l',
    )

# Small explanations of nightpos variable:
# f'CDEF:nightpos=LTIME,86400,%,{sunrise_sec},LT,INF,LTIME,86400,%,{sunset_sec},GT,INF,UNKN,insolation,+,IF,IF',
# LTIME,86400,% - gives current day second, e.g. 42.
# 42,sunrise_sec,LT - gives 1 because it is night.
# So I'v got: 1,INF
# 42,sunset_sec,GT - gives 0.
# Here I have: 1,INF,0,INF.
# UNKN,insolation,+ - here must be some operation on one of the DEF or CDEF variable (see logs from rrdtool if not).
# 1,INF,0,INF,<result of +>,IF,IF - if 0 then INF else if 1 then INF else <result of +> = 1 (it's night)
# INF is for 0 -> positive infinity. If you have some negative values, e.g. outside air temperature
# then you have to add next CDEF variable with NEGINF instead of INF.

# Transform air_states to one set of graphs per period.
temp_colors = [
    '#008000',  # green
    '#000000',  # black
    '#808001',  # olive
    '#CC3118',  # red dark.
    '#7648EC',  # purple light.
    '#EC9D48',  # orange light.
    '#ECD748',  # yellow light.
    '#DE48EC',  # pink light.
    '#54EC48',  # green light.
    #
    # '#EA644A', # red light.
    # '#CC7016', # orange dark.
    # '#C9B215', # yellow dark.
    # '#24BC14', # green dark.
    # '#1598C3', # blue dark.
    # '#B415C7', # pink dark.
    # '#4D18E4', # purple dark.
    #
    '#48C4EC',  # blue light.
    '#808080',  # gray
    '#00FF00',  # lime
    '#C0C0C0',  # silver
    '#FF0000',  # red
    '#FFFF00',  # yellow
]
hum_colors = [
    '#00FFFF',  # aqua
    '#008080',  # teal
    '#000080',  # navy
    '#800080',  # purple
    '#FF00FF',  # fuchsia
    '#0000FF',  # blue
    '#800000',  # maroon
]


def get_temp_colour():
    while True:
        for color in temp_colors:
            yield color


def get_hum_colour():
    while True:
        for color in hum_colors:
            yield color


metrics_map = {
    'temperature': 'temp',
    'humidity': 'hum',
    'insolation': 'ins',
}

metric_type_map = {
    'LAST': 'last',
    'AVERAGE': 'avg',
    'MIN': 'min',
    'MAX': 'max',
}

air_state_metrics = ['temperature', 'humidity']

# Find the longest metric name for properly formatting graph legend.
metric_len_max = 0
for metric in air_state_metrics:
    for location in locations:
        metric_len = len(f'{metric}_{location}')
        if metric_len > metric_len_max:
            metric_len_max = metric_len

params = []
some_of_metric = None # get some of metric name for proper working night layer on the graph.
hum_colour = get_hum_colour()
temp_colour = get_temp_colour()
legend_is_added = False
for metric in air_state_metrics:
    print('Preparing graphs for ', metric)

    for location in locations:
        print("\tlocation: ", location)

        db_name = f"rrdtool/air_states_{location}.rrd"

        metric_name = f'{metrics_map[metric]}_{location}'
        full_metric = f'{metric}_{location}'

        # For proper legend formatting.
        additional_spaces = ' ' * (metric_len_max - len(full_metric))

        if some_of_metric is None:
            some_of_metric = full_metric

        # Get next colour from pool.
        colour = next(temp_colour) if metric == 'temperature' else next(hum_colour)

        params.append(f'DEF:{full_metric}={db_name}:{metric_name}:AVERAGE')
        if not legend_is_added:
            params.append(f'COMMENT:{additional_spaces}                        Last    Avg    Min    Max\l')
            legend_is_added = True
        params.append(f'LINE2:{full_metric}{colour}:{full_metric}')

        params.append(f'GPRINT:{full_metric}:LAST:{additional_spaces}%3.1lf')
        params.append(f'GPRINT:{full_metric}:AVERAGE: %3.1lf')
        params.append(f'GPRINT:{full_metric}:MIN: %3.1lf')
        params.append(f'GPRINT:{full_metric}:MAX: %3.1lf\l')

if params:
    # Put night as a first layer on the graph.
    params.insert(1, f'CDEF:nightpos=LTIME,86400,%,{sunrise_sec},LT,INF,LTIME,86400,%,{sunset_sec},GT,INF,UNKN,{some_of_metric},+,IF,IF')
    params.insert(2, 'AREA:nightpos#CCCCCC')

    print ('Generate graphs for temperature and humidity')
    for time in periods:
        rrdtool.graph(
            f'rrdtool/temp_hum_{time}.png',
            '--start', f'-{time}', '--end', 'now',
            '--full-size-mode', '--slope-mode', '--width=700', '--height=500',
            '--vertical-label=Temp / Hum', f'--title=Temperature and humidity diagram - last {time_map[time]}',
            '--color=SHADEB#9999CC', '--watermark=IoT - temperature and humidity',
            '--font=LEGEND:8:Courier New',
            params,
        )

print("Done")
