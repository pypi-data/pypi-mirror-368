# Loopy Web - Frontend Implementation Guide

## Overview

**loopy-web** is a React + TypeScript frontend application that provides a modern, responsive web interface for CGM data visualization. It consumes the loopy-api backend and creates a Nightscout-style dashboard for DIY diabetes monitoring.

## Architecture

### Key Features
- ✅ **React + TypeScript** - Modern component-based UI with type safety
- ✅ **Plotly.js Visualizations** - Professional CGM charts similar to Nightscout
- ✅ **Material-UI Components** - Professional, accessible UI components
- ✅ **Real-time Updates** - Automatic data refresh every 5 minutes
- ✅ **Mobile Responsive** - Works on phones, tablets, and desktop
- ✅ **PWA Ready** - Can be installed as a mobile app
- ✅ **Static Deployment** - Deployable to Netlify, Vercel, GitHub Pages

### Repository Structure

```
loopy-web/
├── public/
│   ├── index.html
│   ├── manifest.json         # PWA manifest
│   └── favicon.ico
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── CGMChart.tsx     # Main glucose chart (Nightscout-style)
│   │   ├── StatsCards.tsx   # Time in range statistics
│   │   ├── CurrentGlucose.tsx # Current reading display
│   │   ├── TrendArrow.tsx   # Glucose trend indicators
│   │   ├── LoadingSpinner.tsx # Loading states
│   │   └── ErrorBoundary.tsx # Error handling
│   ├── pages/               # Main application pages
│   │   ├── Dashboard.tsx    # Main dashboard view
│   │   ├── Settings.tsx     # Configuration settings
│   │   └── About.tsx        # About/help page
│   ├── services/            # API communication layer
│   │   ├── api.ts           # Backend API client
│   │   ├── types.ts         # TypeScript type definitions
│   │   └── config.ts        # Configuration management
│   ├── hooks/               # Custom React hooks
│   │   ├── useCGMData.ts    # CGM data fetching hook
│   │   ├── useRealTime.ts   # Real-time updates hook
│   │   └── useLocalStorage.ts # Settings persistence
│   ├── utils/               # Utility functions
│   │   ├── glucose.ts       # Glucose calculations
│   │   ├── time.ts          # Time formatting
│   │   └── colors.ts        # Color schemes
│   ├── styles/              # CSS and styling
│   │   ├── globals.css      # Global styles
│   │   └── theme.ts         # Material-UI theme
│   ├── App.tsx              # Main application component
│   └── index.tsx            # Application entry point
├── package.json
├── tsconfig.json
├── .env.example             # API endpoint configuration
└── README.md                # User setup guide
```

## Implementation Steps

### Phase 1: Project Setup

#### 1.1 Create React Application
```bash
# Create new React app with TypeScript
npx create-react-app loopy-web --template typescript
cd loopy-web

# Install additional dependencies
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material
npm install plotly.js react-plotly.js
npm install @types/plotly.js
npm install axios
npm install date-fns
npm install react-router-dom
```

#### 1.2 Environment Configuration

**.env.example**
```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_PREFIX=/api
REACT_APP_REFRESH_INTERVAL=300000

# Application Settings
REACT_APP_APP_NAME=Loopy Web
REACT_APP_VERSION=1.0.0
```

### Phase 2: Core Components

#### 2.1 API Service Layer

