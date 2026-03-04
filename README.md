# Test: News Ingestion Pipeline
This is a test script for Aurora Analytics News Ingestion Pipeline.

## Description
This script request for the latest news - based on the news search key word - for the last 24 hours from the script's execution time. The script also restructure the article format and push them to AWS Kinesis Data Stream.

**Note:** If the script is manually executed, you can change the oldest and latest published date of the searched articles. See Environment Variables for details.

## Prerequisites
* Linux-based OS
* Python3 (3.12)
* Git
* Docker
* AWS Kinesis Data Stream (Access, Permission and Credentials)
* NewsAPI (API Key)

### Environment Variables (Env Vars)
To successfully run this script, kindly set the following env vars:
| Env Var  | Required? | Default | Description | 
| ------------- | :---: | -------------| -------------|
| NEWS_API_KEY      | Yes | | NewsAPI API Key  |
| NEWS_BASE_URL      | Yes | | NewsAPI URL  |
| NEWS_QUERY      | Yes | | Search key word for the news. Request query parameter for NewsAPI. Ex. Penguins |
| NEWS_FROM      | No | Date of execution minus 1 day | Oldest published date of the article to be retrieved |
| NEWS_TO      | No | Date of execution | Latest published date of the article to be retrieved |
| NEWS_STREAM_NAME      | Yes | | Stream name in AWS Kinesis Data Stream  |
| NEWS_UUID_NAME      | Yes | | UUID Name for UUID5 Generation |
| NEWS_STEAM_PARTITION_KEY      | Yes | | Partition key for AWS Kinesis Data Stream |

## How to Use

```
python3 main.py
```

## Dev Notes:
* Not tested with actual AWS Kinesis Data Stream since I do not have one. All AWS processes in this script are based on AWS Kinesis Data Stream Documentation available online.
* It was said the scenario that "the system should regularly pull content from the API". I didn't do any cron here. In my opinion, it is inappropriate to do cron in the script or in the Docker image. If we are using kubernetes, we can set one there - CronJob.
* I also didn't add .env file in the commit since it's inappropriate to add sensitive data in the commit. In my experience, using kubernetes, we add env var in the deployment YAML of the script we are creating/updating.
