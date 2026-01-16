/**
 * Dummy Data Generator for Petrol Pump Analytics
 * 
 * Run: node seed_dummy_data.js
 * Requires: mongoose, uuid
 */

const mongoose = require('mongoose');

// ==================== CONFIGURATION ====================
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/petrol_pump_analytics';
const NUM_RECORDS = 50;

// ==================== SAMPLE DATA POOLS ====================
const SITES = [
    { name: 'HP Petrol Pump - Andheri West', id: 'HP_ANW_001', coords: [72.8362, 19.1364], state: 'Maharashtra', district: 'Mumbai Suburban', city: 'Mumbai' },
    { name: 'Indian Oil - Connaught Place', id: 'IOCL_CP_002', coords: [77.2167, 28.6315], state: 'Delhi', district: 'New Delhi', city: 'New Delhi' },
    { name: 'BPCL PetroMax - Kormangala', id: 'BPCL_KR_003', coords: [77.6245, 12.9352], state: 'Karnataka', district: 'Bengaluru Urban', city: 'Bengaluru' },
    { name: 'Shell Fuel Station - Jubilee Hills', id: 'SHELL_JH_004', coords: [78.4106, 17.4326], state: 'Telangana', district: 'Hyderabad', city: 'Hyderabad' }
];

const CAMERAS = [
    { id: 1, name: 'Pump Bay 1 - Front View' },
    { id: 2, name: 'Pump Bay 2 - Front View' },
    { id: 3, name: 'Pump Bay 3 - Side View' },
    { id: 4, name: 'Entrance Gate - ANPR' },
    { id: 5, name: 'Exit Gate - ANPR' },
    { id: 6, name: 'Office Counter' },
    { id: 7, name: 'Fuel Storage Area' },
    { id: 8, name: 'Parking Lot - Overview' }
];

const LABELS = ['person', 'car', 'motorcycle', 'truck', 'nozzle', 'fire_extinguisher', 'mobile_phone', 'cigarette', 'license_plate'];

const TRIGGERS = [
    'SMOKING_DETECTED', 'MOBILE_PHONE_USE', 'ENGINE_RUNNING', 'NOZZLE_ON_GROUND',
    'CHILD_AT_PUMP', 'WRONG_SIDE_PARKING', 'LICENSE_PLATE_CAPTURED', 'CROWD_DETECTED',
    'EMPLOYEE_ABSENT', 'CUSTOMER_WAITING_LONG'
];

const EMPLOYEES = ['Rajesh Kumar', 'Amit Singh', 'Priya Sharma', 'Suresh Patel', 'Neha Gupta'];
const IDENTITIES = ['Stranger', 'Employee - Rajesh', 'Employee - Amit', 'Regular Customer #127', 'VIP Customer - Mr. Sharma'];

// ==================== HELPER FUNCTIONS ====================
const randomChoice = (arr) => arr[Math.floor(Math.random() * arr.length)];
const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
const randomFloat = (min, max) => Math.random() * (max - min) + min;

function generateDetections(count) {
    const detections = [];
    for (let i = 0; i < count; i++) {
        detections.push({
            class_id: randomInt(0, 17),
            label: randomChoice(LABELS),
            confidence: randomFloat(0.5, 0.99),
            bbox: {
                left: randomInt(0, 1920),
                top: randomInt(0, 1080),
                width: randomInt(50, 300),
                height: randomInt(50, 400)
            },
            object_id: randomInt(1, 999)
        });
    }
    return detections;
}

function generateRecognitions(count) {
    const recognitions = [];
    for (let i = 0; i < count; i++) {
        recognitions.push({
            identity: randomChoice(IDENTITIES),
            confidence: randomFloat(0.7, 0.99),
            identity_id: randomInt(100, 9999)
        });
    }
    return recognitions;
}

function generateTriggers() {
    const triggerCount = randomInt(0, 3);
    const triggers = [];
    for (let i = 0; i < triggerCount; i++) {
        const trigger = randomChoice(TRIGGERS);
        if (!triggers.includes(trigger)) triggers.push(trigger);
    }
    return triggers;
}

