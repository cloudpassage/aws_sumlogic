import sys
import botocore


def create_queue(client, name, fifo):
  print ('[create_queue] Creating Queue (Queue name: %s)' % name)
  try:
    if fifo == 'true':
      # Crete FiFo Queue.  Use ContentBasedDeduplication.
      response = client.create_queue(QueueName=name+'.fifo', Attributes = {'FifoQueue': 'true',
                                                                           'ContentBasedDeduplication': 'true'})
    else:
      # Create regular Queue
      response = client.create_queue(QueueName=name)
    print ('[create_queue] Queue created (Queue name: %s) - Queue URL: %s' % (name, response['QueueUrl']))
    return response

  except botocore.exceptions.ClientError as e:
    print ('[create_queue] Error while creating queue (Queue name: %s) - %s' % (name, e.response['Error']['Code']))
    sys.exit(1)


def enqueue (sqs, queue_url, message, message_group_id=''):
  print ('[enqueue] Enqueue message (Queue URL: %s) - Message: %s' %(queue_url, message))
  try:
    if message_group_id == '':
        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=0,
            MessageAttributes={},
            MessageBody=message
        )
    else:
      print ('MessageGroupId: %s' %message_group_id)
      response = sqs.send_message(
          QueueUrl=queue_url,
          DelaySeconds=0,
          MessageAttributes={},
          MessageBody=message,
          MessageGroupId=message_group_id
      )

    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
      print ('[lambda_handler] Error putting message to the queue (Error code - %d)'
             % response['ResponseMetadata']['HTTPStatusCode'])
      print ('[lambda_handler] Response for send_message - HTTPStatusCode: %d (Message: %s)'
             % (response['ResponseMetadata']['HTTPStatusCode'], message))
    return response

  except Exception as e:
    print ('[enqueue] Error while adding message to the queue (Queue URL: %s) - Message: %s' %(queue_url, message))
    print ('[enqueue] Error message - %s' % e)
    sys.exit(1)


def dequeue(sqs, queue_url):
  print ('[dequeue] Dequeue message (Queue URL: %s)' % queue_url)
  try:
      response = sqs.receive_message(
          QueueUrl=queue_url,
          AttributeNames=[],
          MaxNumberOfMessages=1,
          MessageAttributeNames=[],
          VisibilityTimeout=0,
          WaitTimeSeconds=0
      )
      print ('[dequeue] Length of the queue: %d' % len(response['Messages']))

      if len(response['Messages']) == 1:
          return response
      elif len(response['Messages']) == 0:
          print ('[dequeue] No message to retrieve from the queue. Error!!')
          sys.exit(1)
      else:
          print ('[dequeue] More than 1 message found from the queue. Error!!')
          sys.exit(1)

  except Exception as e:
      print ('[dequeue] Error while getting message from the queue (Queue URL: %s)' % queue_url)
      print ('[dequeue] Error message - %s' % e)
      sys.exit(1)


def delete_message(sqs, receipt_handle, queue_url):
  print ('[delete_message] Delete message (Queue URL: %s) - Receipt Handle ID: %s' % (queue_url, receipt_handle))
  response = sqs.delete_message(
      QueueUrl=queue_url,
      ReceiptHandle=receipt_handle
  )
  return response
