# Alt Audit - Image Accessibility Scanner

A comprehensive web application that scans websites for image accessibility compliance, helping developers and content creators ensure their images have proper alt text attributes.

## 🚀 Features

### Core Functionality
- **URL Scanning**: Enter any website URL to scan for images and alt text
- **Image Analysis**: Comprehensive analysis of all images on a page
- **Accessibility Reporting**: Detailed reports on alt text coverage and issues
- **Real-time Results**: Live updates during scanning process

### User Management
- **User Registration & Authentication**: Secure JWT-based authentication
- **User Dashboard**: Personalized dashboard with scan history
- **Data Isolation**: Each user can only access their own data

### Analytics & Reporting
- **Coverage Trends**: Track accessibility improvements over time
- **Issue Analysis**: Identify common accessibility problems
- **Data Export**: Export scan results in CSV and JSON formats
- **Visual Charts**: Interactive charts and graphs for data visualization

### Security & Performance
- **SSRF Protection**: Secure URL validation and scanning
- **Rate Limiting**: Prevent abuse with configurable rate limits
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: Graceful error handling and user feedback

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database
- **Redis**: In-memory data store for caching and rate limiting
- **SQLAlchemy**: Python SQL toolkit and ORM
- **Alembic**: Database migration tool
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation using Python type annotations

### Frontend
- **React**: Modern JavaScript library for building user interfaces
- **TypeScript**: Typed superset of JavaScript
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **React Hook Form**: Performant forms with easy validation
- **Zod**: TypeScript-first schema validation
- **Recharts**: Composable charting library
- **Axios**: Promise-based HTTP client

### Infrastructure
- **Docker**: Containerization platform
- **Docker Compose**: Multi-container Docker applications
- **Nginx**: High-performance web server and reverse proxy
- **Prometheus**: Monitoring and alerting toolkit
- **Grafana**: Metrics visualization and monitoring platform
- **Loki**: Log aggregation system

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd alt-audit
```

### 2. Environment Setup
```bash
# Copy environment template
cp env.prod.example .env.prod

# Edit environment variables
nano .env.prod
```

### 3. Deploy with Docker
```bash
# Deploy the application
./deploy.sh

# Or deploy with custom options
./deploy.sh --env production --coverage
```

### 4. Access the Application
- **Frontend**: http://localhost
- **API**: http://localhost/api/v1
- **Health Check**: http://localhost/health

## 🔧 Development Setup

### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the development server
npm run dev
```

### Running Tests
```bash
# Run all tests
./run_tests.sh

# Run specific test suites
./run_tests.sh --backend-only
./run_tests.sh --frontend-only

# Run with coverage
./run_tests.sh --coverage
```

## 📊 Monitoring & Observability

### Health Checks
```bash
# Run comprehensive health check
./scripts/health-check.sh

# Check specific URL
./scripts/health-check.sh --url https://your-domain.com

# Verbose output
./scripts/health-check.sh --verbose
```

### Monitoring Stack
```bash
# Start monitoring services
docker-compose -f monitoring/docker-compose.monitoring.yml up -d

# Access monitoring dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# AlertManager: http://localhost:9093
```

## 💾 Backup & Restore

### Backup
```bash
# Create backup
./scripts/backup.sh

# Backup with S3 upload
./scripts/backup.sh --upload-s3 --s3-bucket your-bucket

# Custom retention period
./scripts/backup.sh --retention 7
```

### Restore
```bash
# Restore from backup
./scripts/restore.sh --backup backup/20240101_120000.tar.gz

# Restore specific components
./scripts/restore.sh --backup backup.tar.gz --skip-redis
```

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication with configurable expiration
- Password hashing using bcrypt
- User data isolation and access control
- Rate limiting on authentication endpoints

### Input Validation & Sanitization
- URL validation with SSRF protection
- SQL injection prevention
- XSS protection in API responses
- Content type and size validation

### Network Security
- CORS configuration
- Security headers (HSTS, X-Frame-Options, etc.)
- Rate limiting and abuse prevention
- Private IP address blocking

## 📈 Performance Optimizations

### Backend Optimizations
- Async/await for non-blocking operations
- Database connection pooling
- Redis caching for frequently accessed data
- Background task processing for scans

### Frontend Optimizations
- Code splitting and lazy loading
- Image optimization and compression
- Gzip compression
- Browser caching strategies

### Infrastructure Optimizations
- Nginx reverse proxy with load balancing
- Docker multi-stage builds for smaller images
- Health checks and auto-restart
- Resource limits and monitoring

## 🧪 Testing

### Test Coverage
- **Backend**: 80%+ coverage with pytest
- **Frontend**: 80%+ coverage with Vitest
- **Integration**: End-to-end testing
- **Security**: Comprehensive security testing

### Test Categories
- Unit tests for individual components
- Integration tests for API endpoints
- Security tests for vulnerability assessment
- Performance tests for load testing

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/register` - User registration
- `POST /api/v1/login` - User login
- `GET /api/v1/me` - Get current user
- `POST /api/v1/refresh` - Refresh token

### Scan Endpoints
- `POST /api/v1/scans/` - Create new scan
- `GET /api/v1/scans/` - List user scans
- `GET /api/v1/scans/{id}` - Get scan details
- `GET /api/v1/scans/{id}/images` - Get scan images
- `DELETE /api/v1/scans/{id}` - Delete scan
- `POST /api/v1/scans/{id}/retry` - Retry failed scan

### Analytics Endpoints
- `GET /api/v1/analytics/summary` - Get analytics summary
- `GET /api/v1/analytics/trends` - Get coverage trends
- `GET /api/v1/analytics/top-issues` - Get top issues
- `GET /api/v1/analytics/coverage-distribution` - Get coverage distribution

### Export Endpoints
- `GET /api/v1/export/scans/csv` - Export scans as CSV
- `GET /api/v1/export/scans/{id}/json` - Export scan as JSON
- `GET /api/v1/export/analytics/json` - Export analytics as JSON

## 🚀 Deployment

### Production Deployment
```bash
# Deploy to production
./deploy.sh --env production

# Deploy with monitoring
./deploy.sh --env production
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

### Environment Configuration
- Copy `env.prod.example` to `.env.prod`
- Configure database credentials
- Set JWT secret key
- Configure Redis password
- Set allowed hosts and CORS origins

### SSL/TLS Configuration
- Place SSL certificates in `nginx/ssl/`
- Update Nginx configuration for HTTPS
- Configure HSTS and security headers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation as needed
- Follow conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Troubleshooting
- Check the [health check script](scripts/health-check.sh)
- Review application logs: `docker-compose -f docker-compose.prod.yml logs`
- Check service status: `docker-compose -f docker-compose.prod.yml ps`

### Common Issues
- **Port conflicts**: Ensure ports 80, 443, 5432, 6379 are available
- **Permission issues**: Check Docker permissions and file ownership
- **Database connection**: Verify PostgreSQL is running and accessible
- **Memory issues**: Ensure sufficient system resources

### Getting Help
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide
- Contact the development team

## 🎯 Roadmap

### Upcoming Features
- [ ] Real-time notifications
- [ ] Advanced filtering and search
- [ ] Bulk URL scanning
- [ ] API rate limiting per user
- [ ] Advanced analytics and insights
- [ ] Mobile application
- [ ] Integration with CI/CD pipelines

### Performance Improvements
- [ ] Database query optimization
- [ ] Caching improvements
- [ ] CDN integration
- [ ] Horizontal scaling support

---

**Alt Audit** - Making the web more accessible, one image at a time! 🚀