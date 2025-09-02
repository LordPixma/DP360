# DP360
A light Weight Compliance tool



High level Design

# High-Level Design Proposal: Comp360Flow Compliance Management Platform

## System Architecture Overview

### Architecture Pattern
**Modular Monolithic Architecture** with clear separation of concerns, designed for scalability and maintainability.

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (nginx)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                Flask Application Layer                      │
├─────────────────┬───────────────┬───────────────────────────┤
│   Web Interface │   API Layer   │    Background Tasks       │
│   (Jinja2)      │   (REST/JSON) │    (Celery + Redis)      │
└─────────────────┴───────────────┴───────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                Business Logic Layer                        │
├─────────────────┬───────────────┬───────────────────────────┤
│ Compliance Core │ User Management│   Integration Services   │
└─────────────────┴───────────────┴───────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                Data Access Layer                           │
├─────────────────┬───────────────┬───────────────────────────┤
│   PostgreSQL    │     Redis     │    File Storage (S3)     │
│   (Primary DB)  │   (Cache)     │    (Documents/Evidence)   │
└─────────────────┴───────────────┴───────────────────────────┘
```

## Core Components

### 1. Flask Application Structure

```
comp360flow/
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── config.py                   # Configuration management
│   ├── models/                     # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── compliance.py
│   │   ├── control.py
│   │   ├── task.py
│   │   ├── evidence.py
│   │   └── audit.py
│   ├── blueprints/                 # Feature modules
│   │   ├── auth/                   # Authentication & authorization
│   │   ├── dashboard/              # Main dashboard
│   │   ├── compliance/             # Compliance management
│   │   ├── controls/               # Control library
│   │   ├── tasks/                  # Task management
│   │   ├── reports/                # Reporting & analytics
│   │   ├── integrations/           # Third-party integrations
│   │   └── admin/                  # System administration
│   ├── services/                   # Business logic services
│   │   ├── compliance_service.py
│   │   ├── control_service.py
│   │   ├── task_service.py
│   │   ├── evidence_service.py
│   │   ├── notification_service.py
│   │   └── integration_service.py
│   ├── utils/                      # Utility functions
│   │   ├── decorators.py
│   │   ├── validators.py
│   │   ├── helpers.py
│   │   └── security.py
│   ├── templates/                  # Jinja2 templates
│   │   ├── base/
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── compliance/
│   │   ├── controls/
│   │   ├── tasks/
│   │   └── reports/
│   └── static/                     # CSS, JS, images
│       ├── css/
│       ├── js/
│       └── images/
├── migrations/                     # Database migrations
├── tests/                         # Test suite
├── requirements.txt
├── wsgi.py                        # WSGI entry point
└── run.py                         # Development server
```

### 2. Database Schema Design

#### Core Tables

**Organizations**
```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    size_category VARCHAR(20), -- startup, mid_market, enterprise
    subscription_tier VARCHAR(20), -- starter, professional, enterprise
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Users**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50), -- admin, manager, user, auditor
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Compliance Frameworks**
```sql
CREATE TABLE compliance_frameworks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL, -- SOC2, ISO27001, GDPR, etc.
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20),
    is_active BOOLEAN DEFAULT true
);
```

**Controls**
```sql
CREATE TABLE controls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework_id UUID REFERENCES compliance_frameworks(id),
    control_id VARCHAR(50) NOT NULL, -- Framework-specific ID
    title VARCHAR(255) NOT NULL,
    description TEXT,
    control_type VARCHAR(50), -- preventive, detective, corrective
    risk_level VARCHAR(20), -- high, medium, low
    testing_frequency VARCHAR(50), -- annual, quarterly, monthly
    owner_role VARCHAR(100),
    is_active BOOLEAN DEFAULT true
);
```

**Organization Controls**
```sql
CREATE TABLE organization_controls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    control_id UUID REFERENCES controls(id),
    status VARCHAR(50), -- not_started, in_progress, implemented, non_compliant
    implementation_date DATE,
    next_review_date DATE,
    assigned_user_id UUID REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Tasks**
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    control_id UUID REFERENCES controls(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    task_type VARCHAR(50), -- implementation, testing, review
    priority VARCHAR(20), -- high, medium, low
    status VARCHAR(50), -- pending, in_progress, completed, overdue
    assigned_user_id UUID REFERENCES users(id),
    due_date DATE,
    completed_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Evidence**
```sql
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id),
    control_id UUID REFERENCES controls(id),
    task_id UUID REFERENCES tasks(id),
    file_name VARCHAR(255),
    file_path VARCHAR(500),
    file_size INTEGER,
    file_type VARCHAR(50),
    description TEXT,
    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Service Layer Architecture

#### Compliance Service
```python
class ComplianceService:
    def __init__(self, db_session):
        self.db = db_session
    
    def get_compliance_status(self, org_id, framework_code=None):
        """Calculate overall compliance percentage"""
        
    def initialize_framework(self, org_id, framework_code):
        """Set up framework controls for organization"""
        
    def update_control_status(self, org_control_id, status, notes=None):
        """Update implementation status of a control"""
        
    def generate_compliance_report(self, org_id, framework_code=None):
        """Generate compliance status report"""
```

#### Task Management Service
```python
class TaskService:
    def create_automated_tasks(self, org_id, control_id):
        """Auto-generate tasks based on control requirements"""
        
    def assign_task(self, task_id, user_id):
        """Assign task to user with notifications"""
        
    def get_upcoming_deadlines(self, org_id, days_ahead=30):
        """Get tasks due within specified timeframe"""
        
    def mark_task_complete(self, task_id, evidence_files=None):
        """Complete task and attach evidence"""
```

