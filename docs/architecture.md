# Architecture Documentation

## System Overview

The AI Gym & Activity Memory System is designed as a microservices-based architecture with clear separation of concerns. The system processes natural language input, extracts structured information, stores it efficiently, and enables semantic retrieval.

## Core Components

### 1. API Layer (FastAPI)

**Purpose:** Expose RESTful endpoints for activity logging and querying

**Key Responsibilities:**
- Request validation using Pydantic models
- Route handling and request/response transformation
- Error handling and HTTP status management
- API documentation (OpenAPI/Swagger)

**Endpoints:**
- `POST /api/v1/activities/log` - Log new activities
- `POST /api/v1/queries/search` - Search past activities
- `GET /api/v1/stats` - Get workout statistics
- `GET /health` - Health check endpoint

### 2. Gemini Service

**Purpose:** Extract structured information from natural language input

**Technology:** Google Gemini Flash API

**Process Flow:**
1. Receive natural language message
2. Construct prompt with extraction instructions
3. Call Gemini API with structured output schema
4. Parse response into `ParsedActivity` model
5. Return structured data

**Example Transformation:**
```
Input: "I did 3 sets of bench press with 185 lbs today"

Output:
{
  "exercise": "bench press",
  "sets": 3,
  "reps": null,
  "weight": 185,
  "unit": "lbs",
  "date": "2026-01-21"
}
```

**Prompt Engineering Strategy:**
- Few-shot examples for common workout patterns
- Clear output schema definition
- Handling of ambiguous inputs
- Context preservation for follow-up messages

### 3. Embedding Service

**Purpose:** Generate vector representations of activities for semantic search

**Technology:** Sentence Transformers (all-MiniLM-L6-v2)

**Process:**
1. Convert activity to text representation
   - Example: "bench press, 3 sets, 185 lbs, chest workout"
2. Generate 384-dimensional embedding vector
3. Store vector in ChromaDB with metadata

**Embedding Strategy:**
- Combine exercise name, muscle group, and key metrics
- Include temporal context (day of week, time of day)
- Normalize numerical values for consistency

**Vector Similarity:**
- Cosine similarity for finding related workouts
- Threshold-based filtering (default: 0.7)
- Hybrid search combining semantic + keyword matching

### 4. Memory Service

**Purpose:** Manage storage and retrieval of activity data

**Dual Storage Approach:**

#### PostgreSQL (Structured Data)
- User profiles and authentication
- Activity records with timestamps
- Aggregated statistics and metrics
- Relational queries for reporting

**Schema:**
```sql
CREATE TABLE activities (
    id UUID PRIMARY KEY,
    user_id UUID,
    exercise VARCHAR(255),
    sets INTEGER,
    reps INTEGER,
    weight DECIMAL(10, 2),
    unit VARCHAR(10),
    duration INTEGER,
    notes TEXT,
    created_at TIMESTAMP,
    embedding_id VARCHAR(255)
);
```

#### ChromaDB (Vector Data)
- Activity embeddings for semantic search
- Metadata indexing (date, exercise type, muscle group)
- Fast similarity search with filtering

**Collection Schema:**
```python
{
    "id": "activity_uuid",
    "embedding": [0.123, -0.456, ...],  # 384-dim vector
    "metadata": {
        "exercise": "bench press",
        "date": "2026-01-21",
        "muscle_group": "chest",
        "user_id": "user_uuid"
    },
    "document": "bench press, 3 sets, 185 lbs"
}
```

### 5. Query Processing

**Retrieval Pipeline:**

1. **Intent Recognition** (Gemini Flash)
   - Extract temporal filters (last week, Tuesday, etc.)
   - Identify exercise type or muscle group filters
   - Determine query type (search, stats, comparison)

2. **Vector Search** (ChromaDB)
   - Generate embedding for query text
   - Perform similarity search with metadata filters
   - Apply temporal and categorical constraints
   - Return top-k similar activities

3. **Reranking** (Optional)
   - Boost results by recency
   - Prioritize exact exercise matches
   - Consider user preferences

4. **Response Formatting**
   - Group activities by date
   - Calculate aggregate statistics
   - Include similarity scores

## Data Flow

### Activity Logging Flow

```
User Input → FastAPI Endpoint
    ↓
Gemini Service (Intent Extraction)
    ↓
Parsed Activity Data
    ↓
┌─────────────────┬─────────────────┐
│                 │                 │
PostgreSQL        Embedding Service
(Structured)            ↓
                  ChromaDB
                  (Vectors)
```

### Query Retrieval Flow

```
User Query → FastAPI Endpoint
    ↓
Gemini Service (Query Understanding)
    ↓
Temporal/Categorical Filters
    ↓
ChromaDB Similarity Search
    ↓
PostgreSQL Enrichment (additional data)
    ↓
Response Aggregation & Formatting
    ↓
Return Results to User
```

## Scalability Considerations

### Current Architecture (Single Instance)
- Suitable for 1-1000 users
- Single FastAPI instance
- Single PostgreSQL instance
- Single ChromaDB instance

### Scaling Strategy (Future)

**Horizontal Scaling:**
- Load balancer → Multiple FastAPI instances
- PostgreSQL read replicas
- ChromaDB sharding by user cohorts

**Performance Optimization:**
- Redis caching for frequent queries
- Background task queue for embeddings (Celery)
- Batch embedding generation
- CDN for static assets

**Monitoring:**
- Prometheus metrics collection
- Grafana dashboards
- Error tracking (Sentry)
- API latency monitoring

## Security

- API key rotation for Gemini
- Environment variable management (.env)
- PostgreSQL connection pooling with SSL
- Input sanitization to prevent injection
- Rate limiting on API endpoints
- User authentication (JWT tokens)

## Future Enhancements

1. **Real-time Sync** - WebSocket support for live updates
2. **Multi-modal Input** - Voice and image input (form videos)
3. **Personalized Recommendations** - ML-based workout suggestions
4. **Social Features** - Share workouts, follow friends
5. **Progressive Web App** - Offline-first mobile experience
6. **Advanced Analytics** - Strength progression, volume tracking
