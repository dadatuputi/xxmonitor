# Prepare

```bash
root@xx-node:~# pip3 install python-pushover
...
root@xx-node:~# mkdir -p /opt/scripts
root@xx-node:~# cd /opt/scripts
root@xx-node:/opt/scripts# apt install git
...
```

# Download

```bash
root@xx-node:/opt/scripts# git clone https://github.com/dadatuputi/xx-monitor
...
root@xx-node:/opt/scripts# cd xx-monitor/
root@xx-node:/opt/scripts/xx-monitor#
```

# Update Pushover Secrets

Pushover is initialized on line 53 - input your Client and App secrets here.

```py
po = pushover.Client("<CLIENT API TOKEN>", api_token="<APP API TOKEN>")
```

# Run from Command Line

```bash
root@xx-node:/opt/scripts/xx-monitor# chmod +x xx-monitor.py
root@xx-node:/opt/scripts/xx-monitor# ./xx-monitor.py -h
usage: xx-monitor.py [-h] [-t [s]] [--verbose]

optional arguments:
  -h, --help            show this help message and exit
  -t [s], --timeout [s]
                        Number of seconds to wait before raising alarm
                        (default 300)
  --verbose, -v         add 'v's for more verbosity, e.g. -vvvv
root@xx-node:/opt/scripts/xx-monitor# ./xx-monitor.py -t 60
Spawned subprocess (pid 14030); alarm when 60s elapse without output
...
```

# Install Service

```bash
root@xx-node:/opt/scripts/xx-monitor# cp xx-monitor.service /etc/systemd/system/xx-monitor.service
root@xx-node:/opt/scripts/xx-monitor# systemctl enable xx-monitor
Created symlink /etc/systemd/system/multi-user.target.wants/xx-monitor.service → /etc/systemd/system/xx-monitor.service.
root@xx-node:/opt/scripts/xx-monitor# systemctl start xx-monitor
root@xx-node:/opt/scripts/xx-monitor# systemctl status xx-monitor
● xx-monitor.service - Elixxir Monitor Service
   Loaded: loaded (/etc/systemd/system/xx-monitor.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2021-01-26 13:43:18 EST; 2s ago
 Main PID: 6619 (python3)
    Tasks: 4 (limit: 4915)
   CGroup: /system.slice/xx-monitor.service
           ├─6619 python3 /opt/scripts/xx-monitor/xx-monitor.py
           ├─6620 /bin/sh -c tail -F /opt/xxnetwork/node-logs/node.log | grep --line-buffered "took\|Updating"
           ├─6621 tail -F /opt/xxnetwork/node-logs/node.log
           └─6622 grep --line-buffered took\|Updating

Jan 26 13:43:18 xx-node systemd[1]: Started Elixxir Monitor Service.
root@xx-node:/opt/scripts/xx-monitor#
```

# Test Alert

```bash
root@xx-node:/opt/scripts/xx-monitor# systemctl status xx-monitor
● xx-monitor.service - Elixxir Monitor Service
   Loaded: loaded (/etc/systemd/system/xx-monitor.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2021-01-26 14:48:25 EST; 2s ago
 Main PID: 14633 (python3)
    Tasks: 4 (limit: 4915)
   CGroup: /system.slice/xx-monitor.service
           ├─14633 python3 /opt/scripts/xx-monitor/xx-monitor.py
           ├─14634 /bin/sh -c tail -F /opt/xxnetwork/node-logs/node.log | grep --line-buffered "took\|Updating"
           ├─14635 tail -F /opt/xxnetwork/node-logs/node.log
           └─14636 grep --line-buffered took\|Updating

Jan 26 14:48:25 xx-node systemd[1]: Started Elixxir Monitor Service.
root@xx-node:/opt/scripts/xx-monitor# kill 14636
```

At this point you should have an alert that the service stopped, and an alert that it has started again (`Restart=on-failure` in the `.service` file will restart it if, for some reason, `tail` or `grep` are killed).

Checking the status again will show it's running with new PIDs for the child processes:

```bash
root@xx-node:/opt/scripts/xx-monitor# systemctl status xx-monitor
● xx-monitor.service - Elixxir Monitor Service
   Loaded: loaded (/etc/systemd/system/xx-monitor.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2021-01-26 14:48:32 EST; 4s ago
 Main PID: 14655 (python3)
    Tasks: 4 (limit: 4915)
   CGroup: /system.slice/xx-monitor.service
           ├─14655 python3 /opt/scripts/xx-monitor/xx-monitor.py
           ├─14656 /bin/sh -c tail -F /opt/xxnetwork/node-logs/node.log | grep --line-buffered "took\|Updating"
           ├─14657 tail -F /opt/xxnetwork/node-logs/node.log
           └─14658 grep --line-buffered took\|Updating
```
