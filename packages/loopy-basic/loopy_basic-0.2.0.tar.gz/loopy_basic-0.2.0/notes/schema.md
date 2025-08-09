# Database Schema Documentation

This document provides information about the MongoDB database schema used in the Loopy Basic project.

## Database: myCGMitc

The `myCGMitc` database contains the following collections:

- **`entries`** - CGM/blood glucose readings (primary data for analysis)
- **`treatments`** - Insulin doses and medical treatments
- **`food`** - Food intake and carbohydrate data
- **`settings`** - Loop system configuration
- **`devicestatus`** - Device status and connectivity info
- **`profile`** - User profile and basal rate settings
- **`activity`** - Activity and exercise logs
- **`auth_roles`**, **`auth_subjects`** - Authentication data

## `entries` Collection Schema (CGM Data)

**Collection Stats:**
- Total documents: 243,047 CGM readings
- Date range: March 2023 to July 2025 (~2 years of data)
- Device: Dexcom CGM ("share2")
- Data actively updated (real-time)

**Document Structure:**
```json
{
  "_id": "ObjectId",
  "sgv": 163,                           // Blood glucose value (mg/dL)
  "date": 1678724324000.0,             // Unix timestamp (milliseconds)
  "dateString": "2023-03-13T16:18:44.000Z",  // ISO formatted date
  "trend": 4,                          // Glucose trend indicator (1-7)
  "direction": "Flat",                 // Trend direction text
  "device": "share2",                  // CGM device identifier
  "type": "sgv",                       // Sensor glucose value type
  "utcOffset": 0,                      // UTC offset
  "sysTime": "2023-03-13T16:18:44.000Z"  // System timestamp
}
```

**Key Fields:**
- **`sgv`** - Primary glucose reading in mg/dL
- **`date`** - Unix timestamp for sorting and time-based queries
- **`direction`** - Trend indicators: "Flat", "FortyFiveUp", "FortyFiveDown", "SingleUp", "SingleDown", "DoubleUp", "DoubleDown"
- **`trend`** - Numeric trend value (1-7 scale)

**Database Indexes:**
- Optimized indexes on `date`, `sgv`, `dateString`, `type` for efficient queries