**src/services/types.ts**
```typescript
export interface CGMReading {
  datetime: string;
  sgv: number;
  direction: string;
  trend?: number;
  hour: number;
  day_of_week: number;
  glucose_category: 'Low' | 'Normal' | 'High' | 'Very High';
}

export interface TimeInRange {
  low_percent: number;
  normal_percent: number;
  high_percent: number;
  very_high_percent: number;
}

export interface BasicStats {
  total_readings: number;
  avg_glucose: number;
  median_glucose: number;
  std_glucose: number;
  min_glucose: number;
  max_glucose: number;
}

export interface CGMAnalysis {
  basic_stats: BasicStats;
  time_in_range: TimeInRange;
  temporal_patterns: {
    avg_by_hour: Record<string, number>;
    avg_by_day_of_week: Record<string, number>;
  };
  data_quality: {
    time_span_hours: number;
    readings_per_day: number;
  };
}

export interface CGMDataResponse {
  data: CGMReading[];
  analysis: CGMAnalysis;
  last_updated: string;
  time_range: {
    start: string;
    end: string;
    hours: number;
  };
}

export interface CurrentGlucoseResponse {
  current_glucose: number | null;
  direction: string;
  trend?: number;
  timestamp: string;
  minutes_ago: number | null;
  device?: string;
  type?: string;
}

export interface DataStatusResponse {
  status: 'connected' | 'no_recent_data' | 'error';
  last_reading_count: number;
  message: string;
  last_updated: string;
}
```

**src/services/api.ts**
```typescript
import axios, { AxiosResponse } from 'axios';
import { 
  CGMDataResponse, 
  CurrentGlucoseResponse, 
  DataStatusResponse 
} from './types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_PREFIX = process.env.REACT_APP_API_PREFIX || '/api';

const api = axios.create({
  baseURL: `${API_BASE_URL}${API_PREFIX}`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health and status endpoints
  async healthCheck(): Promise<{ status: string; service: string }> {
    const response: AxiosResponse = await api.get('/health');
    return response.data;
  },

  async getDataStatus(): Promise<DataStatusResponse> {
    const response: AxiosResponse<DataStatusResponse> = await api.get('/cgm/status');
    return response.data;
  },

  // CGM data endpoints
  async getCGMData(hours: number = 24): Promise<CGMDataResponse> {
    const response: AxiosResponse<CGMDataResponse> = await api.get('/cgm/data', {
      params: { hours }
    });
    return response.data;
  },

  async getCurrentGlucose(): Promise<CurrentGlucoseResponse> {
    const response: AxiosResponse<CurrentGlucoseResponse> = await api.get('/cgm/current');
    return response.data;
  },

  async getAnalysis(period: '24h' | 'week' | 'month'): Promise<{
    period: string;
    analysis: any;
    data_points: number;
    time_range: any;
    last_updated: string;
  }> {
    const response: AxiosResponse = await api.get(`/cgm/analysis/${period}`);
    return response.data;
  },
};

export default apiService;
```

#### 2.2 Custom Hooks

**src/hooks/useCGMData.ts**
```typescript
import { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import { CGMDataResponse, CurrentGlucoseResponse, DataStatusResponse } from '../services/types';

export const useCGMData = (refreshInterval: number = 300000) => {
  const [cgmData, setCgmData] = useState<CGMDataResponse | null>(null);
  const [currentGlucose, setCurrentGlucose] = useState<CurrentGlucoseResponse | null>(null);
  const [dataStatus, setDataStatus] = useState<DataStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (hours: number = 24) => {
    try {
      setError(null);
      
      const [dataResponse, currentResponse, statusResponse] = await Promise.all([
        apiService.getCGMData(hours),
        apiService.getCurrentGlucose(),
        apiService.getDataStatus()
      ]);

      setCgmData(dataResponse);
      setCurrentGlucose(currentResponse);
      setDataStatus(statusResponse);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to fetch CGM data';
      setError(errorMessage);
      console.error('Error fetching CGM data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Set up automatic refresh
  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(() => {
        fetchData();
      }, refreshInterval);

      return () => clearInterval(interval);
    }
  }, [fetchData, refreshInterval]);

  const refetch = useCallback((hours?: number) => {
    setLoading(true);
    fetchData(hours);
  }, [fetchData]);

  return {
    cgmData,
    currentGlucose,
    dataStatus,
    loading,
    error,
    refetch,
  };
};
```

#### 2.3 CGM Chart Component

