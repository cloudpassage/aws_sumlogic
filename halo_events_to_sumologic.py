import datetime
import os
import json
import boto3
import botocore
from sumologic_https import sumologic_https_forwarder
import cloudpassage
import queue_utility as q


class LambdaHandler():
    def __init__(self):
        self.sumo_url = os.environ['sumologic_https_url']
        self.halo_api_key_id = os.environ['halo_api_key_id']
        self.halo_api_secret_key = os.environ['halo_api_secret_key']
        self.halo_api_endpoint = os.environ['halo_api_endpoint']
        self.aws_region_name = os.environ['aws_region_name']
        self.max_retry = 3
        self.client = boto3.client('sqs', region_name=self.aws_region_name)
        self.current_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        self.timestamp_queue = 'halo_last_time_ran-test'

    def pull_halo_events(self, since, until):
        session = cloudpassage.HaloSession(self.halo_api_key_id, self.halo_api_secret_key, api_host=self.halo_api_endpoint)
        events = cloudpassage.Event(session)
        list_of_events = events.list_all(pages=50, since=since, until=until)
        return list_of_events

    def run(self, event, context):
        try:
            response = self.client.get_queue_url(QueueName=self.timestamp_queue)
            queue_url = response['QueueUrl']
            print ('[lambda_handler] Queue found (Queue URL: %s)' % queue_url)
            response = q.dequeue(self.client, queue_url=queue_url)
            since = response['Messages'][0]['Body']
            receipt_handle = response['Messages'][0]['ReceiptHandle']
            print ('[lambda_handler] Since = %s\n[lambda_handler] Until = %s' % (since, self.current_time))

            list_of_events = self.pull_halo_events(since, self.current_time)

            print('[lambda_handler] Number of events: %d' % len(list_of_events))

            if len(list_of_events) > 0:
                last_event_created_at = list_of_events[-1]['created_at']

                for each in list_of_events:
                    sumologic_https_forwarder(self.sumo_url,
                                              json.dumps(each, ensure_ascii=False),
                                              self.max_retry)
            else:
                last_event_created_at = self.current_time

            response = q.delete_message(self.client, receipt_handle=receipt_handle, queue_url=queue_url)

            q.enqueue(self.client, queue_url=queue_url, message=last_event_created_at)
            print("The new since time (create_at of the last event) - %s" %last_event_created_at)

        except botocore.exceptions.ClientError as e:
            if 'NonExistentQueue' in e.response['Error']['Code']:
                response = q.create_queue(self.client, name=self.timestamp_queue, fifo='false')
                q.enqueue(self.client, queue_url=response['QueueUrl'], message=self.current_time)

        return self.current_time


def main(event, context):
    print('[CloudPassage Halo Events] Loading Lambda function - Get Since & Until timestamps')
    lambda_handler = LambdaHandler()
    return lambda_handler.run('event', 'context')

if __name__ == "__main__":
    main('event', 'context')
