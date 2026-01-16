/**
 * Petrol Pump Analytics - MongoDB Schema (Mongoose Model)
 * 
 * Collection: petrol_pump_analytics
 * Optimized for video analytics data from petrol pump CCTV cameras
 */

const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

// ==================== SUB-SCHEMAS ====================

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

const PumpMetricsSchema = new mongoose.Schema({
    nozzle_in_use: { type: Boolean, default: false },
    fuel_type: { type: String, enum: ['petrol', 'diesel', 'cng', null], default: null },
    pump_number: Number,
    queue_length: { type: Number, default: 0 },
    transaction_active: { type: Boolean, default: false }
}, { _id: false });

const AddressSchema = new mongoose.Schema({
    country: { type: String, default: 'India' },
    state: String,
    district: String,
    city: String,
    pincode: String
}, { _id: false });

const TriageSchema = new mongoose.Schema({
    triaged_by: String,
    notes: String,
    timestamp: Date,
    action_taken: String
}, { _id: false });

const EvidenceSchema = new mongoose.Schema({
    image_path: String,
    video_path: String,
    thumbnail_path: String
}, { _id: false });

// ==================== MAIN SCHEMA ====================

const PetrolPumpAnalyticsSchema = new mongoose.Schema({
    // Primary Identifiers
    event_id: {
        type: String,
        default: () => uuidv4(),
        unique: true,
        index: true
    },
    cam_id: { type: Number, required: true, index: true },
    cam_name: { type: String, required: true },
    site_name: { type: String, required: true, index: true },
    site_id: { type: String, required: true },

    // Geo-Location (GeoJSON)
    location: {
        type: { type: String, enum: ['Point'], default: 'Point' },
        coordinates: { type: [Number], default: [0, 0] } // [longitude, latitude]
    },
    address: AddressSchema,

    // Event Metrics
    detection_count: { type: Number, default: 0 },
    people_count: { type: Number, default: 0 },
    vehicle_count: { type: Number, default: 0 },

    // Petrol Pump Specific Metrics
    pump_metrics: PumpMetricsSchema,

    // Event Classification
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

    // Flags and Timestamps
    capture_triggered: { type: Boolean, default: false },
    processed_at: { type: Date, default: Date.now },
    event_timestamp: { type: Date, required: true, index: true },

    // Detections (Nested Array)
    detections: [DetectionSchema],

    // Event Triggers
    event_triggers: [{
        type: String,
        enum: [
            'SMOKING_DETECTED', 'FIRE_DETECTED', 'SMOKE_DETECTED',
            'ENGINE_RUNNING', 'MOBILE_PHONE_USE',
            'NOZZLE_ON_GROUND', 'FUEL_SPILLAGE', 'UNAUTHORIZED_ACCESS', 'CROWD_DETECTED',
            'CHILD_AT_PUMP', 'ELDERLY_ASSISTANCE_NEEDED', 'CUSTOMER_WAITING_LONG',
            'WRONG_SIDE_PARKING', 'VEHICLE_TOO_CLOSE', 'LICENSE_PLATE_CAPTURED',
            'EMPLOYEE_ABSENT', 'UNIFORM_VIOLATION', 'SAFETY_GEAR_MISSING'
        ]
    }],

    // Triage and AI
    triage: TriageSchema,
    ai_insights: String,
    evidence: EvidenceSchema,

    // Recognition Data
    display_labels: [String],
    recognitions: [RecognitionSchema]

}, {
    timestamps: true,
    collection: 'petrol_pump_analytics'
});

// ==================== INDEXES ====================
PetrolPumpAnalyticsSchema.index({ site_name: 1, cam_id: 1, event_timestamp: -1 });
PetrolPumpAnalyticsSchema.index({ event_status: 1, event_timestamp: -1 });
PetrolPumpAnalyticsSchema.index({ 'location': '2dsphere' });
PetrolPumpAnalyticsSchema.index({ event_triggers: 1 });
PetrolPumpAnalyticsSchema.index({ 'pump_metrics.pump_number': 1 });

// ==================== VIRTUALS ====================
PetrolPumpAnalyticsSchema.virtual('event_trigger_count').get(function () {
    return this.event_triggers ? this.event_triggers.length : 0;
});

PetrolPumpAnalyticsSchema.virtual('high_confidence_count').get(function () {
    if (!this.detections) return 0;
    return this.detections.filter(d => d.confidence > 0.7).length;
});

// Ensure virtuals are included in JSON output
PetrolPumpAnalyticsSchema.set('toJSON', { virtuals: true });
PetrolPumpAnalyticsSchema.set('toObject', { virtuals: true });

// ==================== EXPORT ====================
module.exports = mongoose.model('PetrolPumpAnalytics', PetrolPumpAnalyticsSchema);
