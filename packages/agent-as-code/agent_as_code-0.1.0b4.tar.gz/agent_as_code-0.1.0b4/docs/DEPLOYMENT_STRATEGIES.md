# Agent as Code Deployment Strategies
====================================

This document outlines comprehensive deployment strategies for Agent as Code agents across different platforms, applications, and use cases.

## Table of Contents

1. [Local Development & Testing](#local-development--testing)
2. [Standalone Micro-Services](#standalone-micro-services)
3. [Container Orchestration](#container-orchestration)
4. [Cloud Platform Integration](#cloud-platform-integration)
5. [Application Integration](#application-integration)
6. [Edge Computing](#edge-computing)
7. [Serverless Deployment](#serverless-deployment)
8. [Hybrid Architectures](#hybrid-architectures)

## Local Development & Testing

### Docker Local Deployment
```bash
# Build and run agent locally
cd /path/to/agent-package
docker build -t my-agent:latest .
docker run -d --name my-agent -p 8080:8080 my-agent:latest

# Using generated deployment files
cd deploy
./run.sh
```

### Docker Compose for Multi-Agent Testing
```yaml
# docker-compose.yml
version: '3.8'
services:
  weather-monitor:
    build: ./weather-monitor
    environment:
      - WEATHER_API_KEY=${WEATHER_API_KEY}
    ports:
      - "8080:8080"
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
  
  sentiment-analyzer:
    build: ./sentiment-analyzer
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8081:8080"
    restart: unless-stopped
  
  data-processor:
    build: ./data-processor
    ports:
      - "8082:8080"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### Local Runtime Testing
```bash
# Test agent functionality
agent test weather-monitor:latest

# Monitor agent logs
docker logs -f weather-monitor

# Check agent health
curl http://localhost:8080/health

# Test agent capabilities
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"operation": "check_weather"}'
```

## Standalone Micro-Services

### Direct Container Deployment
```bash
# Deploy to any container runtime
docker run -d \
  --name weather-monitor \
  -p 8080:8080 \
  -e WEATHER_API_KEY=${WEATHER_API_KEY} \
  -v /var/log/weather:/app/logs \
  weather-monitor:latest
```

### Systemd Service Integration
```ini
# /etc/systemd/system/weather-monitor.service
[Unit]
Description=Weather Monitor Agent
After=docker.service
Requires=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/docker run --rm --name weather-monitor \
  -p 8080:8080 \
  -e WEATHER_API_KEY=${WEATHER_API_KEY} \
  weather-monitor:latest
ExecStop=/usr/bin/docker stop weather-monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Cron Job Integration
```bash
# /etc/cron.d/weather-monitor
# Run weather check every 5 minutes
*/5 * * * * root docker exec weather-monitor python -c "from agent import check_weather; check_weather()"
```

## Container Orchestration

### Kubernetes Deployment
```yaml
# weather-monitor-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weather-monitor
spec:
  replicas: 1
  selector:
    matchLabels:
      app: weather-monitor
  template:
    metadata:
      labels:
        app: weather-monitor
    spec:
      containers:
      - name: weather-monitor
        image: weather-monitor:latest
        ports:
        - containerPort: 8080
        env:
        - name: WEATHER_API_KEY
          valueFrom:
            secretKeyRef:
              name: weather-secrets
              key: api-key
        - name: CITY_NAME
          value: "New York"
        volumeMounts:
        - name: logs
          mountPath: /app/logs
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: logs
        persistentVolumeClaim:
          claimName: weather-logs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: weather-monitor-service
spec:
  selector:
    app: weather-monitor
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: ClusterIP
```

### Docker Swarm Deployment
```yaml
# docker-stack.yml
version: '3.8'
services:
  weather-monitor:
    image: weather-monitor:latest
    deploy:
      replicas: 1
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - WEATHER_API_KEY=${WEATHER_API_KEY}
    ports:
      - "8080:8080"
    volumes:
      - weather-logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  weather-logs:
```

## Cloud Platform Integration

### AWS ECS/Fargate
```yaml
# task-definition.json
{
  "family": "weather-monitor",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "weather-monitor",
      "image": "weather-monitor:latest",
      "portMappings": [
        {
          "containerPort": 8080,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "CITY_NAME",
          "value": "New York"
        }
      ],
      "secrets": [
        {
          "name": "WEATHER_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:weather-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/weather-monitor",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### Google Cloud Run
```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: weather-monitor
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
      - image: gcr.io/PROJECT_ID/weather-monitor:latest
        ports:
        - containerPort: 8080
        env:
        - name: CITY_NAME
          value: "New York"
        - name: WEATHER_API_KEY
          valueFrom:
            secretKeyRef:
              name: weather-secrets
              key: api-key
        resources:
          limits:
            cpu: "1000m"
            memory: "512Mi"
```

### Azure Container Instances
```yaml
# azure-container.yaml
apiVersion: 2019-12-01
location: eastus
properties:
  containers:
  - name: weather-monitor
    properties:
      image: weather-monitor:latest
      ports:
      - port: 8080
      environmentVariables:
      - name: CITY_NAME
        value: "New York"
      - name: WEATHER_API_KEY
        secureValue: "your-api-key"
      resources:
        requests:
          memoryInGB: 0.5
          cpu: 0.5
        limits:
          memoryInGB: 1.0
          cpu: 1.0
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 8080
```

## Application Integration

### REST API Integration
```python
# Python application integration
import requests

class WeatherService:
    def __init__(self, agent_url="http://localhost:8080"):
        self.agent_url = agent_url
    
    def get_weather(self):
        """Get current weather from agent"""
        response = requests.get(f"{self.agent_url}/weather")
        return response.json()
    
    def get_health(self):
        """Check agent health"""
        response = requests.get(f"{self.agent_url}/health")
        return response.json()
    
    def trigger_check(self):
        """Manually trigger weather check"""
        response = requests.post(f"{self.agent_url}/execute", 
                               json={"operation": "check_weather"})
        return response.json()

# Usage
weather_service = WeatherService()
current_weather = weather_service.get_weather()
print(f"Current temperature: {current_weather['temperature']}°C")
```

### gRPC Integration
```python
# Python gRPC integration
import grpc
from agent_pb2 import ExecuteRequest
from agent_pb2_grpc import AgentServiceStub

class WeatherAgentClient:
    def __init__(self, host="localhost", port=50051):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = AgentServiceStub(self.channel)
    
    def execute_weather_check(self):
        """Execute weather check via gRPC"""
        request = ExecuteRequest(
            operation="check_weather",
            parameters={}
        )
        response = self.stub.Execute(request)
        return response
    
    def get_health(self):
        """Get health status via gRPC"""
        request = HealthRequest()
        response = self.stub.HealthCheck(request)
        return response

# Usage
client = WeatherAgentClient()
result = client.execute_weather_check()
print(f"Weather check result: {result}")
```

### Web Application Integration
```javascript
// JavaScript/Node.js integration
class WeatherAgentClient {
    constructor(baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
    }
    
    async getWeather() {
        const response = await fetch(`${this.baseUrl}/weather`);
        return await response.json();
    }
    
    async getHealth() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }
    
    async triggerCheck() {
        const response = await fetch(`${this.baseUrl}/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                operation: 'check_weather'
            })
        });
        return await response.json();
    }
}

// Usage
const weatherClient = new WeatherAgentClient();
weatherClient.getWeather().then(weather => {
    console.log(`Current temperature: ${weather.temperature}°C`);
});
```

### Database Integration
```python
# Database integration for logging
import sqlite3
from datetime import datetime

class WeatherDatabase:
    def __init__(self, db_path="/app/weather.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                city TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity INTEGER NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def log_weather(self, weather_data):
        """Log weather data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO weather_logs 
            (timestamp, city, temperature, humidity, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            weather_data['timestamp'],
            weather_data['city'],
            weather_data['temperature'],
            weather_data['humidity'],
            weather_data['description']
        ))
        conn.commit()
        conn.close()
    
    def get_recent_logs(self, limit=10):
        """Get recent weather logs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM weather_logs 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        logs = cursor.fetchall()
        conn.close()
        return logs
```

## Edge Computing

### IoT Device Deployment
```yaml
# Edge deployment configuration
version: '3.8'
services:
  weather-monitor:
    image: weather-monitor:latest
    environment:
      - WEATHER_API_KEY=${WEATHER_API_KEY}
      - CITY_NAME=${CITY_NAME}
      - CHECK_INTERVAL=15  # Less frequent for edge devices
    volumes:
      - /var/log/weather:/app/logs
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
```

### Raspberry Pi Deployment
```bash
# Raspberry Pi deployment script
#!/bin/bash

# Install Docker on Raspberry Pi
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Create weather monitoring service
sudo mkdir -p /opt/weather-monitor
cd /opt/weather-monitor

# Download agent image
docker pull weather-monitor:latest

# Create systemd service
sudo tee /etc/systemd/system/weather-monitor.service << EOF
[Unit]
Description=Weather Monitor Agent
After=docker.service
Requires=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/docker run --rm --name weather-monitor \\
  -v /opt/weather-monitor/logs:/app/logs \\
  -e WEATHER_API_KEY=\${WEATHER_API_KEY} \\
  -e CITY_NAME=\${CITY_NAME} \\
  weather-monitor:latest
ExecStop=/usr/bin/docker stop weather-monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable weather-monitor
sudo systemctl start weather-monitor
```

## Serverless Deployment

### AWS Lambda Integration
```python
# Lambda function wrapper for agent
import json
import os
from agent import WeatherMonitorAgent

def lambda_handler(event, context):
    """AWS Lambda handler for weather monitoring"""
    
    # Initialize agent
    agent = WeatherMonitorAgent()
    
    # Check weather
    weather_data = agent.get_weather_data()
    
    if weather_data:
        # Log to CloudWatch
        agent.log_weather_data(weather_data)
        
        return {
            'statusCode': 200,
            'body': json.dumps(weather_data)
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to get weather data'})
        }
```

### Cloud Functions Integration
```python
# Google Cloud Function wrapper
import functions_framework
import json
from agent import WeatherMonitorAgent

@functions_framework.http
def weather_monitor(request):
    """Google Cloud Function for weather monitoring"""
    
    agent = WeatherMonitorAgent()
    weather_data = agent.get_weather_data()
    
    if weather_data:
        agent.log_weather_data(weather_data)
        return json.dumps(weather_data), 200
    else:
        return json.dumps({'error': 'Failed to get weather data'}), 500
```

## Hybrid Architectures

### Multi-Cloud Deployment
```yaml
# Multi-cloud deployment configuration
version: '3.8'
services:
  weather-monitor-aws:
    image: weather-monitor:latest
    deploy:
      placement:
        constraints:
          - node.labels.cloud == aws
    environment:
      - CLOUD_PROVIDER=aws
      - WEATHER_API_KEY=${AWS_WEATHER_API_KEY}
  
  weather-monitor-gcp:
    image: weather-monitor:latest
    deploy:
      placement:
        constraints:
          - node.labels.cloud == gcp
    environment:
      - CLOUD_PROVIDER=gcp
      - WEATHER_API_KEY=${GCP_WEATHER_API_KEY}
  
  weather-monitor-azure:
    image: weather-monitor:latest
    deploy:
      placement:
        constraints:
          - node.labels.cloud == azure
    environment:
      - CLOUD_PROVIDER=azure
      - WEATHER_API_KEY=${AZURE_WEATHER_API_KEY}
```

### Edge-to-Cloud Integration
```python
# Edge-to-cloud agent configuration
class EdgeWeatherAgent(WeatherMonitorAgent):
    def __init__(self):
        super().__init__()
        self.cloud_sync = os.getenv('CLOUD_SYNC', 'true').lower() == 'true'
        self.cloud_endpoint = os.getenv('CLOUD_ENDPOINT')
    
    def sync_to_cloud(self, weather_data):
        """Sync data to cloud when connectivity available"""
        if self.cloud_sync and self.cloud_endpoint:
            try:
                requests.post(f"{self.cloud_endpoint}/weather", 
                            json=weather_data, timeout=5)
            except requests.exceptions.RequestException:
                # Store locally if cloud sync fails
                self.log_weather_data(weather_data)
    
    def check_weather(self):
        """Enhanced weather check with cloud sync"""
        weather_data = self.get_weather_data()
        if weather_data:
            self.sync_to_cloud(weather_data)
```

## Monitoring and Observability

### Prometheus Metrics
```python
# Prometheus metrics integration
from prometheus_client import Counter, Gauge, Histogram, start_http_server

class WeatherMonitorWithMetrics(WeatherMonitorAgent):
    def __init__(self):
        super().__init__()
        
        # Prometheus metrics
        self.weather_checks = Counter('weather_checks_total', 'Total weather checks')
        self.weather_temperature = Gauge('weather_temperature_celsius', 'Current temperature')
        self.weather_humidity = Gauge('weather_humidity_percent', 'Current humidity')
        self.weather_check_duration = Histogram('weather_check_duration_seconds', 'Weather check duration')
        
        # Start metrics server
        start_http_server(9090)
    
    def check_weather(self):
        """Weather check with metrics"""
        with self.weather_check_duration.time():
            weather_data = self.get_weather_data()
            
            if weather_data:
                self.weather_checks.inc()
                self.weather_temperature.set(weather_data['temperature'])
                self.weather_humidity.set(weather_data['humidity'])
                self.log_weather_data(weather_data)
```

### Distributed Tracing
```python
# OpenTelemetry tracing integration
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

class WeatherMonitorWithTracing(WeatherMonitorAgent):
    def __init__(self):
        super().__init__()
        
        # Setup tracing
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        
        # Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        self.tracer = tracer
    
    def check_weather(self):
        """Weather check with tracing"""
        with self.tracer.start_as_current_span("weather_check") as span:
            span.set_attribute("city", self.city_name)
            
            weather_data = self.get_weather_data()
            if weather_data:
                span.set_attribute("temperature", weather_data['temperature'])
                span.set_attribute("humidity", weather_data['humidity'])
                self.log_weather_data(weather_data)
```

## Security Considerations

### Secrets Management
```yaml
# Kubernetes secrets
apiVersion: v1
kind: Secret
metadata:
  name: weather-secrets
type: Opaque
data:
  api-key: <base64-encoded-api-key>
  database-url: <base64-encoded-db-url>
```

### Network Security
```yaml
# Network policies
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: weather-monitor-network-policy
spec:
  podSelector:
    matchLabels:
      app: weather-monitor
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: external-apis
    ports:
    - protocol: TCP
      port: 443
```

This comprehensive deployment strategy ensures that Agent as Code agents can be deployed across any platform, integrated with any application, and scaled according to requirements while maintaining security, observability, and reliability. 