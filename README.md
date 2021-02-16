# Prepare

```bash
root@xx-node:~# mkdir -p /opt/scripts
root@xx-node:~# cd /opt/scripts
root@xx-node:/opt/scripts# apt install git
...
```

# Download

```bash
root@xx-node:/opt/scripts# git clone https://github.com/dadatuputi/xxmonitor
...
root@xx-node:/opt/scripts# cd xxmonitor/
root@xx-node:/opt/scripts/xxmonitor#
```

# Configure

Copy the `settings.yaml.example` to `settings.yaml` and fill in your service details. At this time only Pushover is supported. 

# Run from Command Line

```bash
root@xx-node:/opt/scripts/xxmonitor# chmod +x xxmonitor.py
root@xx-node:/opt/scripts/xxmonitor# ./xxmonitor.py -h
usage: xxmonitor.py [-h] [-c CONFIG] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        YAML configuration file containing RSS feeds to check
  --verbose, -v         add 'v's for more verbosity, e.g. -vvvv
  
root@xx-node:/opt/scripts/xxmonitor# ./xxmonitor.py -vv
2021-02-16 16:47:34,275 INFO:Logging level: INFO
2021-02-16 16:47:34,277 INFO:Alarm timeout set to 300
2021-02-16 16:47:34,372 INFO:Loaded in pushover service configuration: {'enabled': True, 'application_token': '<>', 'user_key': '<>', 'priority': 0, 'retry': 3600, 'expire': 10800}
2021-02-16 16:47:34,373 INFO:Spawned subprocess: pid 53319
2021-02-16 16:47:34,373 INFO:Sending start notice to pushover service
2021-02-16 16:47:34,798 INFO:Notified services of monitor start
2021-02-16 16:47:34,798 INFO:Spawned subprocess (pid 53319); alarm when 300s elapse without output
...
```

# Install Service

```bash
root@xx-node:/opt/scripts/xxmonitor# cp xxmonitor.service /etc/systemd/system/xxmonitor.service
root@xx-node:/opt/scripts/xxmonitor# systemctl enable xxmonitor
Created symlink /etc/systemd/system/multi-user.target.wants/xxmonitor.service → /etc/systemd/system/xxmonitor.service.
root@xx-node:/opt/scripts/xxmonitor# systemctl start xxmonitor
root@xx-node:/opt/scripts/xxmonitor# systemctl status xxmonitor
● xxmonitor.service - Elixxir Monitor Service
   Loaded: loaded (/etc/systemd/system/xxmonitor.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2021-01-26 13:43:18 EST; 2s ago
 Main PID: 6619 (python3)
    Tasks: 4 (limit: 4915)
   CGroup: /system.slice/xxmonitor.service
           ├─6619 python3 /opt/scripts/xxmonitor/xxmonitor.py -c /opt/scripts/xxmonitor/settings.yaml
           ├─6620 /bin/sh -c tail -F /opt/xxnetwork/node-logs/node.log | grep --line-buffered "took\|Updating"
           ├─6621 tail -F /opt/xxnetwork/node-logs/node.log
           └─6622 grep --line-buffered took\|Updating

Jan 26 13:43:18 xx-node systemd[1]: Started Elixxir Monitor Service.
root@xx-node:/opt/scripts/xxmonitor#
```

# Test Alert

```bash
root@xx-node:/opt/scripts/xxmonitor# systemctl status xxmonitor
● xxmonitor.service - Elixxir Monitor Service
   Loaded: loaded (/etc/systemd/system/xxmonitor.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2021-01-26 14:48:25 EST; 2s ago
 Main PID: 14633 (python3)
    Tasks: 4 (limit: 4915)
   CGroup: /system.slice/xxmonitor.service
           ├─14633 python3 /opt/scripts/xxmonitor/xxmonitor.py -c /opt/scripts/xxmonitor/settings.yaml
           ├─14634 /bin/sh -c tail -F /opt/xxnetwork/node-logs/node.log | grep --line-buffered "took\|Updating"
           ├─14635 tail -F /opt/xxnetwork/node-logs/node.log
           └─14636 grep --line-buffered took\|Updating

Jan 26 14:48:25 xx-node systemd[1]: Started Elixxir Monitor Service.
root@xx-node:/opt/scripts/xxmonitor# kill 14636
```

At this point you should have an alert that the service stopped, and an alert that it has started again (`Restart=on-failure` in the `.service` file will restart it if, for some reason, `tail` or `grep` are killed).

Checking the status again will show it's running with new PIDs for the child processes:

```bash
root@xx-node:/opt/scripts/xxmonitor# systemctl status xxmonitor
● xxmonitor.service - Elixxir Monitor Service
   Loaded: loaded (/etc/systemd/system/xxmonitor.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2021-01-26 14:48:32 EST; 4s ago
 Main PID: 14655 (python3)
    Tasks: 4 (limit: 4915)
   CGroup: /system.slice/xxmonitor.service
           ├─14655 python3 /opt/scripts/xxmonitor/xxmonitor.py
           ├─14656 /bin/sh -c tail -F /opt/xxnetwork/node-logs/node.log | grep --line-buffered "took\|Updating"
           ├─14657 tail -F /opt/xxnetwork/node-logs/node.log
           └─14658 grep --line-buffered took\|Updating
```