function generateRecord(index) {
    const site = randomChoice(SITES);
    const camera = randomChoice(CAMERAS);
    const triggers = generateTriggers();
    const detectionCount = randomInt(1, 8);
    const peopleCount = randomInt(0, 5);

    // Determine event status based on triggers
    let eventStatus = 'safe';
    if (triggers.includes('SMOKING_DETECTED') || triggers.includes('FIRE_DETECTED')) {
        eventStatus = 'critical';
    } else if (triggers.includes('MOBILE_PHONE_USE') || triggers.includes('ENGINE_RUNNING')) {
        eventStatus = 'warning';
    } else if (triggers.length > 0) {
        eventStatus = randomChoice(['safe', 'warning']);
    }

    const eventTimestamp = new Date(Date.now() - randomInt(0, 7 * 24 * 60 * 60 * 1000)); // Last 7 days

    return {
        cam_id: camera.id,
        cam_name: camera.name,
        site_name: site.name,
        site_id: site.id,

        location: {
            type: 'Point',
            coordinates: site.coords
        },
        address: {
            country: 'India',
            state: site.state,
            district: site.district,
            city: site.city,
            pincode: String(randomInt(100000, 999999))
        },

        detection_count: detectionCount,
        people_count: peopleCount,
        vehicle_count: randomInt(0, 4),

        pump_metrics: {
            nozzle_in_use: Math.random() > 0.5,
            fuel_type: randomChoice(['petrol', 'diesel', 'cng', null]),
            pump_number: randomInt(1, 6),
            queue_length: randomInt(0, 5),
            transaction_active: Math.random() > 0.4
        },

        event_type: randomChoice(['metric', 'event', 'ai-info']),
        event_status: eventStatus,

        capture_triggered: triggers.length > 0,
        processed_at: new Date(),
        event_timestamp: eventTimestamp,

        detections: generateDetections(detectionCount),
        event_triggers: triggers,

        triage: triggers.length > 0 && Math.random() > 0.7 ? {
            triaged_by: randomChoice(EMPLOYEES),
            notes: 'Reviewed and marked as false positive',
            timestamp: new Date(),
            action_taken: 'No action required'
        } : undefined,

        ai_insights: triggers.length > 0 ? `Detected ${triggers.length} potential safety concern(s). Confidence: ${randomFloat(0.7, 0.95).toFixed(2)}` : null,

        evidence: triggers.length > 0 ? {
            image_path: `/evidence/${site.id}/img_${Date.now()}.jpg`,
            video_path: `/evidence/${site.id}/clip_${Date.now()}.mp4`,
            thumbnail_path: `/evidence/${site.id}/thumb_${Date.now()}.jpg`
        } : undefined,

        display_labels: generateDetections(peopleCount).map(d => d.label),
        recognitions: generateRecognitions(Math.min(peopleCount, 3))
    };
}

// ==================== MAIN EXECUTION ====================
async function seedDatabase() {
    try {
        console.log('🔌 Connecting to MongoDB...');
        await mongoose.connect(MONGODB_URI);
        console.log('✅ Connected to MongoDB');

        // Define schema inline for seeding
        const PetrolPumpAnalytics = mongoose.model('PetrolPumpAnalytics', new mongoose.Schema({}, { strict: false, collection: 'petrol_pump_analytics' }));

        console.log(`📝 Generating ${NUM_RECORDS} dummy records...`);
        const records = [];
        for (let i = 0; i < NUM_RECORDS; i++) {
            records.push(generateRecord(i));
        }

        console.log('💾 Inserting records into database...');
        await PetrolPumpAnalytics.insertMany(records);

        console.log(`✅ Successfully inserted ${NUM_RECORDS} records!`);

        // Print sample record
        console.log('\n📋 Sample Record:');
        console.log(JSON.stringify(records[0], null, 2));

    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        await mongoose.disconnect();
        console.log('\n🔌 Disconnected from MongoDB');
    }
}

// Run if executed directly
if (require.main === module) {
    seedDatabase();
}

module.exports = { generateRecord, seedDatabase };
