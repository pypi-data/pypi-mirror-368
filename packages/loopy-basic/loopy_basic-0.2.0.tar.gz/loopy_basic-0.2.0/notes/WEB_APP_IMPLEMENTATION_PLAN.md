# Web-Based CGM Data Display Implementation Plan

## Project Overview

Create a **DIY web-based diabetes monitoring application** similar to Nightscout, built on the `loopy-basic` package. This is designed for technically-minded Loop users who have their own MongoDB database and can configure their own Atlas credentials.

**MVP Approach**: Start with a single-user prototype for personal use, with potential for multi-user expansion later.

## 📋 Implementation Guides

This plan has been split into focused implementation guides for each repository:

- **[LOOPY_API_IMPLEMENTATION.md](./LOOPY_API_IMPLEMENTATION.md)** - Complete backend API implementation guide
- **[LOOPY_WEB_IMPLEMENTATION.md](./LOOPY_WEB_IMPLEMENTATION.md)** - Complete frontend web application guide

## Quick Start

1. **Publish loopy-basic to PyPI** (see below)
2. **Backend**: Follow [LOOPY_API_IMPLEMENTATION.md](./LOOPY_API_IMPLEMENTATION.md)
3. **Frontend**: Follow [LOOPY_WEB_IMPLEMENTATION.md](./LOOPY_WEB_IMPLEMENTATION.md)

## Architecture Decision: Separate Repositories

### Repository Structure

**1. Backend Repository: `loopy-api`**
- FastAPI application
- Uses loopy-basic package for data access
- Provides REST API for CGM data
- No user management initially (MVP)

**2. Frontend Repository: `loopy-web`** 
- React + TypeScript application
- Consumes backend API
- Focuses on visualization and user experience

**3. Core Package: `loopy-basic` (existing)**
- Published to PyPI
- Handles all MongoDB data access
- Shared between projects

### Recommended Tech Stack

**Backend: FastAPI**
- ✅ **Simple deployment** - Single Docker container
- ✅ **Auto-generated docs** - Built-in OpenAPI/Swagger
- ✅ **Type safety** - Leverages loopy-basic type hints
- ✅ **Environment-based config** - MongoDB credentials via env vars
- ✅ **Minimal complexity** - No user database needed for MVP

**Frontend: React + TypeScript**
- ✅ **Modern UI** - Component-based, responsive design
- ✅ **Rich visualizations** - Plotly.js for Nightscout-style charts
- ✅ **Type safety** - TypeScript for robust development
- ✅ **Static hosting** - Can be deployed to Netlify/Vercel
- ✅ **Mobile-friendly** - PWA capabilities

**Configuration Approach**
- ✅ **Environment variables** - MongoDB credentials in backend .env
- ✅ **No permanent storage** - No user accounts to manage
- ✅ **DIY setup** - Users configure their own MongoDB Atlas

## Project Structure

### Backend Repository: `loopy-api`
```
loopy-api/
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app entry point
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   ├── cgm.py            # CGM data endpoints
│   │   └── health.py         # Health check endpoints
│   ├── core/                  # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py         # Environment configuration
│   │   └── cors.py           # CORS settings
│   ├── models/                # Pydantic response models
│   │   ├── __init__.py
│   │   └── cgm.py            # CGM data models
│   └── services/              # Business logic
│       ├── __init__.py
│       └── cgm_service.py    # Uses loopy-basic package
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example              # Example environment variables
└── README.md                 # Setup instructions
```

### Frontend Repository: `loopy-web`
```
loopy-web/
├── public/
├── src/
│   ├── components/           # Reusable components
│   │   ├── CGMChart.tsx     # Main glucose chart (Nightscout-style)
│   │   ├── StatsCards.tsx   # Time in range cards
│   │   ├── CurrentGlucose.tsx # Current reading display
│   │   └── TrendArrow.tsx   # Glucose trend indicators
│   ├── pages/               # Main pages
│   │   ├── Dashboard.tsx    # Main dashboard
│   │   └── Setup.tsx        # Configuration help page
│   ├── services/            # API communication
│   │   ├── api.ts           # Backend API client
│   │   └── types.ts         # TypeScript types
│   ├── hooks/               # Custom React hooks
│   │   ├── useCGMData.ts    # CGM data fetching
│   │   └── useRealTime.ts   # Real-time updates
│   └── utils/               # Utility functions
│       ├── glucose.ts       # Glucose calculations
│       └── time.ts          # Time formatting
├── package.json
├── tsconfig.json
├── .env.example             # API endpoint configuration
└── README.md                # User setup guide
```

## Implementation Phases

### Phase 1: MVP Backend Setup (Week 1)

