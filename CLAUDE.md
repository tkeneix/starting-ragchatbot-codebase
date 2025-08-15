# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
- **Start server**: `./run.sh` (creates docs directory and runs backend server)
- **Manual start**: `cd backend && uv run uvicorn app:app --reload --port 8000`
- **Install dependencies**: `uv sync`

### Environment Setup
- Requires `.env` file in root with `ANTHROPIC_API_KEY=your_key_here`
- Python 3.13+ and uv package manager required
- Uses Claude Sonnet 4 model (claude-sonnet-4-20250514)

## Architecture Overview

This is a full-stack RAG (Retrieval-Augmented Generation) system for querying course materials:

### Backend Components (`backend/`)
- **app.py**: FastAPI server with API endpoints (`/api/query`, `/api/courses`) and static file serving
- **rag_system.py**: Main orchestrator coordinating all components
- **document_processor.py**: Parses course documents with specific format (Course Title/Link/Instructor + Lesson markers)
- **vector_store.py**: ChromaDB wrapper with dual collections (course_catalog, course_content)
- **ai_generator.py**: Anthropic Claude integration for response generation
- **session_manager.py**: Conversation history management
- **search_tools.py**: Tool-based search system for Claude function calling
- **models.py**: Pydantic models (Course, Lesson, CourseChunk)
- **config.py**: Configuration with environment variable loading

### Frontend (`frontend/`)
- Static HTML/CSS/JS served by FastAPI
- Uses marked.js for markdown rendering
- Real-time chat interface with session management

### Document Format
Course documents must follow this structure:
```
Course Title: [title]
Course Link: [url]
Course Instructor: [instructor]

Lesson 1: [lesson title]
Lesson Link: [lesson url]
[lesson content]

Lesson 2: [lesson title]
...
```

### Key Technical Details
- Uses sentence-based chunking with configurable overlap (800 chars, 100 overlap)
- Dual vector store: metadata search for course resolution + content search
- Tool-based RAG approach where Claude calls search functions
- Automatic course loading from `docs/` folder on startup
- Session-based conversation with configurable history (2 messages)
- ChromaDB persistent storage in `./chroma_db`

### Data Flow
1. Documents processed into Course/Lesson objects and text chunks
2. Metadata stored in course_catalog collection for semantic course matching
3. Content chunks stored in course_content collection with course/lesson metadata
4. Queries resolved via tool calling: course name resolution → filtered content search
5. AI generates responses using retrieved context and conversation history

## Configuration
- Chunk size: 800 characters with 100 character overlap
- Max search results: 5
- Embedding model: all-MiniLM-L6-v2
- Max conversation history: 2 exchanges