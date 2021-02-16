from abc import ABCMeta, abstractmethod

class XxAlert(metaclass=ABCMeta):
    @abstractmethod
    def alert_start(self, title, msg):
        """Send an alert when the monitor starts"""

    @abstractmethod
    def alert_timeout(self, title, msg):
        """Send an alert when the monitor detects a timeout"""

    @abstractmethod
    def alert_stop(self, title, msg):
        """Send an alert when the monitor stops"""