# Urban-Infra

Multi-agent system for urban planning analysis in San Francisco neighborhoods.

## Architecture

- **Backend**: FastAPI + CrewAI + PostgreSQL/PostGIS
- **Frontend**: Next.js + ShadCN UI + MapLibre GL JS
- **Agents**: Interpreter → Planner → Evaluator

## Target Neighborhoods

- Marina District (low density, transit-poor)
- Hayes Valley (transit-rich, gentrification pressure)
- Mission District (dense, equity concerns)

## Development

```bash
# Start with Docker
docker-compose up -d

# Or run individually
cd backend && uvicorn main:app --reload
cd frontend && npm run dev
```

## API Endpoints

- `POST /scenarios` - Create new scenario
- `GET /scenarios/{id}` - Get scenario results
- `GET /health` - Health check