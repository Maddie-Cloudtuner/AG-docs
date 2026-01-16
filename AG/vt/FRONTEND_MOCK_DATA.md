# Virtual Tags - Frontend Mock Data & Testing Guide

**Last Updated**: 2025-11-28  
**Purpose**: Complete mock data set for end-to-end frontend testing  
**Related Document**: [FRONTEND_GUIDE.md](file:///c:/Users/LENOVO/Desktop/my_docs/AG/vt/FRONTEND_GUIDE.md)

---

## 📋 Table of Contents

1. [Quick Setup](#quick-setup)
2. [Mock API Server](#mock-api-server)
3. [Sample Data](#sample-data)
4. [Test Scenarios](#test-scenarios)
5. [WebSocket Mock Events](#websocket-mock-events)
6. [GraphQL Mock Responses](#graphql-mock-responses)

---

## 🚀 Quick Setup

### Option 1: JSON Server (Recommended)

Install and run a mock REST API server:

```bash
npm install -g json-server
json-server --watch mock-db.json --port 3001
```

### Option 2: MSW (Mock Service Worker)

For in-browser mocking:

```bash
npm install msw --save-dev
npx msw init public/
```

### Option 3: Manual Mock Implementation

Implement mocks directly in your frontend code - **perfect for rapid prototyping without any server setup!**

**Jump to**: [Complete Implementation Guide](#-manual-mock-implementation-complete-guide)

---

## 🗄️ Sample Data

### Complete Mock Database (mock-db.json)

```json
{
  "resources": [
    {
      "resource_id": "res-001-ec2-prod-web",
      "resource_name": "web-server-prod-001",
      "provider": "aws",
      "resource_type": "ec2",
      "region": "us-east-1",
      "account_id": "123456789012",
      "created_at": "2025-10-15T10:00:00Z",
      "virtual_tags": [
        {
          "key": "environment",
          "value": "production",
          "source": "USER_CONFIRMED",
          "confidence": 1.0,
          "created_at": "2025-11-20T10:00:00Z",
          "updated_at": "2025-11-20T10:00:00Z",
          "created_by": "user@company.com"
        },
        {
          "key": "cost-center",
          "value": "CC-1234",
          "source": "RULE_BASED",
          "confidence": 0.95,
          "created_at": "2025-11-21T14:30:00Z",
          "updated_at": "2025-11-21T14:30:00Z",
          "applied_by_rule": "Auto-tag by naming convention"
        },
        {
          "key": "owner",
          "value": "platform-team@company.com",
          "source": "INFERRED",
          "confidence": 0.89,
          "created_at": "2025-11-22T08:15:00Z",
          "updated_at": "2025-11-22T08:15:00Z"
        },
        {
          "key": "application",
          "value": "web-portal",
          "source": "MANUAL",
          "confidence": 1.0,
          "created_at": "2025-11-23T11:45:00Z",
          "updated_at": "2025-11-23T11:45:00Z"
        }
      ],
      "ml_suggestions": [
        {
          "key": "team",
          "value": "platform-engineering",
          "confidence": 0.92,
          "reasoning": "Based on similar resources tagged by the same owner",
          "alternatives": [
            {
              "value": "devops",
              "confidence": 0.78
            },
            {
              "value": "infrastructure",
              "confidence": 0.65
            }
          ]
        },
        {
          "key": "data-classification",
          "value": "confidential",
          "confidence": 0.85,
          "reasoning": "Production resources typically handle confidential data",
          "alternatives": [
            {
              "value": "internal",
              "confidence": 0.72
            }
          ]
        }
      ],
      "compliance_status": {
        "is_compliant": false,
        "score": 0.75,
        "violations": [
          {
            "violation_type": "MISSING_REQUIRED_TAGS",
            "severity": "HIGH",
            "description": "Missing required tag: business-unit",
            "policy_name": "Corporate Tagging Policy",
            "missing_tags": ["business-unit"]
          }
        ]
      }
    },
    {
      "resource_id": "res-002-s3-dev-data",
      "resource_name": "dev-data-bucket-001",
      "provider": "aws",
      "resource_type": "s3",
      "region": "us-west-2",
      "account_id": "123456789012",
      "created_at": "2025-09-10T14:00:00Z",
      "virtual_tags": [
        {
          "key": "environment",
          "value": "development",
          "source": "INFERRED",
          "confidence": 0.97,
          "created_at": "2025-11-15T09:00:00Z",
          "updated_at": "2025-11-15T09:00:00Z"
        },
        {
          "key": "project",
          "value": "data-analytics",
          "source": "MANUAL",
          "confidence": 1.0,
          "created_at": "2025-11-16T10:30:00Z",
          "updated_at": "2025-11-16T10:30:00Z"
        }
      ],
      "ml_suggestions": [
        {
          "key": "cost-center",
          "value": "CC-5678",
          "confidence": 0.88,
          "reasoning": "Derived from project association with Analytics team",
          "alternatives": []
        }
      ],
      "compliance_status": {
        "is_compliant": true,
        "score": 1.0,
        "violations": []
      }
    },
    {
      "resource_id": "res-003-vm-test-app",
      "resource_name": "test-app-vm-azure-001",
      "provider": "azure",
      "resource_type": "virtual_machine",
      "region": "eastus",
      "subscription_id": "sub-azure-123",
      "created_at": "2025-11-01T12:00:00Z",
      "virtual_tags": [],
      "ml_suggestions": [
        {
          "key": "environment",
          "value": "testing",
          "confidence": 0.94,
          "reasoning": "Name contains 'test' keyword",
          "alternatives": [
            {
              "value": "staging",
              "confidence": 0.71
            }
          ]
        },
        {
          "key": "owner",
          "value": "qa-team@company.com",
          "confidence": 0.81,
          "reasoning": "Similar test resources owned by QA team",
          "alternatives": []
        }
      ],
      "compliance_status": {
        "is_compliant": false,
        "score": 0.0,
        "violations": [
          {
            "violation_type": "MISSING_REQUIRED_TAGS",
            "severity": "CRITICAL",
            "description": "No virtual tags applied. All resources must have minimum tags.",
            "policy_name": "Minimum Tagging Standard",
            "missing_tags": ["environment", "owner", "cost-center"]
          }
        ]
      }
    }
  ],
  "tag_rules": [
    {
      "id": "rule-001",
      "rule_name": "Auto-tag Production Resources",
      "enabled": true,
      "priority": 1,
      "created_at": "2025-10-01T00:00:00Z",
      "updated_at": "2025-11-15T10:00:00Z",
      "conditions": {
        "operator": "AND",
        "rules": [
          {
            "field": "name",
            "operator": "CONTAINS",
            "value": "prod"
          },
          {
            "field": "provider",
            "operator": "EQUALS",
            "value": "aws"
          }
        ]
      },
      "actions": {
        "apply_tags": [
          {
            "tag_key": "environment",
            "tag_value": "production",
            "override_existing": false
          },
          {
            "tag_key": "critical",
            "tag_value": "true",
            "override_existing": false
          }
        ]
      },
      "execution_stats": {
        "total_executions": 1250,
        "resources_tagged": 487,
        "last_execution": "2025-11-27T22:00:00Z"
      }
    },
    {
      "id": "rule-002",
      "rule_name": "Tag Development S3 Buckets",
      "enabled": true,
      "priority": 2,
      "created_at": "2025-10-05T00:00:00Z",
      "updated_at": "2025-11-20T14:30:00Z",
      "conditions": {
        "operator": "AND",
        "rules": [
          {
            "field": "resource_type",
            "operator": "EQUALS",
            "value": "s3"
          },
          {
            "field": "name",
            "operator": "CONTAINS",
            "value": "dev"
          }
        ]
      },
      "actions": {
        "apply_tags": [
          {
            "tag_key": "environment",
            "tag_value": "development",
            "override_existing": false
          },
          {
            "tag_key": "data-classification",
            "tag_value": "internal",
            "override_existing": true
          }
        ]
      },
      "execution_stats": {
        "total_executions": 890,
        "resources_tagged": 234,
        "last_execution": "2025-11-27T22:00:00Z"
      }
    },
    {
      "id": "rule-003",
      "rule_name": "Inherit Cost Center from Account",
      "enabled": false,
      "priority": 5,
      "created_at": "2025-09-15T00:00:00Z",
      "updated_at": "2025-11-10T09:00:00Z",
      "conditions": {
        "operator": "OR",
        "rules": [
          {
            "field": "account_id",
            "operator": "EQUALS",
            "value": "123456789012"
          }
        ]
      },
      "actions": {
        "apply_tags": [
          {
            "tag_key": "cost-center",
            "tag_value": "CC-9999",
            "override_existing": false
          }
        ]
      },
      "execution_stats": {
        "total_executions": 0,
        "resources_tagged": 0,
        "last_execution": null
      }
    }
  ],
  "compliance_policies": [
    {
      "id": "policy-001",
      "policy_name": "Corporate Tagging Policy",
      "description": "Minimum required tags for all production resources",
      "enabled": true,
      "severity": "HIGH",
      "required_tags": ["environment", "owner", "cost-center", "business-unit"],
      "conditions": {
        "operator": "AND",
        "rules": [
          {
            "field": "environment",
            "operator": "EQUALS",
            "value": "production"
          }
        ]
      }
    },
    {
      "id": "policy-002",
      "policy_name": "Minimum Tagging Standard",
      "description": "All resources must have basic tags",
      "enabled": true,
      "severity": "CRITICAL",
      "required_tags": ["environment", "owner", "cost-center"],
      "conditions": {
        "operator": "OR",
        "rules": []
      }
    }
  ],
  "compliance_status": {
    "overall_compliance_score": 0.67,
    "total_resources": 2500,
    "compliant_resources": 1675,
    "non_compliant_resources": 825,
    "by_severity": {
      "CRITICAL": {
        "total_violations": 145,
        "affected_resources": 145
      },
      "HIGH": {
        "total_violations": 423,
        "affected_resources": 380
      },
      "MEDIUM": {
        "total_violations": 256,
        "affected_resources": 200
      },
      "LOW": {
        "total_violations": 102,
        "affected_resources": 100
      }
    },
    "by_policy": [
      {
        "policy_id": "policy-001",
        "policy_name": "Corporate Tagging Policy",
        "compliance_rate": 0.72,
        "violations": 423
      },
      {
        "policy_id": "policy-002",
        "policy_name": "Minimum Tagging Standard",
        "compliance_rate": 0.94,
        "violations": 145
      }
    ]
  },
  "ml_predictions": [
    {
      "resource_id": "res-001-ec2-prod-web",
      "predictions": [
        {
          "tag_key": "team",
          "tag_value": "platform-engineering",
          "confidence": 0.92,
          "model_version": "v2.3.1",
          "reasoning": "Based on similar resources tagged by the same owner"
        }
      ]
    }
  ],
  "audit_trail": [
    {
      "id": "audit-001",
      "timestamp": "2025-11-27T15:30:00Z",
      "action": "TAG_APPLIED",
      "resource_id": "res-001-ec2-prod-web",
      "tag_key": "application",
      "tag_value": "web-portal",
      "source": "MANUAL",
      "performed_by": "user@company.com",
      "metadata": {
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0..."
      }
    },
    {
      "id": "audit-002",
      "timestamp": "2025-11-27T14:20:00Z",
      "action": "TAG_UPDATED",
      "resource_id": "res-002-s3-dev-data",
      "tag_key": "environment",
      "old_value": "dev",
      "new_value": "development",
      "source": "USER_CONFIRMED",
      "performed_by": "admin@company.com"
    },
    {
      "id": "audit-003",
      "timestamp": "2025-11-27T13:10:00Z",
      "action": "RULE_EXECUTED",
      "rule_id": "rule-001",
      "rule_name": "Auto-tag Production Resources",
      "resources_affected": 15,
      "tags_applied": 30
    },
    {
      "id": "audit-004",
      "timestamp": "2025-11-27T12:00:00Z",
      "action": "ML_SUGGESTION_ACCEPTED",
      "resource_id": "res-001-ec2-prod-web",
      "tag_key": "owner",
      "tag_value": "platform-team@company.com",
      "confidence": 0.89,
      "performed_by": "user@company.com"
    }
  ]
}
```

---

## 🔌 Mock API Server

### Complete Express Mock Server

Save as `mock-server.js`:

```javascript
const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// Load mock data
const mockData = require('./mock-db.json');

// ===== REST API ENDPOINTS =====

// GET /api/v1/resources/:resourceId/virtual-tags
app.get('/api/v1/resources/:resourceId/virtual-tags', (req, res) => {
  const resource = mockData.resources.find(r => r.resource_id === req.params.resourceId);
  
  if (!resource) {
    return res.status(404).json({ error: 'Resource not found' });
  }
  
  res.json(resource);
});

// POST /api/v1/virtual-tags/apply
app.post('/api/v1/virtual-tags/apply', (req, res) => {
  const { resource_ids, tags, source, reason } = req.body;
  
  // Simulate processing
  setTimeout(() => {
    res.json({
      success: true,
      tags_applied: tags.length * resource_ids.length,
      resources_updated: resource_ids.length,
      applied_tags: tags.map(tag => ({
        key: tag.key,
        value: tag.value,
        source: source || 'MANUAL',
        confidence: 1.0,
        created_at: new Date().toISOString()
      }))
    });
  }, 500); // Simulate network delay
});

// GET /api/v1/tag-rules
app.get('/api/v1/tag-rules', (req, res) => {
  const { enabled, limit = 50, offset = 0 } = req.query;
  
  let rules = mockData.tag_rules;
  
  if (enabled !== undefined) {
    const enabledBool = enabled === 'true';
    rules = rules.filter(r => r.enabled === enabledBool);
  }
  
  const paginatedRules = rules.slice(offset, offset + parseInt(limit));
  
  res.json({
    rules: paginatedRules,
    pagination: {
      total: rules.length,
      limit: parseInt(limit),
      offset: parseInt(offset)
    }
  });
});

// POST /api/v1/tag-rules
app.post('/api/v1/tag-rules', (req, res) => {
  const newRule = {
    id: `rule-${Date.now()}`,
    ...req.body,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    execution_stats: {
      total_executions: 0,
      resources_tagged: 0,
      last_execution: null
    }
  };
  
  mockData.tag_rules.push(newRule);
  
  res.status(201).json({
    success: true,
    rule: newRule
  });
});

// GET /api/v1/compliance/status
app.get('/api/v1/compliance/status', (req, res) => {
  res.json(mockData.compliance_status);
});

// POST /api/v1/ml/infer
app.post('/api/v1/ml/infer', (req, res) => {
  const { resource_ids, include_alternatives, min_confidence } = req.body;
  
  const predictions = resource_ids.map(resourceId => {
    const resource = mockData.resources.find(r => r.resource_id === resourceId);
    
    if (!resource) {
      return { resource_id: resourceId, predictions: [] };
    }
    
    let suggestions = resource.ml_suggestions || [];
    
    if (min_confidence) {
      suggestions = suggestions.filter(s => s.confidence >= min_confidence);
    }
    
    if (!include_alternatives) {
      suggestions = suggestions.map(s => ({
        key: s.key,
        value: s.value,
        confidence: s.confidence,
        reasoning: s.reasoning
      }));
    }
    
    return {
      resource_id: resourceId,
      predictions: suggestions
    };
  });
  
  setTimeout(() => {
    res.json({ predictions });
  }, 800); // Simulate ML inference delay
});

// GET /api/v1/audit-trail
app.get('/api/v1/audit-trail', (req, res) => {
  const { resource_id, action, limit = 50 } = req.query;
  
  let logs = mockData.audit_trail;
  
  if (resource_id) {
    logs = logs.filter(log => log.resource_id === resource_id);
  }
  
  if (action) {
    logs = logs.filter(log => log.action === action);
  }
  
  res.json({
    logs: logs.slice(0, parseInt(limit)),
    total: logs.length
  });
});

// DELETE /api/v1/virtual-tags/:resourceId/:tagKey
app.delete('/api/v1/virtual-tags/:resourceId/:tagKey', (req, res) => {
  const { resourceId, tagKey } = req.params;
  
  const resource = mockData.resources.find(r => r.resource_id === resourceId);
  
  if (!resource) {
    return res.status(404).json({ error: 'Resource not found' });
  }
  
  const tagIndex = resource.virtual_tags.findIndex(t => t.key === tagKey);
  
  if (tagIndex === -1) {
    return res.status(404).json({ error: 'Tag not found' });
  }
  
  resource.virtual_tags.splice(tagIndex, 1);
  
  res.json({
    success: true,
    message: `Tag ${tagKey} deleted from resource ${resourceId}`
  });
});

// POST /api/v1/ml/feedback
app.post('/api/v1/ml/feedback', (req, res) => {
  const { resource_id, feedback } = req.body;
  
  // Simulate feedback processing
  setTimeout(() => {
    res.json({
      success: true,
      feedback_recorded: feedback.length,
      message: 'Feedback will improve future predictions'
    });
  }, 300);
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`🚀 Mock API Server running on http://localhost:${PORT}`);
  console.log(`📊 Serving ${mockData.resources.length} resources`);
  console.log(`📋 ${mockData.tag_rules.length} tag rules`);
  console.log(`✅ Ready for testing!`);
});
```

### Start the Mock Server

```bash
# Install dependencies
npm install express cors

# Start server
node mock-server.js
```

---

## 🎯 Mock Service Worker (MSW) Setup

For browser-based mocking, use MSW:

### handlers.js

```javascript
import { rest } from 'msw';
import mockData from './mock-db.json';

const API_BASE = 'https://api.cloudtuner.ai/api/v1';

export const handlers = [
  // Get resource tags
  rest.get(`${API_BASE}/resources/:resourceId/virtual-tags`, (req, res, ctx) => {
    const { resourceId } = req.params;
    const resource = mockData.resources.find(r => r.resource_id === resourceId);
    
    if (!resource) {
      return res(ctx.status(404), ctx.json({ error: 'Resource not found' }));
    }
    
    return res(
      ctx.delay(200), // Simulate network delay
      ctx.status(200),
      ctx.json(resource)
    );
  }),

  // Apply tags
  rest.post(`${API_BASE}/virtual-tags/apply`, (req, res, ctx) => {
    const { resource_ids, tags } = req.body;
    
    return res(
      ctx.delay(500),
      ctx.status(200),
      ctx.json({
        success: true,
        tags_applied: tags.length * resource_ids.length,
        resources_updated: resource_ids.length
      })
    );
  }),

  // Get tag rules
  rest.get(`${API_BASE}/tag-rules`, (req, res, ctx) => {
    return res(
      ctx.delay(300),
      ctx.status(200),
      ctx.json({
        rules: mockData.tag_rules,
        pagination: {
          total: mockData.tag_rules.length,
          limit: 50,
          offset: 0
        }
      })
    );
  }),

  // Get compliance status
  rest.get(`${API_BASE}/compliance/status`, (req, res, ctx) => {
    return res(
      ctx.delay(400),
      ctx.status(200),
      ctx.json(mockData.compliance_status)
    );
  }),

  // ML inference
  rest.post(`${API_BASE}/ml/infer`, (req, res, ctx) => {
    const { resource_ids } = req.body;
    
    const predictions = resource_ids.map(resourceId => {
      const resource = mockData.resources.find(r => r.resource_id === resourceId);
      return {
        resource_id: resourceId,
        predictions: resource?.ml_suggestions || []
      };
    });
    
    return res(
      ctx.delay(800),
      ctx.status(200),
      ctx.json({ predictions })
    );
  })
];
```

### browser.js

```javascript
import { setupWorker } from 'msw';
import { handlers } from './handlers';

export const worker = setupWorker(...handlers);
```

### index.js (Enable in development)

```javascript
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

if (process.env.NODE_ENV === 'development') {
  const { worker } = require('./mocks/browser');
  worker.start();
}

ReactDOM.render(<App />, document.getElementById('root'));
```

---

## 🔄 WebSocket Mock Events

### Mock WebSocket Server

```javascript
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  console.log('Client connected');
  
  ws.on('message', (message) => {
    const data = JSON.parse(message);
    
    if (data.event === 'subscribe') {
      console.log(`Subscribed to resource: ${data.resourceId}`);
      
      // Simulate real-time tag updates
      setTimeout(() => {
        ws.send(JSON.stringify({
          event: 'tag:created',
          data: {
            resource_id: data.resourceId,
            tag: {
              key: 'updated-at',
              value: new Date().toISOString(),
              source: 'MANUAL',
              confidence: 1.0
            }
          }
        }));
      }, 3000);
      
      // Simulate ML suggestions
      setTimeout(() => {
        ws.send(JSON.stringify({
          event: 'ml:new_suggestions',
          data: {
            resource_id: data.resourceId,
            suggestions: [
              {
                key: 'priority',
                value: 'high',
                confidence: 0.88,
                reasoning: 'Production resource with high usage'
              }
            ]
          }
        }));
      }, 5000);
    }
  });
});

console.log('🔌 WebSocket server running on ws://localhost:8080');
```

### Mock WebSocket Events Library

```javascript
export const mockWebSocketEvents = {
  tagCreated: {
    event: 'tag:created',
    data: {
      resource_id: 'res-001-ec2-prod-web',
      tag: {
        key: 'new-tag',
        value: 'new-value',
        source: 'MANUAL',
        confidence: 1.0,
        created_at: new Date().toISOString()
      }
    }
  },
  
  tagUpdated: {
    event: 'tag:updated',
    data: {
      resource_id: 'res-001-ec2-prod-web',
      tag: {
        key: 'environment',
        old_value: 'prod',
        new_value: 'production',
        updated_at: new Date().toISOString()
      }
    }
  },
  
  tagDeleted: {
    event: 'tag:deleted',
    data: {
      resource_id: 'res-001-ec2-prod-web',
      tag_key: 'deprecated-tag',
      deleted_at: new Date().toISOString()
    }
  },
  
  newMLSuggestions: {
    event: 'ml:new_suggestions',
    data: {
      resource_id: 'res-001-ec2-prod-web',
      suggestions: [
        {
          key: 'backup-required',
          value: 'true',
          confidence: 0.91,
          reasoning: 'Production database resources require backup'
        }
      ]
    }
  },
  
  complianceAlert: {
    event: 'compliance:violation',
    data: {
      resource_id: 'res-003-vm-test-app',
      violation: {
        type: 'MISSING_REQUIRED_TAGS',
        severity: 'CRITICAL',
        missing_tags: ['environment', 'owner']
      }
    }
  }
};
```

---

## 📊 GraphQL Mock Responses

### Mock Apollo Client Setup

```javascript
import { ApolloClient, InMemoryCache } from '@apollo/client';
import { SchemaLink } from '@apollo/client/link/schema';
import { makeExecutableSchema } from '@graphql-tools/schema';

const typeDefs = `
  type VirtualTag {
    key: String!
    value: String!
    source: String!
    confidence: Float!
    createdAt: String!
  }
  
  type MLSuggestion {
    key: String!
    value: String!
    confidence: Float!
    reasoning: String
    alternatives: [Alternative]
  }
  
  type Alternative {
    value: String!
    confidence: Float!
  }
  
  type ComplianceViolation {
    violationType: String!
    severity: String!
    description: String!
  }
  
  type ComplianceStatus {
    isCompliant: Boolean!
    score: Float!
    violations: [ComplianceViolation]
  }
  
  type Resource {
    id: ID!
    name: String!
    provider: String!
    resourceType: String!
    virtualTags: [VirtualTag]
    mlSuggestions: [MLSuggestion]
    complianceStatus: ComplianceStatus
  }
  
  type Query {
    resource(id: ID!): Resource
  }
  
  type Mutation {
    applyVirtualTags(input: ApplyTagsInput!): ApplyTagsResponse
  }
  
  input ApplyTagsInput {
    resourceIds: [ID!]!
    tags: [TagInput!]!
    source: String!
  }
  
  input TagInput {
    key: String!
    value: String!
    overrideExisting: Boolean
  }
  
  type ApplyTagsResponse {
    success: Boolean!
    tagsApplied: Int!
    resourcesUpdated: Int!
    errors: [String]
  }
`;

const resolvers = {
  Query: {
    resource: (_, { id }) => {
      const mockResource = {
        id: 'res-001-ec2-prod-web',
        name: 'web-server-prod-001',
        provider: 'aws',
        resourceType: 'ec2',
        virtualTags: [
          {
            key: 'environment',
            value: 'production',
            source: 'USER_CONFIRMED',
            confidence: 1.0,
            createdAt: '2025-11-20T10:00:00Z'
          }
        ],
        mlSuggestions: [
          {
            key: 'team',
            value: 'platform-engineering',
            confidence: 0.92,
            reasoning: 'Based on similar resources',
            alternatives: [
              { value: 'devops', confidence: 0.78 }
            ]
          }
        ],
        complianceStatus: {
          isCompliant: false,
          score: 0.75,
          violations: [
            {
              violationType: 'MISSING_REQUIRED_TAGS',
              severity: 'HIGH',
              description: 'Missing required tag: business-unit'
            }
          ]
        }
      };
      
      return mockResource;
    }
  },
  
  Mutation: {
    applyVirtualTags: (_, { input }) => {
      return {
        success: true,
        tagsApplied: input.tags.length * input.resourceIds.length,
        resourcesUpdated: input.resourceIds.length,
        errors: []
      };
    }
  }
};

const schema = makeExecutableSchema({ typeDefs, resolvers });

export const mockClient = new ApolloClient({
  cache: new InMemoryCache(),
  link: new SchemaLink({ schema })
});
```

---

## 🧪 Test Scenarios

### Scenario 1: Complete Tag Lifecycle

```javascript
// Test applying, updating, and deleting tags
async function testTagLifecycle() {
  const resourceId = 'res-001-ec2-prod-web';
  
  // 1. Get initial state
  const initial = await fetch(`http://localhost:3001/api/v1/resources/${resourceId}/virtual-tags`);
  console.log('Initial tags:', await initial.json());
  
  // 2. Apply new tag
  const applyResult = await fetch('http://localhost:3001/api/v1/virtual-tags/apply', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resource_ids: [resourceId],
      tags: [{ key: 'test-tag', value: 'test-value' }],
      source: 'MANUAL'
    })
  });
  console.log('Apply result:', await applyResult.json());
  
  // 3. Verify tag was applied
  const updated = await fetch(`http://localhost:3001/api/v1/resources/${resourceId}/virtual-tags`);
  console.log('Updated tags:', await updated.json());
  
  // 4. Delete tag
  const deleteResult = await fetch(
    `http://localhost:3001/api/v1/virtual-tags/${resourceId}/test-tag`,
    { method: 'DELETE' }
  );
  console.log('Delete result:', await deleteResult.json());
}
```

### Scenario 2: ML Suggestion Workflow

```javascript
// Test accepting ML suggestions
async function testMLSuggestions() {
  const resourceId = 'res-001-ec2-prod-web';
  
  // 1. Get ML predictions
  const predictions = await fetch('http://localhost:3001/api/v1/ml/infer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resource_ids: [resourceId],
      include_alternatives: true,
      min_confidence: 0.7
    })
  });
  const mlData = await predictions.json();
  console.log('ML Suggestions:', mlData);
  
  // 2. Accept first suggestion
  const firstSuggestion = mlData.predictions[0].predictions[0];
  
  const applyResult = await fetch('http://localhost:3001/api/v1/virtual-tags/apply', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resource_ids: [resourceId],
      tags: [{
        key: firstSuggestion.key,
        value: firstSuggestion.value
      }],
      source: 'USER_CONFIRMED'
    })
  });
  console.log('Applied ML suggestion:', await applyResult.json());
  
  // 3. Submit feedback
  const feedback = await fetch('http://localhost:3001/api/v1/ml/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      resource_id: resourceId,
      feedback: [{
        tag_key: firstSuggestion.key,
        predicted_value: firstSuggestion.value,
        actual_value: firstSuggestion.value,
        action: 'ACCEPTED'
      }]
    })
  });
  console.log('Feedback submitted:', await feedback.json());
}
```

### Scenario 3: Compliance Dashboard

```javascript
// Test compliance monitoring
async function testCompliance() {
  // 1. Get overall compliance
  const status = await fetch('http://localhost:3001/api/v1/compliance/status');
  const complianceData = await status.json();
  console.log('Compliance Score:', complianceData.overall_compliance_score);
  console.log('Violations by severity:', complianceData.by_severity);
  
  // 2. Get non-compliant resources
  const nonCompliantResources = mockData.resources.filter(
    r => !r.compliance_status.is_compliant
  );
  console.log('Non-compliant resources:', nonCompliantResources.length);
  
  // 3. Auto-fix first violation
  const resource = nonCompliantResources[0];
  const violation = resource.compliance_status.violations[0];
  
  if (violation.missing_tags) {
    const fixResult = await fetch('http://localhost:3001/api/v1/virtual-tags/apply', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resource_ids: [resource.resource_id],
        tags: violation.missing_tags.map(tag => ({
          key: tag,
          value: 'auto-generated'
        })),
        source: 'COMPLIANCE_FIX'
      })
    });
    console.log('Auto-fix result:', await fixResult.json());
  }
}
```

### Scenario 4: Rule Management

```javascript
// Test creating and managing tag rules
async function testRuleManagement() {
  // 1. Get all enabled rules
  const rulesResponse = await fetch('http://localhost:3001/api/v1/tag-rules?enabled=true');
  const rulesData = await rulesResponse.json();
  console.log('Enabled rules:', rulesData.rules.length);
  
  // 2. Create new rule
  const newRule = {
    rule_name: 'Tag Staging VMs',
    enabled: true,
    priority: 10,
    conditions: {
      operator: 'AND',
      rules: [
        { field: 'resource_type', operator: 'EQUALS', value: 'virtual_machine' },
        { field: 'name', operator: 'CONTAINS', value: 'staging' }
      ]
    },
    actions: {
      apply_tags: [
        { tag_key: 'environment', tag_value: 'staging', override_existing: false }
      ]
    }
  };
  
  const createResult = await fetch('http://localhost:3001/api/v1/tag-rules', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(newRule)
  });
  console.log('Created rule:', await createResult.json());
}
```

---

## 🎨 React Testing Library Examples

### Test Component with Mock Data

```jsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import TagPanel from './TagPanel';
import mockData from './mock-db.json';

