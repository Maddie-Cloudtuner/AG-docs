# AI Sales Buddy - API Specification
## Integration with Hyundai LMS/H-Smart App

---

## 📋 Overview

This document defines the complete API specification for the AI Sales Buddy integration with Hyundai's existing Courseplay Cloud Architecture.

### Base URLs

| Environment | URL |
|-------------|-----|
| Development | `https://api-dev.salesbuddy.hyundai.co.in` |
| Staging | `https://api-staging.salesbuddy.hyundai.co.in` |
| Production | `https://api.salesbuddy.hyundai.co.in` |

### Authentication

All API calls require JWT token authentication obtained via SSO integration with Hyundai's Identity Provider.

```
Authorization: Bearer <jwt_token>
X-Hyundai-App-Id: <app_id>
X-Request-Id: <uuid>
```

---

## 🔐 Authentication APIs

### 1. SSO Token Exchange

Exchanges LMS SSO token for Sales Buddy session token.

```
POST /api/v1/auth/token-exchange
```

**Request Headers:**
```
Content-Type: application/json
X-LMS-SSO-Token: <lms_sso_token>
```

**Request Body:**
```json
{
  "lms_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "app_context": {
    "source": "LMS|HSMART",
    "device_type": "mobile|web",
    "device_id": "device-uuid-123"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4...",
    "expires_in": 3600,
    "token_type": "Bearer",
    "user": {
      "id": "SC-12345",
      "name": "Rahul Sharma",
      "email": "rahul.sharma@dealer.hyundai.co.in",
      "role": "sales_consultant",
      "dealer_code": "DL001",
      "region": "North",
      "zone": "Delhi-NCR",
      "preferred_language": "hi"
    }
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": {
    "code": "AUTH_INVALID_TOKEN",
    "message": "Invalid or expired SSO token",
    "details": null
  }
}
```

---

### 2. Refresh Token

```
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "new_access_token...",
    "expires_in": 3600
  }
}
```

---

## 💬 Conversation APIs

### 3. Start New Session

Creates a new conversation session for tracking analytics.

```
POST /api/v1/conversations/sessions
```

**Request Body:**
```json
{
  "context": {
    "entry_point": "product_page|home|training",
    "initial_model": "Creta|Venue|i20|null",
    "customer_present": true
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123xyz",
    "created_at": "2024-12-22T10:30:00Z",
    "avatar_url": "https://cdn.salesbuddy.hyundai.co.in/avatars/buddy-v2.mp4",
    "greeting": {
      "text": "नमस्ते राहुल जी! मैं आपका सेल्स बडी हूं। आज मैं आपकी कैसे मदद कर सकता हूं?",
      "audio_url": "https://cdn.salesbuddy.hyundai.co.in/audio/greeting_hi_123.mp3",
      "language": "hi"
    }
  }
}
```

---

### 4. Send Message (Core Chat API)

Main API for sending user queries and receiving AI responses.

```
POST /api/v1/conversations/{session_id}/messages
```

**Request Body:**
```json
{
  "input": {
    "type": "text|audio|video",
    "content": "Compare Creta with Seltos",
    "audio_base64": null,
    "language": "en"
  },
  "output_preferences": {
    "format": "text|audio|video|all",
    "include_avatar": true,
    "include_sources": true
  },
  "context": {
    "current_model": "Creta",
    "customer_segment": "executive|family|youth"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message_id": "msg_xyz789",
    "intent": "competitor_comparison",
    "confidence": 0.95,
    "response": {
      "text": "Here's a detailed comparison between Hyundai Creta and Kia Seltos...",
      "formatted_html": "<div class='comparison'>...</div>",
      "audio_url": "https://cdn.salesbuddy.hyundai.co.in/audio/resp_123.mp3",
      "avatar_video_url": "https://cdn.salesbuddy.hyundai.co.in/video/resp_123.mp4",
      "language": "en"
    },
    "comparison_data": {
      "hyundai_model": {
        "name": "Creta SX",
        "price": "₹18.50 Lakh",
        "features": [
          {"name": "Engine", "value": "1.5L Turbo GDi"},
          {"name": "Power", "value": "160 PS"},
          {"name": "Sunroof", "value": "Panoramic", "is_advantage": true},
          {"name": "ADAS", "value": "Level 2", "is_advantage": true}
        ]
      },
      "competitor_model": {
        "name": "Seltos HTK+",
        "price": "₹18.80 Lakh",
        "features": [
          {"name": "Engine", "value": "1.5L Turbo GDi"},
          {"name": "Power", "value": "160 PS"},
          {"name": "Sunroof", "value": "Single Pane", "is_advantage": false},
          {"name": "ADAS", "value": "Not Available", "is_advantage": false}
        ]
      },
      "hyundai_advantages": [
        "Panoramic Sunroof vs Single Pane",
        "ADAS Level 2 included",
        "Better value at ₹30K lower price"
      ]
    },
    "sources": [
      {"type": "lms", "document": "Creta Product Guide 2024", "confidence": 0.98},
      {"type": "web", "url": "https://www.kia.com/in/seltos", "fetched_at": "2024-12-22T09:00:00Z"}
    ],
    "suggested_followups": [
      "Tell me more about Creta's ADAS features",
      "What colors are available in Creta SX?",
      "Show me the EMI options"
    ],
    "processing_time_ms": 1250
  }
}
```