**src/components/CGMChart.tsx**
```typescript
import React from 'react';
import Plot from 'react-plotly.js';
import { CGMReading } from '../services/types';
import { Card, CardContent, Typography, Box } from '@mui/material';

interface CGMChartProps {
  data: CGMReading[];
  height?: number;
  title?: string;
}

export const CGMChart: React.FC<CGMChartProps> = ({ 
  data, 
  height = 400, 
  title = 'Continuous Glucose Monitor' 
}) => {
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {title}
          </Typography>
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography color="textSecondary">
              No CGM data available
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // Sort data by datetime
  const sortedData = [...data].sort((a, b) => 
    new Date(a.datetime).getTime() - new Date(b.datetime).getTime()
  );

  // Create trace with color coding
  const trace = {
    x: sortedData.map(d => d.datetime),
    y: sortedData.map(d => d.sgv),
    type: 'scatter' as const,
    mode: 'lines+markers' as const,
    name: 'Glucose',
    line: { 
      color: '#2196f3', 
      width: 2 
    },
    marker: { 
      size: 4,
      color: sortedData.map(d => {
        if (d.sgv < 70) return '#f44336'; // Red for low
        if (d.sgv > 180) return '#ff9800'; // Orange for high
        if (d.sgv > 250) return '#d32f2f'; // Dark red for very high
        return '#4caf50'; // Green for normal
      })
    },
    hovertemplate: 
      '<b>%{y} mg/dL</b><br>' +
      '%{x}<br>' +
      '<extra></extra>'
  };

  const layout = {
    title: {
      text: title,
      font: { size: 18 }
    },
    xaxis: { 
      title: 'Time',
      type: 'date' as const,
      showgrid: true,
      gridcolor: '#e0e0e0'
    },
    yaxis: { 
      title: 'Glucose (mg/dL)',
      range: [50, Math.max(400, Math.max(...sortedData.map(d => d.sgv)) + 50)],
      showgrid: true,
      gridcolor: '#e0e0e0'
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
      // Low threshold line (70 mg/dL)
      {
        type: 'line' as const,
        xref: 'paper' as const,
        yref: 'y' as const,
        x0: 0,
        x1: 1,
        y0: 70,
        y1: 70,
        line: { color: '#f44336', width: 1, dash: 'dash' }
      },
      // High threshold line (180 mg/dL)
      {
        type: 'line' as const,
        xref: 'paper' as const,
        yref: 'y' as const,
        x0: 0,
        x1: 1,
        y0: 180,
        y1: 180,
        line: { color: '#ff9800', width: 1, dash: 'dash' }
      }
    ],
    margin: { t: 60, b: 50, l: 60, r: 30 },
    plot_bgcolor: '#fafafa',
    paper_bgcolor: 'white'
  };

  const config = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
  };

  return (
    <Card>
      <CardContent>
        <Plot
          data={[trace]}
          layout={layout}
          config={config}
          style={{ width: '100%', height: `${height}px` }}
        />
      </CardContent>
    </Card>
  );
};
```

#### 2.4 Current Glucose Display

