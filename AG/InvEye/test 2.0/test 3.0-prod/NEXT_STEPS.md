# Next Steps for Developer

## Files in Handoff

| File | Purpose |
|------|---------|
| `API_REFERENCE.md` | 2 API endpoints with request/response |
| `heatmap_v2.html` | Frontend with date filter (ready to use) |
| `schema_doc.md` | Existing ClickHouse schema reference |

---

## Implementation Checklist

### Phase 1: Zone Dashboard
- [ ] Implement `GET /api/v1/dashboard/{site_name}?date=`
- [ ] Test with existing `camera_events` data
- [ ] Connect `heatmap_v2.html` to API

### Phase 2: Spatial Heatmap
- [ ] Create materialized view `mv_spatial_density` (optional, for perf)
- [ ] Implement `GET /api/v1/heatmap/{site}/{cam}?date=`
- [ ] Add spatial canvas renderer to frontend

### Phase 3: Person Deduplication (Future)
- [ ] Use `detections.object_id` for frame-level tracking
- [ ] Use `recognition.identity_id` for cross-camera Re-ID
- [ ] Change `count()` to `uniqExact(object_id)`

---

## Key Schema Columns

```
camera_events:
  ├── site_name          → Site filter
  ├── cam_name           → Zone/camera identifier
  ├── people_count       → Peak occupancy
  ├── event_timestamp    → Date filter
  ├── event_triggers[]   → Critical events
  └── detections.*       → BBox arrays for spatial heatmap
      ├── bbox_left[]
      ├── bbox_top[]
      ├── bbox_width[]
      ├── bbox_height[]
      └── object_id[]    → For deduplication
```

---

## Frontend Config

In `heatmap_v2.html`, update:
```javascript
const CONFIG = {
    API_BASE_URL: 'https://your-api.com/api/v1',
    SITE_ID: 'HEAD_OFFICE'  // Must match site_name in DB
};
```

---

## Questions?

Contact: [Your Team Contact]