---

### 5. Send Audio Message

For voice input processing.

```
POST /api/v1/conversations/{session_id}/messages/audio
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
audio_file: <binary audio file>
language_hint: "hi" (optional)
output_format: "audio|text|both"
include_avatar: true
```

**Response:** Same structure as text message response.

---

### 6. Get Conversation History

```
GET /api/v1/conversations/{session_id}/messages
```

**Query Parameters:**
- `limit`: Number of messages (default: 20, max: 100)
- `offset`: Pagination offset
- `include_audio`: Include audio URLs (default: false)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123xyz",
    "messages": [
      {
        "message_id": "msg_001",
        "role": "user",
        "content": "What is the price of Creta?",
        "timestamp": "2024-12-22T10:31:00Z"
      },
      {
        "message_id": "msg_002",
        "role": "assistant",
        "content": "Hyundai Creta starts at ₹11.00 Lakh (ex-showroom)...",
        "intent": "pricing_query",
        "timestamp": "2024-12-22T10:31:02Z"
      }
    ],
    "total_count": 12,
    "has_more": false
  }
}
```

---

### 7. End Session

```
POST /api/v1/conversations/{session_id}/end
```

**Request Body:**
```json
{
  "feedback": {
    "rating": 5,
    "helpful": true,
    "comments": "Very useful for competitor comparison"
  },
  "outcome": {
    "customer_interested": true,
    "test_drive_scheduled": false,
    "model_discussed": "Creta"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "session_summary": {
      "duration_seconds": 420,
      "messages_count": 15,
      "queries_answered": 12,
      "comparison_generated": 2
    }
  }
}
```

---

## 🚗 Product APIs

### 8. Get Product Information

```
GET /api/v1/products/{model}
```

**Path Parameters:**
- `model`: Hyundai model name (e.g., "creta", "venue", "i20")

**Query Parameters:**
- `variant`: Specific variant (optional)
- `include_competitors`: Include competitor comparison (default: false)
- `language`: Response language (default: "en")

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "model": "Creta",
    "tagline": "The Ultimate SUV",
    "price_range": {
      "min": "₹11.00 Lakh",
      "max": "₹20.15 Lakh",
      "type": "ex-showroom"
    },
    "variants": [
      {
        "name": "E",
        "price": "₹11.00 Lakh",
        "engine": "1.5L MPi Petrol",
        "transmission": "MT"
      },
      {
        "name": "SX (O)",
        "price": "₹18.50 Lakh",
        "engine": "1.5L Turbo GDi",
        "transmission": "DCT",
        "highlights": ["Panoramic Sunroof", "ADAS Level 2", "Ventilated Seats"]
      }
    ],
    "key_features": [
      {"category": "Safety", "features": ["6 Airbags", "ESC", "Hill Assist"]},
      {"category": "Comfort", "features": ["Ventilated Seats", "Wireless Charging"]}
    ],
    "colors": [
      {"name": "Phantom Black", "hex": "#000000", "availability": "all_variants"},
      {"name": "Titan Grey", "hex": "#4A4A4A", "availability": "all_variants"}
    ],
    "competitors": ["Kia Seltos", "Toyota Grand Vitara", "VW Taigun"],
    "source": "LMS Database",
    "last_updated": "2024-12-22T00:00:00Z"
  }
}
```

---

### 9. Compare Products

```
POST /api/v1/products/compare
```