**src/components/CurrentGlucose.tsx**
```typescript
import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { 
  TrendingUp, 
  TrendingDown, 
  TrendingFlat,
  KeyboardDoubleArrowUp,
  KeyboardDoubleArrowDown,
  KeyboardArrowUp,
  KeyboardArrowDown
} from '@mui/icons-material';
import { CurrentGlucoseResponse } from '../services/types';

interface CurrentGlucoseProps {
  data: CurrentGlucoseResponse | null;
}

export const CurrentGlucose: React.FC<CurrentGlucoseProps> = ({ data }) => {
  if (!data || data.current_glucose === null) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Current Glucose
          </Typography>
          <Box display="flex" alignItems="center" gap={1}>
            <Typography variant="h3" color="text.secondary">
              --
            </Typography>
            <Typography variant="h6" color="text.secondary">
              mg/dL
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            No recent data
          </Typography>
        </CardContent>
      </Card>
    );
  }

  const { current_glucose, direction, minutes_ago, timestamp } = data;

  const getTrendIcon = () => {
    const iconProps = { fontSize: 'large' as const };
    
    switch (direction) {
      case 'DoubleUp':
        return <KeyboardDoubleArrowUp {...iconProps} color="warning" />;
      case 'SingleUp':
        return <KeyboardArrowUp {...iconProps} color="warning" />;
      case 'FortyFiveUp':
        return <TrendingUp {...iconProps} color="warning" />;
      case 'FortyFiveDown':
        return <TrendingDown {...iconProps} color="primary" />;
      case 'SingleDown':
        return <KeyboardArrowDown {...iconProps} color="primary" />;
      case 'DoubleDown':
        return <KeyboardDoubleArrowDown {...iconProps} color="error" />;
      case 'Flat':
      default:
        return <TrendingFlat {...iconProps} color="action" />;
    }
  };

  const getGlucoseColor = () => {
    if (current_glucose < 70) return 'error.main';
    if (current_glucose > 250) return 'error.main';
    if (current_glucose > 180) return 'warning.main';
    return 'success.main';
  };

  const getStatusChip = () => {
    if (!minutes_ago) return null;
    
    if (minutes_ago < 10) {
      return <Chip label="Current" color="success" size="small" />;
    } else if (minutes_ago < 30) {
      return <Chip label="Recent" color="primary" size="small" />;
    } else {
      return <Chip label="Stale" color="warning" size="small" />;
    }
  };

  const formatTimestamp = () => {
    if (!minutes_ago) return 'Unknown time';
    
    if (minutes_ago < 1) return 'Less than 1 minute ago';
    if (minutes_ago < 60) return `${Math.round(minutes_ago)} minutes ago`;
    
    const hours = Math.floor(minutes_ago / 60);
    const mins = Math.round(minutes_ago % 60);
    return `${hours}h ${mins}m ago`;
  };

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="h6">
            Current Glucose
          </Typography>
          {getStatusChip()}
        </Box>
        
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Typography variant="h2" color={getGlucoseColor()} fontWeight="bold">
            {current_glucose}
          </Typography>
          <Box display="flex" flexDirection="column" alignItems="center">
            <Typography variant="body2" color="text.secondary">
              mg/dL
            </Typography>
            {getTrendIcon()}
          </Box>
        </Box>
        
        <Typography variant="body2" color="text.secondary">
          {formatTimestamp()}
        </Typography>
        
        <Typography variant="caption" color="text.secondary" display="block" mt={1}>
          Trend: {direction}
        </Typography>
      </CardContent>
    </Card>
  );
};
```

#### 2.5 Time in Range Cards

