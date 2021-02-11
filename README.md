# Zero IoT monitoring

This is monitoring system for air parameters (like temperature or humidity) and activity of the sun.
The main goal is to run this software on Raspberry Pi Zero or similar small computer with small amount of hardware and low power consumption.

First layer contains IoT RESTful server based on Flask and SQLite database which stores data come from external sensors.
Second layer is set of scripts for converting data from SQLite database to RRDTool databases and generate set of time based graphs.
These graphs are shown in third layer on html site served by lighttpd server.

If you have more powerful computer you can use Grafana or similar software to show nice graphs with some metrics.
Below I descbided how to install this on Raspberry OS system.

## Requirements:
- Raspberry OS 
- SQLite
- RRDTool
- Sunwait
- some HTTP server, e.g. Lighttpd

## More descriptive - for proper working IoT system you need:
- this IoT server for grabbing and collecting IoT data in simple SQLite database.
- lightweight HTTP server for serving static files like graphs with IoT metrics, e.g. Lighttpd.
- RRDTool for storing time based series of IoT data and generating graphs mentioned above.

## What do you need to run on your Raspberry OS:

### Sunwait installation:
```
git clone https://github.com/risacher/sunwait
cd sunwait
make
sudo mv sunwait /usr/bin/
```

### Install and setup required packages:
```
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
  
You can run zeroiot step by step or run it in Docker container (please see comments in configs/Dockerfile)
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

By default Gunicorn has turned off logging and it is what I expected for on production environment (Raspberry Pi SD card).
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

Add some data using zeroiot. For testing you can add some mocked data into crontab:
```
* * * * * bash -c "curl 'http://localhost:3000/insolation' -H 'Content-Type: application/json;charset=UTF-8' --data-raw '{\"insolation\":`shuf -i 700-800 -n 1`,\"device\":\"esp8266_nodemcu_v2\"}'"
* * * * * bash -c "curl 'http://localhost:3000/air_state' -H 'Content-Type: application/json;charset=UTF-8' --data-raw '{\"temperature\":`shuf -i 18-23 -n 1`,\"humidity\":`shuf -i 40-60 -n 1`,\"device\":\"esp-01S_1\",\"location\":\"kitchen\"}'"
* * * * * bash -c "curl 'http://localhost:3000/air_state' -H 'Content-Type: application/json;charset=UTF-8' --data-raw '{\"temperature\":`shuf -i 18-23 -n 1`,\"humidity\":`shuf -i 40-60 -n 1`,\"device\":\"esp-01S_1\",\"location\":\"bathroom\"}'"
* * * * * bash -c "curl 'http://localhost:3000/air_state' -H 'Content-Type: application/json;charset=UTF-8' --data-raw '{\"temperature\":`shuf -i 18-23 -n 1`,\"humidity\":`shuf -i 40-60 -n 1`,\"device\":\"esp-01S_2\",\"location\":\"big_room\"}'"
* * * * * bash -c "curl 'http://localhost:3000/air_state' -H 'Content-Type: application/json;charset=UTF-8' --data-raw '{\"temperature\":`shuf -i 18-23 -n 1`,\"humidity\":`shuf -i 40-60 -n 1`,\"device\":\"esp-01S_2\",\"location\":\"small_room\"}'"
```

After 5 minutes you should see new files in rrdtool dir and everything on site http://localhost.

Enjoy!
