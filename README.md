# 🏋️ AI Gym & Activity Memory System

AI-powered conversational system to log gym workouts and daily activities using natural language input with semantic memory retrieval.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Overview

Traditional workout tracking apps require manual input of exercises, sets, reps, and weights. This system allows users to log their workouts naturally by saying things like:

- *"I did 3 sets of bench press with 185 lbs today"*
- *"What did I train last Tuesday?"*
- *"Show me my shoulder workouts from this month"*

The system uses **Gemini Flash** for intent extraction and **vector embeddings** for semantic search, enabling intelligent memory retrieval of past activities.

## ✨ Features

- 🗣️ **Natural Language Input** - Log workouts conversationally without structured forms
- 🧠 **Semantic Memory Retrieval** - Ask questions about past workouts using natural language
- 🔍 **Intent Extraction** - Powered by Gemini Flash to understand user intent
- 📊 **Activity Tracking** - Track workouts, cardio, nutrition, and daily activities
- 🎯 **Embedding-based Search** - Find similar workouts using vector similarity
- 💾 **Persistent Storage** - PostgreSQL for structured data + ChromaDB for vectors
- 🚀 **Fast API** - RESTful endpoints built with FastAPI for high performance

## 🏗️ Architecture

```
┌─────────────┐
│    User     │
│   (Voice/   │
│    Text)    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌───────────────────────────────┐  │
│  │   Gemini Flash Service        │  │
│  │   (Intent Extraction)         │  │
│  └───────────┬───────────────────┘  │
│              ▼                       │
│  ┌───────────────────────────────┐  │
│  │   Activity Parser             │  │
│  │   (Extract: exercise, reps,   │  │
│  │    sets, weight, date)        │  │
│  └───────────┬───────────────────┘  │
│              ▼                       │
│  ┌───────────────────────────────┐  │
│  │   Embedding Service           │  │
│  │   (Generate vector            │  │
│  │    representations)           │  │
│  └───────────┬───────────────────┘  │
│              ▼                       │
│  ┌───────────────────────────────┐  │
│  │   Storage Layer               │  │
│  │   • PostgreSQL (structured)   │  │
│  │   • ChromaDB (vectors)        │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│   Retrieval  │
│   • Hybrid   │
│   • Semantic │
│   • Temporal │
└──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Docker & Docker Compose (optional but recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ahadkhan9/ai-gym-memory-system.git
   cd ai-gym-memory-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run with Docker Compose** (Recommended)
   ```bash
   docker-compose up -d
   ```

   OR **Run locally**
   ```bash
   uvicorn src.main:app --reload
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📁 Project Structure

```
ai-gym-memory-system/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── activities.py   # Activity logging endpoints
│   │   │   └── queries.py      # Memory retrieval endpoints
│   │   └── dependencies.py     # Dependency injection
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_service.py   # Gemini Flash integration
│   │   ├── embedding_service.py # Vector embedding generation
│   │   └── memory_service.py   # Memory storage & retrieval
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models
│   └── core/
│       ├── __init__.py
│       └── config.py           # Configuration management
├── tests/
│   ├── __init__.py
│   ├── test_activities.py
│   └── test_memory.py
├── docs/
│   └── architecture.md         # Detailed architecture docs
├── data/
│   └── sample_activities.json  # Sample data for testing
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔌 API Endpoints

### Log Activity
```http
POST /api/v1/activities/log
Content-Type: application/json

{
  "message": "I did 3 sets of bench press with 185 lbs today"
}
```

**Response:**
```json
{
  "activity_id": "uuid-here",
  "parsed_data": {
    "exercise": "bench press",
    "sets": 3,
    "weight": 185,
    "unit": "lbs",
    "date": "2026-01-21"
  },
  "message": "Activity logged successfully!"
}
```

### Query Past Activities
```http
POST /api/v1/queries/search
Content-Type: application/json

{
  "query": "What did I train last Tuesday?"
}
```

**Response:**
```json
{
  "results": [
    {
      "date": "2026-01-14",
      "activities": [
        {
          "exercise": "squat",
          "sets": 4,
          "reps": 8,
          "weight": 225,
          "unit": "lbs"
        }
      ],
      "similarity_score": 0.92
    }
  ]
}
```

## 🧠 Technical Highlights

### 1. Intent Extraction with Gemini Flash
- Uses Google's Gemini Flash model for fast intent understanding
- Extracts structured data from unstructured natural language
- Handles ambiguity and context in user inputs

### 2. Embedding Strategy
- **Activity Embeddings**: Each workout is converted to a vector representation
- **Similarity Search**: Find similar workouts based on semantic meaning
- **Hybrid Approach**: Combines keyword matching with vector similarity

### 3. Memory Persistence
- **Structured Storage**: PostgreSQL for transactional data
- **Vector Storage**: ChromaDB for fast similarity search
- **Metadata Indexing**: Efficient retrieval by date, exercise type, muscle group

### 4. Query Optimization
- Semantic search with configurable similarity thresholds
- Temporal filtering (last week, this month, etc.)
- Result ranking based on relevance and recency

## 🔧 Configuration

Key environment variables in `.env`:

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-flash

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/gym_memory
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Embedding
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# API
API_VERSION=v1
LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_activities.py -v
```

## 🚀 Future Enhancements

- [ ] **Workout Recommendations** - Suggest exercises based on training history
- [ ] **Progress Tracking** - Visualize strength gains and volume over time
- [ ] **Voice Input Integration** - Direct voice-to-text logging
- [ ] **Multi-user Support** - User authentication and isolated data
- [ ] **Mobile App** - iOS/Android clients
- [ ] **Nutrition Integration** - Track meals and macros alongside workouts
- [ ] **AI Coaching** - Personalized workout plans based on goals

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)

## 👨‍💻 Author

**Ahad Ahmad Khan**
- GitHub: [@ahadkhan9](https://github.com/ahadkhan9)
- LinkedIn: [Ahad Khan](https://www.linkedin.com/in/ahadkhan9)
- Email: ahadkhan5547@gmail.com

---

⭐ **Star this repo if you find it useful!**
