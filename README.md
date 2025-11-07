# PDF Image Analyzer Backend

Django REST Framework backend application for PDF and image analysis with three main apps:
- **File Upload**: Handle file uploads and presigned URL generation
- **Jobs**: Manage job creation and status tracking
- **Analytics**: Track and analyze user events

## Architecture

This application is designed to run in a private subnet and receives authenticated requests from an AWS ALB (Application Load Balancer). Authentication is handled by AWS Cognito via a separate auth service.

## Features

- Django REST Framework API
- **OpenAPI/Swagger** documentation compatible with Orval for frontend code generation
- **pgvector** PostgreSQL database for vector embeddings and similarity search
- AWS Cognito authentication integration (to be implemented)
- Celery for async task processing with **Flower** monitoring
- Redis for task queue and caching
- **Testing** with pytest and coverage reporting
- **AI/Data Processing**: OpenAI, NumPy, Pandas integration
- **Image Processing**: Pillow for image handling
- Docker support for local and production deployment
- All dependencies use MIT-compatible licenses

## Project Structure

```
pdf_image_analyzer_backend/
├── apps/
│   ├── file_upload/
│   │   ├── management/
│   │   ├── migrations/
│   │   ├── models/
│   │   ├── serializer/
│   │   ├── services/
│   │   ├── tasks/
│   │   ├── viewsets/
│   │   ├── filtersets/
│   │   └── tests/
│   ├── jobs/
│   │   └── [same structure as file_upload]
│   └── analytics/
│       └── [same structure as file_upload]
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py
├── manage.py
├── requirements.txt
├── Dockerfile
├── Dockerfile.local
└── docker-compose.yml
```

## Setup

### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Update `.env` with your configuration

6. Run migrations:
   ```bash
   python manage.py migrate
   ```

7. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

8. Run development server:
   ```bash
   python manage.py runserver
   ```

### Docker Development

1. Create `.env` file from `.env.example`
2. Run with docker-compose:
   ```bash
   docker-compose up
   ```

This will start:
- PostgreSQL with pgvector extension on port 5432
- Redis on port 6379
- Django application on port 8000
- Celery worker
- Flower (Celery monitoring) on port 5555

## API Endpoints

- `/health/` - Health check endpoint (no authentication required)
- `/docs/` - Swagger UI API documentation (no authentication required)
- `/redoc/` - ReDoc API documentation (no authentication required)
- `/swagger.json` - OpenAPI JSON specification for Orval
- `/swagger.yaml` - OpenAPI YAML specification for Orval
- `/api/v1/file-upload/` - File upload endpoints
- `/api/v1/jobs/` - Job management endpoints
- `/api/v1/analytics/` - Analytics endpoints

### OpenAPI/Orval Integration

The API provides OpenAPI 3.0 specification that can be used with [Orval](https://github.com/anymaniax/orval) to generate TypeScript/JavaScript client code for the frontend:

```bash
# Access OpenAPI spec at:
# http://localhost:8000/swagger.json
# or
# http://localhost:8000/swagger.yaml
```

### Flower - Celery Monitoring

Access Flower dashboard at `http://localhost:5555` to monitor Celery tasks, workers, and job status.

## Authentication

All endpoints except `/health/` and `/docs/` require AWS Cognito authentication. The authentication middleware will be implemented to validate JWT tokens from Cognito.

## Database Setup

The project uses **pgvector** for vector storage and similarity search. The pgvector extension is automatically enabled via migration on first `migrate` run.

To manually enable pgvector:
```bash
python manage.py init_pgvector
# or
python manage.py migrate
```

## Testing

Run tests with pytest:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov
```

Coverage reports are generated in:
- `htmlcov/index.html` - HTML coverage report
- `coverage.xml` - XML coverage report (for CI/CD)

Coverage threshold is set to 70% minimum.

## Environment Variables

See `env.example` for required environment variables.

## Production Deployment

The application is configured to run in a private subnet behind an ALB. Use `Dockerfile` for production builds which includes:
- Static file collection
- Gunicorn as WSGI server
- Production-ready configuration

## Technology Stack

### Core
- Django 5.0.1
- Django REST Framework 3.14.0
- PostgreSQL with pgvector extension

### AI & Data Processing
- OpenAI 0.27.2
- NumPy 2.2.3
- Pandas 2.2.3

### File/Image Processing
- Pillow 10.0.0

### Task Queue & Monitoring
- Celery 5.3.4
- Redis 5.0.1
- Flower 2.0.1

### Testing
- pytest 7.4.3
- pytest-django 4.7.0
- coverage 7.3.4

### API Documentation
- drf-yasg 1.21.7 (OpenAPI/Swagger)

## License

MIT License - All dependencies use MIT-compatible licenses.

