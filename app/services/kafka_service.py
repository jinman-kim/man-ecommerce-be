from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

class KafkaService:
    def __init__(self, bootstrap_servers: str = "localhost:29092"):
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = self._create_admin_client()

    def _create_admin_client(self):
        """Kafka AdminClient를 생성하여 반환합니다."""
        admin_client = KafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        print(f"Connected to Kafka at {self.bootstrap_servers}")
        return admin_client

    def create_topic(self, topic_name: str, num_partitions: int = 1, replication_factor: int = 1):
        """주어진 설정으로 새 Kafka 토픽을 생성합니다."""
        topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
        try:
            self.admin_client.create_topics(new_topics=[topic], validate_only=False)
            print(f"Topic '{topic_name}' created successfully.")
        except TopicAlreadyExistsError:
            print(f"Topic '{topic_name}' already exists.")

    def list_topics(self):
        """사용 가능한 모든 Kafka 토픽 목록을 반환합니다."""
        topics = self.admin_client.list_topics()
        print("Available topics:", topics)
        return topics

# KafkaService 클래스 사용 예
if __name__ == "__main__":
    kafka_service = KafkaService()
    kafka_service.create_topic("test-topic")
    kafka_service.list_topics()
