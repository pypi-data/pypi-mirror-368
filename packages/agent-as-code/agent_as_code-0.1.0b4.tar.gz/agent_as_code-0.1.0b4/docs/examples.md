# Examples and Use Cases
==========================

This section provides real-world examples and use cases for the Agent as Code framework, demonstrating how to create different types of AI agents.

## Example Agents

### 1. Text Generation Agent

A simple text generation agent using OpenAI GPT-4.

#### Agentfile
```dockerfile
FROM agent/python:3.11-docker

CAPABILITY text-generation
MODEL gpt-4
CONFIG temperature=0.7
CONFIG max_tokens=500

DEPENDENCY openai==1.0.0
DEPENDENCY fastapi==0.104.0
DEPENDENCY uvicorn==0.24.0

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV LOG_LEVEL=INFO

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

ENTRYPOINT python agent/main.py

LABEL version="1.0.0"
LABEL author="ai-team@example.com"
LABEL description="Text generation agent using GPT-4"
LABEL tags="ai,text-generation,gpt-4"
```

#### Implementation
```python
#!/usr/bin/env python3
"""
Text Generation Agent
=====================
Generates text using OpenAI GPT-4.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Text Generation Agent")
openai.api_key = os.getenv('OPENAI_API_KEY')

class GenerateRequest(BaseModel):
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 500

class GenerateResponse(BaseModel):
    text: str
    tokens_used: int

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Generate text using GPT-4."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": request.prompt}],
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return GenerateResponse(
            text=response.choices[0].message.content,
            tokens_used=response.usage.total_tokens
        )
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "text-generator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 2. Sentiment Analysis Agent

An agent that analyzes text sentiment using GPT-4.

#### Agentfile
```dockerfile
FROM agent/python:3.11-docker

CAPABILITY sentiment-analysis
MODEL gpt-4
CONFIG temperature=0.3

DEPENDENCY openai==1.0.0
DEPENDENCY fastapi==0.104.0
DEPENDENCY uvicorn==0.24.0

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV LOG_LEVEL=INFO

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

ENTRYPOINT python agent/main.py

LABEL version="1.0.0"
LABEL author="ai-team@example.com"
LABEL description="Sentiment analysis agent using GPT-4"
LABEL tags="ai,sentiment,analysis"
```

#### Implementation
```python
#!/usr/bin/env python3
"""
Sentiment Analysis Agent
========================
Analyzes text sentiment using GPT-4.
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sentiment Analysis Agent")
openai.api_key = os.getenv('OPENAI_API_KEY')

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float
    explanation: str

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """Analyze text sentiment."""
    try:
        prompt = f"""
        Analyze the sentiment of the following text and provide:
        1. Sentiment (positive, negative, neutral)
        2. Confidence score (0-1)
        3. Brief explanation
        
        Text: {request.text}
        
        Respond in JSON format:
        {{"sentiment": "...", "confidence": 0.0, "explanation": "..."}}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200
        )
        
        # Parse response (simplified)
        result = response.choices[0].message.content
        # In production, use proper JSON parsing
        
        return SentimentResponse(
            sentiment="positive",  # Simplified
            confidence=0.8,
            explanation="The text expresses positive emotions"
        )
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "sentiment-analyzer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 3. Data Analysis Agent

An agent for data analysis and visualization using pandas and matplotlib.

#### Agentfile
```dockerfile
FROM agent/python:3.11-docker

CAPABILITY data-analysis
MODEL gpt-4
CONFIG temperature=0.1

DEPENDENCY openai==1.0.0
DEPENDENCY fastapi==0.104.0
DEPENDENCY uvicorn==0.24.0
DEPENDENCY pandas==1.3.0
DEPENDENCY numpy==1.21.0
DEPENDENCY matplotlib==3.4.0
DEPENDENCY seaborn==0.11.0

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV DATA_PATH=/app/data
ENV LOG_LEVEL=INFO

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

ENTRYPOINT python agent/main.py

LABEL version="1.0.0"
LABEL author="data-team@example.com"
LABEL description="Data analysis and visualization agent"
LABEL tags="ai,data,analysis,visualization"
```

