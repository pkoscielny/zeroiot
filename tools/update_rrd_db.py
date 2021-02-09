from re import sub as re_sub
from rrdtool import create as rrd_create, update as rrd_update
from os import path, getenv
from pytz import utc, timezone
from dateutil.parser import parse as dt_parse
from configparser import ConfigParser
from sqlite3 import Error as SqlError, connect as sql_connect


'''
 Configuration.
'''
config = ConfigParser()
config.read('configs/config.ini')

my_tz = getenv('IOT_TIMEZONE') or config['TIME']['TIMEZONE']
sqlite_db = config['DATABASE']['SQLITE_DB']
insolations_rrd_db = config['DATABASE']['INSOLATIONS_RRD_DB']


'''
 Required functions.
'''

def convert_str_to_unix_ts(str):
    # Create datetime object.
    dt = dt_parse(str)

    # Convert UTC to local timezone.
    dt = utc.localize(dt)
    dt = dt.astimezone(timezone(my_tz))

    # Return UNIX timestamp.
    return dt.strftime("%s")


'''
 Read fresh data from sqlite db.
'''
try:
    print('Connecting to SQLite DB')
    dbh = sql_connect(sqlite_db)
except SqlError as error:
    print('Error while connecting to sqlite: ', error)
    exit()

# Create table if not exists for saving state of work.
dbh.execute('''
    CREATE TABLE IF NOT EXISTS iot_system_state (
        subsystem VARCHAR NOT NULL PRIMARY KEY,
        last_processed_id INTEGER NOT NULL DEFAULT 0
    )
''')

# Fetch information about points where the script finished work last time.
subsystem = dict()
for state in dbh.execute("SELECT subsystem, last_processed_id FROM iot_system_state"):
    subsystem[state[0]] = state[1]

print('subsystems state: ', subsystem)
air_state_last_id = subsystem['air_states'] if 'air_states' in subsystem else 0
insolation_last_id = subsystem['insolations'] if 'insolations' in subsystem else 0

# Fetch new data to process.
db_air_states = dbh.execute(f"SELECT temperature, humidity, location, id, created FROM air_states WHERE id > {air_state_last_id}")
db_insolations = dbh.execute(f"SELECT insolation, id, created FROM insolations WHERE id > {insolation_last_id}")

# Create dict with different kind of metrics or localizations. These are in separate rrd databases.
air_states = dict() # many sensors (each location has its own sensor).
insolations = list() # only one sensor.

for item in db_air_states:
    location = re_sub('(\s+)', '_', item[2].strip())
    if location not in air_states:
        air_states[location] = list()

    item_dict = dict(
        temperature = item[0],
        humidity    = item[1],
        id          = item[3],
        created     = convert_str_to_unix_ts(item[4]),
    )
    air_states[location].append(item_dict)

for item in db_insolations:
    item_dict = dict(
        insolation = item[0],
        id         = item[1],
        created    = convert_str_to_unix_ts(item[2]),
    )
    insolations.append(item_dict)

'''
 Check rrdtool db existence. Create it if needed.
 Also find min UNIX timestamp for each rrdtool db.
'''
# Create database for insolation.
if not path.exists(insolations_rrd_db) and insolations:
    print(f"DB {insolations_rrd_db} doesn't exist. Creating...")

    min_timestamp = min(map(lambda i: int(i['created']), insolations)) - 10
    rrd_create(
        insolations_rrd_db,
        '--start', str(min_timestamp),
        '--step', '60',
        'DS:ins:GAUGE:200:0:1024',
        'RRA:AVERAGE:0.5:1:360',  # 6 hours (6*60) with 1 minute resolution.
        'RRA:AVERAGE:0.5:1:1440',  # 1 day (60*24) with 1 minute resolustion.
        'RRA:AVERAGE:0.5:60:168',  # 1 week (24*7) with 1 hour resolustion.
        'RRA:AVERAGE:0.5:360:120',  # 1 month (4*30) with 6 hour resolustion.
        'RRA:AVERAGE:0.5:1440:365',  # 1 year with 1 day resolustion.
        'RRA:MIN:0.5:1:60',
        'RRA:MAX:0.5:1:60',
    )

# Create databases for temperature and humidity per location.
for location, values in air_states.items():
    db_name = f"rrdtool/air_states_{location}.rrd"

    if not path.exists(db_name) and values:  # .path.isfile ?
        print(f"DB {db_name} doesn't exist. Creating...")

        min_timestamp = min(map(lambda i: int(i['created']), values)) - 10
        rrd_create(
            db_name,
            '--start', str(min_timestamp),
            '--step', '60',
            f'DS:temp_{location}:GAUGE:200:0:50',
            f'DS:hum_{location}:GAUGE:200:0:100',
            'RRA:AVERAGE:0.5:1:360',  # 6 hours (6*60) with 1 minute resolution.
            'RRA:AVERAGE:0.5:1:1440',  # 1 day (60*24) with 1 minute resolustion.
            'RRA:AVERAGE:0.5:60:168',  # 1 week (24*7) with 1 hour resolustion.
            'RRA:AVERAGE:0.5:360:120',  # 1 month (4*30) with 6 hour resolustion.
            'RRA:AVERAGE:0.5:1440:365',  # 1 year with 1 day resolustion.
            'RRA:MIN:0.5:1:60',
            'RRA:MAX:0.5:1:60',
        )


'''
 Write new the data to rrdtool db.
'''
# Why in tyr? I'm not sure what with time switch twice a year. We will see.
try:
    print('Updating insolations rrd db')
    max_insolation_id = 0
    for item in insolations:
        if item['id'] > max_insolation_id:
            max_insolation_id = item['id']

        new_row = str(item['created']) + ':' + str(item['insolation'])
        rrd_update(insolations_rrd_db, new_row)

    if max_insolation_id > 0:
        dbh.execute(f"REPLACE INTO iot_system_state(subsystem, last_processed_id) VALUES ('insolations', {max_insolation_id})")
        dbh.commit()
except Exception as error:
    print("Problems during update insolations.rrd: ", error)

try:
    print('Updating air_states rrd dbs')
    max_air_state_id = 0
    for location, values in air_states.items():
        db_name = f"rrdtool/air_states_{location}.rrd"

        for item in values:
            if item['id'] > max_air_state_id:
                max_air_state_id = item['id']

            new_row = str(item['created']) + ':' + str(item['humidity']) + ':' + str(item['temperature'])
            rrd_update(
                db_name, '--template', f'hum_{location}:temp_{location}',
                new_row
            )

    if max_air_state_id > 0:
        dbh.execute(f"REPLACE INTO iot_system_state(subsystem, last_processed_id) VALUES ('air_states', {max_air_state_id})")
        dbh.commit()
except Exception as error:
    print("Problems during update air_states_*.rrd: ", error)

if dbh:
    dbh.close()
    print("Closed connection to SQLite DB")
