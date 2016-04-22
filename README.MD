# Temperature Monitor
###### Python programs to run both on a Raspberry Pi (/pi) and a server (/app) for recording temperatures and displaying them on a website.

## SETUP
1. Create the pi_config file.
  * Find out the bus # for the sensor:
   `cd /sys/bus/w1/devices/`
   `ls`
  * Copy this into a new file called `pi_config.py` in the TemperatureMonitor directory:
   `sensor_id = 'id-goes-here`
  * Add Email recipients, SendGrid key and a sender address.
2. Set up a cron job on the pi.
  * Open the crontab file:
   `crontab -e`
  * Insert this line at the end:
   `*/2 * * * * python3 /home/pi/TemperatureMonitor/logger.py`
3. TBC