#### 1.1 Create Backend Repository
```bash
# Create new repository: loopy-api
git init loopy-api
cd loopy-api

# Install dependencies
pip install fastapi uvicorn loopy-basic python-dotenv
# Or if loopy-basic isn't on PyPI yet:
pip install git+https://github.com/yourusername/loopy-basic.git
```

#### 1.2 Minimal FastAPI Backend

**app/main.py**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import cgm, health
from app.core.config import settings

app = FastAPI(
    title="CGM Dashboard API",
    description="Personal CGM data visualization API",
    version="1.0.0"
)

# CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(cgm.router, prefix="/api/cgm", tags=["cgm"])

@app.get("/")
async def root():
    return {"message": "CGM Dashboard API", "status": "running"}
```

**app/core/config.py**
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB connection (from environment variables)
    mongodb_username: str
    mongodb_password: str  
    mongodb_uri: str
    mongodb_database: str = "myCGMitc"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**app/services/cgm_service.py**
```python
from loopy.data.cgm import CGMDataAccess
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os

class CGMService:
    @staticmethod
    def get_cgm_data(hours: int = 24) -> Dict[str, Any]:
        """Get recent CGM data using environment-configured MongoDB connection."""
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Use loopy-basic with context manager
        # MongoDB connection details come from environment variables
        with CGMDataAccess() as cgm:
            df = cgm.get_dataframe_for_period('custom', start_time, end_time)
            
            if df.empty:
                return {
                    "data": [],
                    "analysis": None,
                    "message": "No data found for the specified period",
                    "last_updated": datetime.now().isoformat()
                }
            
            analysis = cgm.analyze_dataframe(df)
            
            # Convert DataFrame to JSON-serializable format
            data_records = df.to_dict('records')
            
            return {
                "data": data_records,
                "analysis": analysis,
                "last_updated": datetime.now().isoformat(),
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "hours": hours
                }
            }
    
    @staticmethod
    def get_current_glucose() -> Dict[str, Any]:
        """Get the most recent glucose reading."""
        
        with CGMDataAccess() as cgm:
            recent_readings = cgm.get_recent_readings(limit=1)
            
            if not recent_readings:
                return {"current_glucose": None, "message": "No recent data"}
            
            latest = recent_readings[0]
            return {
                "current_glucose": latest.get('sgv'),
                "direction": latest.get('direction'),
                "trend": latest.get('trend'),
                "timestamp": latest.get('dateString'),
                "minutes_ago": (datetime.now() - datetime.fromisoformat(latest.get('dateString').replace('Z', '+00:00'))).total_seconds() / 60
            }
```

#### 1.3 API Endpoints

**app/api/cgm.py**
```python
from fastapi import APIRouter, HTTPException, Query
from app.services.cgm_service import CGMService
from typing import Dict, Any

router = APIRouter()