// Setup MSW server
const server = setupServer(
  rest.get('/api/v1/resources/:resourceId/virtual-tags', (req, res, ctx) => {
    return res(ctx.json(mockData.resources[0]));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('displays virtual tags for resource', async () => {
  render(<TagPanel resourceId="res-001-ec2-prod-web" />);
  
  await waitFor(() => {
    expect(screen.getByText('environment: production')).toBeInTheDocument();
    expect(screen.getByText('cost-center: CC-1234')).toBeInTheDocument();
  });
});

test('accepts ML suggestion', async () => {
  render(<TagPanel resourceId="res-001-ec2-prod-web" />);
  
  await waitFor(() => {
    expect(screen.getByText(/AI Suggestions/i)).toBeInTheDocument();
  });
  
  const acceptButton = screen.getAllByText(/Accept/i)[0];
  await userEvent.click(acceptButton);
  
  await waitFor(() => {
    expect(screen.getByText('team: platform-engineering')).toBeInTheDocument();
  });
});
```

---

## 🎯 Manual Mock Implementation - Complete Guide

This section shows you how to implement mocks **directly in your frontend code** without any external servers or tools. Perfect for rapid prototyping!

### Step 1: Create Mock Data Module

Create `src/mocks/mockData.js`:

```javascript
// src/mocks/mockData.js

// All your mock data in one place
export const mockResources = [
  {
    resource_id: "res-001-ec2-prod-web",
    resource_name: "web-server-prod-001",
    provider: "aws",
    resource_type: "ec2",
    region: "us-east-1",
    account_id: "123456789012",
    virtual_tags: [
      {
        key: "environment",
        value: "production",
        source: "USER_CONFIRMED",
        confidence: 1.0,
        created_at: "2025-11-20T10:00:00Z"
      },
      {
        key: "cost-center",
        value: "CC-1234",
        source: "RULE_BASED",
        confidence: 0.95,
        created_at: "2025-11-21T14:30:00Z"
      },
      {
        key: "owner",
        value: "platform-team@company.com",
        source: "INFERRED",
        confidence: 0.89,
        created_at: "2025-11-22T08:15:00Z"
      }
    ],
    ml_suggestions: [
      {
        key: "team",
        value: "platform-engineering",
        confidence: 0.92,
        reasoning: "Based on similar resources tagged by the same owner",
        alternatives: [
          { value: "devops", confidence: 0.78 },
          { value: "infrastructure", confidence: 0.65 }
        ]
      },
      {
        key: "data-classification",
        value: "confidential",
        confidence: 0.85,
        reasoning: "Production resources typically handle confidential data",
        alternatives: [
          { value: "internal", confidence: 0.72 }
        ]
      }
    ],
    compliance_status: {
      is_compliant: false,
      score: 0.75,
      violations: [
        {
          violation_type: "MISSING_REQUIRED_TAGS",
          severity: "HIGH",
          description: "Missing required tag: business-unit",
          policy_name: "Corporate Tagging Policy",
          missing_tags: ["business-unit"]
        }
      ]
    }
  },
  {
    resource_id: "res-002-s3-dev-data",
    resource_name: "dev-data-bucket-001",
    provider: "aws",
    resource_type: "s3",
    region: "us-west-2",
    virtual_tags: [
      {
        key: "environment",
        value: "development",
        source: "INFERRED",
        confidence: 0.97,
        created_at: "2025-11-15T09:00:00Z"
      },
      {
        key: "project",
        value: "data-analytics",
        source: "MANUAL",
        confidence: 1.0,
        created_at: "2025-11-16T10:30:00Z"
      }
    ],
    ml_suggestions: [
      {
        key: "cost-center",
        value: "CC-5678",
        confidence: 0.88,
        reasoning: "Derived from project association with Analytics team",
        alternatives: []
      }
    ],
    compliance_status: {
      is_compliant: true,
      score: 1.0,
      violations: []
    }
  },
  {
    resource_id: "res-003-vm-test-app",
    resource_name: "test-app-vm-azure-001",
    provider: "azure",
    resource_type: "virtual_machine",
    region: "eastus",
    virtual_tags: [],
    ml_suggestions: [
      {
        key: "environment",
        value: "testing",
        confidence: 0.94,
        reasoning: "Name contains 'test' keyword",
        alternatives: [
          { value: "staging", confidence: 0.71 }
        ]
      },
      {
        key: "owner",
        value: "qa-team@company.com",
        confidence: 0.81,
        reasoning: "Similar test resources owned by QA team",
        alternatives: []
      }
    ],
    compliance_status: {
      is_compliant: false,
      score: 0.0,
      violations: [
        {
          violation_type: "MISSING_REQUIRED_TAGS",
          severity: "CRITICAL",
          description: "No virtual tags applied. All resources must have minimum tags.",
          policy_name: "Minimum Tagging Standard",
          missing_tags: ["environment", "owner", "cost-center"]
        }
      ]
    }
  }
];

export const mockTagRules = [
  {
    id: "rule-001",
    rule_name: "Auto-tag Production Resources",
    enabled: true,
    priority: 1,
    created_at: "2025-10-01T00:00:00Z",
    conditions: {
      operator: "AND",
      rules: [
        { field: "name", operator: "CONTAINS", value: "prod" },
        { field: "provider", operator: "EQUALS", value: "aws" }
      ]
    },
    actions: {
      apply_tags: [
        { tag_key: "environment", tag_value: "production", override_existing: false },
        { tag_key: "critical", tag_value: "true", override_existing: false }
      ]
    },
    execution_stats: {
      total_executions: 1250,
      resources_tagged: 487,
      last_execution: "2025-11-27T22:00:00Z"
    }
  },
  {
    id: "rule-002",
    rule_name: "Tag Development S3 Buckets",
    enabled: true,
    priority: 2,
    created_at: "2025-10-05T00:00:00Z",
    conditions: {
      operator: "AND",
      rules: [
        { field: "resource_type", operator: "EQUALS", value: "s3" },
        { field: "name", operator: "CONTAINS", value: "dev" }
      ]
    },
    actions: {
      apply_tags: [
        { tag_key: "environment", tag_value: "development", override_existing: false }
      ]
    }
  }
];

export const mockComplianceStatus = {
  overall_compliance_score: 0.67,
  total_resources: 2500,
  compliant_resources: 1675,
  non_compliant_resources: 825,
  by_severity: {
    CRITICAL: { total_violations: 145, affected_resources: 145 },
    HIGH: { total_violations: 423, affected_resources: 380 },
    MEDIUM: { total_violations: 256, affected_resources: 200 },
    LOW: { total_violations: 102, affected_resources: 100 }
  },
  by_policy: [
    {
      policy_id: "policy-001",
      policy_name: "Corporate Tagging Policy",
      compliance_rate: 0.72,
      violations: 423
    },
    {
      policy_id: "policy-002",
      policy_name: "Minimum Tagging Standard",
      compliance_rate: 0.94,
      violations: 145
    }
  ]
};

export const mockAuditTrail = [
  {
    id: "audit-001",
    timestamp: "2025-11-27T15:30:00Z",
    action: "TAG_APPLIED",
    resource_id: "res-001-ec2-prod-web",
    tag_key: "application",
    tag_value: "web-portal",
    source: "MANUAL",
    performed_by: "user@company.com"
  },
  {
    id: "audit-002",
    timestamp: "2025-11-27T14:20:00Z",
    action: "TAG_UPDATED",
    resource_id: "res-002-s3-dev-data",
    tag_key: "environment",
    old_value: "dev",
    new_value: "development",
    source: "USER_CONFIRMED",
    performed_by: "admin@company.com"
  }
];
```

### Step 2: Create Mock API Service

Create `src/api/mockApi.js`:

```javascript
// src/api/mockApi.js
import { 
  mockResources, 
  mockTagRules, 
  mockComplianceStatus,
  mockAuditTrail 
} from '../mocks/mockData';

// Simulate network delay
const delay = (ms = 500) => new Promise(resolve => setTimeout(resolve, ms));

// Helper to clone data (avoid mutations)
const clone = (data) => JSON.parse(JSON.stringify(data));

// Mock API Implementation
export const mockApi = {
  // Get resource with virtual tags
  async getResourceTags(resourceId) {
    await delay(300);
    
    const resource = mockResources.find(r => r.resource_id === resourceId);
    
    if (!resource) {
      throw new Error('Resource not found');
    }
    
    return clone(resource);
  },

  // Apply tags to resources
  async applyTags(resourceIds, tags, source = 'MANUAL', reason = '') {
    await delay(500);
    
    // Simulate updating the mock data
    resourceIds.forEach(resourceId => {
      const resource = mockResources.find(r => r.resource_id === resourceId);
      if (resource) {
        tags.forEach(tag => {
          const existingTagIndex = resource.virtual_tags.findIndex(
            t => t.key === tag.key
          );
          
          const newTag = {
            key: tag.key,
            value: tag.value,
            source: source,
            confidence: 1.0,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          };
          
          if (existingTagIndex > -1 && tag.override_existing) {
            resource.virtual_tags[existingTagIndex] = newTag;
          } else if (existingTagIndex === -1) {
            resource.virtual_tags.push(newTag);
          }
        });
      }
    });
    
    return {
      success: true,
      tags_applied: tags.length * resourceIds.length,
      resources_updated: resourceIds.length,
      applied_tags: tags.map(tag => ({
        key: tag.key,
        value: tag.value,
        source: source,
        confidence: 1.0,
        created_at: new Date().toISOString()
      }))
    };
  },

  // Delete tag
  async deleteTag(resourceId, tagKey) {
    await delay(300);
    
    const resource = mockResources.find(r => r.resource_id === resourceId);
    
    if (!resource) {
      throw new Error('Resource not found');
    }
    
    const tagIndex = resource.virtual_tags.findIndex(t => t.key === tagKey);
    
    if (tagIndex === -1) {
      throw new Error('Tag not found');
    }
    
    resource.virtual_tags.splice(tagIndex, 1);
    
    return {
      success: true,
      message: `Tag ${tagKey} deleted from resource ${resourceId}`
    };
  },

  // Get tag rules
  async getTagRules(filters = {}) {
    await delay(300);
    
    let rules = clone(mockTagRules);
    
    if (filters.enabled !== undefined) {
      rules = rules.filter(r => r.enabled === filters.enabled);
    }
    
    const limit = filters.limit || 50;
    const offset = filters.offset || 0;
    
    return {
      rules: rules.slice(offset, offset + limit),
      pagination: {
        total: rules.length,
        limit: limit,
        offset: offset
      }
    };
  },

  // Create tag rule
  async createTagRule(ruleData) {
    await delay(500);
    
    const newRule = {
      id: `rule-${Date.now()}`,
      ...ruleData,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      execution_stats: {
        total_executions: 0,
        resources_tagged: 0,
        last_execution: null
      }
    };
    
    mockTagRules.push(newRule);
    
    return {
      success: true,
      rule: clone(newRule)
    };
  },

  // Get compliance status
  async getComplianceStatus() {
    await delay(400);
    return clone(mockComplianceStatus);
  },

  // Get ML predictions
  async getMLPredictions(resourceIds, options = {}) {
    await delay(800); // Simulate ML processing
    
    const predictions = resourceIds.map(resourceId => {
      const resource = mockResources.find(r => r.resource_id === resourceId);
      
      if (!resource) {
        return { resource_id: resourceId, predictions: [] };
      }
      
      let suggestions = clone(resource.ml_suggestions || []);
      
      if (options.min_confidence) {
        suggestions = suggestions.filter(s => s.confidence >= options.min_confidence);
      }
      
      if (!options.include_alternatives) {
        suggestions = suggestions.map(s => ({
          key: s.key,
          value: s.value,
          confidence: s.confidence,
          reasoning: s.reasoning
        }));
      }
      
      return {
        resource_id: resourceId,
        predictions: suggestions
      };
    });
    
    return { predictions };
  },

  // Submit ML feedback
  async submitMLFeedback(resourceId, feedback) {
    await delay(300);
    
    return {
      success: true,
      feedback_recorded: feedback.length,
      message: 'Feedback will improve future predictions'
    };
  },

  // Get audit trail
  async getAuditTrail(filters = {}) {
    await delay(300);
    
    let logs = clone(mockAuditTrail);
    
    if (filters.resource_id) {
      logs = logs.filter(log => log.resource_id === filters.resource_id);
    }
    
    if (filters.action) {
      logs = logs.filter(log => log.action === filters.action);
    }
    
    const limit = filters.limit || 50;
    
    return {
      logs: logs.slice(0, limit),
      total: logs.length
    };
  },

  // Search resources
  async searchResources(query, filters = {}) {
    await delay(400);
    
    let resources = clone(mockResources);
    
    if (query) {
      resources = resources.filter(r => 
        r.resource_name.toLowerCase().includes(query.toLowerCase()) ||
        r.resource_id.toLowerCase().includes(query.toLowerCase())
      );
    }
    
    if (filters.provider) {
      resources = resources.filter(r => r.provider === filters.provider);
    }
    
    if (filters.resource_type) {
      resources = resources.filter(r => r.resource_type === filters.resource_type);
    }
    
    return {
      resources,
      total: resources.length
    };
  }
};

export default mockApi;
```

### Step 3: Create API Service with Environment Switching

Create `src/api/index.js`:

```javascript
// src/api/index.js
import mockApi from './mockApi';

// Configuration
const USE_MOCK_API = process.env.REACT_APP_USE_MOCK_API === 'true';
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'https://api.cloudtuner.ai/api/v1';

// Real API implementation (fetch-based)
const realApi = {
  async getResourceTags(resourceId) {
    const response = await fetch(`${API_BASE_URL}/resources/${resourceId}/virtual-tags`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch resource tags');
    }
    
    return await response.json();
  },

  async applyTags(resourceIds, tags, source, reason) {
    const response = await fetch(`${API_BASE_URL}/virtual-tags/apply`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        resource_ids: resourceIds,
        tags: tags,
        source: source,
        reason: reason
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to apply tags');
    }
    
    return await response.json();
  },

  async deleteTag(resourceId, tagKey) {
    const response = await fetch(`${API_BASE_URL}/virtual-tags/${resourceId}/${tagKey}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to delete tag');
    }
    
    return await response.json();
  },

  async getTagRules(filters) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${API_BASE_URL}/tag-rules?${params}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch tag rules');
    }
    
    return await response.json();
  },

  async createTagRule(ruleData) {
    const response = await fetch(`${API_BASE_URL}/tag-rules`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(ruleData)
    });
    
    if (!response.ok) {
      throw new Error('Failed to create tag rule');
    }
    
    return await response.json();
  },

  async getComplianceStatus() {
    const response = await fetch(`${API_BASE_URL}/compliance/status`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch compliance status');
    }
    
    return await response.json();
  },

  async getMLPredictions(resourceIds, options) {
    const response = await fetch(`${API_BASE_URL}/ml/infer`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        resource_ids: resourceIds,
        ...options
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to get ML predictions');
    }
    
    return await response.json();
  },

  async submitMLFeedback(resourceId, feedback) {
    const response = await fetch(`${API_BASE_URL}/ml/feedback`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        resource_id: resourceId,
        feedback: feedback
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to submit feedback');
    }
    
    return await response.json();
  },

  async getAuditTrail(filters) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${API_BASE_URL}/audit-trail?${params}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch audit trail');
    }
    
    return await response.json();
  },

  async searchResources(query, filters) {
    const params = new URLSearchParams({ q: query, ...filters });
    const response = await fetch(`${API_BASE_URL}/resources/search?${params}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to search resources');
    }
    
    return await response.json();
  }
};

// Export the appropriate API based on environment
const api = USE_MOCK_API ? mockApi : realApi;

export default api;

// Also export individual methods for convenience
export const {
  getResourceTags,
  applyTags,
  deleteTag,
  getTagRules,
  createTagRule,
  getComplianceStatus,
  getMLPredictions,
  submitMLFeedback,
  getAuditTrail,
  searchResources
} = api;
```

### Step 4: Create Custom React Hooks

Create `src/hooks/useResourceTags.js`:

```javascript
// src/hooks/useResourceTags.js
import { useState, useEffect } from 'react';
import api from '../api';

export function useResourceTags(resourceId) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!resourceId) return;

    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        const result = await api.getResourceTags(resourceId);
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [resourceId]);

  const refetch = async () => {
    if (!resourceId) return;
    
    try {
      setLoading(true);
      setError(null);
      const result = await api.getResourceTags(resourceId);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, refetch };
}

export function useApplyTags() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const applyTags = async (resourceIds, tags, source = 'MANUAL') => {
    try {
      setLoading(true);
      setError(null);
      const result = await api.applyTags(resourceIds, tags, source);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { applyTags, loading, error };
}

export function useComplianceStatus() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        const result = await api.getComplianceStatus();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  return { data, loading, error };
}
```

### Step 5: Use in Components

Create `src/components/TagPanel.jsx`:

```jsx
// src/components/TagPanel.jsx
import React from 'react';
import { useResourceTags, useApplyTags } from '../hooks/useResourceTags';

function TagPanel({ resourceId }) {
  const { data, loading, error, refetch } = useResourceTags(resourceId);
  const { applyTags, loading: applyingTags } = useApplyTags();

  const handleAcceptSuggestion = async (suggestion) => {
    try {
      await applyTags(
        [resourceId],
        [{ key: suggestion.key, value: suggestion.value, override_existing: true }],
        'USER_CONFIRMED'
      );
      
      // Refetch to show updated tags
      await refetch();
      
      alert('Tag applied successfully!');
    } catch (err) {
      alert('Failed to apply tag: ' + err.message);
    }
  };

  const handleAddTag = async (key, value) => {
    try {
      await applyTags(
        [resourceId],
        [{ key, value, override_existing: false }],
        'MANUAL'
      );
      
      await refetch();
      alert('Tag added successfully!');
    } catch (err) {
      alert('Failed to add tag: ' + err.message);
    }
  };

  if (loading) return <div>Loading tags...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return <div>No data</div>;

  return (
    <div className="tag-panel">
      <h2>{data.resource_name}</h2>
      <span className="badge">{data.provider}</span>
      <span className="badge">{data.resource_type}</span>

      {/* Virtual Tags */}
      <div className="virtual-tags">
        <h3>Virtual Tags</h3>
        <div className="tag-list">
          {data.virtual_tags.map(tag => (
            <div key={tag.key} className="tag-badge">
              <span className="tag-key">{tag.key}:</span>
              <span className="tag-value">{tag.value}</span>
              <span className="tag-source">{tag.source}</span>
              {tag.confidence && (
                <span className="confidence">
                  {Math.round(tag.confidence * 100)}%
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Compliance Status */}
      {!data.compliance_status.is_compliant && (
        <div className="compliance-alert">
          <h4>⚠️ Compliance Issues</h4>
          {data.compliance_status.violations.map((violation, idx) => (
            <div key={idx} className="violation">
              <span className="severity">{violation.severity}</span>
              <span className="description">{violation.description}</span>
            </div>
          ))}
        </div>
      )}

      {/* ML Suggestions */}
      {data.ml_suggestions && data.ml_suggestions.length > 0 && (
        <div className="ml-suggestions">
          <h3>🤖 AI Suggestions</h3>
          {data.ml_suggestions.map(suggestion => (
            <div key={suggestion.key} className="suggestion-card">
              <div className="suggestion-header">
                <strong>{suggestion.key}:</strong> {suggestion.value}
                <span className="confidence">
                  {Math.round(suggestion.confidence * 100)}% confident
                </span>
              </div>
              {suggestion.reasoning && (
                <p className="reasoning">💡 {suggestion.reasoning}</p>
              )}
              <button
                onClick={() => handleAcceptSuggestion(suggestion)}
                disabled={applyingTags}
              >
                ✓ Accept
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default TagPanel;
```

### Step 6: Environment Configuration

Create `.env.development`:

```bash
# .env.development
REACT_APP_USE_MOCK_API=true
REACT_APP_API_BASE_URL=https://api.cloudtuner.ai/api/v1
```

Create `.env.production`:

```bash
# .env.production
REACT_APP_USE_MOCK_API=false
REACT_APP_API_BASE_URL=https://api.cloudtuner.ai/api/v1
```

### Step 7: Quick Toggle for Testing

Add a toggle button in your app:

```jsx
// src/App.jsx
import React, { useState } from 'react';
import TagPanel from './components/TagPanel';

function App() {
  const [useMock, setUseMock] = useState(
    process.env.REACT_APP_USE_MOCK_API === 'true'
  );

  // Toggle between mock and real API
  const toggleMockApi = () => {
    const newValue = !useMock;
    setUseMock(newValue);
    process.env.REACT_APP_USE_MOCK_API = newValue.toString();
    window.location.reload(); // Reload to apply changes
  };

  return (
    <div className="app">
      <header>
        <h1>CloudTuner Virtual Tags</h1>
        <button onClick={toggleMockApi}>
          {useMock ? '🔄 Switch to Real API' : '🔄 Switch to Mock API'}
        </button>
        <span className="api-mode">
          {useMock ? '📦 Mock Mode' : '🌐 Live Mode'}
        </span>
      </header>

      <main>
        <TagPanel resourceId="res-001-ec2-prod-web" />
      </main>
    </div>
  );
}

export default App;
```

### Usage Examples

#### Example 1: Using in a Component

```jsx
import React from 'react';
import { useResourceTags } from '../hooks/useResourceTags';

function MyComponent() {
  const { data, loading, error } = useResourceTags('res-001-ec2-prod-web');

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>{data.resource_name}</h2>
      {data.virtual_tags.map(tag => (
        <div key={tag.key}>{tag.key}: {tag.value}</div>
      ))}
    </div>
  );
}
```

#### Example 2: Direct API Call

```jsx
import api from '../api';

async function handleButtonClick() {
  try {
    const result = await api.applyTags(
      ['res-001-ec2-prod-web'],
      [{ key: 'environment', value: 'production' }],
      'MANUAL'
    );
    
    console.log('Success:', result);
  } catch (error) {
    console.error('Error:', error);
  }
}
```

#### Example 3: Testing Mode Toggle

```jsx
// Anywhere in your code
import api from '../api';

// Check which API is active
console.log('Using mock API:', process.env.REACT_APP_USE_MOCK_API);

// Test with mock data
const data = await api.getResourceTags('res-001-ec2-prod-web');
console.log('Mock data:', data);
```

### Folder Structure

```
src/
├── api/
│   ├── index.js          # Main API service with env switching
│   └── mockApi.js        # Mock API implementation
├── mocks/
│   └── mockData.js       # All mock data
├── hooks/
│   └── useResourceTags.js  # Custom React hooks
├── components/
│   └── TagPanel.jsx      # Example component
├── App.jsx
└── index.js
```

### Advantages of This Approach

✅ **No external dependencies** - Works out of the box  
✅ **Environment-based switching** - Use `.env` files to toggle  
✅ **Instant testing** - No server setup required  
✅ **Realistic delays** - Simulates network latency  
✅ **Full control** - Modify mock data anytime  
✅ **Easy debugging** - All code is in your project  
✅ **Works offline** - Perfect for development  
✅ **Type-safe** - Add TypeScript if needed  

### Quick Start Commands

```bash
# 1. Copy the files above into your React project

# 2. Install dependencies (if not already installed)
npm install react

# 3. Start development with mock API
REACT_APP_USE_MOCK_API=true npm start

# 4. Start development with real API
REACT_APP_USE_MOCK_API=false npm start
```

### Testing Different Scenarios

```javascript
// Test with different resources
const resource1 = await api.getResourceTags('res-001-ec2-prod-web');  // Has tags
const resource2 = await api.getResourceTags('res-002-s3-dev-data');   // Compliant
const resource3 = await api.getResourceTags('res-003-vm-test-app');   // No tags

// Test applying tags
await api.applyTags(
  ['res-003-vm-test-app'],
  [
    { key: 'environment', value: 'testing' },
    { key: 'owner', value: 'qa-team@company.com' }
  ]
);

// Test ML predictions
const predictions = await api.getMLPredictions(
  ['res-001-ec2-prod-web'],
  { include_alternatives: true, min_confidence: 0.7 }
);

// Test compliance
const compliance = await api.getComplianceStatus();
console.log('Compliance Score:', compliance.overall_compliance_score);
```

---

## 📝 Summary

### Available Mock Resources

| Resource ID | Provider | Type | Tags | Suggestions | Compliant |
|------------|----------|------|------|------------|-----------|
| `res-001-ec2-prod-web` | AWS | EC2 | 4 | 2 | ❌ |
| `res-002-s3-dev-data` | AWS | S3 | 2 | 1 | ✅ |
| `res-003-vm-test-app` | Azure | VM | 0 | 2 | ❌ |

### API Endpoints Ready for Testing

✅ GET `/api/v1/resources/{id}/virtual-tags`  
✅ POST `/api/v1/virtual-tags/apply`  
✅ DELETE `/api/v1/virtual-tags/{resourceId}/{tagKey}`  
✅ GET `/api/v1/tag-rules`  
✅ POST `/api/v1/tag-rules`  
✅ GET `/api/v1/compliance/status`  
✅ POST `/api/v1/ml/infer`  
✅ POST `/api/v1/ml/feedback`  
✅ GET `/api/v1/audit-trail`

### Next Steps

1. Choose your mock strategy (JSON Server, MSW, or Express)
2. Copy the `mock-db.json` content to your project
3. Start the mock server
4. Update your API base URL to point to `http://localhost:3001`
5. Run your frontend application and test!

---

**Happy Testing! 🚀**

For questions, refer to [FRONTEND_GUIDE.md](file:///c:/Users/LENOVO/Desktop/my_docs/AG/vt/FRONTEND_GUIDE.md)
