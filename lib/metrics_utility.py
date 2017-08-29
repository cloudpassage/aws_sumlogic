import datetime
import cloudpassage
import json
import os
from sumologic_https import sumologic_https_forwarder


class MetricsUtility(object):
    def __init__(self):
        halo_api_key_id = os.environ['halo_api_key_id']
        halo_api_secret_key = os.environ['halo_api_secret_key']
        halo_api_endpoint = os.environ['halo_api_endpoint']
        self.sumo_url = os.environ['sumologic_https_url']
        self.current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        self.max_retry = 3
        session = cloudpassage.HaloSession(halo_api_key_id, halo_api_secret_key, api_host=halo_api_endpoint)
        self.api = cloudpassage.HttpHelper(session)

        groups = self.api.get("/v2/groups")
        for group in groups["groups"]:
            if not group["parent_id"]:
                self.root_group = group

    def server_state_summary(self):
        url = "/v2/servers?group_id=%s&state=active,missing,deactivated,retired&descendants=true&group_by=state" % self.root_group["id"]
        servers = self.api.get(url)
        log = { 'os_types_summary': servers }
        data = { 'source': 'script', 'log': log, 'created_time': self.current_time }

        sumologic_https_forwarder(
            url=self.sumo_url,
            data=json.dumps(data, ensure_ascii=False),
            max_retry=self.max_retry
        )

    def critical_issues_summary(self):
        url = "/v2/issues?group_id=%s&descendants=true&state=active,deactivated,missing&status=active&group_by=issue_type,critical" % self.root_group["id"]
        issues = self.api.get(url)
        log = { 'current_issues_by_criticality_summary': issues }
        data = { 'source': 'script', 'log': log, 'created_time': self.current_time }

        sumologic_https_forwarder(
            url=self.sumo_url,
            data=json.dumps(data, ensure_ascii=False),
            max_retry=self.max_retry
        )

    def os_types_summary(self):
        url = "/v2/servers?group_id=%s&descendants=true&state=active&group_by=os_distribution,os_version" % self.root_group["id"]
        os_types = self.api.get(url)
        log = { 'os_types_summary': os_types }
        data = { 'source': 'script', 'log': log, 'created_time': self.current_time }

        sumologic_https_forwarder(
            url=self.sumo_url,
            data=json.dumps(data, ensure_ascii=False),
            max_retry=self.max_retry
        )

    def sw_packages_summary(self):
        url = "/v2/servers?group_id=%s&descendants=true&state=active,missing,deactivated&group_by=os_type,package_name,package_version" % self.root_group["id"]
        sw_packages = self.api.get(url)
        log = { 'sw_packages_summary': sw_packages }
        data = { 'source': 'script', 'log': log, 'created_time': self.current_time }

        sumologic_https_forwarder(
            url=self.sumo_url,
            data=json.dumps(data, ensure_ascii=False),
            max_retry=self.max_retry
        )

    def processes_summary(self):
        url = "/v2/servers?group_id=%s&descendants=true&state=active,missing,deactivated&group_by=os_type,process_name" % self.root_group["id"]
        processes = self.api.get(url)
        log = { 'processes_summary': processes }
        data = { 'source': 'script', 'log': log, 'created_time': self.current_time }

        sumologic_https_forwarder(
            url=self.sumo_url,
            data=json.dumps(data, ensure_ascii=False),
            max_retry=self.max_retry
        )

    def local_accounts_summary(self):
        url = "/v1/local_accounts?group_id=%s&descendants=true&group_by=os_type,username&per_page=100" % self.root_group["id"]
        local_accounts = self.api.get(url)
        log = { 'local_accounts_summary': local_accounts }
        data = { 'source': 'script', 'log': log, 'created_time': self.current_time }

        sumologic_https_forwarder(
            url=self.sumo_url,
            data=json.dumps(data, ensure_ascii=False),
            max_retry=self.max_retry
        )

    def sw_vuln_summary(self):
        url = "/v2/issues?group_id=%s&issue_type=sva&per_page=100&page=1&state=active,missing,deactivated&sort_by=critical.desc,count.desc&descendants=true&group_by=critical,issue_type,rule_key,name,policy_id&status=active" % self.root_group["id"]
        sw_vuln = self.api.get(url)
        log = { 'sw_vulnerability_summary': sw_vuln }
        data = { 'source': 'script', 'log': log, 'created_time': self.current_time }

        sumologic_https_forwarder(
            url=self.sumo_url,
            data=json.dumps(data, ensure_ascii=False),
            max_retry=self.max_retry
        )
