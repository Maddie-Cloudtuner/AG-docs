# ClickHouse Schema Documentation

## Table: `camera_events`

This table stores event and metric data from camera feeds, enriched with metadata, recognition details, and triage information.

### Schema Definition

```sql
CREATE TABLE IF NOT EXISTS camera_events (
    -- Primary identifiers
    event_id UUID DEFAULT generateUUIDv4(),
    cam_id UInt16,
    cam_name LowCardinality(String),
    site_name LowCardinality(String),
    site_id String,

    -- Geo-Location
    latitude Float64 DEFAULT 0,
    longitude Float64 DEFAULT 0,
    country LowCardinality(String),
    state LowCardinality(String),
    district LowCardinality(String),

    -- Event metrics
    detection_count UInt16 DEFAULT 0,
    people_count UInt16 DEFAULT 0,

    -- Event classification
    event_type Enum8('metric' = 1, 'event' = 2, 'ai-info'=3),
    event_status Enum8('safe' = 1, 'warning' = 2, 'critical' = 3, 'emergency' = 4, 'triaged' = 5),

    -- Flags and timestamps
    capture_triggered Bool DEFAULT false,
    processed_at UInt16,
    event_timestamp UInt16,

    -- Nested detection arrays
    `detections.class_id` Array(UInt8) DEFAULT [],
    `detections.label` Array(LowCardinality(String)) DEFAULT [],
    `detections.confidence` Array(Float32) DEFAULT [],
    `detections.bbox_left` Array(UInt16) DEFAULT [],
    `detections.bbox_top` Array(UInt16) DEFAULT [],
    `detections.bbox_width` Array(UInt16) DEFAULT [],
    `detections.bbox_height` Array(UInt16) DEFAULT [],
    `detections.object_id` Array(UInt16) DEFAULT [],

    -- Event triggers
    event_triggers Array(LowCardinality(String)) DEFAULT [],

    -- Triage and AI
    triaged_by LowCardinality(String),
    triage_notes String,
    triage_timestamp UInt16,
    ai_insights String,
    evidence_path String,

    -- Recognition Data
    display_label Array(LowCardinality(String)) DEFAULT [],
    `recognition.identity` Array(LowCardinality(String)) DEFAULT [],
    `recognition.confidence` Array(Float32) DEFAULT [],
    `recognition.identity_id` Array(UInt32) DEFAULT [],

    -- Auto-calculated columns
    event_trigger_count UInt8 DEFAULT length(event_triggers),
    high_confidence_count UInt16 DEFAULT arrayCount(x -> x > 0.7, `detections.confidence`),

    -- Indexes
    INDEX idx_cam_id cam_id TYPE minmax GRANULARITY 4,
    INDEX idx_event_status event_status TYPE set(4) GRANULARITY 4,
    INDEX idx_site_name site_name TYPE bloom_filter(0.01) GRANULARITY 4,
    INDEX idx_cam_name cam_name TYPE bloom_filter(0.01) GRANULARITY 4

) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(toDateTime(event_timestamp))
ORDER BY (site_name, cam_id, event_timestamp, event_id)
SETTINGS index_granularity = 8192
```

### Column Descriptions

| Column Name               | Type                            | Description                                                                          |
| :------------------------ | :------------------------------ | :----------------------------------------------------------------------------------- |
| `event_id`                | `UUID`                          | Unique event identifier (PK).                                                        |
| `cam_id`                  | `UInt16`                        | Camera identifier (PK). **Note**: Input strings are cast to int; default 0.          |
| `cam_name`                | `LowCardinality(String)`        | Human-readable camera name.                                                          |
| `site_name`               | `LowCardinality(String)`        | Site/location name (PK).                                                             |
| `site_id`                 | `String`                        | Unique site identifier.                                                              |
| `latitude`                | `Float64`                       | GPS Latitude.                                                                        |
| `longitude`               | `Float64`                       | GPS Longitude.                                                                       |
| `country`                 | `LowCardinality(String)`        | Country name.                                                                        |
| `state`                   | `LowCardinality(String)`        | State/Province name.                                                                 |
| `district`                | `LowCardinality(String)`        | District/City name.                                                                  |
| `detection_count`         | `UInt16`                        | Total count of object detections in the frame.                                       |
| `people_count`            | `UInt16`                        | Count of people detected.                                                            |
| `video_count`             | `UInt16`                        | Number of videos captured (e.g., clips associated with event).                       |
| `image_count`             | `UInt16`                        | Number of images captured (e.g., snapshots associated with event).                   |
| `event_type`              | `Enum8`                         | Classification: `metric` (1), `event` (2), `ai-info` (3).                            |
| `event_status`            | `Enum8`                         | Severity: `safe` (1), `warning` (2), `critical` (3), `emergency` (4), `triaged` (5). |
| `capture_triggered`       | `Bool`                          | Whether an image/video capture was triggered.                                        |
| `processed_at`            | `UInt16`                        | Timestamp when the event was processed by the API.                                   |
| `event_timestamp`         | `UInt16`                        | Unix timestamp of the event occurrence (Partition Key).                              |
| `detections.*`            | `Array`                         | Flattened arrays representing object detections.                                     |
| `detections.object_id`    | `Array(UInt16)`                 | Tracking IDs for detected objects.                                                   |
| `event_triggers`          | `Array(LowCardinality(String))` | List of specific triggers fired (e.g., "UNAUTHORIZED_ACCESS").                       |
| `triaged_by`              | `LowCardinality(String)`        | User ID/Name who triaged the event.                                                  |
| `triage_notes`            | `String`                        | Manual notes added during triage.                                                    |
| `triage_timestamp`        | `UInt16`                        | Timestamp when triage occurred.                                                      |
| `ai_insights`             | `String`                        | AI-generated summary or insights about the event.                                    |
| `evidence_path`           | `String`                        | File path/URL to evidence (image/video).                                             |
| `display_label`           | `Array(LowCardinality(String))` | Label to display on UI for each detection.                                           |
| `recognition.identity`    | `Array(LowCardinality(String))` | Identity recognized (e.g., "Stranger", "John Doe").                                  |
| `recognition.confidence`  | `Array(Float32)`                | Confidence score of the face recognition.                                            |
| `recognition.identity_id` | `Array(UInt32)`                 | ID associated with the recognized identity.                                          |

### Data Mapping Notes

- **Enums**: `event_type` and `event_status` are stored as Enums. The API automatically lowercases input strings to match these values.
- **Timestamps**: Stored as `UInt16`. **Warning**: `UInt16` max value is 65,535. This seems to be a legacy schema constraint; standard Unix timestamps (e.g., 1700000000) will overflow `UInt16`. _Please verify if `UInt32` was intended in the actual live database if this is a new deployment._
- **Arrays**: Nested JSON objects (like `detections`) are flattened into parallel arrays (e.g., `detections[i]` properties correspond to `detections.label[i]`, `detections.confidence[i]`, etc.).

### Partitioning & Sorting

- **Partition Key**: `toYYYYMMDD(toDateTime(event_timestamp))` - Data is partitioned by day.
- **Ordering**: `(site_name, cam_id, event_timestamp, event_id)` - Optimized for querying events by site and camera over time.