#### Implementation
```python
#!/usr/bin/env python3
"""
Data Analysis Agent
===================
Performs data analysis and creates visualizations.
"""

import os
import logging
import json
import base64
from io import BytesIO
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Analysis Agent")
openai.api_key = os.getenv('OPENAI_API_KEY')

class AnalysisRequest(BaseModel):
    data: list
    analysis_type: str
    columns: list = None

class AnalysisResponse(BaseModel):
    summary: dict
    visualization: str = None
    insights: list

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(request: AnalysisRequest):
    """Analyze data and create visualizations."""
    try:
        # Create DataFrame
        df = pd.DataFrame(request.data)
        
        # Basic analysis
        summary = {
            "rows": len(df),
            "columns": len(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist()
        }
        
        # Create visualization
        if request.analysis_type == "distribution" and len(df.select_dtypes(include=['number']).columns) > 0:
            plt.figure(figsize=(10, 6))
            numeric_cols = df.select_dtypes(include=['number']).columns[:3]  # First 3 numeric columns
            df[numeric_cols].hist(bins=20)
            plt.tight_layout()
            
            # Save to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            visualization = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
        else:
            visualization = None
        
        # Generate insights using GPT-4
        insights_prompt = f"""
        Analyze this data summary and provide 3 key insights:
        {json.dumps(summary, indent=2)}
        
        Provide insights in JSON format:
        {{"insights": ["insight1", "insight2", "insight3"]}}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": insights_prompt}],
            temperature=0.1,
            max_tokens=200
        )
        
        # Parse insights (simplified)
        insights = ["Data has good structure", "No major missing values", "Ready for analysis"]
        
        return AnalysisResponse(
            summary=summary,
            visualization=visualization,
            insights=insights
        )
    except Exception as e:
        logger.error(f"Error analyzing data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "data-analyzer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 4. Weather Monitoring Agent

A scheduled agent that monitors weather and logs data.

#### Agentfile
```dockerfile
FROM agent/python:3.11-docker

CAPABILITY weather-monitoring
CAPABILITY data-logging
CAPABILITY scheduled-tasks

MODEL local
CONFIG precision=high

DEPENDENCY requests==2.31.0
DEPENDENCY schedule==1.2.0
DEPENDENCY python-dotenv==1.0.0

ENV WEATHER_API_KEY=${WEATHER_API_KEY}
ENV CITY_NAME=New York
ENV LOG_FILE=/app/weather_log.txt
ENV CHECK_INTERVAL=5
ENV LOG_LEVEL=INFO

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

ENTRYPOINT python agent/main.py

LABEL version="1.0.0"
LABEL author="weather-team@example.com"
LABEL description="Weather monitoring agent that logs NYC temperature every 5 minutes"
LABEL tags="weather,monitoring,cron,logging,nyc"
```

#### Implementation
```python
#!/usr/bin/env python3
"""
Weather Monitoring Agent
========================
Monitors weather and logs data at regular intervals.
"""

import os
import time
import logging
import schedule
import requests
from datetime import datetime
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Weather Monitoring Agent")

