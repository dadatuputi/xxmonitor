#! /usr/bin/env python3

import time, subprocess, select, time, logging, signal, pushover, argparse, sys

"""xx-monitor.py: Monitors an elixxir node log for signs of activity and alerts when time elapses without activity"""

# Alarm Handler - this runs when the timeout has been reached
last_log = time.time()
def alarm_handler(signum, stack):
    _t_elapsed = time.time() - last_log
    _msg = "Alert - Elixxir node hasn't participated in a round for {} seconds".format(int(_t_elapsed))
    logging.error(_msg)
    po.send_message(_msg, title="Elixxir Alert")
    signal.alarm(args.timeout)

# Exit Handler - this runs when the script is killed
def exit_handler(signum, frame):
    logging.warning("SIGTERM received, exiting")
    po.send_message("Elixxir monitor stopped")
    sys.exit(signum)

# Main function - this is where the magic happens
if __name__=='__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description=__doc__)
    _timeout_default = 60*5
    parser.add_argument('-t', '--timeout', 
        metavar='s', 
        type=int, 
        nargs='?', 
        default=_timeout_default, 
        help='Number of seconds to wait before raising alarm (default {})'.format(_timeout_default))
    parser.add_argument('--verbose', '-v', action='count', default=0, help="add 'v's for more verbosity, e.g. -vvvv")
    args = parser.parse_args()

    # Initialize logging
    # janky way to translate v-level to logging level
    _ll = max(logging.ERROR - (10*args.verbose), logging.DEBUG)
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=_ll)

    logging.info("Logging level: {}".format(logging._levelToName[_ll]))
    logging.info("Alarm timeout set to {}".format(args.timeout))

    # Set alarm handler to trigger if we don't receive an alert in time
    signal.signal(signal.SIGALRM, alarm_handler)
    logging.debug("Set alarm handler")

    # Set exit handler to trigger when the script is stopped
    signal.signal(signal.SIGTERM, exit_handler)
    logging.debug("Set exit handler")

    # Initialize Pushover
    po = pushover.Client("<CLIENT API TOKEN>", api_token="<APP API TOKEN>")
    logging.debug("Initialized Pushover client")

    # Spawn a process to tail the log and grep for the search string
    _logfile = "/opt/xxnetwork/node-logs/node.log"
    _search_string = '"took\|Updating"'
    proc = subprocess.Popen('tail -F {} | grep --line-buffered {}'.format(_logfile, _search_string), 
            shell=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    logging.info("Spawned subprocess: pid {}".format(proc.pid))

    po.send_message("Elixxir monitor started")
    logging.info("Notified Pushover of monitor start")

    print("Spawned subprocess (pid {}); alarm when {}s elapse without output".format(proc.pid, args.timeout))

    try:
        # Wait for output from the process until it exits
        while not proc.poll():
            signal.alarm(args.timeout)
            _l = proc.stdout.readline().decode('utf-8').strip()
            logging.info("Log read: {}".format(_l))
            last_log = time.time()

    finally:
        logging.error("Subprocess ended unexpectedly, sending SIGTERM")
        exit_handler(signal.SIGTERM, None)