#### Notification Service
```python
class NotificationService:
    def send_deadline_reminders(self):
        """Send automated deadline reminders"""
        
    def notify_task_assignment(self, task_id, user_id):
        """Notify user of new task assignment"""
        
    def send_compliance_alerts(self, org_id, alert_type):
        """Send compliance-related alerts"""
```

### 4. Frontend Architecture (Jinja2 Templates)

#### Template Hierarchy
```
templates/
├── base/
│   ├── layout.html              # Main layout
│   ├── navigation.html          # Navigation bar
│   ├── sidebar.html             # Sidebar navigation
│   └── footer.html              # Footer
├── dashboard/
│   ├── index.html               # Main dashboard
│   ├── widgets/                 # Dashboard widgets
│   │   ├── compliance_status.html
│   │   ├── upcoming_tasks.html
│   │   ├── recent_activities.html
│   │   └── risk_summary.html
├── compliance/
│   ├── frameworks.html          # Framework selection
│   ├── controls.html            # Control management
│   ├── assessments.html         # Risk assessments
│   └── roadmap.html            # Compliance roadmap
├── tasks/
│   ├── list.html               # Task list view
│   ├── detail.html             # Task detail view
│   ├── create.html             # Task creation
│   └── calendar.html           # Calendar view
└── reports/
    ├── compliance_status.html   # Status reports
    ├── audit_ready.html        # Audit preparation
    └── custom.html             # Custom reports
```

#### Key Frontend Components

**Dashboard Widgets**
```html
<!-- Compliance Status Widget -->
<div class="compliance-widget">
    <h3>Overall Compliance</h3>
    <div class="progress-circle" data-percentage="{{ compliance_percentage }}">
        <span>{{ compliance_percentage }}%</span>
    </div>
    <div class="framework-breakdown">
        {% for framework in frameworks %}
        <div class="framework-status">
            <span>{{ framework.name }}</span>
            <div class="progress-bar">
                <div class="progress" style="width: {{ framework.percentage }}%"></div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
```

**Task Management Interface**
```html
<!-- Task List with Filters -->
<div class="task-management">
    <div class="filters">
        <select name="status">
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="overdue">Overdue</option>
        </select>
        <select name="priority">
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
        </select>
    </div>
    
    <div class="task-list">
        {% for task in tasks %}
        <div class="task-item priority-{{ task.priority }}">
            <div class="task-header">
                <h4>{{ task.title }}</h4>
                <span class="status-badge status-{{ task.status }}">
                    {{ task.status|title }}
                </span>
            </div>
            <div class="task-meta">
                <span class="due-date">Due: {{ task.due_date|date('M d, Y') }}</span>
                <span class="assignee">{{ task.assigned_user.name }}</span>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
```

### 5. Security Implementation

#### Authentication & Authorization
```python
# Role-based access control decorator
def require_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if not current_user.has_role(role):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Multi-factor authentication
class MFAService:
    def generate_totp_secret(self, user):
        """Generate TOTP secret for user"""
        
    def verify_totp_token(self, user, token):
        """Verify TOTP token"""
        
    def send_sms_token(self, user):
        """Send SMS verification token"""
```

#### Data Encryption
```python
# Sensitive data encryption
class EncryptionService:
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data before storage"""
        
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data for use"""
```

### 6. Background Tasks & Jobs

#### Celery Configuration
```python
# Automated compliance tasks
@celery.task
def generate_recurring_tasks():
    """Generate recurring compliance tasks based on schedules"""

@celery.task  
def send_deadline_notifications():
    """Send notifications for upcoming deadlines"""

@celery.task
def update_compliance_scores():
    """Recalculate compliance scores for all organizations"""

@celery.task
def sync_external_integrations():
    """Sync data from external systems"""
```

### 7. Integration Architecture

#### External Service Integrations
```python
class IntegrationManager:
    def __init__(self):
        self.integrations = {
            'microsoft365': Microsoft365Integration(),
            'google_workspace': GoogleWorkspaceIntegration(),
            'slack': SlackIntegration(),
            'jira': JiraIntegration(),
            'aws': AWSIntegration()
        }
    
    def sync_users(self, org_id, integration_type):
        """Sync users from external systems"""
        
    def collect_evidence(self, org_id, control_id, integration_type):
        """Automatically collect evidence from integrated systems"""
```

### 8. Deployment Architecture

#### Production Environment
```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/comp360flow
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=comp360flow
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
  
  worker:
    build: .
    command: celery -A app.celery worker --loglevel=info
    depends_on:
      - db
      - redis
  
  scheduler:
    build: .
    command: celery -A app.celery beat --loglevel=info
    depends_on:
      - db
      - redis
```

### 9. Performance & Scalability Considerations

#### Database Optimization
- Proper indexing on frequently queried columns
- Connection pooling with SQLAlchemy
- Read replicas for reporting queries
- Partitioning for large evidence tables

#### Caching Strategy
- Redis for session storage
- Application-level caching for compliance calculations
- Template fragment caching for dashboard widgets

#### File Storage
- AWS S3 or similar for evidence files
- CDN for static assets
- Virus scanning for uploaded files

### 10. Monitoring & Observability

#### Application Monitoring
```python
# Logging configuration
import logging
from flask import request
import time

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    logger.info(f"Request: {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Duration: {duration:.3f}s")
    return response
```

#### Health Checks
```python
@app.route('/health')
def health_check():
    try:
        # Check database connectivity
        db.session.execute('SELECT 1')
        
        # Check Redis connectivity
        redis_client.ping()
        
        return {'status': 'healthy', 'timestamp': datetime.utcnow()}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```

This high-level design provides a comprehensive foundation for building Comp360Flow using Python, Flask, Jinja templates, and PostgreSQL. The modular architecture ensures maintainability and scalability while addressing all the key features outlined in the requirements document.
