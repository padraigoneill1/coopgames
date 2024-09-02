# coopgames
POC project

#TODO

Manual Setup:
Get Keys
https://api-docs.igdb.com/#getting-started
Setup Localstack
https://docs.localstack.cloud/getting-started/installation/
Run Localstack
localstack start -d

Create SQS Fifo Queue

aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name coop-queue.fifo --attributes FifoQueue=true,ContentBasedDeduplication=true

See messages in SQS
curl -H "Accept: application/json" \
    "http://localhost.localstack.cloud:4566/_aws/sqs/messages?QueueUrl=http://sqs.us-west-2.localhost.localstack.cloud:4566/000000000000/coop-queue.fifo"


Create SQS Fifo Queue
awslocal dynamodb create-table \
    --table-name coopgames \
    --key-schema AttributeName=id,KeyType=HASH \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --billing-mode PAY_PER_REQUEST \
    --region us-west-2


Data Increment
Update Table to have a stream
Invoke lambda from stream
Send email
