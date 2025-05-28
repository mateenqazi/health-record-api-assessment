
# Health Record API

A secure REST API for managing personal health records with patient-doctor relationships, built with Django and Django REST Framework.

## 🎯 Features

### User Authentication & Authorization
- JWT-based authentication with short-lived tokens (5 minutes)
- Role-based access control (Patient/Doctor)
- Secure token refresh mechanism

### Health Records Management
- Patients can create, view, update, and delete their health records
- Doctors can view and comment on records of assigned patients
- Multiple record types: Checkup, Diagnosis, Prescription, Lab Result, Emergency

### Doctor-Patient Relationships
- Admin can assign doctors to patients
- Doctors receive notifications when assigned to new patients
- Doctors can view all records of their assigned patients

### Notification System
- Asynchronous notifications using Celery and Redis
- Real-time notifications for patient assignments and new records
- Mark notifications as read functionality

## 🛠️ Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT with djangorestframework-simplejwt
- **Task Queue**: Celery with Redis broker
- **API Documentation**: Built-in Django REST Framework browsable API

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Redis

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone 
cd health_record_api
```

### 2. Create Virtual Environment
```bash
python -m venv health_record_env
source health_record_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
```bash
# Create PostgreSQL database
createdb health_records_db

# Or using PostgreSQL command line:
sudo -u postgres psql
CREATE DATABASE health_records_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE health_records_db TO postgres;
\q
```

### 5. Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=health_record_secret_key
DEBUG=True
DB_NAME=health_records_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 6. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. Start Redis Server
```bash
redis-server
```

### 9. Start Celery Worker (New Terminal)
```bash
celery -A health_record_api worker --loglevel=info
```

### 10. Run Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/auth/register/` | User registration | Public |
| POST | `/api/auth/login/` | User login | Public |
| POST | `/api/auth/token/refresh/` | Refresh JWT token | Public |
| GET | `/api/auth/profile/` | Get user profile | Authenticated |
| PUT | `/api/auth/profile/` | Update user profile | Authenticated |
| GET | `/api/auth/doctors/` | List all doctors | Authenticated |
| POST | `/api/auth/assign-doctor/` | Assign doctor to patient | Doctor/Admin |

### Health Records
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/health-records/` | List health records | Authenticated |
| POST | `/api/health-records/` | Create health record | Patients only |
| GET | `/api/health-records/{id}/` | Get specific health record | Owner/Assigned Doctor |
| PUT | `/api/health-records/{id}/` | Update health record | Patients only |
| DELETE | `/api/health-records/{id}/` | Delete health record | Patients only |
| POST | `/api/health-records/{id}/comments/` | Add doctor comment | Assigned Doctor only |
| GET | `/api/health-records/my-patients/` | List assigned patients | Doctors only |

### Notifications
| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/notifications/` | List user notifications | Authenticated |
| POST | `/api/notifications/{id}/read/` | Mark notification as read | Authenticated |
| POST | `/api/notifications/mark-all-read/` | Mark all notifications as read | Authenticated |

## 💡 API Usage Examples

### 1. Register a Patient
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "patient1",
    "email": "patient@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "PATIENT",
    "phone_number": "+1234567890"
  }'
```

### 2. Register a Doctor
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "doctor1",
    "email": "doctor@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "Jane",
    "last_name": "Smith",
    "user_type": "DOCTOR",
    "phone_number": "+1234567891"
  }'
```

### 3. Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "patient1",
    "password": "securepass123"
  }'
```

### 4. Create Health Record (with JWT token)
```bash
curl -X POST http://localhost:8000/api/health-records/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "record_type": "CHECKUP",
    "title": "Annual Physical",
    "description": "Routine annual physical examination",
    "symptoms": "No specific symptoms",
    "diagnosis": "Patient appears healthy",
    "treatment": "Continue current lifestyle",
    "medications": "None",
    "visit_date": "2025-05-27T10:00:00Z"
  }'
```

### 5. Add Doctor Comment
```bash
curl -X POST http://localhost:8000/api/health-records/1/comments/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer DOCTOR_JWT_TOKEN" \
  -d '{
    "comment": "Patient shows good health indicators. Recommend annual follow-up.",
    "is_private": false
  }'
```

### 6. Get Notifications
```bash
curl -X GET http://localhost:8000/api/notifications/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔐 Security Features

- **JWT Authentication**: Short-lived access tokens (5 minutes) with refresh mechanism
- **Role-based Permissions**: Strict access control based on user types
- **Data Isolation**: Patients can only access their own records
- **Doctor Assignment**: Doctors can only view records of assigned patients
- **Secure Password Storage**: Django's built-in password hashing
- **Input Validation**: Comprehensive serializer validation
- **CORS Protection**: Configured for secure cross-origin requests

