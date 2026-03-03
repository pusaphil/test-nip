class KinesisStream:
	"""Encapsulates a Kinesis stream."""

	def __init__(self, kinesis_client):
		"""
		:param kinesis_client: A Boto3 Kinesis client.
		"""
		self.kinesis_client = kinesis_client
		self.name = None
		self.details = None
		self.stream_exists_waiter = kinesis_client.get_waiter("stream_exists")


	def create(self, name, wait_until_exists=True):
		"""
		Creates a stream.

		:param name: The name of the stream.
		:param wait_until_exists: When True, waits until the service reports that
			the stream exists, then queries for its metadata.
		"""
		try:
			self.kinesis_client.create_stream(StreamName=name, ShardCount=1)
			self.name = name
			logger.info("Created stream %s.", name)
			if wait_until_exists:
				logger.info("Waiting until exists.")
				self.stream_exists_waiter.wait(StreamName=name)
				self.describe(name)
		except ClientError:
			logger.exception("Couldn't create stream %s.", name)
			raise

	def delete(self):
		"""
		Deletes a stream.
		"""
		try:
			self.kinesis_client.delete_stream(StreamName=self.name)
			self._clear()
			logger.info("Deleted stream %s.", self.name)
		except ClientError:
			logger.exception("Couldn't delete stream %s.", self.name)
			raise

	def put_record(self, data, partition_key):
		"""
		Puts data into the stream. The data is formatted as JSON before it is passed
		to the stream.

		:param data: The data to put in the stream.
		:param partition_key: The partition key to use for the data.
		:return: Metadata about the record, including its shard ID and sequence number.
		"""
		try:
			response = self.kinesis_client.put_record(
					StreamName=self.name, Data=json.dumps(data), PartitionKey=partition_key
			)
			logger.info("Put record in stream %s.", self.name)
		except ClientError:
			logger.exception("Couldn't put record in stream %s.", self.name)
			raise
		else:
			return response
