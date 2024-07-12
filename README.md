
# Real-Time Analytics with Kafka

This project sets up a real-time analytics environment using Apache Kafka, Zookeeper, and custom Python applications for producing and consuming messages. The environment is containerized using Docker and managed with Docker Compose.

## Prerequisites
Before you begin, ensure you have the following installed on your system:

- Docker
- VS Code

You can download Docker [here](https://www.docker.com/products/docker-desktop/) and find installation instructions for VS Code [here](https://code.visualstudio.com/download).

## Repository Structure

- consumer: Contains the Docker setup and scripts for the Kafka consumer.
    - Dockerfile - Docker configuration for building the consumer service image.
    - kafka_consumer.py - Python script that consumes messages from Kafka, processes them, and writes results.
    - requirements.txt - Lists the Python packages required by kafka_consumer.py.
- insights: Directory where processed data files are saved after being handled by the consumer
- docker-compose.yml
    - Here’s what each service in the docker-compose.yml file does:
        - Zookeeper: Manages cluster state for Kafka.
        - Kafka: Handles message storage and processing.
        - my-python-producer: Produces messages and sends them to Kafka.
        - my-python-consumer: Consumes messages from Kafka, processes them, and potentially performs further actions.

## Setup
Follow these steps to get the environment up and running:

#### 1. Clone the Repository
Clone this repository to your local machine:
```bash
git clone https://github.com/BharathRajuPalla/real-time-analytics-with-kafka.git
cd real-time-analytics-with-kafka
```
#### 2. Build and Run with Docker Compose
From the directory containing the docker-compose.yml file, run the following command to build and start the containers:

```bash
docker-compose up --build
```
This command builds the images if they don't exist and starts the services defined in docker-compose.yml. The --build option ensures that any changes in the Dockerfiles or in the context are included.

#### 3. Verify the Services
Ensure that all services are up and running by checking the output of Docker Compose in your terminal. You should see logs indicating that the services have started successfully.


## Usage
After the containers are running, you can interact with them as follows:

- Accessing Kafka: Connect to Kafka on localhost:9092 or localhost:29092 for external clients.
- Producing Messages: Use the my-python-producer service to generate messages.
- Consuming Messages: The my-python-consumer service will automatically consume messages from Kafka and process them as configured.

## Stopping the Services
To stop and remove the containers, networks, and volumes created by Docker Compose, run:
```bash
docker-compose down
```

## Design Choices and Data Flow
####    1. Zookeeper:

- Role: Manages cluster state and configuration, essential for Kafka.
- Configuration: Client port set to 2181, the default for client connections.
    - Tick time set to 2000 ms, determining the heartbeat interval for the server.
    - Health Check: Uses netcat (nc) to check if the Zookeeper service is up by sending a stat command.
- Network: All components are connected via a bridge network (kafka-network), which provides isolated networking among the services.

####    2. Kafka:

- Dependencies: Depends on Zookeeper being healthy (service_healthy).
- Configuration: 
    - Broker ID and Zookeeper connection specifics ensure proper linkage to Zookeeper.
    - Advertised listeners are configured for internal Kafka communications and external connections, facilitating both internal service communication and external access for debugging or remote connections.
    - Topics such as user-login and processed-data are pre-configured, which helps in quick setup and testing.
- Health Check: Checks if Kafka is listening on its designated port, ensuring the service is functional before allowing dependent services to start.

####    3. Python Producer (my-python-producer):
    
- Role: Generates or fetches data and publishes it to the user-login Kafka topic.
- Configuration:
    - Relies on Kafka being healthy.
    - Automatically restarts up to 10 times if it fails, enhancing reliability.
- Data Flow: Fetches or simulates data related to user login activities, then sends this data to Kafka for real-time processing or storage.

####    4. Python Consumer (my-python-consumer):

- Role: Subscribes to the user-login topic, processes the data, and potentially enriches it before publishing to processed-data
- Configuration:
    - Builds from a local Dockerfile, allowing customization of the consumer application.
    - Volumes are used to persist processed data or insights, facilitating data analysis and backup.
- Data Flow: Consumes messages from user-login, processes them according to the business logic, and then outputs the results to processed-data.

## Scalability, Efficiency, and Fault Tolerance

### Scalability:
- Kafka supports horizontal scaling, which can be achieved by adding more brokers to the Kafka service. This setup allows for partitioning of topics across multiple brokers, enhancing throughput and storage capacity.
- Both the Python producer and consumer can be scaled by increasing the number of service instances as needed, facilitated by Docker's easy replication features.

### Efficiency:
- The use of a bridge network minimizes network overhead while ensuring isolated communication among services.
- Health checks prevent cascading failures by ensuring that dependent services only start when their dependencies are fully operational.

### Fault Tolerance:
- Zookeeper and Kafka configurations ensure that messages are not lost in case of a service failure, maintaining the integrity of the data flow.
- The consumer uses a volume to store processed data, which means that in case of a consumer failure, not all processed data is lost, and recovery is manageable.

## Deploying the Application in Production

### Infrastructure Setup:
- Cloud or On-Premises: Decide whether to deploy on cloud services like AWS, Azure, or GCP, or on-premises. Cloud services offer managed Kafka services (e.g., Amazon MSK, Confluent Cloud) that simplify deployment and maintenance.
- Container Orchestration: Use Kubernetes or Docker Swarm for container orchestration. Kubernetes, in particular, offers extensive support for management, autoscaling, and maintenance of containerized applications.

### Monitoring and Logging:
- Monitoring: Implement monitoring solutions such as Prometheus and Grafana to monitor the performance and health of your Kafka clusters and applications.
- Logging: Set up centralized logging with tools like ELK Stack (Elasticsearch, Logstash, Kibana) or Splunk to collect and analyze logs from all components of your application.

### Security:
- Network Security: Configure firewalls, VPNs, and other network security measures to protect your data and infrastructure.
- Access Control: Implement proper authentication and authorization mechanisms, possibly integrating with existing enterprise solutions like LDAP or Active Directory.

## Components to Make it Production Ready

### High Availability and Disaster Recovery:
- Replication: Configure Kafka for high availability by setting up multi-node Kafka clusters with data replication.
- Backup and Recovery: Implement regular backup procedures and ensure you have a tested recovery process in place.

### Enhanced Security:
- Encryption: Use TLS/SSL to encrypt data in transit and at rest.
- Auditing: Enable auditing features to track and review actions taken on critical data and configurations.

### Quality of Service:
- Rate Limiting: Implement rate limiting to prevent abuse and to manage load under peak traffic conditions.
- Caching: Use caching mechanisms to improve response times and reduce load on backend services.

## Scaling the Application with Growing Dataset

### Kafka Scaling:
- Partitions: Increase the number of partitions in Kafka topics to distribute the load more effectively across the cluster.
- Brokers: Add more brokers to your Kafka cluster to increase throughput and fault tolerance.

### Database Scaling:
- Sharding: Implement sharding for your databases to distribute the data across multiple nodes, reducing the load on individual servers.
- Read Replicas: Use read replicas to distribute read queries and reduce the load on the primary database server.

## Microservices Architecture:
- Microservices: Break down the application into smaller, independently scalable microservices that can be scaled out or up as needed based on demand.
- Load Balancing: Use load balancers to distribute traffic evenly across servers, ensuring no single server bears too much load.

## Auto-scaling:
- Auto-scaling: Utilize auto-scaling capabilities of your orchestration tool (e.g., Kubernetes) to automatically scale up or down based on workload.
