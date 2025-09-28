# Alt Audit - Image Accessibility Scanner

A simple web application that scans websites for image accessibility compliance, helping developers ensure their images have proper alt text attributes.

## 🚀 Features

- **URL Scanning**: Enter any website URL to scan for images and alt text
- **Image Analysis**: Comprehensive analysis of all images on a page
- **Accessibility Reporting**: Detailed reports on alt text coverage and issues
- **User Authentication**: Secure JWT-based authentication
- **Analytics Dashboard**: View scan trends and statistics
- **CSV Export**: Export scan results for analysis

## 🛠 Tech Stack

- **Backend**: FastAPI + PostgreSQL + Redis
- **Frontend**: React + TypeScript + Tailwind CSS
- **Infrastructure**: Docker + Docker Compose + Nginx

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Setup (2 minutes)
```bash
# Clone the repository
git clone https://github.com/karthikpk-dev/Alt-Audit.git
cd alt-audit

# Start the application
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

That's it! The application is running with all services.

## 🔧 Development

### Local Development
```bash
# Start development environment
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

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Scans
- `POST /api/v1/scans/` - Create new scan
- `GET /api/v1/scans/` - List user scans
- `GET /api/v1/scans/{id}` - Get scan details
- `DELETE /api/v1/scans/{id}` - Delete scan

### Analytics
- `GET /api/v1/analytics/summary` - Get analytics summary
- `GET /api/v1/analytics/trends` - Get coverage trends
- `GET /api/v1/analytics/top-issues` - Get top issues

### Export
- `GET /api/v1/export/scans/{id}/csv` - Export scan as CSV

## 🛠 Project Structure

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

## 🔒 Security Features

- **JWT Authentication**: Secure user authentication
- **SSRF Protection**: Safe URL validation
- **Rate Limiting**: Prevent abuse
- **Input Validation**: Comprehensive sanitization
- **CORS Configuration**: Secure cross-origin requests

## 🧪 Testing

- **Backend**: pytest with 80%+ coverage
- **Frontend**: Vitest with comprehensive tests
- **Integration**: End-to-end testing
- **Security**: Vulnerability assessment

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues
- **Port conflicts**: Ensure ports 3000, 8000, 5432, 6379 are available
- **Docker issues**: Check if Docker is running
- **Database connection**: Verify PostgreSQL is accessible
- **Frontend not loading**: Check if all services are running

### Debug Commands
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up -d --build
```

---

**Alt Audit** - Making the web more accessible, one image at a time! 🚀