**Request Body:**
```json
{
  "hyundai_model": "Creta",
  "hyundai_variant": "SX (O)",
  "competitor": "Seltos",
  "competitor_variant": "HTK+",
  "comparison_type": "detailed|summary",
  "include_web_data": true
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "comparison_id": "cmp_12345",
    "generated_at": "2024-12-22T10:45:00Z",
    "models": {
      "hyundai": {
        "model": "Creta",
        "variant": "SX (O)",
        "price": "₹18.50 Lakh"
      },
      "competitor": {
        "model": "Seltos",
        "variant": "HTK+",
        "price": "₹18.80 Lakh"
      }
    },
    "comparison_table": [
      {
        "category": "Engine",
        "hyundai": "1.5L Turbo GDi (160 PS)",
        "competitor": "1.5L Turbo GDi (160 PS)",
        "winner": "tie"
      },
      {
        "category": "Sunroof",
        "hyundai": "Panoramic",
        "competitor": "Single Pane",
        "winner": "hyundai",
        "advantage_text": "Larger panoramic sunroof for better experience"
      },
      {
        "category": "ADAS",
        "hyundai": "Level 2 (19 features)",
        "competitor": "Not Available",
        "winner": "hyundai",
        "advantage_text": "Advanced safety features not available in competitor"
      }
    ],
    "summary": {
      "hyundai_wins": 8,
      "competitor_wins": 3,
      "ties": 5,
      "top_advantages": [
        "ADAS Level 2 with 19 safety features",
        "Panoramic sunroof vs single pane",
        "₹30,000 lower price"
      ]
    },
    "sales_pitch": "The Creta SX (O) offers significantly better value with ADAS Level 2 and a panoramic sunroof, all at a lower price than the Seltos HTK+.",
    "data_sources": {
      "hyundai": {"source": "LMS", "freshness": "real-time"},
      "competitor": {"source": "web_search", "cached_at": "2024-12-22T06:00:00Z"}
    }
  }
}
```

---

## 🎓 Training & Skills APIs

### 10. Get Sales Process Guidance

```
GET /api/v1/training/sales-process
```

**Query Parameters:**
- `stage`: Specific sales stage (enquiry|test-drive|negotiation|closing)
- `scenario`: Specific scenario type

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "stages": [
      {
        "stage_id": "enquiry",
        "title": "Customer Enquiry",
        "order": 1,
        "key_steps": [
          "Greet warmly and introduce yourself",
          "Understand customer needs through open questions",
          "Identify primary use case (commute/family/adventure)"
        ],
        "best_practices": [
          "Never assume customer's budget",
          "Always offer refreshments",
          "Use customer's name during conversation"
        ],
        "common_mistakes": [
          "Jumping to product features too quickly",
          "Not listening to customer preferences"
        ],
        "video_url": "https://cdn.lms.hyundai.co.in/training/enquiry-best-practices.mp4"
      }
    ]
  }
}
```

---

### 11. Get Soft Skills Tips

```
GET /api/v1/training/soft-skills
```

**Query Parameters:**
- `skill`: negotiation|communication|objection-handling|relationship-building
- `language`: Response language

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "skill": "negotiation",
    "tips": [
      {
        "title": "Understand Before Countering",
        "description": "Always understand the customer's perspective before presenting counter-offers",
        "example": "Instead of immediately defending the price, ask what factors are most important to them"
      },
      {
        "title": "Focus on Value, Not Just Price",
        "description": "Shift the conversation from price to total value ownership",
        "example": "When discussing the ₹1 lakh difference, highlight the ADAS features that provide safety worth millions"
      }
    ],
    "scenarios": [
      {
        "scenario": "Customer says competitor is cheaper",
        "recommended_response": "I understand price is important. Let's look at what you get for that difference - in Creta, you're getting ADAS Level 2 which includes features like automatic emergency braking..."
      }
    ]
  }
}
```

---

### 12. Handle Negative/Tough Questions

```
POST /api/v1/training/objection-handling
```

**Request Body:**
```json
{
  "objection": "Your car has transmission issues, I've read many complaints online",
  "model": "Creta",
  "context": "customer_conversation"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "objection_category": "quality_concern",
    "severity": "high",
    "recommended_response": {
      "acknowledge": "I appreciate you bringing this up - it shows you're doing thorough research, which is great.",
      "address": "The concerns you might have seen were related to early batches of DCT units in 2019. Since then, Hyundai has made significant improvements with upgraded clutch packs and better cooling systems.",
      "reassure": "We now offer a 3-year/unlimited km warranty on the transmission specifically. Would you like me to show you the latest customer satisfaction data?",
      "redirect": "Many of our customers who had similar concerns are now happy Creta owners. I can connect you with one of them if you'd like a real-world perspective."
    },
    "supporting_facts": [
      "DCT transmission upgraded in 2021 with improved clutch pack",
      "Extended warranty now covers transmission for 3 years",
      "Customer satisfaction score improved to 4.5/5 in 2024"
    ],
    "do_not_say": [
      "Those complaints are false",
      "Our competitors have worse problems",
      "That was a long time ago, forget it"
    ]
  }
}
```