## 🏗️ Architecture

### Database Models
- **User**: Custom user model with role-based types (Patient/Doctor)
- **DoctorProfile**: Additional information for doctors
- **PatientProfile**: Additional information for patients with doctor assignment
- **HealthRecord**: Patient health records with various types
- **DoctorComment**: Doctor annotations on health records
- **Notification**: System notifications for users

### Permissions System
- **IsPatientOwnerOrAssignedDoctor**: Access to health records
- **IsPatientOwner**: Patient-only operations
- **IsDoctorAssignedToPatient**: Doctor operations on assigned patients

### Async Processing
- **Celery Tasks**: Background notification processing
- **Redis Broker**: Message queue for async tasks
- **Django Signals**: Automatic notification triggers

## 🐳 Docker Setup

### Using Docker Compose
```bash
# Build and start all services
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access the API at http://localhost:8000
```

### Individual Services
```bash
# Start PostgreSQL
docker run --name postgres -e POSTGRES_DB=health_records_db -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:13

# Start Redis
docker run --name redis -p 6379:6379 -d redis:alpine
```

### Database Migration
```bash
python manage.py migrate --settings=health_record_api.settings_prod
```

## 📊 API Response Examples

### Successful Registration Response
```json
{
  "user": {
    "id": 1,
    "username": "patient1",
    "email": "patient@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "PATIENT"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### Health Record Response
```json
{
  "id": 1,
  "patient": 1,
  "record_type": "CHECKUP",
  "title": "Annual Physical",
  "description": "Routine annual physical examination",
  "symptoms": "No specific symptoms",
  "diagnosis": "Patient appears healthy",
  "treatment": "Continue current lifestyle",
  "medications": "None",
  "visit_date": "2025-05-27T10:00:00Z",
  "created_by": {
    "id": 1,
    "username": "patient1",
    "email": "patient@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "user_type": "PATIENT"
  },
  "doctor_comments": [
    {
      "id": 1,
      "comment": "Patient shows good health indicators.",
      "is_private": false,
      "created_at": "2025-05-27T11:00:00Z",
      "doctor": {
        "id": 1,
        "specialization": "General Medicine",
        "license_number": "DOC000001",
        "years_of_experience": 5
      }
    }
  ],
  "created_at": "2025-05-27T10:30:00Z",
  "updated_at": "2025-05-27T10:30:00Z"
}
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify database exists
psql -h localhost -U postgres -l
```

#### 2. Redis Connection Error
```bash
# Check Redis is running
redis-cli ping
# Should return PONG
```

#### 3. Celery Not Processing Tasks
```bash
# Check Celery worker status
celery -A health_record_api inspect ping

# Restart Celery worker
celery -A health_record_api worker --loglevel=info
```

#### 4. JWT Token Expired
```bash
# Use refresh token to get new access token
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "YOUR_REFRESH_TOKEN"}'
```

#### 5. Permission Denied Errors
- Ensure user has correct role (PATIENT/DOCTOR)
- Check if doctor is assigned to patient
- Verify JWT token is valid and not expired

## 📈 Performance Considerations

- **Database Indexing**: Indexes on frequently queried fields
- **Query Optimization**: Select related and prefetch related for joins
- **Caching**: Redis caching for frequently accessed data
- **Pagination**: Built-in DRF pagination for large datasets
- **Async Processing**: Background tasks for non-critical operations

## 🔮 Future Enhancements

- **File Attachments**: Support for medical images and documents
- **Audit Logging**: Track all data access and modifications
- **Advanced Search**: Full-text search capabilities for health records
- **Appointment Scheduling**: Integration with calendar systems
- **Telemedicine**: Video consultation capabilities
- **Analytics Dashboard**: Health trends and insights
- **Mobile App**: React Native or Flutter mobile application
- **API Versioning**: Support for multiple API versions
- **Real-time Notifications**: WebSocket support for instant notifications
- **Data Export**: PDF/CSV export functionality

## 🎯 Assessment Requirements Fulfilled

- ✅ **User Registration & Authentication**: JWT with 5-minute expiry
- ✅ **Role-based Access Control**: Patient/Doctor permissions
- ✅ **Health Record Management**: Full CRUD operations
- ✅ **Doctor-Patient Assignments**: Admin assignment functionality
- ✅ **Automatic Notifications**: Celery-based async notifications
- ✅ **RESTful API Design**: Clean, well-structured endpoints
- ✅ **Security Features**: Data isolation and access control
- ✅ **Modern Django Practices**: Clean, modular architecture
- ✅ **PostgreSQL Database**: Production-ready database setup
- ✅ **Background Processing**: Non-blocking notification system

