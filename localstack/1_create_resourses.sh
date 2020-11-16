#!/usr/bin/env bash

set -euo pipefail
echo "Creating resources..."
echo "Creating queues..."

# contract-event-listener integration test queues
awslocal sqs create-queue --queue-name "message-received-event" --output text > /dev/null
awslocal sqs create-queue --queue-name "message-sent-event" --output text > /dev/null
awslocal sqs create-queue --queue-name "message-event" --output text > /dev/null

# websub-hub integration test queues
awslocal sqs create-queue --queue-name "notifications-dev" --output text > /dev/null
awslocal sqs create-queue --queue-name "delivery-outbox-dev" --output text > /dev/null
awslocal sqs create-queue --queue-name "channel-dev" --output text > /dev/null

# SENDER "GB" system test queues
awslocal sqs create-queue --queue-name "notifications-gb" --output text > /dev/null
awslocal sqs create-queue --queue-name "delivery-outbox-gb" --output text > /dev/null
awslocal sqs create-queue --queue-name "channel-gb" --output text > /dev/null

# SENDER "AU" system test queues
awslocal sqs create-queue --queue-name "notifications-au" --output text > /dev/null
awslocal sqs create-queue --queue-name "delivery-outbox-au" --output text > /dev/null
awslocal sqs create-queue --queue-name "channel-au" --output text > /dev/null

echo "Done"
echo "Creating buckets..."
# websub-hub integration test bucket
awslocal s3api create-bucket --bucket "subscriptions-dev"
# SENDER "GB" system test bucket
awslocal s3api create-bucket --bucket "subscriptions-gb"
# SENDER "AU" system test bucket
awslocal s3api create-bucket --bucket "subscriptions-au"
# truffle build artifacts storage bucket used by contract-deployer
awslocal s3api create-bucket --bucket "contract"
echo "Done"
echo "Done"
awslocal sqs list-queues --output table
awslocal s3api list-buckets --output table
# unlocking services that are waiting for aws resources initialization
if [ -d /tmp/unlock-file ]; then
  echo "Unlock file /tmp/unlock-file/AWS created"
  touch /tmp/unlock-file/AWS
fi
