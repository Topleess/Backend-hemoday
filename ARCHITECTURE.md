# HemoDay Backend Architecture

## Overview

HemoDay backend implements an **Offline-First architecture** using the **WatermelonDB synchronization protocol**. This allows the mobile app to work seamlessly offline and sync data when connection is available.

## Technology Stack

- **Python 3.12** - Modern Python with type hints
- **FastAPI** - High-performance async web framework
- **Tortoise-ORM** - Async ORM for PostgreSQL
- **PostgreSQL** - Robust relational database
- **Aerich** - Database migration tool
- **uv** - Fast Python package manager
- **JWT** - Stateless authentication
- **Docker** - Containerization

## Architecture Principles

### 1. Offline-First Synchronization

The system uses WatermelonDB protocol:

- **Pull**: Client requests changes since `last_pulled_at` timestamp
- **Push**: Client sends local changes (created/updated/deleted)
- **Conflict Resolution**: Last-write-wins strategy with timestamps
- **Soft Deletes**: Records marked with `deleted_at` instead of hard deletion

### 2. Data Isolation

All data is isolated by `family_id`:

```
Family (1) ─── (N) Users
            └─ (N) Transfusions
            └─ (N) BloodTests
            └─ (N) Documents
            └─ ...
```

### 3. WatermelonDB Schema

Every table includes required fields:

- `id` (UUID) - Primary key
- `created_at` (datetime) - Record creation timestamp
- `updated_at` (datetime) - Last modification timestamp
- `deleted_at` (datetime, nullable) - Soft delete marker

## Project Structure

```
Backend-hemoday/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── models/                 # Tortoise-ORM models
│   │   ├── __init__.py
│   │   ├── base.py            # WatermelonDBModel base class
│   │   ├── user.py
│   │   ├── family.py
│   │   ├── transfusion.py
│   │   ├── blood_test.py
│   │   ├── analysis_template.py
│   │   ├── reminder.py
│   │   └── document.py
│   ├── api/                    # API endpoints
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py      # Main router
│   │       ├── schemas.py     # Pydantic models
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── sync.py        # Sync endpoints
│   │       └── upload.py      # File upload
│   ├── core/                   # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py          # Settings & Tortoise config
│   │   ├── security.py        # JWT & password hashing
│   │   └── dependencies.py    # FastAPI dependencies
│   └── services/               # Business logic
│       ├── __init__.py
│       └── sync.py            # Sync service
├── migrations/                 # Aerich migrations
├── uploads/                    # User uploaded files
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-container setup
├── pyproject.toml             # Dependencies (uv)
├── requirements.txt           # Fallback dependencies
├── aerich.ini                 # Aerich configuration
├── .env                       # Environment variables
├── .gitignore
├── Makefile                   # Common commands
├── README.md
├── DEPLOYMENT.md
└── ARCHITECTURE.md
```

## Data Models

### User
- Authentication and family membership
- Email-based login with JWT

### Family
- Container for all medical data
- Unique 6-character invite code
- Patient information (name, weight, birth date)

### Transfusion
- Blood transfusion records
- Volume, patient weight, medication
- Indicator values (before/after)

### BloodTest & BloodTestResult
- Test events (date, comment)
- Individual results (name, value, unit)
- One-to-many relationship

### AnalysisTemplate
- User-created test presets
- JSON array of indicator names

### Reminder
- Scheduled reminders
- Frequency settings
- Completion tracking

### Document
- File metadata
- Category classification
- File URL storage

## API Endpoints

### Authentication (`/api/v1/auth`)

- `POST /register` - Create user + family
- `POST /login` - Authenticate user
- `POST /join-family` - Join by invite code
- `GET /me` - Current user info

### Synchronization (`/api/v1/sync`)

- `GET /sync?last_pulled_at=<timestamp>` - Pull changes
- `POST /sync` - Push changes

### File Upload (`/api/v1/upload`)

- `POST /upload` - Upload file

## Synchronization Flow

### Pull (Server → Client)

```python
GET /sync?last_pulled_at=1705234567000

Response:
{
  "changes": {
    "transfusions": {
      "created": [...],
      "updated": [...],
      "deleted": ["uuid1", "uuid2"]
    },
    "blood_tests": { ... }
  },
  "timestamp": 1705234890000
}
```

### Push (Client → Server)

```python
POST /sync
{
  "changes": {
    "transfusions": {
      "created": [{...}],
      "updated": [{...}],
      "deleted": ["uuid"]
    }
  }
}
```

## Security

### Authentication
- JWT tokens with configurable expiration
- bcrypt password hashing
- Bearer token authentication

### Authorization
- Family-based data isolation
- All queries filtered by `family_id`
- No cross-family data access

### Data Protection
- Soft deletes preserve data integrity
- Environment-based configuration
- CORS protection (configurable)

## Database Schema

```sql
-- Core tables
families (id, invite_code, patient_name, ...)
users (id, email, password_hash, family_id, ...)

-- Medical data (all with family_id foreign key)
transfusions (id, family_id, date, volume_ml, ...)
blood_tests (id, family_id, date, comment, ...)
blood_test_results (id, blood_test_id, family_id, name, value, unit, ...)
analysis_templates (id, family_id, name, indicators_json, ...)
reminders (id, family_id, title, remind_at, ...)
documents (id, family_id, name, category, file_url, ...)

-- All tables include WatermelonDB fields:
-- created_at, updated_at, deleted_at
```

## Performance Considerations

### Database
- Indexes on `family_id`, `email`, `invite_code`
- Async queries with Tortoise-ORM
- Connection pooling via asyncpg

### API
- Async/await throughout
- Efficient bulk operations for sync
- Pagination support (future enhancement)

### Files
- Direct file storage (simple deployment)
- Family-based directory organization
- Configurable size limits

## Future Enhancements

1. **Real-time Sync** - WebSocket support for live updates
2. **Pagination** - Large dataset handling
3. **Search** - Full-text search on records
4. **Analytics** - Data visualization endpoints
5. **Notifications** - Push notifications for reminders
6. **S3 Storage** - Cloud file storage integration
7. **Rate Limiting** - API request throttling
8. **Audit Log** - Track all changes
9. **Multi-language** - i18n support
10. **Data Export** - PDF/CSV generation

## Testing Strategy

### Unit Tests
- Model validation
- Business logic in services
- Utility functions

### Integration Tests
- API endpoints
- Authentication flow
- Sync operations

### E2E Tests
- Complete user workflows
- Mobile app integration
- Offline scenarios

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

### Development
```bash
docker-compose up -d
```

### Production
- Use managed PostgreSQL
- Configure HTTPS/SSL
- Set up monitoring
- Enable backups
- Use S3 for uploads
