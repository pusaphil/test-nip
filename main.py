#!/usr/bin/env python3

import sys
import os
import requests
import uuid
import boto3
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

from logger import Logger
from kinesis import KinesisStream
from get_news_dummy import get_news_dummy

news_uuid_name = os.getenv("NEWS_UUID_NAME") or 'Sample'

log = Logger(__name__, 10)

# Initialized Boto3 and AWS Kinesis
client = boto3.client('kinesis')
kinesis = KinesisStream(client)

def get_news(news_base_url: str, headers: str, params: str, timeout: int = 30):
  try:
    resp = requests.get(news_base_url, headers=headers, params=params, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "ok":
      raise RuntimeError(f"NewsAPI error: {data}")
    return data
  except requests.exceptions.RequestException as e:
    raise RuntimeError(f"NewsAPI request error: {e}")

def get_news_count(news_api_key: str, news_base_url: str, news_query: str, news_from: str, news_to: str, page: int):
  headers = {
    "X-Api-Key": news_api_key
  }

  params: Dict[str, Any] = {
    "q": news_query,
    "from": news_from,
    "to": news_to,
    "page": page
  }

  return get_news(news_base_url, headers, params)

def loop_through_pages(news_api_key: str, news_base_url: str, news_query: str, news_from: str, news_to: str, news_stream_partition_key: str):
  page = 1
  total_article_count = 0

  while True:
    response = []
    data = get_news_count(news_api_key, news_base_url, news_query, news_from, news_to, page)
    logger.debug(f'Total number of news: {data.get("totalResults")} | page: {page}')
    article_page_count = len(data.get("articles"))
    
    if article_page_count == 0:
      break

    # Loop through articles in the page and structure them
    for article in data.get("articles"):
      response.append(structure_data(article))

    # Push data to AWS Kinesis
    kinesis.push_records(response, news_stream_partition_key)

    total_article_count += article_page_count
    page += 1

  return total_article_count

def structure_data(article: dict):
  return {
    "article_id": uuid.uuid5(uuid.NAMESPACE_DNS, news_uuid_name),
    "source_name": article.get('source', {}).get('name'),
    "title": article.get('title'),
    "content": article.get('content'),
    "url": article.get('url'),
    "author": article.get('author'),
    "published_at": article.get('publishedAt'),
    "ingested_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") # datetime now
  }

def main():
  log.info("Starting ingest pipeline...")

  # LOADING ENV VARIABLES  
  load_dotenv()
  news_api_key = os.getenv("NEWS_API_KEY")
  news_base_url = os.getenv("NEWS_BASE_URL")
  news_query = os.getenv("NEWS_QUERY")
  news_from = os.getenv("NEWS_FROM")
  news_to = os.getenv("NEWS_TO")
  news_stream_name = os.getenv("NEWS_STREAM_NAME")
  news_stream_partition_key = os.getenv("NEWS_STEAM_PARTITION_KEY")

  # VALIDATED ENV VARIABLES
  if not news_api_key:
    log.error("Error: Please set the NEWSAPI_KEY environment variable with your NewsAPI key.")
    sys.exit(1)
  if not news_base_url:
    log.error("ERROR: Please set the NEWS_BASE_URL environment variable with your NewsAPI base URL.")
    sys.exit(1)
  if not news_query:
    log.error("ERROR: Please set the NEWS_QUERY environment variable with your NewsAPI query.")
    sys.exit(1)
  if not news_stream_name:
    log.error("ERROR: Please set the NEWS_STREAM_NAME environment variable with your AWS Kinesis Data Stream Name.")
    sys.exit(1)
  if not news_stream_partition_key:
    log.error("ERROR: Please set the NEWS_STEAM_PARTITION_KEY environment variable with your AWS Kinesis Data Stream Partition Key.")
    sys.exit(1)

  # SET DEFAULT VALUES FOR NEWS_FROM AND NEWS_TO
  if not news_from:
    # Set default news_from to 1 days ago
    news_from = datetime.now(timezone.utc) - timedelta(days=2)
    news_from = news_from.strftime("%Y-%m-%dT%H:%M:%S")
    news_from = "2026-03-02T12:00:00" # HARD CODED FOR TESTING
  if not news_to:
    # Set default news_to to now
    news_to = datetime.now(timezone.utc)
    news_to = news_to.strftime("%Y-%m-%dT%H:%M:%S")

  # Create AWS Kinesis Stream
  kinesis.create(news_stream_name)

  loop_through_pages(news_api_key, news_base_url, news_query, news_from, news_to, news_stream_partition_key)

if __name__ == "__main__":
  main()