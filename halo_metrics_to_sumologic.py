import datetime
from metrics_utility import MetricsUtility
from timeout import Timeout
import time


class HaloMetrics():
    def __init__(self):
        self.t = Timeout(240)
        self.metrics_utility = MetricsUtility()
        self.current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    def run(self, event, context):
        try:
            with self.t:
                self.metrics_utility.server_state_summary
                self.metrics_utility.critical_issues_summary
                self.metrics_utility.os_types_summary
                self.metrics_utility.sw_packages_summary
                self.metrics_utility.processes_summary
                self.metrics_utility.local_accounts_summary
                self.metrics_utility.sw_packages_summary
        except:
            return self.current_time
        return self.current_time

def main(event, context):
    print('[CloudPassage Halo Metrics] Loading Lambda function - Get Since & Until timestamps')
    lambda_handler = HaloMetrics()
    return lambda_handler.run('event', 'context')

if __name__ == "__main__":
    main('event', 'context')
