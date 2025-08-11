# PAT Quick Reference Guide

## Quick Start

### 1. Get Your PAT
1. Log in to [Agents Registry](https://myagentregistry.com)
2. Go to Profile → Personal Access Token
3. Click "Generate Token"
4. Copy the token immediately (64 characters)

### 2. Use PAT in CLI Tools

```bash
# Set environment variable
export AGENTS_REGISTRY_PAT="your_pat_here"

# Test connection
curl -X GET "https://api.myagentregistry.com/agents" \
  -H "Authorization: Bearer $AGENTS_REGISTRY_PAT"
```

## Common Commands

### Create Agent
```bash
curl -X POST "https://api.myagentregistry.com/agents" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AGENTS_REGISTRY_PAT" \
  -d '{
    "name": "My Agent",
    "description": "Agent description",
    "category": "automation"
  }'
```

### List Agents
```bash
curl -X GET "https://api.myagentregistry.com/agents" \
  -H "Authorization: Bearer $AGENTS_REGISTRY_PAT"
```

### Update Agent
```bash
curl -X PUT "https://api.myagentregistry.com/agents/AGENT_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $AGENTS_REGISTRY_PAT" \
  -d '{"description": "Updated description"}'
```

### Delete Agent
```bash
curl -X DELETE "https://api.myagentregistry.com/agents/AGENT_ID" \
  -H "Authorization: Bearer $AGENTS_REGISTRY_PAT"
```

## Python Example

```python
import requests

class AgentsRegistry:
    def __init__(self, pat):
        self.base_url = "https://api.myagentregistry.com"
        self.headers = {
            'Authorization': f'Bearer {pat}',
            'Content-Type': 'application/json'
        }
    
    def create_agent(self, name, description):
        data = {'name': name, 'description': description}
        response = requests.post(f"{self.base_url}/agents", 
                               headers=self.headers, json=data)
        return response.json()

# Usage
registry = AgentsRegistry("your_pat_here")
agent = registry.create_agent("My Agent", "Description")
```

## Node.js Example

```javascript
const axios = require('axios');

class AgentsRegistry {
    constructor(pat) {
        this.client = axios.create({
            baseURL: 'https://api.myagentregistry.com',
            headers: { 'Authorization': `Bearer ${pat}` }
        });
    }
    
    async createAgent(name, description) {
        const response = await this.client.post('/agents', {
            name, description
        });
        return response.data;
    }
}

// Usage
const registry = new AgentsRegistry('your_pat_here');
registry.createAgent('My Agent', 'Description');
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| 401 Unauthorized | Check PAT is correct and not revoked |
| 404 Not Found | Verify agent ID exists |
| 400 Bad Request | Check JSON payload format |

## Security Notes

- ✅ Store PAT in environment variables
- ✅ Never commit PAT to source code
- ✅ Rotate PAT every 90 days
- ❌ Don't share PAT publicly
- ❌ Don't use PAT in client-side code

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents` | POST | Create agent |
| `/agents` | GET | List agents |
| `/agents/{id}` | GET | Get agent |
| `/agents/{id}` | PUT | Update agent |
| `/agents/{id}` | DELETE | Delete agent |

## Support

- **Documentation**: See `PAT_DOCUMENTATION.md`
- **API Health**: `GET https://api.myagentregistry.com/health`
- **Test PAT**: Use any agents endpoint with your PAT 