import datetime
from metrics_utility import MetricsUtility
import signal
import time


class Timeout():
    """Timeout class using ALARM signal."""
    class Timeout(Exception):
        pass

    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.sec)

    def __exit__(self, *args):
        signal.alarm(0)

    def raise_timeout(self, *args):
        raise Timeout.Timeout()


class HaloMetrics():
    def __init__(self):
        self.timeout = 240
        self.metrics_utility = MetricsUtility()
        self.current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    def run(self, event, context):
        try:
            with Timeout(self.timeout):
                self.metrics_utility.server_state_summary
                self.metrics_utility.critical_issues_summary
                self.metrics_utility.os_types_summary
                self.metrics_utility.sw_packages_summary
                self.metrics_utility.processes_summary
                self.metrics_utility.local_accounts_summary
                self.metrics_utility.sw_packages_summary
        except Timeout.Timeout:
            return self.current_time
        return self.current_time

def main(event, context):
    print('[CloudPassage Halo Metrics] Loading Lambda function - Get Since & Until timestamps')
    lambda_handler = HaloMetrics()
    return lambda_handler.run('event', 'context')

if __name__ == "__main__":
    main('event', 'context')
