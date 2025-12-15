# Progress Service

* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [GraphQL API](#graphql-api)
* [Application features](#application-features)

## General info

<details>
<summary>Click here to see general information about <b>Project</b>!</summary>
<b>Progress Service - Online Learning Platform API</b>.
FastAPI-based GraphQL API for tracking user progress, completed lessons/courses, learning statistics, certificates, and achievements in an online programming learning platform.
</details>

## Tools & Technologies

<ul>
<li>Python 3.12+</li>
<li>FastAPI</li>
<li>Strawberry GraphQL</li>
<li>SQLAlchemy (async)</li>
<li>PostgreSQL</li>
<li>Alembic</li>
<li>Pydantic</li>
<li>Pydantic Settings</li>
</ul>

## Setup

### Prerequisites

- Python 3.12 or higher
- PostgreSQL 17.0 or higher
- Poetry (for dependency management)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/wszeborj/Progress_Service.git
```

2. Go to project folder:
```bash
cd Progress_Service
```

3. Install Poetry (if not already installed):
```bash
pip install poetry
```

4. Install all dependencies:
```bash
poetry install
```

5. Create a `.env` file in the root directory:
```env
```

6. Create PostgreSQL database:
```bash
psql -U postgres
# Provide password
CREATE DATABASE progress_service_db;
\q
```

7. Run database migrations:
```bash
alembic upgrade head
```

8. Run the application:
```bash
poetry run fastapi dev app/main.py
```

Or using uvicorn directly:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Setup

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The service will be available at `http://localhost:8300`

## GraphQL API

### Endpoint

- **GraphQL Endpoint**: `http://localhost:8000/graphql`
- **GraphQL Playground**: `http://localhost:8000/graphql` (when `graphql_playground=True`)

### Queries

#### Get all user progress

##### Returns all course progress entries for a user.
```
query GetUserProgress($userId: Int!) {
  getUserProgress(userId: $userId) {
    id
    courseId
    status
    completionPercentage
    totalTimeSpent
    lastAccessedAt
    startedAt
    completedAt
    notes
  }
}
```

###### Variables
```
{
  "userId": 1
}
```

##### Get progress for a specific course
```
query GetProgress($userId: Int!, $courseId: Int!) {
  getProgress(userId: $userId, courseId: $courseId) {
    id
    status
    completionPercentage
    totalTimeSpent
    startedAt
    completedAt
  }
}
```

###### Variables
```
{
  "userId": 1,
  "courseId": 10
}
```
##### Get completed courses (IDs only)
```
query GetCompletedCourses($userId: Int!) {
  getCompletedCourses(userId: $userId)
}
```

###### Variables
```
{
  "userId": 1
}
```

##### Get user achievements
```
query GetUserAchievements($userId: Int!) {
  getUserAchievements(userId: $userId) {
    id
    achievementType
    achievementName
    description
    earnedAt
  }
}
```

##### Get user achievements filtered by type
```
query GetUserAchievementsByType($userId: Int!, $type: String!) {
  getUserAchievements(userId: $userId, achievementType: $type) {
    id
    achievementName
    earnedAt
  }
}
```

###### Variables
```
{
  "userId": 1,
  "type": "MILESTONE"
}
```

##### Get user certificates
```
query GetUserCertificates($userId: Int!) {
  getUserCertificates(userId: $userId) {
    id
    courseId
    finalScore
    grade
    completionTime
    expiresAt
    pdfUrl
  }
}
```

##### Get a specific certificate
```
query GetCertificate($userId: Int!, $courseId: Int!) {
  getCertificate(userId: $userId, courseId: $courseId) {
    id
    finalScore
    grade
    pdfUrl
  }
}
```

##### Get user learning statistics
```
query GetUserStatistics($userId: Int!) {
  getUserStatistics(userId: $userId) {
    userId
    totalCompletedLessons
    totalCoursesInProgress
    totalCompletedCourses
    totalCertificates
    totalAchievements
    totalTimeSpentSeconds
    averageCompletionPercentage
  }
}
```
### Mutations
#### Update or create user progress

##### Creates a new progress entry if it does not exist, otherwise updates it.
```
mutation UpdateUserProgress($userId: Int!, $input: UpdateProgressInput!) {
  updateUserProgress(userId: $userId, input: $input) {
    id
    courseId
    status
    completionPercentage
    totalTimeSpent
    lastAccessedAt
  }
}
```

###### Variables
```
{
  "userId": 1,
  "input": {
    "courseId": 10,
    "status": "IN_PROGRESS",
    "completionPercentage": 45.0,
    "timeSpentSeconds": 1200,
    "notes": "Halfway through the course"
  }
}
```
##### Create achievement
```
mutation CreateAchievement($userId: Int!, $input: CreateAchievementInput!) {
  createAchievement(userId: $userId, input: $input) {
    id
    achievementType
    achievementName
    earnedAt
  }
}
```

###### Variables
```
{
  "userId": 1,
  "input": {
    "achievementType": "MILESTONE",
    "achievementName": "First Course Completed",
    "description": "Completed your first course"
  }
}
```
#### Create course certificate

##### If a certificate already exists, the existing one is returned.
```
mutation CreateCertificate($userId: Int!, $input: CreateCertificateInput!) {
  createCertificate(userId: $userId, input: $input) {
    id
    courseId
    finalScore
    grade
    completionTime
    pdfUrl
  }
}
```

###### Variables
```
{
  "userId": 1,
  "input": {
    "courseId": 10,
    "finalScore": 95.5,
    "grade": "A",
    "pdfUrl": "https://example.com/certificates/course-10.pdf",
    "notes": "Excellent performance"
  }
}
```

## Application features

* **Progress Tracking**: Track completion status of lessons and courses
* **Statistics**: Comprehensive learning statistics for users
* **Certificates**: Automatic certificate generation upon course completion
* **Achievements**: Track and manage user achievements
* **GraphQL API**: Flexible and efficient GraphQL API for data fetching
* **Async Operations**: Fully asynchronous database operations
* **Auto Documentation**: GraphQL Playground for interactive API exploration
* **Database Migrations**: Alembic for database schema management
* **Type Safety**: Full type hints and Pydantic validation

## Database Models

### LessonProgress
Tracks the completion status of individual lessons for users.

### CourseCertificate
Stores certificates earned by users upon completing courses.

### Achievement
Tracks various achievements earned by users (e.g., first lesson, course completion, streaks).

## Development

### Running Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

### Code Quality

The project uses:
- **mypy** for type checking
- **pre-commit** hooks for code quality
- **bandit** for security scanning

Run type checking:
```bash
poetry run mypy app
```

## Integration

This service is designed to work with:
- **API Gateway**: Routes requests to this service
- **User Service**: For user authentication and profile management
- **Course Service**: For course, lesson, and exercise data

## License

This project is part of the Online Learning Platform microservices architecture.
