# MongoDB Schema for Petrol Pump Analytics

## Overview

This document defines the MongoDB schema for petrol pump video analytics, adapted from the ClickHouse `video_analytics_logs` schema. The schema is optimized for document-based storage, leveraging MongoDB's native support for nested objects and arrays.

---

## Schema Definition

```javascript
// Collection: petrol_pump_analytics

const mongoose = require('mongoose');

const DetectionSchema = new mongoose.Schema({
  class_id: { type: Number, min: 0, max: 255 },
  label: { type: String, index: true },
  confidence: { type: Number, min: 0, max: 1 },
  bbox: {
    left: Number,
    top: Number,
    width: Number,
    height: Number
  },
  object_id: Number
}, { _id: false });

const RecognitionSchema = new mongoose.Schema({
  identity: { type: String, default: 'Stranger' },
  confidence: { type: Number, min: 0, max: 1 },
  identity_id: Number
}, { _id: false });

const PetrolPumpAnalyticsSchema = new mongoose.Schema({
  // ========== PRIMARY IDENTIFIERS ==========
  event_id: { 
    type: String, 
    default: () => new mongoose.Types.UUID().toString(),
    unique: true,
    index: true
  },
  cam_id: { type: Number, required: true, index: true },
  cam_name: { type: String, required: true },
  site_name: { type: String, required: true, index: true },
  site_id: { type: String, required: true },

  // ========== GEO-LOCATION ==========
  location: {
    type: { type: String, enum: ['Point'], default: 'Point' },
    coordinates: { type: [Number], default: [0, 0] } // [longitude, latitude]
  },
  address: {
    country: { type: String, default: 'India' },
    state: String,
    district: String,
    city: String,
    pincode: String
  },

  // ========== EVENT METRICS ==========
  detection_count: { type: Number, default: 0 },
  people_count: { type: Number, default: 0 },
  vehicle_count: { type: Number, default: 0 },

  // ========== PETROL PUMP SPECIFIC METRICS ==========
  pump_metrics: {
    nozzle_in_use: { type: Boolean, default: false },
    fuel_type: { type: String, enum: ['petrol', 'diesel', 'cng', null], default: null },
    pump_number: Number,
    queue_length: { type: Number, default: 0 },
    transaction_active: { type: Boolean, default: false }
  },

  // ========== EVENT CLASSIFICATION ==========
  event_type: { 
    type: String, 
    enum: ['metric', 'event', 'ai-info'],
    required: true,
    index: true
  },
  event_status: { 
    type: String, 
    enum: ['safe', 'warning', 'critical', 'emergency', 'triaged'],
    default: 'safe',
    index: true
  },

  // ========== FLAGS AND TIMESTAMPS ==========
  capture_triggered: { type: Boolean, default: false },
  processed_at: { type: Date, default: Date.now },
  event_timestamp: { type: Date, required: true, index: true },

  // ========== DETECTIONS (Nested Array) ==========
  detections: [DetectionSchema],

  // ========== PETROL PUMP SPECIFIC TRIGGERS ==========
  event_triggers: [{
    type: String,
    enum: [
      // Safety Triggers
      'SMOKING_DETECTED',
      'FIRE_DETECTED',
      'SMOKE_DETECTED',
      'ENGINE_RUNNING',
      'MOBILE_PHONE_USE',
      
      // Operational Triggers
      'NOZZLE_ON_GROUND',
      'FUEL_SPILLAGE',
      'UNAUTHORIZED_ACCESS',
      'CROWD_DETECTED',
      
      // Customer Behavior
      'CHILD_AT_PUMP',
      'ELDERLY_ASSISTANCE_NEEDED',
      'CUSTOMER_WAITING_LONG',
      
      // Vehicle Related
      'WRONG_SIDE_PARKING',
      'VEHICLE_TOO_CLOSE',
      'LICENSE_PLATE_CAPTURED',
      
      // Employee Monitoring
      'EMPLOYEE_ABSENT',
      'UNIFORM_VIOLATION',
      'SAFETY_GEAR_MISSING'
    ]
  }],

  // ========== TRIAGE AND AI ==========
  triage: {
    triaged_by: String,
    notes: String,
    timestamp: Date,
    action_taken: String
  },
  ai_insights: String,
  evidence: {
    image_path: String,
    video_path: String,
    thumbnail_path: String
  },

  // ========== RECOGNITION DATA ==========
  display_labels: [String],
  recognitions: [RecognitionSchema],

  // ========== AUTO-CALCULATED (Virtual Fields) ==========
  // These are computed at query time or via aggregation

}, {
  timestamps: true,
  collection: 'petrol_pump_analytics'
});

// ========== INDEXES ==========
PetrolPumpAnalyticsSchema.index({ site_name: 1, cam_id: 1, event_timestamp: -1 });
PetrolPumpAnalyticsSchema.index({ event_status: 1, event_timestamp: -1 });
PetrolPumpAnalyticsSchema.index({ 'location': '2dsphere' });
PetrolPumpAnalyticsSchema.index({ event_triggers: 1 });
PetrolPumpAnalyticsSchema.index({ 'pump_metrics.pump_number': 1 });

// ========== VIRTUALS ==========
PetrolPumpAnalyticsSchema.virtual('event_trigger_count').get(function() {
  return this.event_triggers ? this.event_triggers.length : 0;
});

PetrolPumpAnalyticsSchema.virtual('high_confidence_count').get(function() {
  if (!this.detections) return 0;
  return this.detections.filter(d => d.confidence > 0.7).length;
});

module.exports = mongoose.model('PetrolPumpAnalytics', PetrolPumpAnalyticsSchema);
```

