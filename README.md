# Zero IoT monitoring

This is a monitoring system for air parameters (like temperature or humidity) and activity of the sun. 
The main goal is to run this software on Raspberry Pi Zero or similar small computer with small amount of hardware and low power consumption.

The data could come from external sensors connected to WiFi network by devices (e.g. ESP8266 devices family).

The first layer contains IoT RESTful server based on Flask REST JSON:API and SQLite database which stores data that come from external sensors. 
The second layer is a set of scripts for converting data from SQLite database to RRDTool databases and generating set of time based graphs. 
These graphs are shown in the third layer on html site served by lighttpd server.

If you have more powerful computer you can use Grafana or similar software to show nice graphs with some metrics.
Below I described how to install this on Raspberry OS system.

## Requirements:
- Raspberry OS 
- SQLite
- RRDTool
- Sunwait
- some HTTP server, e.g. Lighttpd

## More descriptive - for proper working ZeroIoT system you need:
- this ZeroIoT server for grabbing and collecting IoT data in simple SQLite database.
- lightweight HTTP server for serving static files like graphs with IoT metrics, e.g. Lighttpd.
- RRDTool for storing time based series of IoT data and generating graphs mentioned above.

## What do you need to run on your Raspberry OS:

### Sunwait installation:
For marking day and night on the grahps.
```
git clone https://github.com/risacher/sunwait
cd sunwait
make
sudo mv sunwait /usr/bin/
```

### Install and setup required packages:
```
sudo apt install sqlite3
sudo apt install lighttpd
sudo apt install rrdtool librrd-dev python3-dev
git clone https://github.com/pkoscielny/zeroiot
cd zeroiot
sudo cp /etc/lighttpd/lighttpd.conf /etc/lighttpd/lighttpd.conf_bak
sudo bash -c 'cat configs/lighttpd.conf > /etc/lighttpd/lighttpd.conf'
```

Open `/etc/lighttpd/lighttpd.conf` with root rights and set absolute path to rrdtool dir in `server.document-root` and restart server:
```
sudo systemctl restart lighttpd
sudo systemctl status lighttpd
```

Set up configuration file and change some configurations as you want:
```
cp configs/config.ini_example configs/config.ini 
```
  
You can run zeroiot step by step or run it in Docker container (please see comments in `configs/Dockerfile`)
Step by step version:
```
sudo apt install python3-venv
python3 -m venv ./venv
source venv/bin/activate
pip install -r configs/requirements.txt
./venv/bin/gunicorn --bind :3000 -w 1 app.main:app
```

Check if Gunicorn works properly:
```
curl http://localhost:3000/air_state
```

If works then add this server to systemd as a service:
```
sudo cp configs/zeroiot.service /etc/systemd/system/ 
```

Set correct paths in /etc/systemd/system/zeroiot.service and run:
```
sudo systemctl daemon-reload
sudo systemctl start zeroiot
sudo systemctl status zeroiot
sudo systemctl enable zeroiot
```
Try to ask ZeroIoT server: http://localhost:3000/air_state

By default Gunicorn has turned off logging and this is what I expected on production environment (vitality of microSD card).
You can observe logs from this service here:
```
sudo journalctl -u zeroiot.service
```

Try run scripts for updating RRD databases and generating graphs:
```
./venv/bin/python tools/update_rrd_db.py 
./venv/bin/python tools/generate_rrd_graphs.py  
```

If these work fine with no errors add these to crontab:
```
*/5 * * * * bash -c 'cd /path/to/your/zeroiot && ./venv/bin/python tools/update_rrd_db.py > /dev/null && ./venv/bin/python tools/generate_rrd_graphs.py > /dev/null'
```

For debugging you can send output to file, e.g: `bash -c '.... > /tmp/zeroiot.log 2>&1'` and observe this:
```
watch -n1 cat /tmp/zeroiot.log
```

Add some data using ZeroIoT. For testing you can add some mocked data using crontab:
```
* * * * * bash -c "curl 'http://localhost:3000/insolation' -H 'Content-Type: application/vnd.api+json' --data-raw '{\"data\":{\"type\":\"insolation\",\"attributes\":{\"insolation\":`shuf -i 700-800 -n 1`,\"device\":\"esp8266_nodemcu_v2\"}}}'"
* * * * * bash -c "curl 'http://localhost:3000/air_state' -H 'Content-Type: application/vnd.api+json' --data-raw '{\"data\":{\"type\":\"air_state\",\"attributes\":{\"temperature\":`shuf -i 18-23 -n 1`,\"humidity\":`shuf -i 40-60 -n 1`,\"device\":\"esp-01S_1\",\"location\":\"kitchen\"}}}'"
* * * * * bash -c "curl 'http://localhost:3000/air_state' -H 'Content-Type: application/vnd.api+json' --data-raw '{\"data\":{\"type\":\"air_state\",\"attributes\":{\"temperature\":`shuf -i 18-23 -n 1`,\"humidity\":`shuf -i 40-60 -n 1`,\"device\":\"esp-01S_2\",\"location\":\"bathroom\"}}}'"
* * * * * bash -c "curl 'http://localhost:3000/air_state' -H 'Content-Type: application/vnd.api+json' --data-raw '{\"data\":{\"type\":\"air_state\",\"attributes\":{\"temperature\":`shuf -i 18-23 -n 1`,\"humidity\":`shuf -i 40-60 -n 1`,\"device\":\"esp-01S_3\",\"location\":\"big_room\"}}}'"
* * * * * bash -c "curl 'http://localhost:3000/air_state' -H 'Content-Type: application/vnd.api+json' --data-raw '{\"data\":{\"type\":\"air_state\",\"attributes\":{\"temperature\":`shuf -i 18-23 -n 1`,\"humidity\":`shuf -i 40-60 -n 1`,\"device\":\"esp-01S_4\",\"location\":\"small_room\"}}}'"
```