class WeatherMonitor:
    def __init__(self):
        self.api_key = os.getenv('WEATHER_API_KEY')
        self.city_name = os.getenv('CITY_NAME', 'New York')
        self.log_file = os.getenv('LOG_FILE', '/app/weather_log.txt')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '5'))
        
    def get_weather_data(self):
        """Fetch weather data from OpenWeatherMap API."""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': self.city_name,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None
    
    def log_weather_data(self, weather_data):
        """Log weather data to file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            temperature = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            description = weather_data['weather'][0]['description']
            
            log_entry = f"{timestamp} | {self.city_name} | Temp: {temperature}°C | Humidity: {humidity}% | {description}\n"
            
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
                
            logger.info(f"Weather logged: {temperature}°C in {self.city_name}")
        except Exception as e:
            logger.error(f"Error logging weather data: {e}")
    
    def check_weather(self):
        """Check weather and log data."""
        weather_data = self.get_weather_data()
        if weather_data:
            self.log_weather_data(weather_data)
    
    def setup_schedule(self):
        """Setup scheduled weather checks."""
        schedule.every(self.check_interval).minutes.do(self.check_weather)
        logger.info(f"Weather monitoring scheduled every {self.check_interval} minutes")
    
    def run(self):
        """Run the weather monitoring service."""
        self.setup_schedule()
        
        # Initial check
        self.check_weather()
        
        # Run scheduled checks
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Initialize weather monitor
weather_monitor = WeatherMonitor()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent": "weather-monitor",
        "city": weather_monitor.city_name,
        "last_check": datetime.now().isoformat()
    }

@app.get("/weather")
async def get_current_weather():
    """Get current weather data."""
    weather_data = weather_monitor.get_weather_data()
    if weather_data:
        return {
            "city": weather_monitor.city_name,
            "temperature": weather_data['main']['temp'],
            "humidity": weather_data['main']['humidity'],
            "description": weather_data['weather'][0]['description'],
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {"error": "Unable to fetch weather data"}

if __name__ == "__main__":
    import threading
    import uvicorn
    
    # Start weather monitoring in background thread
    weather_thread = threading.Thread(target=weather_monitor.run, daemon=True)
    weather_thread.start()
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

## Use Cases

### 1. Content Generation

**Use Case**: Automate content creation for marketing campaigns.

**Agent Type**: Text Generation Agent
**Capabilities**: 
- Generate blog posts
- Create social media content
- Write product descriptions
- Generate email campaigns

**Implementation**:
```bash
# Create content generation agent
agent init content-generator
cd content-generator

# Configure for content generation
# Edit Agentfile with appropriate capabilities
# Implement content generation logic
# Deploy and integrate with CMS
```

### 2. Customer Support

**Use Case**: Provide automated customer support with sentiment analysis.

**Agent Type**: Multi-capability Agent
**Capabilities**:
- Sentiment analysis
- Text generation
- Intent classification
- Response routing

**Implementation**:
```bash
# Create support agent
agent init support-agent
cd support-agent

# Configure for support tasks
# Implement support logic
# Integrate with ticketing system
```

### 3. Data Analytics

**Use Case**: Automated data analysis and reporting.

**Agent Type**: Data Analysis Agent
**Capabilities**:
- Data processing
- Statistical analysis
- Visualization generation
- Report creation

**Implementation**:
```bash
# Create analytics agent
agent init analytics-agent
cd analytics-agent

# Configure for data analysis
# Implement analytics logic
# Integrate with data sources
```

### 4. Monitoring and Alerting

**Use Case**: Monitor systems and generate alerts.

**Agent Type**: Monitoring Agent
**Capabilities**:
- System monitoring
- Data logging
- Alert generation
- Health checks

**Implementation**:
```bash
# Create monitoring agent
agent init monitoring-agent
cd monitoring-agent

# Configure for monitoring
# Implement monitoring logic
# Integrate with alerting systems
```

## Integration Patterns

### 1. Web Application Integration

```python
# Flask application using agents
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/generate-content', methods=['POST'])
def generate_content():
    data = request.json
    
    # Call text generation agent
    response = requests.post(
        'http://text-generator:8080/generate',
        json={'prompt': data['prompt']}
    )
    
    return jsonify(response.json())

@app.route('/analyze-sentiment', methods=['POST'])
def analyze_sentiment():
    data = request.json
    
    # Call sentiment analysis agent
    response = requests.post(
        'http://sentiment-analyzer:8080/analyze',
        json={'text': data['text']}
    )
    
    return jsonify(response.json())
```

### 2. Microservices Architecture

```yaml
# docker-compose.yml
version: '3.8'
services:
  text-generator:
    image: text-generator:latest
    ports:
      - "8081:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  
  sentiment-analyzer:
    image: sentiment-analyzer:latest
    ports:
      - "8082:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  
  data-analyzer:
    image: data-analyzer:latest
    ports:
      - "8083:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
  
  api-gateway:
    image: api-gateway:latest
    ports:
      - "8080:8080"
    depends_on:
      - text-generator
      - sentiment-analyzer
      - data-analyzer
```

### 3. Event-Driven Architecture

```python
# Event-driven agent integration
import asyncio
import aio_pika
from fastapi import FastAPI

app = FastAPI()

async def process_message(message):
    """Process incoming messages and route to appropriate agents."""
    body = message.body.decode()
    
    if message.routing_key == "content.generation":
        # Route to text generation agent
        await call_text_generator(body)
    elif message.routing_key == "sentiment.analysis":
        # Route to sentiment analysis agent
        await call_sentiment_analyzer(body)

async def setup_rabbitmq():
    """Setup RabbitMQ connection and queues."""
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    
    # Declare queues
    await channel.declare_queue("content.generation")
    await channel.declare_queue("sentiment.analysis")
    
    # Setup consumers
    await channel.set_qos(prefetch_count=1)
    
    return connection, channel
```

## Best Practices

### 1. Agent Design

- **Single Responsibility**: Each agent should focus on one capability
- **Clear Interfaces**: Define clear input/output schemas
- **Error Handling**: Implement robust error handling
- **Logging**: Add comprehensive logging

### 2. Performance

- **Resource Limits**: Set appropriate resource limits
- **Caching**: Implement caching where appropriate
- **Async Operations**: Use async/await for I/O operations
- **Connection Pooling**: Reuse connections when possible

### 3. Security

- **API Key Management**: Use secure API key management
- **Input Validation**: Validate all inputs
- **Rate Limiting**: Implement rate limiting
- **Network Security**: Use secure communication

### 4. Monitoring

- **Health Checks**: Implement health check endpoints
- **Metrics**: Collect performance metrics
- **Logging**: Use structured logging
- **Alerting**: Set up alerting for failures

## Next Steps

1. **Start Simple**: Begin with a basic text generation agent
2. **Add Capabilities**: Gradually add more capabilities
3. **Integrate**: Integrate with your existing systems
4. **Scale**: Scale up as needed
5. **Share**: Share your agents with the community

---

**Ready to build your own agents?** Use these examples as a starting point and customize them for your specific needs! 