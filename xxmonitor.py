#! /usr/bin/env python3

import time, subprocess, select, time, logging, signal, argparse, sys, yaml, importlib


"""xx-monitor.py: Monitors an elixxir node log for signs of activity and alerts when time elapses without activity"""

_services = {}

# Alarm Handler - this runs when the timeout has been reached
last_log = time.time()
def alarm_handler(signum, stack):
    _t_elapsed = time.time() - last_log
    _title = "Elixxir Timeout"
    _msg = "Elixxir node hasn't participated in a round for {} seconds".format(int(_t_elapsed))
    logging.error(_msg)

    for service in _services:
        logging.info("Sending timeout notice to {} service".format(service))
        _services[service].alert_timeout(_title, _msg)

    signal.alarm(_timeout)

# Exit Handler - this runs when the script is killed
def exit_handler(signum, frame):
    _msg = "Elixxir monitor stopped: {} ({}) received, exiting".format(signal.Signals(signum).name, signum)
    logging.warning(_msg)

    for service in _services:
        logging.info("Sending stop alert to {} service".format(service))
        _services[service].alert_stop("Elixxir Monitor Stopped", _msg)
    
    sys.exit(signum)
   

# Main function - this is where the magic happens
if __name__=='__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--config', default='settings.yaml', help='YAML configuration file containing RSS feeds to check')
    parser.add_argument('--verbose', '-v', action='count', default=0, help="add 'v's for more verbosity, e.g. -vvvv")
    args = parser.parse_args()

    # Initialize logging
    # janky way to translate v-level to logging level
    _ll = max(logging.ERROR - (10*args.verbose), logging.DEBUG)
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=_ll)
    logging.info("Logging level: {}".format(logging._levelToName[_ll]))

    # Read in configuration file
    config = {}
    try:
        with open(args.config) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("Configuration file {} does not exist or is not accessible, exiting".format(args.config))
        sys.exit(1)

    _timeout = config.get('timeout', 300)
    logging.info("Alarm timeout set to {}".format(_timeout))

    # Set up each notification service from the config file. _services is a dict with the key as the service name, and the value is a class object
    try:
        for service_name in config.get('services', {}):
            if config['services'].get(service_name) and config['services'].get(service_name).get('enabled', False):
                # Import module containing service alert class
                _m = importlib.import_module('xxalerts.{}'.format(service_name))
                # Initialize service with values from yaml config file
                _c = getattr(_m, 'Alert{}'.format(service_name.capitalize()))
                _svc_args = config['services'].get(service_name)
                _service = _c(**_svc_args)
                _services[service_name] = _service
                logging.info("Loaded in {} service configuration: {}".format(service_name, _svc_args))
    except (AttributeError, ModuleNotFoundError):
        logging.error("Configuration has settings for `{}` notification type, but no `alarm_{}` handler exists, exiting".format(service_name, service_name))
        sys.exit(1)

    # Set alarm handler to trigger if we don't receive an alert in time
    signal.signal(signal.SIGALRM, alarm_handler)
    logging.debug("Set alarm handler")

    # Set exit handler to trigger when the script is stopped
    signal.signal(signal.SIGTERM, exit_handler)
    logging.debug("Set exit handler")

    # Spawn a process to tail the log and grep for the search string
    _logfile = "/opt/xxnetwork/node-logs/node.log"
    _search_string = '"took\|Updating"'
    proc = subprocess.Popen('tail -F {} | grep -a --line-buffered {}'.format(_logfile, _search_string), 
            shell=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    logging.info("Spawned subprocess: pid {}".format(proc.pid))

    # Send alert to services that monitoring has started
    _title = "Elixxir monitor started" 
    _msg = "Alerting when {}s elapse without participating in a round".format(_timeout)
    for service in _services:
        logging.info("Sending start notice to {} service".format(service))
        _services[service].alert_start(_title, _msg)

    logging.info("Notified services of monitor start")
    logging.info("Spawned subprocess (pid {}); alarm when {}s elapse without output".format(proc.pid, _timeout))

    try:
        # Wait for output from the process until it exits
        while not proc.poll():
            signal.alarm(_timeout)
            _l = proc.stdout.readline().decode('utf-8').strip()
            logging.info("Log read: {}".format(_l))
            last_log = time.time()

    finally:
        logging.error("Subprocess ended unexpectedly, sending SIGTERM")
        exit_handler(signal.SIGTERM, None)
