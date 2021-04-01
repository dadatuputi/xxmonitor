from xxalerts.xxalert import XxAlert
import pushover
import logging
import threading
import time

class AlertPushover(XxAlert):
    def __init__(self, **kwargs):
        self.application_token = kwargs['api_token']
        self.user_key = kwargs['user_key']
        self.priority = kwargs.get('priority', 0)
        self.retry = kwargs.get('retry', 3600)
        self.expire = kwargs.get('expire', 10800)
        self.po = pushover.Client(self.user_key, api_token=self.application_token)
        self._ack_thread = None
        logging.debug("Initialized Pushover client")

    def alert_start(self, title, msg):
        self.po.send_message(msg, title=title, priority=min(0,self.priority))

    def alert_timeout(self, title, msg):
        _pargs = {}
        if self.priority == 2:
            # If there's an existing _ack_thread, check it out and handle it if it's completed
            if self._ack_thread:
                if self._ack_thread.is_alive():
                    logging.info("Alert hasn't been acknowledged yet, continuing...")
                else:
                    self._ack_thread = None
                    logging.info("Alert has been acknowledged.")

            # If there's no existing _ack_thread, this will trigger an ack polling thread
            if not self._ack_thread:
                _pargs['retry'] = self.retry
                _pargs['expire'] = self.expire
                _mr = self.po.send_message(msg, title=title, priority=self.priority, **_pargs)

                # Start threaded poll to await ack if priority == 2
                logging.info("Starting polling thread to check for ack for level 2 alert")
                self._ack_thread = threading.Thread(target=self._poll_for_ack, args=(_mr,))
                self._ack_thread.start()
        else:
            self.po.send_message(msg, title=title, priority=self.priority)


    def alert_stop(self, title, msg):
        self.alert_timeout(title, msg)

    def _poll_for_ack(self, message_request):
        while message_request.poll():
            time.sleep(10)