@router.get("/data")
async def get_cgm_data(hours: int = Query(24, ge=1, le=168)) -> Dict[str, Any]:
    """Get CGM data for the specified number of hours (max 7 days)."""
    try:
        return CGMService.get_cgm_data(hours=hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving CGM data: {str(e)}")

@router.get("/current")
async def get_current_glucose() -> Dict[str, Any]:
    """Get the most recent glucose reading."""
    try:
        return CGMService.get_current_glucose()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving current glucose: {str(e)}")

@router.get("/status")
async def get_data_status() -> Dict[str, Any]:
    """Get data availability and connection status."""
    try:
        # Quick check with last hour of data
        result = CGMService.get_cgm_data(hours=1)
        return {
            "status": "connected" if result["data"] else "no_recent_data",
            "last_reading_count": len(result["data"]),
            "message": result.get("message", "Data available")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

**app/api/health.py**
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "cgm-dashboard-api"}
```

### Phase 2: MVP Frontend Setup (Week 2)

#### 2.1 Create Frontend Repository
```bash
# Create new repository: loopy-web  
npx create-react-app loopy-web --template typescript
cd loopy-web

# Install visualization and UI dependencies
npm install plotly.js react-plotly.js
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install axios
npm install date-fns  # for time formatting
```

#### 2.2 Environment Configuration

**.env.example**
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_PREFIX=/api
```

#### 2.3 Core Components

**src/components/CGMChart.tsx**
```typescript
import React from 'react';
import Plot from 'react-plotly.js';

interface CGMReading {
  datetime: string;
  sgv: number;
  direction: string;
}

interface CGMChartProps {
  data: CGMReading[];
  height?: number;
}

export const CGMChart: React.FC<CGMChartProps> = ({ data, height = 400 }) => {
  const trace = {
    x: data.map(d => d.datetime),
    y: data.map(d => d.sgv),
    type: 'scatter' as const,
    mode: 'lines+markers' as const,
    name: 'Glucose',
    line: { color: '#2196f3', width: 2 },
    marker: { size: 4 }
  };

  const layout = {
    title: {
      text: 'Continuous Glucose Monitor',
      font: { size: 18 }
    },
    xaxis: { 
      title: 'Time',
      type: 'date' as const
    },
    yaxis: { 
      title: 'Glucose (mg/dL)',
      range: [50, 400]
    },
    shapes: [
      // Target range shading (70-180 mg/dL)
      {
        type: 'rect' as const,
        xref: 'paper' as const,
        yref: 'y' as const,
        x0: 0,
        x1: 1,
        y0: 70,
        y1: 180,
        fillcolor: 'rgba(76, 175, 80, 0.1)',
        line: { width: 0 }
      },
      // High range line
      {
        type: 'line' as const,
        xref: 'paper' as const,
        yref: 'y' as const,
        x0: 0,
        x1: 1,
        y0: 180,
        y1: 180,
        line: { color: 'orange', width: 1, dash: 'dash' }
      }
    ],
    margin: { t: 50, b: 50, l: 50, r: 50 }
  };

  return (
    <Plot
      data={[trace]}
      layout={layout}
      style={{ width: '100%', height: `${height}px` }}
      config={{ responsive: true }}
    />
  );
};
```

**src/components/CurrentGlucose.tsx**
```typescript
import React from 'react';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';

interface CurrentGlucoseProps {
  glucose: number | null;
  direction: string;
  timestamp: string;
  minutesAgo: number;
}

export const CurrentGlucose: React.FC<CurrentGlucoseProps> = ({ 
  glucose, direction, timestamp, minutesAgo 
}) => {
  const getTrendIcon = () => {
    switch (direction) {
      case 'SingleUp':
      case 'DoubleUp':
      case 'FortyFiveUp':
        return <TrendingUp color="warning" />;
      case 'SingleDown':
      case 'DoubleDown': 
      case 'FortyFiveDown':
        return <TrendingDown color="primary" />;
      default:
        return <TrendingFlat color="action" />;
    }
  };

  const getGlucoseColor = () => {
    if (!glucose) return 'text.secondary';
    if (glucose < 70) return 'error.main';
    if (glucose > 180) return 'warning.main';
    return 'success.main';
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Current Glucose
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Typography variant="h3" color={getGlucoseColor()}>
            {glucose || '--'}
          </Typography>
          <Typography variant="h6" color="text.secondary">
            mg/dL
          </Typography>
          {getTrendIcon()}
        </Box>
        <Typography variant="body2" color="text.secondary">
          {minutesAgo < 60 ? `${Math.round(minutesAgo)} minutes ago` : 'Over 1 hour ago'}
        </Typography>
      </CardContent>
    </Card>
  );
};
```

#### 2.4 Simple Dashboard

**src/pages/Dashboard.tsx**
```typescript
import React, { useState, useEffect } from 'react';
import { Box, Grid, Typography, Alert } from '@mui/material';
import { CGMChart } from '../components/CGMChart';
import { CurrentGlucose } from '../components/CurrentGlucose';
import { TimeInRangeCard } from '../components/TimeInRangeCard';
import { apiService } from '../services/api';

export const Dashboard: React.FC = () => {
  const [cgmData, setCgmData] = useState([]);
  const [currentGlucose, setCurrentGlucose] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dataResponse, currentResponse] = await Promise.all([
          apiService.getCGMData(24), // Last 24 hours
          apiService.getCurrentGlucose()
        ]);
        
        setCgmData(dataResponse.data);
        setAnalysis(dataResponse.analysis);
        setCurrentGlucose(currentResponse);
        setError(null);
      } catch (err) {
        setError('Failed to load CGM data. Check your backend connection.');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    
    // Refresh data every 5 minutes
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <Typography>Loading CGM data...</Typography>;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        CGM Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <CGMChart data={cgmData} />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <CurrentGlucose {...currentGlucose} />
        </Grid>
        
        <Grid item xs={12} md={8}>
          <TimeInRangeCard analysis={analysis} />
        </Grid>
      </Grid>
    </Box>
  );
};
```

### Phase 3: Deployment & Configuration (Week 3)

#### 3.1 Backend Deployment Files

**.env.example** (for backend)
```env
# MongoDB Atlas Configuration
MONGODB_USERNAME=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password  
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.yourcluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=myCGMitc

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

**Dockerfile** (backend)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml** (backend)
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
```

#### 3.2 Frontend Deployment

**Dockerfile** (frontend)
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Phase 4: Future Enhancements

#### 4.1 Real-time Updates (Optional)
- WebSocket endpoint for live data
- Auto-refresh every 5 minutes
- Browser notifications for alerts

#### 4.2 Additional Visualizations
- Daily patterns (average by hour)
- Weekly summaries
- Glucose variability metrics

#### 4.3 Multi-user Support (Future)
- User authentication
- Individual MongoDB configurations
- Data isolation

## Deployment Options

### Development Setup
1. **Backend**: Run FastAPI locally (`uvicorn app.main:app --reload`)
2. **Frontend**: React dev server (`npm start`)  
3. **Environment**: Configure `.env` files for MongoDB connection

### Production Deployment

**Option 1: Simple VPS (Recommended for MVP)**
- Deploy backend with Docker on DigitalOcean/Linode ($5-10/month)
- Frontend on Netlify/Vercel (free)
- SSL via Let's Encrypt

**Option 2: Cloud Platforms**
- Backend: Railway, Render, or Fly.io (easy deployment)
- Frontend: Netlify, Vercel, or GitHub Pages
- Environment variables for MongoDB credentials

**Option 3: Self-hosted (Docker)**
- Single VPS running both backend and frontend
- Nginx proxy for SSL and routing
- Simple setup for personal use

## DIY User Setup Instructions

### Prerequisites for Users
1. **Loop system running** with MongoDB database
2. **MongoDB Atlas account** with credentials
3. **Basic technical knowledge** to follow setup instructions

### User Setup Process
1. **Clone backend repository**
2. **Configure `.env` file** with their MongoDB credentials
3. **Run backend** (Docker or local Python)
4. **Clone frontend repository**  
5. **Configure API endpoint** in frontend `.env`
6. **Run frontend** (Docker or local npm)
7. **Access dashboard** at localhost or deployed URL

### Documentation Requirements
- Clear setup instructions for each repository
- MongoDB Atlas credential finding guide
- Troubleshooting common connection issues
- Docker deployment instructions
- Environment variable configuration examples

## Package Publishing Strategy

### 1. loopy-basic → PyPI
```bash
# Prepare for PyPI publication
pip install build twine
python -m build
twine check dist/*
twine upload dist/*
```

### 2. Repository Structure
- **loopy-basic** (existing) → Core package on PyPI
- **loopy-api** → Backend repository
- **loopy-web** → Frontend repository

### 3. Installation Flow
```bash
# Backend setup
git clone https://github.com/username/loopy-api
cd loopy-api
pip install -r requirements.txt  # includes loopy-basic from PyPI
cp .env.example .env  # user configures MongoDB credentials
uvicorn app.main:app

# Frontend setup  
git clone https://github.com/username/loopy-web
cd loopy-web
npm install
cp .env.example .env  # user configures API endpoint
npm start
```

## Future Expansion Planning

### Phase 5: Pump Data Integration (Future)
- Extend `CGMService` to include pump data from MongoDB
- Additional API endpoints for insulin delivery data
- Enhanced visualizations showing CGM + pump correlation
- Analysis of insulin timing vs glucose response

### Phase 6: Multi-user Support (Optional Future)
- User authentication system
- Individual MongoDB connection management
- Data isolation and security
- Sharing/export capabilities

## Security Considerations

### MVP Security (Environment-based)
- ✅ **Environment variables** for MongoDB credentials
- ✅ **HTTPS only** in production
- ✅ **No data persistence** - read-only access to user's MongoDB
- ✅ **Input validation** for API endpoints
- ✅ **CORS configuration** for frontend/backend communication

### Future Security Enhancements
- User authentication with encrypted credential storage
- Rate limiting and API protection
- Audit logging for data access
- Advanced input sanitization

## Success Metrics

### MVP Goals
- ✅ **Personal use ready** - You can view your own CGM data
- ✅ **Nightscout-style interface** - Familiar glucose visualization
- ✅ **Mobile responsive** - Works on phones and tablets
- ✅ **Easy deployment** - Clear setup instructions for DIY users

### Technical Targets
- Sub-3 second initial load time
- Real-time data updates (5-minute refresh)
- Mobile-first responsive design
- Clear error messages and connection status

## Getting Started Checklist

### MVP Implementation
- [ ] Publish loopy-basic to PyPI
- [ ] Create cgm-dashboard-api repository with FastAPI backend
- [ ] Create cgm-dashboard-web repository with React frontend
- [ ] Test with your personal MongoDB Atlas database
- [ ] Create Docker deployment configurations
- [ ] Write comprehensive setup documentation
- [ ] Deploy your personal instance

### Future Enhancements
- [ ] Add pump data visualization
- [ ] Implement multi-user support
- [ ] Create mobile app version
- [ ] Add advanced analytics and reporting

This plan provides a focused, achievable path to create a personal diabetes monitoring dashboard that can be shared with the DIY diabetes community while maintaining simplicity and security.