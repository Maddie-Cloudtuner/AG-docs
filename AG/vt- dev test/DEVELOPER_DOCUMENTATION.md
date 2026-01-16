# 🔧 Virtual Tagging Prototype - Developer Documentation

## 📋 **Table of Contents**
- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Setup & Installation](#setup--installation)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Frontend Components](#frontend-components)
- [Backend Structure](#backend-structure)
- [Rule Engine](#rule-engine)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## 🎯 **Project Overview**

Virtual Tagging is a full-stack prototype application that simulates cloud resource tagging without modifying actual cloud infrastructure. It provides a safe environment to test and visualize tagging strategies across AWS, GCP, and Azure.

### **Core Concepts**
- **Virtual Tags**: Simulated tags that overlay real resource data
- **Rule Engine**: Automated tagging based on resource properties
- **Multi-Cloud Support**: Unified interface for AWS, GCP, Azure resources
- **Mock Database Fallback**: Automatic fallback when PostgreSQL unavailable

---

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React)       │◄──►│   (Node.js)     │◄──►│ (PostgreSQL/    │
│   Port: 5173    │    │   Port: 5000    │    │  Mock DB)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Request Flow**
1. **Frontend** sends HTTP requests to backend API
2. **Backend** processes requests and applies business logic
3. **Database** stores/retrieves resources, virtual tags, and rules
4. **Rule Engine** evaluates conditions and applies tags automatically

---

## 💻 **Technology Stack**

### **Frontend**
- **React 18**: Component-based UI framework
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API calls

### **Backend**
- **Node.js**: JavaScript runtime
- **Express.js**: Web framework
- **PostgreSQL**: Primary database (with mock fallback)
- **pg**: PostgreSQL client library
- **cors**: Cross-Origin Resource Sharing
- **dotenv**: Environment variable management

### **Development Tools**
- **nodemon**: Auto-restart development server
- **ESLint**: Code linting
- **Prettier**: Code formatting

---

## 🚀 **Setup & Installation**

### **Prerequisites**
```bash
- Node.js 16+ 
- npm or yarn
- PostgreSQL 12+ (optional - mock DB fallback available)
```

### **Clone & Install**
```bash
# Clone repository
git clone <repository-url>
cd virtual-tagging-prototype

# Install backend dependencies
cd server
npm install

# Install frontend dependencies
cd ../client
npm install
```

### **Environment Setup**

**Backend (.env)**
```bash
# server/.env
PORT=5000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=virtual_tagging
DB_USER=postgres
DB_PASSWORD=postgres
```

**Frontend (.env)**
```bash
# client/.env
VITE_API_URL=http://localhost:5000/api
```

### **Database Setup (Optional)**
```bash
# Create PostgreSQL database
createdb virtual_tagging

# Or using psql
psql -c "CREATE DATABASE virtual_tagging;"
```

### **Start Application**
```bash
# Terminal 1 - Backend
cd server
npm run dev

# Terminal 2 - Frontend
cd client
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000/api
- Health Check: http://localhost:5000/api/health

---

## 📡 **API Documentation**

### **Base URL**
```
http://localhost:5000/api
```

### **Authentication**
Currently no authentication required (prototype phase)

### **Common Response Format**
```json
{
  "data": {},
  "error": "Error message (if any)",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 🔌 **API Endpoints**

### **Health Check**

#### `GET /health`
Check API server status

**Response:**
```json
{
  "message": "Virtual Tagging API is running!",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Example:**
```bash
curl http://localhost:5000/api/health
```

---

### **Resources API**

#### `GET /resources`
Retrieve all resources with merged virtual tags

**Response:**
```json
[
  {
    "id": 1,
    "resource_id": "aws-ec2-i-1234567890abcdef0",
    "name": "prod-web-server-01",
    "cloud": "AWS",
    "account_id": "123456789012",
    "native_tags": {
      "Environment": "production",
      "Team": "frontend"
    },
    "virtualTags": {
      "CostCenter": "Production",
      "Criticality": "High"
    },
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

**Example:**
```bash
curl http://localhost:5000/api/resources
```

#### `POST /resources`
Create a new resource

**Request Body:**
```json
{
  "resourceId": "aws-ec2-i-new123456789",
  "name": "new-web-server",
  "cloud": "AWS",
  "accountId": "123456789012",
  "nativeTags": {
    "Environment": "development"
  }
}
```

**Response:**
```json
{
  "id": 5,
  "resource_id": "aws-ec2-i-new123456789",
  "name": "new-web-server",
  "cloud": "AWS",
  "account_id": "123456789012",
  "native_tags": {
    "Environment": "development"
  },
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/resources \
  -H "Content-Type: application/json" \
  -d '{
    "resourceId": "aws-ec2-i-new123456789",
    "name": "new-web-server",
    "cloud": "AWS",
    "accountId": "123456789012",
    "nativeTags": {"Environment": "development"}
  }'
```

---

### **Virtual Tags API**

#### `POST /virtual-tags`
Add a virtual tag to a resource

**Request Body:**
```json
{
  "resourceId": "aws-ec2-i-1234567890abcdef0",
  "tagKey": "Owner",
  "tagValue": "john.doe@company.com",
  "createdBy": "manual"
}
```

**Response:**
```json
{
  "id": 10,
  "resource_id": "aws-ec2-i-1234567890abcdef0",
  "tag_key": "Owner",
  "tag_value": "john.doe@company.com",
  "created_by": "manual",
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/virtual-tags \
  -H "Content-Type: application/json" \
  -d '{
    "resourceId": "aws-ec2-i-1234567890abcdef0",
    "tagKey": "Owner", 
    "tagValue": "john.doe@company.com",
    "createdBy": "manual"
  }'
```

#### `GET /virtual-tags/:resourceId`
Get all virtual tags for a specific resource

**Response:**
```json
[
  {
    "id": 1,
    "resource_id": "aws-ec2-i-1234567890abcdef0",
    "tag_key": "CostCenter",
    "tag_value": "Production",
    "created_by": "rule:Production Environment Tagging",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

**Example:**
```bash
curl http://localhost:5000/api/virtual-tags/aws-ec2-i-1234567890abcdef0
```

---

### **Rules API**

#### `GET /rules`
Retrieve all tagging rules

**Response:**
```json
[
  {
    "id": 1,
    "rule_name": "Production Environment Tagging",
    "condition": "name CONTAINS 'prod'",
    "tag_key": "CostCenter",
    "tag_value": "Production", 
    "scope": "All",
    "priority": 1,
    "created_by": "system",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

**Example:**
```bash
curl http://localhost:5000/api/rules
```

#### `POST /rules`
Create a new tagging rule

**Request Body:**
```json
{
  "ruleName": "AWS Critical Resources",
  "condition": "cloud EQUALS 'AWS'",
  "tagKey": "Criticality",
  "tagValue": "High",
  "scope": "AWS",
  "priority": 2,
  "createdBy": "admin"
}
```

**Response:**
```json
{
  "id": 3,
  "rule_name": "AWS Critical Resources",
  "condition": "cloud EQUALS 'AWS'",
  "tag_key": "Criticality",
  "tag_value": "High",
  "scope": "AWS", 
  "priority": 2,
  "created_by": "admin",
  "created_at": "2024-01-01T12:00:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/rules \
  -H "Content-Type: application/json" \
  -d '{
    "ruleName": "AWS Critical Resources",
    "condition": "cloud EQUALS '\''AWS'\''",
    "tagKey": "Criticality",
    "tagValue": "High",
    "scope": "AWS",
    "priority": 2,
    "createdBy": "admin"
  }'
```

#### `POST /rules/apply`
Apply all rules to all resources

**Response:**
```json
{
  "message": "Applied 15 tags from 3 rules to 4 resources",
  "appliedCount": 15,
  "details": [
    {
      "resourceId": "aws-ec2-i-1234567890abcdef0",
      "resourceName": "prod-web-server-01", 
      "ruleName": "Production Environment Tagging",
      "tagKey": "CostCenter",
      "tagValue": "Production"
    }
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/rules/apply
```

---

## 🗄️ **Database Schema**

### **Resources Table**
```sql
CREATE TABLE IF NOT EXISTS resources (
  id SERIAL PRIMARY KEY,
  resource_id VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  cloud VARCHAR(50) NOT NULL,
  account_id VARCHAR(255) NOT NULL,
  native_tags JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Virtual Tags Table**
```sql
CREATE TABLE IF NOT EXISTS virtual_tags (
  id SERIAL PRIMARY KEY,
  resource_id VARCHAR(255) NOT NULL,
  tag_key VARCHAR(255) NOT NULL,
  tag_value VARCHAR(255) NOT NULL,
  created_by VARCHAR(255) DEFAULT 'system',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(resource_id, tag_key)
);
```

### **Rules Table**  
```sql
CREATE TABLE IF NOT EXISTS rules (
  id SERIAL PRIMARY KEY,
  rule_name VARCHAR(255) NOT NULL,
  condition VARCHAR(500) NOT NULL,
  tag_key VARCHAR(255) NOT NULL,
  tag_value VARCHAR(255) NOT NULL,
  scope VARCHAR(50) DEFAULT 'All',
  priority INTEGER DEFAULT 1,
  created_by VARCHAR(255) DEFAULT 'system',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Indexes**
```sql
-- Performance indexes
CREATE INDEX idx_resources_cloud ON resources(cloud);
CREATE INDEX idx_resources_name ON resources(name);
CREATE INDEX idx_virtual_tags_resource ON virtual_tags(resource_id);
CREATE INDEX idx_rules_priority ON rules(priority DESC);
```

---

## ⚛️ **Frontend Components**

### **Component Structure**
```
src/
├── components/
│   ├── Navbar.jsx              # Navigation component
│   ├── ResourceCard.jsx        # Individual resource display
│   ├── RuleCard.jsx           # Individual rule display
│   ├── AddResourceModal.jsx    # Resource creation form
│   ├── AddVirtualTagModal.jsx  # Virtual tag creation form
│   └── AddRuleModal.jsx       # Rule creation form
├── pages/
│   ├── LandingPage.jsx        # Home page
│   ├── ResourcesPage.jsx      # Resource management
│   └── RulesPage.jsx          # Rule management
├── services/
│   └── api.js                 # API client functions
└── App.jsx                    # Main application component
```

### **Key Components**

#### **ResourceCard.jsx**
Displays individual resource with native and virtual tags

**Props:**
```javascript
{
  resource: {
    resource_id: string,
    name: string,
    cloud: string,
    native_tags: object,
    virtualTags: object
  },
  onAddVirtualTag: function
}
```

#### **AddRuleModal.jsx**  
Modal form for creating tagging rules with condition builder

**Features:**
- Visual condition builder
- Rule preview
- Priority setting
- Scope selection

#### **API Service (api.js)**
Centralized API client with axios

**Methods:**
```javascript
// Resources
resourcesApi.getAll()
resourcesApi.create(data)

// Virtual Tags  
virtualTagsApi.getByResourceId(id)
virtualTagsApi.create(data)

// Rules
rulesApi.getAll()
rulesApi.create(data)
rulesApi.apply()

// Health
healthApi.check()
```

---

## 🔧 **Backend Structure**

### **Project Structure**
```
server/
├── src/
│   ├── models/
│   │   ├── Resource.js         # Resource data model
│   │   ├── VirtualTag.js       # Virtual tag model
│   │   └── Rule.js            # Rule model
│   ├── routes/
│   │   ├── resources.js        # Resource endpoints
│   │   ├── virtualTags.js     # Virtual tag endpoints
│   │   └── rules.js           # Rule endpoints
│   ├── utils/
│   │   ├── database.js         # Database connection
│   │   ├── mockDatabase.js     # Mock DB fallback
│   │   ├── ruleEngine.js      # Rule processing logic
│   │   └── initDb.js          # Database initialization
│   └── app.js                 # Express application setup
├── package.json
└── .env
```

### **Model Methods**

#### **Resource.js**
```javascript
Resource.createTable()           // Create table schema
Resource.create(resourceData)    // Insert new resource
Resource.findAll()              // Get all resources  
Resource.findById(resourceId)   // Get specific resource
```

#### **VirtualTag.js**
```javascript
VirtualTag.createTable()                    // Create table schema
VirtualTag.create(tagData)                 // Insert/update virtual tag
VirtualTag.findByResourceId(resourceId)    // Get tags for resource
VirtualTag.findAll()                       // Get all virtual tags
```

#### **Rule.js**
```javascript
Rule.createTable()           // Create table schema
Rule.create(ruleData)       // Insert new rule
Rule.findAll()             // Get all rules
Rule.findById(id)          // Get specific rule
```

---

## 🎯 **Rule Engine**

### **Rule Condition Format**
```
[field] [operator] '[value]'
```

### **Supported Operators**
- **CONTAINS**: Field contains the specified value
- **STARTS_WITH**: Field starts with the specified value  
- **EQUALS**: Field exactly matches the specified value

### **Supported Fields**
- **name**: Resource name
- **cloud**: Cloud provider (AWS, GCP, Azure)
- **account_id**: Cloud account identifier

### **Example Conditions**
```javascript
"name CONTAINS 'prod'"           // Production resources
"name STARTS_WITH 'web'"         // Web servers
"cloud EQUALS 'AWS'"            // AWS resources only
"account_id EQUALS '123456'"    // Specific account
```

### **Rule Processing Logic**
```javascript
// Rule evaluation flow
function evaluateCondition(resource, condition) {
  const regex = /(\w+)\s+(CONTAINS|STARTS_WITH|EQUALS)\s+['"]([^'"]+)['"]/i;
  const match = condition.match(regex);
  
  const [, field, operator, value] = match;
  const resourceValue = resource[field.toLowerCase()];
  
  switch (operator.toUpperCase()) {
    case 'CONTAINS': return resourceValue.includes(value);
    case 'STARTS_WITH': return resourceValue.startsWith(value);
    case 'EQUALS': return resourceValue === value;
  }
}
```

### **Rule Application Process**
1. Fetch all active rules (ordered by priority)
2. Fetch all resources
3. For each rule:
   - Check scope (All, AWS, GCP, Azure)
   - For each matching resource:
     - Evaluate condition
     - Apply virtual tag if condition passes
4. Return application summary

---

## 🔄 **Development Workflow**

### **Code Style**
```bash
# Use ESLint for code linting
npm run lint

# Use Prettier for code formatting  
npm run format
```

### **Environment Variables**
```bash
# Backend environment variables
PORT=5000                    # Server port
DB_HOST=localhost           # Database host
DB_PORT=5432               # Database port  
DB_NAME=virtual_tagging    # Database name
DB_USER=postgres           # Database user
DB_PASSWORD=postgres       # Database password

# Frontend environment variables
VITE_API_URL=http://localhost:5000/api  # API base URL
```

### **Development Commands**
```bash
# Backend development
cd server
npm run dev         # Start with nodemon auto-restart
npm start          # Production start

# Frontend development  
cd client
npm run dev        # Start Vite dev server
npm run build      # Production build
npm run preview    # Preview production build
```

### **Database Management**
```bash
# Initialize database and sample data
node src/utils/initDb.js

# Reset mock data (development)
# Restart server to reset in-memory mock data
```

---

## 🧪 **Testing**

### **Manual Testing**

#### **API Testing with curl**
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test resources endpoint
curl http://localhost:5000/api/resources

# Test rule creation
curl -X POST http://localhost:5000/api/rules \
  -H "Content-Type: application/json" \
  -d '{"ruleName": "Test Rule", "condition": "name CONTAINS '\''test'\''", "tagKey": "Test", "tagValue": "Value"}'

# Test rule application
curl -X POST http://localhost:5000/api/rules/apply
```

#### **Frontend Testing**
1. Navigate to all pages
2. Test resource creation
3. Test virtual tag addition
4. Test rule creation and application
5. Verify visual tag distinction

### **Database Testing**
```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d virtual_tagging -c "SELECT version();"

# Test mock database fallback
# Stop PostgreSQL service and restart server
sudo service postgresql stop
npm run dev  # Should automatically use mock database
```

---

## 🚀 **Deployment**

### **Production Build**
```bash
# Build frontend
cd client
npm run build
# Creates dist/ folder with static files

# Backend is ready for production
cd server  
npm start
```

### **Environment Setup**
```bash
# Production environment variables
NODE_ENV=production
PORT=8080
DB_HOST=production-db-host
DB_NAME=virtual_tagging_prod
# ... other production settings
```

### **Docker Deployment (Optional)**
```dockerfile
# Dockerfile example
FROM node:16-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
EXPOSE 5000

CMD ["npm", "start"]
```

### **Reverse Proxy (nginx)**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
        root /path/to/client/dist;
    }
    
    # API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test locally
4. Commit with descriptive messages
5. Push and create pull request

### **Code Standards**
- Use ESLint configuration
- Follow React best practices
- Write descriptive commit messages
- Add comments for complex logic
- Update documentation for API changes

### **Pull Request Process**
1. Update README if needed
2. Test all functionality locally
3. Ensure no console errors
4. Update API documentation for new endpoints
5. Add sample data if new features require it

---

## 📚 **Additional Resources**

### **Technology Documentation**
- [React Documentation](https://react.dev/)
- [Express.js Guide](https://expressjs.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)

### **API Testing Tools**
- [Postman](https://www.postman.com/) - API testing GUI
- [curl](https://curl.se/) - Command line HTTP client
- [HTTPie](https://httpie.io/) - User-friendly HTTP client

### **Database Tools**
- [pgAdmin](https://www.pgadmin.org/) - PostgreSQL administration
- [DBeaver](https://dbeaver.io/) - Universal database tool

---

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Database Connection Failed**
```bash
Error: Database connection error
Solution: Check PostgreSQL service status, credentials, database exists
Fallback: Application automatically uses mock database
```

#### **Port Already in Use**
```bash
Error: EADDRINUSE :::5000
Solution: Kill process on port 5000 or change PORT in .env
Command: lsof -ti:5000 | xargs kill
```

#### **CORS Issues**
```bash
Error: Access-Control-Allow-Origin
Solution: Verify VITE_API_URL in client/.env matches server URL
Check: cors() middleware is enabled in server/src/app.js
```

#### **Frontend Build Issues**
```bash
Error: Module not found
Solution: Clear node_modules and reinstall
Commands: rm -rf node_modules package-lock.json && npm install
```

### **Debug Mode**
```bash
# Enable debug logging
DEBUG=* npm run dev

# Check server logs
tail -f server.log

# Monitor database queries
# Enable query logging in PostgreSQL configuration
```

---

## 📞 **Support**

For technical questions or issues:

1. **Check this documentation** for common solutions
2. **Review error logs** in browser console and server terminal  
3. **Test API endpoints** directly with curl or Postman
4. **Verify environment variables** are set correctly
5. **Check database connection** and fallback behavior

**Development Contact**: Your development team lead
**Documentation Updates**: Submit PR with documentation changes

---

*This developer documentation provides complete technical details for understanding, modifying, and extending the Virtual Tagging prototype.* 🔧📚