---

## 📊 Analytics APIs

### 13. Get User Analytics (SC Level)

```
GET /api/v1/analytics/users/{user_id}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user_id": "SC-12345",
    "period": "last_30_days",
    "metrics": {
      "total_sessions": 45,
      "total_queries": 312,
      "avg_session_duration_seconds": 420,
      "queries_per_session": 6.9
    },
    "query_breakdown": {
      "product_info": 145,
      "competitor_comparison": 78,
      "pricing": 45,
      "sales_process": 24,
      "soft_skills": 20
    },
    "engagement_score": 85,
    "skill_assessment": {
      "product_knowledge": {"score": 88, "trend": "improving"},
      "competitor_awareness": {"score": 72, "trend": "stable"},
      "sales_process": {"score": 65, "trend": "needs_improvement"}
    },
    "recommendations": [
      {
        "type": "training",
        "title": "Sales Process Refresher",
        "reason": "Low queries on sales process indicates potential knowledge gap",
        "priority": "high"
      }
    ]
  }
}
```

---

### 14. Get Dashboard Analytics (HO/RO Level)

```
GET /api/v1/analytics/dashboard
```

**Query Parameters:**
- `scope`: national|zone|region|dealer
- `zone`: Zone code (if scope is zone or lower)
- `region`: Region code (if scope is region or dealer)
- `period`: today|week|month|quarter

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "scope": "national",
    "period": "today",
    "summary": {
      "total_sessions": 2450,
      "total_queries": 15680,
      "avg_session_duration_seconds": 510,
      "active_users": 1890,
      "inactive_users": 560,
      "active_percentage": 77.1
    },
    "trends": {
      "sessions_change_percent": 12.5,
      "queries_change_percent": 8.3,
      "engagement_change_percent": 5.2
    },
    "top_queries": [
      {"query": "Creta vs Seltos comparison", "count": 234},
      {"query": "i20 N Line features", "count": 189},
      {"query": "Venue price list", "count": 156}
    ],
    "top_models_queried": [
      {"model": "Creta", "percentage": 35},
      {"model": "Venue", "percentage": 25},
      {"model": "i20", "percentage": 18}
    ],
    "zone_breakdown": [
      {"zone": "North", "sessions": 680, "engagement_score": 82},
      {"zone": "South", "sessions": 720, "engagement_score": 88},
      {"zone": "West", "sessions": 580, "engagement_score": 79},
      {"zone": "East", "sessions": 470, "engagement_score": 75}
    ],
    "leaderboard": {
      "top_users": [
        {"rank": 1, "user_id": "SC-12345", "name": "Rahul Sharma", "dealer": "Delhi", "score": 95},
        {"rank": 2, "user_id": "SC-67890", "name": "Priya Singh", "dealer": "Mumbai", "score": 92}
      ]
    },
    "adaptive_learning_insights": {
      "training_recommendations": [
        {"topic": "Venue variant differences", "users_needing": 156, "priority": "high"},
        {"topic": "Negotiation skills", "users_needing": 89, "priority": "medium"}
      ]
    }
  }
}
```

---

### 15. Get Gamification Leaderboard

```
GET /api/v1/analytics/leaderboard
```

**Query Parameters:**
- `scope`: national|zone|region|dealer
- `period`: week|month|quarter|all-time
- `limit`: Number of entries (default: 10)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "period": "month",
    "scope": "national",
    "leaderboard": [
      {
        "rank": 1,
        "user_id": "SC-12345",
        "name": "Rahul Sharma",
        "dealer": "Hyundai Delhi Central",
        "zone": "North",
        "score": 2450,
        "badges": ["Product Expert", "Top Performer", "Streak Master"],
        "metrics": {
          "queries_answered": 312,
          "comparisons_generated": 45,
          "training_completed": 8
        }
      }
    ],
    "user_rank": {
      "rank": 45,
      "score": 1280,
      "percentile": 85
    }
  }
}
```

---

## 📤 Content Management APIs