After 5 minutes you should see new files in rrdtool dir and everything on site http://localhost.


### Remove the data

If you want to remove the data completely from your ZeroIoT system you can do it this way:
```
cd path/to/your/zeroiot
sudo systemctl stop zeroiot.service
rm iot.db
rm rrdtool/*.rrd
sudo systemctl start zeroiot.service
```

### Dev mode

Run server in dev mode:
```
FLASK_APP="app:create_app('dev')" FLASK_ENV="development" ./venv/bin/python -m flask run --port=3000
```


## API description

These are two main resources with their attributes:
* air state
  * temperature (float)
  * humidity (float)
  * location (string)
  * device (string)
* insolation
  * insolation (int)
  * device (string) 

    
Table of resources:

| url | method | action |
| :--- | :--- | :--- |
| /air_state | GET | list of air state items |
| /air_state | POST | create an air state item |
| /air_state/<int\:id>| GET | retrieve details of an air state item |
| /air_state/<int\:id>| PATCH | update an air state item |
| /air_state/<int\:id>| DELETE | delete an air state item |
| /insolation | GET | list of insolation values |
| /insolation | POST | create  insolation |
| /insolation/<int\:id>| GET | retrieve details of insolation |
| /insolation/<int\:id>| PATCH | update insolation |
| /insolation/<int\:id>| DELETE | delete insolation |


Probably you will need only add new items or show list of items.
Below you can see examples.

### Insolation

This data could come from sensor based on photoresistor.
You can easily saving the state of the sun activity. It affects the state of the air inside.
In cloudy day these values will be significantly lower.
Send this data to ZeroIoT server.

#### Add new insolation value.
Request:
```json
POST /insolation HTTP/1.1
Content-Type: application/vnd.api+json
Accept: application/vnd.api+json

{
  "data": {
    "type": "insolation",
    "attributes": {
      "insolation": 230,
      "device": "esp8266_nodemcu_v2"
    }
  }
}
```
Response:
```json
HTTP/1.1 201 Created
Content-Type: application/vnd.api+json

{
  "data": {
    "type": "insolation",
    "id": "2",
    "attributes": {
      "created": "2021-03-07 09:01:02",
      "insolation": 230,
      "device": "esp8266_nodemcu_v2"
    },
    "links": {
      "self": "/insolation/2"
    }
  },
  "links": {
    "self": "/insolation/2"
  },
  "jsonapi": {
    "version": "1.0"
  }
}
```

#### List of insolation values.
Request:
```json
GET /insolation HTTP/1.1
Accept: application/vnd.api+json
```
Response:
```json
HTTP/1.1 200
Content-Type: application/vnd.api+json

{
  "data": [
    {
      "type": "insolation",
      "attributes": {
        "created": "2021-03-07 09:00:35",
        "insolation": 123,
        "device": "esp8266_nodemcu_v2"
      },
      "id": "1",
      "links": {
        "self": "/insolation/1"
      }
    },
    {
      "type": "insolation",
      "attributes": {
        "created": "2021-03-07 09:01:02",
        "insolation": 230,
        "device": "esp8266_nodemcu_v2"
      },
      "id": "2",
      "links": {
        "self": "/insolation/2"
      }
    }
  ],
  "links": {
    "self": "http://localhost:3000/insolation"
  },
  "meta": {
    "count": 2
  },
  "jsonapi": {
    "version": "1.0"
  }
}
```

### Air states

Many sensors can provide the temperature and the humidity values. 
I recommend to use better quality sensors like DHT21 or better.
Send this data to ZeroIoT server.

#### Add new air state attributes.
Request:
```json
POST /air_state HTTP/1.1
Content-Type: application/vnd.api+json
Accept: application/vnd.api+json

{
  "data": {
    "type": "air_state",
    "attributes": {
      "temperature": 24.1,
      "humidity": 65.4,
      "location": "bathroom",
      "device": "esp8266_dev1"
    }
  }
}
```
Response:
```json
HTTP/1.1 201 Created
Content-Type: application/vnd.api+json

{
  "data": {
    "type": "air_state",
    "attributes": {
      "temperature": "24.1",
      "location": "bathroom",
      "created": "2021-03-07 14:46:37",
      "device": "esp8266_dev1",
      "humidity": "65.4"
    },
    "id": "2",
    "links": {
      "self": "/air_state/2"
    }
  },
  "links": {
    "self": "/air_state/2"
  },
  "jsonapi": {
    "version": "1.0"
  }
}
```

#### List of air states.
Request:
```json
GET /air_state HTTP/1.1
Accept: application/vnd.api+json
```
Response:
```json
HTTP/1.1 200
Content-Type: application/vnd.api+json

{
  "data": [
    {
      "type": "air_state",
      "attributes": {
        "temperature": "23.2",
        "location": "kitchen",
        "created": "2021-03-07 14:45:24",
        "device": "esp8266_dev2",
        "humidity": "56.3"
      },
      "id": "1",
      "links": {
        "self": "/air_state/1"
      }
    },
    {
      "type": "air_state",
      "attributes": {
        "temperature": "24.1",
        "location": "bathroom",
        "created": "2021-03-07 14:46:37",
        "device": "esp8266_dev1",
        "humidity": "65.4"
      },
      "id": "2",
      "links": {
        "self": "/air_state/2"
      }
    }
  ],
  "links": {
    "self": "http://localhost:3000/air_state"
  },
  "meta": {
    "count": 2
  },
  "jsonapi": {
    "version": "1.0"
  }
}
```

For updating and deleting the data you can also use standard JSON:API syntax (https://jsonapi.org/).


Enjoy!