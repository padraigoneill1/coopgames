# coopgames
This project is a Proof of Concept designed 
to consume and process data from IGDB, store it in 
DynamoDB, and provide access via a FastAPI-based REST API. 
The project focuses on identifying cooperative games with splitscreen 
multiplayer modes and includes setting up a local development 
environment using LocalStack.

## Project Setup
Before starting 
1. Obtain IGDB API Keys - https://api-docs.igdb.com/#getting-started
2. Install and setup Localstack - https://docs.localstack.cloud/getting-started/installation/
3. Create a .env file with required values. An example is in the repo called example_env.txt. Rename to .env, and add relevant key values.
4. Configure Venv or add required packages to default installation with provided requirements.txt
5. Start Localstack 
   1. localstack start -d
   2. Logs can be viewed in Docker Desktop if needed
6. Create SQS Fifo Queue 
   1. aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name coop-queue.fifo --attributes FifoQueue=true,ContentBasedDeduplication=true
   2. Verify Queue is created - curl -H "Accept: application/json" \
    "http://localhost.localstack.cloud:4566/_aws/sqs/messages?QueueUrl=http://sqs.us-west-2.localhost.localstack.cloud:4566/000000000000/coop-queue.fifo"
7. Create DynamoDB Table
   1. awslocal dynamodb create-table --table-name coopgames --key-schema AttributeName=id,KeyType=HASH --attribute-definitions AttributeName=id,AttributeType=S --billing-mode PAY_PER_REQUEST --region us-west-2 --stream-specification StreamEnabled=true,StreamViewType=NEW_IMAGE
8. Create Lambda
   1. zip function.zip lambda_function.py
   2. Deploy to localstack 
      1. aws --endpoint-url=http://localhost:4566 lambda create-function --function-name ProcessDynamoDBStream --runtime python3.12 --handler lambda_function.lambda_handler --zip-file fileb://function.zip --role arn:aws:iam::000000000000:role/lambda-ex 
   3. Get Dynamodb stream 
      1. aws --endpoint-url=http://localhost:4566 dynamodbstreams list-streams --table-name coopgames
   4. Add event source mapping 
      1. aws --endpoint-url=http://localhost:4566 lambda create-event-source-mapping --function-name ProcessDynamoDBStream --event-source-arn ARN_FROM_ABOVE --starting-position LATEST
7. Run API FrontEnd
   8. uvicorn frontend_api:app --reload

## Testing
If all other components have been setup below can be run to test 
1. Run Data Scrape
   1. python3 ingest_game_data.py
   2. Data Should be scraped and sent to the SQS Queue
2. Transform Data and Write to DB. Also Test data Increment
   1. python3 transform_game_data.py
   2. Data will be transformed and sent to DynamoDB
   3. This will also invoke our lambda and send a test email via Mailtrap.
3. Run Data Backup
   1. python3 data_backup.py
4. Data Backfill
   1. This script is just an example as it requires additional record manipulation in order to utilize it
   2. but the script show the expected logic.
5. RestAPI
   1. If uvicorn is running then the api can be viewed at http://127.0.0.1:8000/
   2. The API documentation is at http://127.0.0.1:8000/docs
   3. AN API Key must be entered to be authorized. This should ,atch what is provided in the .env file.
   4. The Modheader chrome/firefox plugin can be used to add the required header in browser.

    