**src/components/StatsCards.tsx**
```typescript
import React from 'react';
import { Grid, Card, CardContent, Typography, LinearProgress, Box } from '@mui/material';
import { CGMAnalysis } from '../services/types';

interface StatsCardsProps {
  analysis: CGMAnalysis | null;
}

export const StatsCards: React.FC<StatsCardsProps> = ({ analysis }) => {
  if (!analysis) {
    return (
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography color="textSecondary">
                No analysis data available
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  }

  const { basic_stats, time_in_range } = analysis;

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    subtitle?: string;
    color?: string;
    progress?: number;
  }> = ({ title, value, subtitle, color = 'primary.main', progress }) => (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h4" color={color} fontWeight="bold">
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
        {progress !== undefined && (
          <Box mt={1}>
            <LinearProgress 
              variant="determinate" 
              value={progress} 
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Grid container spacing={2}>
      {/* Average Glucose */}
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Average Glucose"
          value={`${basic_stats.avg_glucose.toFixed(1)}`}
          subtitle="mg/dL"
          color={
            basic_stats.avg_glucose < 70 ? 'error.main' :
            basic_stats.avg_glucose > 180 ? 'warning.main' : 
            'success.main'
          }
        />
      </Grid>

      {/* Time in Range */}
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Time in Range"
          value={`${time_in_range.normal_percent.toFixed(1)}%`}
          subtitle="70-180 mg/dL"
          color={
            time_in_range.normal_percent >= 70 ? 'success.main' :
            time_in_range.normal_percent >= 50 ? 'warning.main' :
            'error.main'
          }
          progress={time_in_range.normal_percent}
        />
      </Grid>

      {/* Low Glucose */}
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Time Below Range"
          value={`${time_in_range.low_percent.toFixed(1)}%`}
          subtitle="< 70 mg/dL"
          color={
            time_in_range.low_percent < 4 ? 'success.main' :
            time_in_range.low_percent < 10 ? 'warning.main' :
            'error.main'
          }
          progress={time_in_range.low_percent}
        />
      </Grid>

      {/* High Glucose */}
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Time Above Range"
          value={`${(time_in_range.high_percent + time_in_range.very_high_percent).toFixed(1)}%`}
          subtitle="> 180 mg/dL"
          color={
            (time_in_range.high_percent + time_in_range.very_high_percent) < 25 ? 'success.main' :
            (time_in_range.high_percent + time_in_range.very_high_percent) < 50 ? 'warning.main' :
            'error.main'
          }
          progress={time_in_range.high_percent + time_in_range.very_high_percent}
        />
      </Grid>

      {/* Additional Stats */}
      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Total Readings"
          value={basic_stats.total_readings.toLocaleString()}
          subtitle="data points"
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Glucose Range"
          value={`${basic_stats.min_glucose.toFixed(0)}-${basic_stats.max_glucose.toFixed(0)}`}
          subtitle="mg/dL"
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Standard Deviation"
          value={basic_stats.std_glucose.toFixed(1)}
          subtitle="mg/dL"
          color={
            basic_stats.std_glucose < 30 ? 'success.main' :
            basic_stats.std_glucose < 50 ? 'warning.main' :
            'error.main'
          }
        />
      </Grid>

      <Grid item xs={12} sm={6} md={3}>
        <StatCard
          title="Median Glucose"
          value={basic_stats.median_glucose.toFixed(1)}
          subtitle="mg/dL"
        />
      </Grid>
    </Grid>
  );
};
```

#### 2.6 Main Dashboard

**src/pages/Dashboard.tsx**
```typescript
import React, { useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Alert,
  CircularProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Paper
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { CGMChart } from '../components/CGMChart';
import { CurrentGlucose } from '../components/CurrentGlucose';
import { StatsCards } from '../components/StatsCards';
import { useCGMData } from '../hooks/useCGMData';

export const Dashboard: React.FC = () => {
  const [timeRange, setTimeRange] = useState(24);
  const refreshInterval = parseInt(process.env.REACT_APP_REFRESH_INTERVAL || '300000');
  
  const { cgmData, currentGlucose, dataStatus, loading, error, refetch } = useCGMData(refreshInterval);

  const handleTimeRangeChange = (newRange: number) => {
    setTimeRange(newRange);
    refetch(newRange);
  };

  const handleRefresh = () => {
    refetch(timeRange);
  };

  if (loading && !cgmData) {
    return (
      <Box 
        sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '50vh' 
        }}
      >
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Loading CGM data...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="h6">Connection Error</Typography>
          <Typography variant="body2">
            {error}
          </Typography>
          <Button 
            variant="outlined" 
            onClick={handleRefresh} 
            sx={{ mt: 1 }}
            startIcon={<Refresh />}
          >
            Retry Connection
          </Button>
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          CGM Dashboard
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => handleTimeRangeChange(Number(e.target.value))}
            >
              <MenuItem value={6}>6 Hours</MenuItem>
              <MenuItem value={12}>12 Hours</MenuItem>
              <MenuItem value={24}>24 Hours</MenuItem>
              <MenuItem value={72}>3 Days</MenuItem>
              <MenuItem value={168}>1 Week</MenuItem>
            </Select>
          </FormControl>
          
          <Button
            variant="outlined"
            onClick={handleRefresh}
            startIcon={<Refresh />}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </Button>
        </Box>
      </Box>

      {/* Status Alert */}
      {dataStatus && dataStatus.status !== 'connected' && (
        <Alert 
          severity={dataStatus.status === 'error' ? 'error' : 'warning'} 
          sx={{ mb: 2 }}
        >
          {dataStatus.message}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Current Glucose */}
        <Grid item xs={12} md={4}>
          <CurrentGlucose data={currentGlucose} />
        </Grid>

        {/* Last Updated */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Last Updated: {cgmData?.last_updated ? 
                new Date(cgmData.last_updated).toLocaleString() : 
                'Unknown'
              }
            </Typography>
            {cgmData?.time_range && (
              <Typography variant="body2" color="text.secondary">
                Showing {cgmData.data?.length || 0} readings from {timeRange} hours
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* CGM Chart */}
        <Grid item xs={12}>
          <CGMChart 
            data={cgmData?.data || []} 
            height={500}
            title={`CGM Readings - Last ${timeRange} Hours`}
          />
        </Grid>

        {/* Statistics Cards */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom>
            Statistics
          </Typography>
          <StatsCards analysis={cgmData?.analysis || null} />
        </Grid>
      </Grid>
    </Box>
  );
};
```

