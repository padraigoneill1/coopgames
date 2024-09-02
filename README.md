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