### 16. Upload Training Content (CMS)

```
POST /api/v1/cms/content
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
file: <binary file - PDF/DOC/Video>
metadata: {
  "title": "Creta 2025 Product Guide",
  "category": "product|training|policy|pricing",
  "model": "Creta",
  "language": "en",
  "effective_date": "2024-12-22",
  "tags": ["Creta", "2025", "Features", "Specifications"]
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "content_id": "cnt_abc123",
    "status": "processing",
    "estimated_processing_time_seconds": 120,
    "webhook_url": "https://api.salesbuddy.hyundai.co.in/webhooks/content/cnt_abc123"
  }
}
```

---

### 17. Get Content Processing Status

```
GET /api/v1/cms/content/{content_id}/status
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "content_id": "cnt_abc123",
    "status": "completed",
    "processing_details": {
      "chunks_created": 45,
      "embeddings_generated": 45,
      "index_updated": true
    },
    "preview": {
      "title": "Creta 2025 Product Guide",
      "pages": 24,
      "word_count": 8500
    },
    "completed_at": "2024-12-22T11:02:00Z"
  }
}
```

---

## 🔄 Integration APIs (For LMS Team)

### 18. LMS Data Sync Webhook

Receives updates from LMS when content changes.

```
POST /api/v1/integrations/lms/webhook
```

**Request Body:**
```json
{
  "event_type": "content_updated|content_deleted|price_updated",
  "timestamp": "2024-12-22T10:00:00Z",
  "payload": {
    "entity_type": "product|training|policy",
    "entity_id": "creta_2025",
    "action": "update",
    "data": {
      "model": "Creta",
      "variant": "SX (O)",
      "new_price": "₹18.50 Lakh",
      "effective_from": "2024-12-22"
    }
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "webhook_id": "wh_12345",
    "status": "accepted",
    "processing_eta_seconds": 30
  }
}
```

---

### 19. HRMS User Sync

Receives user updates from HRMS.

```
POST /api/v1/integrations/hrms/users
```

**Request Body:**
```json
{
  "action": "create|update|deactivate",
  "users": [
    {
      "employee_id": "SC-12345",
      "name": "Rahul Sharma",
      "email": "rahul.sharma@dealer.hyundai.co.in",
      "role": "sales_consultant",
      "dealer_code": "DL001",
      "region": "North",
      "zone": "Delhi-NCR",
      "status": "active",
      "joined_date": "2023-01-15"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "processed": 1,
    "created": 0,
    "updated": 1,
    "failed": 0
  }
}
```

---

## 🌐 iFrame Embed APIs

### 20. Get Embed Configuration

Returns configuration for embedding the Sales Buddy iFrame.

```
GET /api/v1/embed/config
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "iframe_url": "https://salesbuddy.hyundai.co.in/embed",
    "allowed_origins": [
      "https://lms.hyundai.co.in",
      "https://hsmart.hyundai.co.in"
    ],
    "embed_code": "<iframe src='https://salesbuddy.hyundai.co.in/embed?token={{SSO_TOKEN}}' width='400' height='600' frameborder='0' allow='microphone; camera'></iframe>",
    "javascript_sdk": "https://cdn.salesbuddy.hyundai.co.in/sdk/v1/salesbuddy.min.js",
    "features": {
      "voice_input": true,
      "avatar": true,
      "dark_mode": true
    }
  }
}
```

---

## 📝 Error Codes Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_INVALID_TOKEN` | 401 | Invalid or expired authentication token |
| `AUTH_INSUFFICIENT_PERMISSIONS` | 403 | User doesn't have required permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `VALIDATION_ERROR` | 400 | Request validation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `LLM_SERVICE_ERROR` | 503 | AI service temporarily unavailable |
| `LMS_SYNC_ERROR` | 502 | Error connecting to LMS |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## 📈 Rate Limits

| Endpoint Type | Rate Limit |
|---------------|------------|
| Chat Messages | 60 requests/minute per user |
| Product Queries | 100 requests/minute per user |
| Analytics | 30 requests/minute per user |
| CMS Uploads | 10 requests/hour per admin |
| Webhooks | 1000 requests/minute total |

---

## 🔒 Security Headers

All responses include:

```
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

---

## 📞 Support

**Technical Support:** api-support@salesbuddy.hyundai.co.in  
**Documentation:** https://docs.salesbuddy.hyundai.co.in  
**Status Page:** https://status.salesbuddy.hyundai.co.in

---
