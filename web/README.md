# Collectivist Web Interface

Complete web interface for non-terminal users.

## Backend (FastAPI)

```bash
# Install dependencies
pip install -r ../requirements.txt

# Run backend server
cd backend
python main.py
```

Server runs on http://localhost:8000

## Frontend (Vite + React)

```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev
```

Frontend runs on http://localhost:5173

## Features

- **Collection Management**: Add, configure, and delete collections
- **Pipeline Execution**: Run any pipeline stage with real-time progress
- **LLM Configuration**: Configure any LLM provider (OpenAI, Anthropic, OpenRouter, Local)
- **Real-time Updates**: WebSocket-powered live progress updates
- **No Styling**: Pure functional UI scaffold - add your own styling

## API Endpoints

- `GET /collections` - List collections
- `POST /collections` - Create collection
- `PUT /collections/{id}` - Update collection
- `DELETE /collections/{id}` - Delete collection
- `POST /collections/{id}/run` - Run pipeline
- `GET /config/llm` - Get LLM config
- `PUT /config/llm` - Update LLM config
- `POST /config/llm/test` - Test LLM connection
- `WS /ws` - WebSocket for real-time events