### Phase 3: Application Setup

#### 3.1 Main App Component

**src/App.tsx**
```typescript
import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, AppBar, Toolbar, Typography } from '@mui/material';
import { Dashboard } from './pages/Dashboard';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              {process.env.REACT_APP_APP_NAME || 'Loopy Web'}
            </Typography>
            <Typography variant="body2">
              v{process.env.REACT_APP_VERSION || '1.0.0'}
            </Typography>
          </Toolbar>
        </AppBar>
        
        <main>
          <Dashboard />
        </main>
      </Box>
    </ThemeProvider>
  );
}

export default App;
```

### Phase 4: Development & Deployment

#### 4.1 Development Scripts

**package.json scripts:**
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject",
    "lint": "eslint src --ext .ts,.tsx",
    "format": "prettier --write src/**/*.{ts,tsx}"
  }
}
```

#### 4.2 Deployment Configuration

**For Netlify (_redirects file in public/):**
```
/*    /index.html   200
```

**For Vercel (vercel.json):**
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/" }
  ]
}
```

#### 4.3 Environment Setup

**Development:**
```bash
# Copy environment template
cp .env.example .env.local

# Edit with your API endpoint
REACT_APP_API_URL=http://localhost:8000

# Start development server
npm start
```

**Production Build:**
```bash
# Build for production
npm run build

# Test production build locally
npm install -g serve
serve -s build
```

## Deployment Options

### 1. Netlify (Recommended)
- Connect GitHub repository
- Set build command: `npm run build`
- Set publish directory: `build`
- Configure environment variables

### 2. Vercel
- Connect GitHub repository
- Automatic deployment on push
- Configure environment variables
- Built-in performance optimization

### 3. GitHub Pages
- Enable GitHub Pages in repository settings
- Use `gh-pages` package for deployment
- Static hosting with custom domain support

## Features Roadmap

### MVP (Current)
- ✅ CGM data visualization
- ✅ Current glucose display
- ✅ Time in range statistics
- ✅ Real-time updates
- ✅ Mobile responsive design

### Future Enhancements
- [ ] Multiple time period views
- [ ] Data export functionality
- [ ] Alert thresholds configuration
- [ ] Dark mode support
- [ ] PWA offline capabilities
- [ ] Historical trend analysis
- [ ] Insulin/treatment correlation

## Security & Performance

### Security
- No sensitive data stored in frontend
- Environment variables for configuration
- HTTPS required in production
- CORS properly configured

### Performance
- Code splitting with React.lazy
- Memoized components
- Efficient data fetching
- Responsive images
- Minimal bundle size

## Next Steps

1. Complete component implementation
2. Test with loopy-api backend
3. Configure environment variables
4. Deploy to chosen platform
5. Test mobile responsiveness
6. Configure automatic updates