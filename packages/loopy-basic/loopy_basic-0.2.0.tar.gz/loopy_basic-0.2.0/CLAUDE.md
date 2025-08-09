# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python proof of concept project for accessing and analyzing Type 1 diabetes data from a DIY Loop system stored in MongoDB. The primary focus is CGM (Continuous Glucose Monitor) data analysis to identify patterns and trends for optimizing diabetes management.

## Analysis Goals

**Primary Focus: CGM Data Pattern Analysis**
- Time-scale analysis: past weeks, months (not viewing all 243K+ readings at once)
- Temporal patterns: specific times of day, days of week
- Trend identification for diabetes management optimization
- Eventually: correlation with treatment settings for better glucose control

**Analysis Workflow:**
1. Exploratory analysis in marimo notebooks
2. Pattern discovery and statistical analysis
3. Treatment optimization insights (future goal)
4. Potential migration to other tools based on findings

## Development Standards

This project follows **Python best practices for professional coding** with emphasis on:

**Code Quality:**
- Type hints for all functions and methods
- Comprehensive docstrings following Google/NumPy style
- Clear variable and function names
- Modular design with single responsibility principle
- Error handling with informative messages

**Reproducibility:**
- Pinned dependencies with exact versions
- Environment configuration via `.env` files
- Consistent data processing pipelines
- Deterministic analysis workflows

**Documentation:**
- All public functions must have detailed docstrings
- Inline comments for complex logic
- README with complete setup instructions
- Analysis methodology documented in `docs/`
- Code examples and usage patterns

**Testing & Validation:**
- Input validation for all public methods
- Data quality checks and cleaning
- Error handling for database connections
- Comprehensive testing of core functionality

## Development Setup

This project uses uv for dependency management and follows a modern Python package structure with src layout. Key commands:

- `uv sync` - Install dependencies
- `uv pip install -e .` - Install package in editable mode (recommended for development)
- `uv run python -m src.loopy.module` - Run Python modules directly
- `uv add <package>` - Add new dependencies

**Package Installation:**
For development and usage, install the package in editable mode:
```bash
uv pip install -e .
```
This allows you to import modules naturally:
```python
from loopy.data.cgm import CGMDataAccess
from loopy.connection.mongodb import MongoDBConnection
```

## Project Structure

```
src/loopy/
├── connection/    # Database connectivity
│   └── mongodb.py
├── data/          # Data access modules
│   └── cgm.py
└── utils/         # Utilities and debugging
    └── debug.py
docs/              # Documentation
dev/               # Development and analysis scripts
├── exploratory/   # Exploratory analysis notebooks
└── reports/       # Analysis reports
tests/             # Test modules
```

## Key Dependencies

Current dependencies for MongoDB diabetes data analysis:
- `pymongo` - MongoDB Python driver
- `pandas` - Data manipulation and analysis (with PyArrow backend for performance)
- `pyarrow` - High-performance backend for pandas
- `matplotlib` and `plotly` - Data visualization
- `marimo` - Interactive notebook environment for exploratory data analysis
- `python-dateutil` - Date/time parsing utilities
- `python-dotenv` - Environment variable management

**Configuration:**
```python
import pandas as pd
pd.options.mode.dtype_backend = "pyarrow"  # Enable PyArrow backend
```

**Module Imports:**
```python
from src.loopy.connection.mongodb import MongoDBConnection
from src.loopy.data.cgm import CGMDataAccess
from src.loopy.utils.debug import debug_connection_info
```

**Exploratory Analysis:**
- `marimo` notebooks for interactive data exploration and visualization
- Run with: `uv run marimo edit dev/exploratory/analysis.py`
- Ideal for pattern discovery and temporal analysis of CGM data

## Data Architecture

The MongoDB database contains DIY Loop system data with these expected collections:
- CGM readings (glucose values, timestamps)
- Insulin pump data (basal rates, bolus doses, timestamps)
- Loop system decisions and predictions

## Development Stages

### Stage 1: Database Connection
- Create connection module with MongoDB URI from environment variables
- Test basic connection and authentication
- List available databases and collections
- Verify connection can be established and closed properly

### Stage 2: CGM Data Access
- Connect to CGM/blood glucose readings collection
- Explore collection schema and document structure
- Implement basic query to retrieve recent CGM readings
- Test data retrieval and verify data format

### Stage 3: Time-Range Queries
- Implement date/time filtering for CGM data
- Add functions to query specific time periods (last 24h, week, custom range)
- Test with various time ranges and validate results

### Stage 4: Data Processing & DataFrame Integration
- Convert MongoDB documents to pandas DataFrames with PyArrow backend
- Implement efficient data cleaning and validation
- Handle timestamp conversions and timezone management
- Prepare data for time-series analysis (weeks/months focus)

### Stage 5: Pattern Analysis & Temporal Insights
- Time-of-day pattern analysis (hourly glucose trends)
- Day-of-week pattern identification
- Weekly and monthly trend analysis
- Statistical summaries for specific time periods
- Data preparation for marimo notebook exploration

### Stage 6: Treatment Correlation Analysis (Future)
- Extend to insulin pump data collections
- Correlate CGM data with treatment settings
- Identify optimal settings for glucose control
- Generate insights for diabetes management optimization

## Analysis Patterns

**CGM-Focused Time-Series Analysis:**
- Glucose trends over weeks/months (not full dataset)
- Temporal patterns: hourly, daily, weekly cycles
- Statistical analysis for specific time periods
- Pattern discovery for treatment optimization
- Efficient data processing for exploratory analysis in marimo notebooks

See `docs/analysis_patterns.md` for detailed analysis methodology and approaches.

## Key Module Commands

**Test Database Connection:**
```bash
uv run python -m src.loopy.connection.mongodb
```

**Debug Connection Issues:**
```bash
uv run python -m src.loopy.utils.debug
```

**Test CGM Data Access:**
```bash
uv run python -m src.loopy.data.cgm
```

**Usage Example (3 months of data):**
```bash
uv run python dev/usage_example.py
```

## Security Considerations

- Store MongoDB connection strings in environment variables
- Never commit database credentials to version control
- Use read-only database connections when possible