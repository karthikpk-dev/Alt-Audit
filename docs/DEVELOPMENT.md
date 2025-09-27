# Alt Audit Development Guide

## Quick Start

### Prerequisites
- **Docker & Docker Compose** - Containerization
- **Git** - Version control

### Setup (2 minutes)

1. **Clone and start everything**
   ```bash
   git clone <repository-url>
   cd alt-audit
   docker-compose up -d
   ```

2. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

That's it! The application is running with all services.

## Project Structure

```
alt-audit/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI application
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database connection
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # API schemas
│   │   ├── auth.py          # Authentication
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utilities
│   ├── tests/               # Backend tests
│   └── requirements.txt     # Dependencies
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   └── types/           # TypeScript types
│   └── package.json         # Dependencies
├── docs/                    # Documentation
├── docker-compose.yml       # Development
├── docker-compose.prod.yml  # Production
└── README.md               # Project info
```

## Development Commands

### Start Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Run Tests
```bash
# Run all tests
./run_tests.sh

# Run backend tests only
./run_tests.sh --backend-only

# Run with coverage
./run_tests.sh --coverage
```

### Database
```bash
# Database is automatically created and managed by Docker
# No manual setup needed!
```

## Key Features

### What This App Does
- **URL Scanning** - Scans websites for accessibility issues
- **Image Analysis** - Checks alt text and image accessibility
- **User Authentication** - Secure login and registration
- **Analytics Dashboard** - View scan results and trends
- **CSV Export** - Export scan results for analysis

### Main Components
- **Backend** - FastAPI with PostgreSQL and Redis
- **Frontend** - React with TypeScript and Tailwind CSS
- **Database** - PostgreSQL for data storage
- **Cache** - Redis for session management

## Troubleshooting

### Common Issues

**App won't start:**
```bash
# Check if Docker is running
docker --version

# Restart services
docker-compose down
docker-compose up -d
```

**Database connection errors:**
```bash
# Check database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

**Frontend not loading:**
```bash
# Check frontend logs
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend
```

**API not responding:**
```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Debug Mode
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Need Help?

- **Check the logs** - `docker-compose logs -f`
- **Restart services** - `docker-compose restart`
- **View API docs** - http://localhost:8000/docs
- **Check README** - See main README.md for more info

That's it! This is a simple, focused development guide for your Alt Audit project.
