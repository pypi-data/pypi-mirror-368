# Personal Access Token (PAT) System Overview

## 🎯 **What is the PAT System?**

The Personal Access Token (PAT) system is a secure authentication mechanism that allows CLI tools and external applications to interact with the Agents Registry API without using traditional Cognito authentication tokens.

## 🏗️ **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Tools     │    │   Frontend      │    │   External Apps │
│                 │    │                 │    │                 │
│ • Use PAT for   │    │ • Use Cognito   │    │ • Use PAT for   │
│   API access    │    │   tokens        │    │   API access    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   API Gateway   │
                    │                 │
                    │ • Route requests│
                    │ • Handle CORS   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Lambda Router  │
                    │                 │
                    │ • PAT validation│
                    │ • Route to      │
                    │   handlers      │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Agents Handler │    │  Users Handler  │    │ Frameworks      │
│                 │    │                 │    │ Handler         │
│ • Accepts PAT   │    │ • Cognito only  │    │ • Public access │
│ • CRUD agents   │    │ • PAT management│    │• List frameworks│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   DynamoDB      │
                    │                 │
                    │ • Users table   │
                    │ • Agents table  │
                    │ • Frameworks    │
                    └─────────────────┘
```

## 🔐 **Authentication Strategy**

### **Endpoint Access Matrix**

| Endpoint Type | Cognito Token | PAT Token | Public Access |
|---------------|---------------|-----------|---------------|
| **Frameworks** | ✅ | ✅ | ✅ |
| **Agents** | ✅ | ✅ | ❌ |
| **Users** | ✅ | ❌ | ❌ |
| **PAT Management** | ✅ | ❌ | ❌ |

### **Authentication Flow**

1. **CLI Tool Request**: Sends request with PAT in Authorization header
2. **API Gateway**: Routes request to appropriate Lambda handler
3. **PAT Validation**: Lambda validates PAT against DynamoDB
4. **User Context**: System identifies user associated with PAT
5. **Request Processing**: Agent operations performed with user context
6. **Response**: Results returned to CLI tool

## 🛡️ **Security Features**

### **PAT Security Model**

- **One-Way Hashing**: Original PAT never stored, only SHA-256 hash
- **User Isolation**: Each PAT tied to specific user account
- **Revocation Support**: Users can revoke PATs anytime
- **Usage Tracking**: Last used timestamp updated on each request
- **No Expiration**: PATs remain valid until explicitly revoked

### **Security Best Practices**

- ✅ Store PATs in environment variables
- ✅ Never commit PATs to source code
- ✅ Rotate PATs every 90 days
- ✅ Monitor usage patterns
- ❌ Don't share PATs publicly
- ❌ Don't use PATs in client-side code

## 📋 **PAT Lifecycle**

### **1. Generation**
```
User requests PAT → System generates 64-char token → Hash stored in DB → Token returned to user
```

### **2. Usage**
```
CLI tool sends PAT → System hashes PAT → Looks up hash in DB → Validates user → Processes request
```

### **3. Management**
```
User can view, copy, or revoke PAT → System updates DB → PAT becomes invalid
```

## 🚀 **Usage Examples**

### **CLI Tool Integration**

```bash
# Set PAT environment variable
export AGENTS_REGISTRY_PAT="YOUR_PAT_TOKEN_HERE"

# Create agent
curl -X POST "https://api.myagentregistry.com/agents" \
  -H "Authorization: Bearer $AGENTS_REGISTRY_PAT" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Agent", "description": "Agent description"}'
```

### **Python Integration**

```python
import requests

class AgentsRegistry:
    def __init__(self, pat):
        self.base_url = "https://api.myagentregistry.com"
        self.headers = {'Authorization': f'Bearer {pat}'}
    
    def create_agent(self, name, description):
        data = {'name': name, 'description': description}
        response = requests.post(f"{self.base_url}/agents", 
                               headers=self.headers, json=data)
        return response.json()

# Usage
registry = AgentsRegistry("your_pat_here")
agent = registry.create_agent("My Agent", "Description")
```

## 📊 **System Benefits**

### **For CLI Tools**
- **Simplified Authentication**: No need for complex OAuth flows
- **Persistent Access**: PATs don't expire automatically
- **Secure**: One-way hashing prevents token exposure
- **User Context**: Full user context for operations

### **For Users**
- **Easy Management**: Generate, view, and revoke from profile
- **Secure**: PATs are cryptographically secure
- **Flexible**: Can be used across multiple tools
- **Trackable**: Usage patterns are logged

### **For System**
- **Scalable**: Efficient DynamoDB lookups
- **Secure**: Multiple layers of security validation
- **Maintainable**: Clear separation of concerns
- **Extensible**: Easy to add new features

## 🔧 **Technical Implementation**

### **Key Components**

1. **PAT Generation**: `UserService.generate_pat()`
2. **PAT Validation**: `UserService.validate_pat()`
3. **PAT Management**: User profile UI endpoints
4. **Authentication Middleware**: Lambda handler authentication logic

### **Database Schema**

```json
{
  "user_id": "string",
  "pat_hash": "string (SHA-256)",
  "pat_value": "string (original PAT)",
  "pat_created_at": "timestamp",
  "pat_last_used": "timestamp"
}
```

### **API Endpoints**

- **PAT Generation**: `POST /users/pat/generate`
- **PAT Info**: `GET /users/pat`
- **PAT Value**: `GET /users/pat/value`
- **PAT Revocation**: `DELETE /users/pat/revoke`

## 📈 **Monitoring & Analytics**

### **Usage Metrics**
- PAT generation frequency
- PAT usage patterns
- Failed authentication attempts
- User activity correlation

### **Security Monitoring**
- Suspicious usage patterns
- Multiple failed attempts
- Geographic anomalies
- Rate limiting violations

## 🔮 **Future Enhancements**

### **Planned Features**
1. **PAT Scopes**: Fine-grained permissions
2. **PAT Expiration**: Optional expiration dates
3. **PAT Analytics**: Usage reporting
4. **PAT Rotation**: Automatic rotation policies
5. **MFA Integration**: Multi-factor authentication

### **Implementation Roadmap**
- ✅ **Phase 1**: Basic PAT functionality
- 🔄 **Phase 2**: PAT scopes and permissions
- 📋 **Phase 3**: Advanced security features
- 📋 **Phase 4**: Analytics and monitoring
- 📋 **Phase 5**: Enterprise features

## 📚 **Documentation**

### **For Users**
- [PAT Documentation](./PAT_DOCUMENTATION.md) - Complete user guide
- [PAT Quick Reference](./PAT_QUICK_REFERENCE.md) - Quick start guide

### **For Developers**
- [PAT Technical Implementation](./PAT_TECHNICAL_IMPLEMENTATION.md) - Technical details
- [API Documentation](./API_TESTING_SUMMARY.md) - API reference

## 🎉 **Summary**

The PAT system provides a secure, scalable, and user-friendly way for CLI tools and external applications to interact with the Agents Registry API. It maintains the security of Cognito authentication while providing the flexibility needed for programmatic access.

**Key Benefits:**
- 🔒 **Secure**: One-way hashing and user isolation
- 🚀 **Simple**: Easy to integrate with CLI tools
- 📊 **Trackable**: Usage monitoring and analytics
- 🔧 **Flexible**: Supports multiple use cases
- 🛡️ **Reliable**: Robust error handling and validation

---

**Last Updated**: August 4, 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready 