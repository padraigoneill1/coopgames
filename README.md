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

awslocal dynamodb create-table \
    --table-name coopgames \
    --key-schema AttributeName=id,KeyType=HASH \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --billing-mode PAY_PER_REQUEST \
    --region us-west-2 \ 
    --stream-specification StreamEnabled=true,StreamViewType=NEW_IMAGE

Zip code
zip function.zip lambda_function.py

Deploy to localstack 
aws --endpoint-url=http://localhost:4566 lambda create-function \
    --function-name ProcessDynamoDBStream \
    --runtime python3.8 \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://function.zip \
    --role arn:aws:iam::000000000000:role/lambda-ex 

Get Dynamodb stream 
aws --endpoint-url=http://localhost:4566 dynamodbstreams list-streams --table-name coopgames

Add event source mapping 
aws --endpoint-url=http://localhost:4566 lambda create-event-source-mapping \
    --function-name ProcessDynamoDBStream \
    --event-source-arn ARN_FROM_ABOVE \
    --starting-position LATEST

Test by adding items (I.E) Running transform