---

## Column Descriptions

### Primary Identifiers

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | UUID String | Unique event identifier (auto-generated) |
| `cam_id` | Number | Camera identifier (0-65535) |
| `cam_name` | String | Human-readable camera name (e.g., "Pump Bay 1 - Front") |
| `site_name` | String | Site/location name (e.g., "HP Petrol Pump - Andheri") |
| `site_id` | String | Unique site identifier |

### Geo-Location

| Field | Type | Description |
|-------|------|-------------|
| `location.coordinates` | [Number] | GeoJSON format [longitude, latitude] for geo-queries |
| `address.country` | String | Country name (default: "India") |
| `address.state` | String | State/Province name |
| `address.district` | String | District name |
| `address.city` | String | City name |
| `address.pincode` | String | Postal code |

### Event Metrics

| Field | Type | Description |
|-------|------|-------------|
| `detection_count` | Number | Total count of object detections in the frame |
| `people_count` | Number | Count of people detected |
| `vehicle_count` | Number | Count of vehicles detected |

### Petrol Pump Specific Metrics

| Field | Type | Description |
|-------|------|-------------|
| `pump_metrics.nozzle_in_use` | Boolean | Whether fuel nozzle is currently dispensing |
| `pump_metrics.fuel_type` | String | Type of fuel being dispensed |
| `pump_metrics.pump_number` | Number | Pump station number (1, 2, 3...) |
| `pump_metrics.queue_length` | Number | Number of vehicles waiting |
| `pump_metrics.transaction_active` | Boolean | Whether a fuel transaction is in progress |

### Event Classification

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | Enum | Classification: `metric`, `event`, `ai-info` |
| `event_status` | Enum | Severity: `safe`, `warning`, `critical`, `emergency`, `triaged` |

### Event Triggers (Petrol Pump Specific)

| Trigger | Category | Description |
|---------|----------|-------------|
| `SMOKING_DETECTED` | Safety | Person smoking near pump area |
| `FIRE_DETECTED` | Safety | Fire/flames detected |
| `SMOKE_DETECTED` | Safety | Smoke detected (possible fire) |
| `ENGINE_RUNNING` | Safety | Vehicle engine running during fueling |
| `MOBILE_PHONE_USE` | Safety | Customer using mobile phone at pump |
| `NOZZLE_ON_GROUND` | Operational | Fuel nozzle dropped/left on ground |
| `FUEL_SPILLAGE` | Operational | Fuel spill detected |
| `UNAUTHORIZED_ACCESS` | Operational | Person in restricted area |
| `CROWD_DETECTED` | Operational | Unusual crowd gathering |
| `CHILD_AT_PUMP` | Customer | Child near fueling area |
| `WRONG_SIDE_PARKING` | Vehicle | Vehicle parked on wrong side |
| `EMPLOYEE_ABSENT` | Employee | No attendant at pump |
| `UNIFORM_VIOLATION` | Employee | Attendant not in proper uniform |

### Detections Array

| Field | Type | Description |
|-------|------|-------------|
| `detections[].class_id` | Number | YOLO class ID (0-255) |
| `detections[].label` | String | Detection label (e.g., "person", "car", "nozzle") |
| `detections[].confidence` | Float | Detection confidence (0.0 - 1.0) |
| `detections[].bbox` | Object | Bounding box coordinates |
| `detections[].object_id` | Number | Object tracking ID |

### Recognition Data

| Field | Type | Description |
|-------|------|-------------|
| `recognitions[].identity` | String | Recognized identity (e.g., "Employee - Rajesh", "Stranger") |
| `recognitions[].confidence` | Float | Recognition confidence score |
| `recognitions[].identity_id` | Number | Database ID of recognized person |

---

## Data Mapping Notes

1. **Nested Objects**: Unlike ClickHouse's flattened arrays, MongoDB uses proper nested objects for `detections` and `recognitions`.

2. **GeoJSON**: Location uses GeoJSON `Point` format for MongoDB's geospatial queries.

3. **Timestamps**: Uses proper `Date` type instead of UInt16 (fixing the overflow issue).

4. **Enums**: Implemented as String with validation, more flexible than ClickHouse Enums.

5. **Indexes**: Compound indexes optimized for common query patterns:
   - Site + Camera + Time queries
   - Event status filtering
   - Geospatial queries
   - Trigger-based queries

---

## Sample Queries

```javascript
// Find all critical events at a site in last 24 hours
db.petrol_pump_analytics.find({
  site_name: "HP Petrol Pump - Andheri",
  event_status: { $in: ['critical', 'emergency'] },
  event_timestamp: { $gte: new Date(Date.now() - 24*60*60*1000) }
}).sort({ event_timestamp: -1 });

// Find smoking incidents near a location
db.petrol_pump_analytics.find({
  event_triggers: 'SMOKING_DETECTED',
  location: {
    $near: {
      $geometry: { type: "Point", coordinates: [72.8777, 19.0760] },
      $maxDistance: 5000
    }
  }
});

// Aggregation: Events by pump number
db.petrol_pump_analytics.aggregate([
  { $match: { event_timestamp: { $gte: new Date("2026-01-01") } } },
  { $group: { 
    _id: "$pump_metrics.pump_number",
    total_events: { $sum: 1 },
    critical_events: { 
      $sum: { $cond: [{ $in: ["$event_status", ["critical", "emergency"]] }, 1, 0] }
    }
  }}
]);
```
