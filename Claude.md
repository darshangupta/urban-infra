# Urban-Infra: Multi-Agent Urban Planning System

**A comprehensive AI-powered tool for urban planning analysis in San Francisco neighborhoods using real data and constraint validation.**

---

## 🏙️ Project Overview

Urban-Infra is a multi-agent system that answers complex urban planning questions like:
- *"What if we added affordable housing near BART in Hayes Valley?"*
- *"How can we make the Marina more walkable while respecting flood risks?"*  
- *"What zoning changes would prevent displacement in the Mission?"*

The system provides **concrete, implementable recommendations** backed by real SF zoning laws, demographic data, and spatial analysis.

---

## 🎯 Target Neighborhoods

### Marina District
- **Characteristics**: Low density, waterfront, affluent
- **Zoning**: RH-1 (Residential House, One-Family)
- **Constraints**: Flood risk, limited transit, height restrictions
- **Planning Focus**: Climate resilience, walkability improvements

### Hayes Valley  
- **Characteristics**: Transit-rich, mixed-use, gentrifying
- **Zoning**: NCT-3 (Neighborhood Commercial Transit)  
- **Constraints**: Historic preservation, displacement pressure
- **Planning Focus**: Transit-oriented development, anti-displacement

### Mission District
- **Characteristics**: Dense, diverse, cultural significance
- **Zoning**: NCT-4 (High-density mixed-use)
- **Constraints**: Displacement risk, cultural preservation
- **Planning Focus**: Community-controlled development, equity

---

## 🚀 What We've Built (Completed)

### ✅ Infrastructure Foundation
- **Docker Environment**: PostGIS (port 5434) + Redis (port 6379)
- **Database**: Real SF neighborhood data loaded and queryable
- **API Server**: FastAPI with auto-generated docs at `/docs`
- **Testing**: Comprehensive constraint validation test suite (8/8 passing)

### ✅ Real SF Data Integration
```bash
# Loaded and validated:
- SF Open Data Portal (zoning, parcels, demographics)
- Real zoning classifications (RH-1, RM-2, NCT-3, NCT-4)  
- Transit accessibility data (BART, Muni stops)
- Flood zones and seismic constraints
- Cultural asset locations and displacement risk indicators
```

### ✅ Constraint Validation System
**Implements actual SF Planning Code rules:**
- Floor Area Ratio (FAR) limits by zone
- Height restrictions (40ft Marina, 85ft Mission corridors)
- Setback requirements and parking mandates
- Inclusionary housing percentages (12%-25% by zone)
- Ground floor commercial requirements in transit zones

**Example validation:**
```python
# Marina District proposal validation
validator.validate_zoning_proposal(
    zone_type=SFZoneType.RH_1,
    proposed_far=2.0,      # ❌ Exceeds 0.8 limit
    proposed_height_ft=60, # ❌ Exceeds 40ft limit
    num_units=8            # ✅ Triggers inclusionary requirement
)
# Returns: violations with specific suggestions for compliance
```

### ✅ Working API Endpoints
**Base URL**: `http://localhost:8000/api/v1`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/neighborhoods/` | GET | List all SF neighborhoods with zoning data |
| `/neighborhoods/{name}/zoning` | GET | Get zoning rules for specific neighborhood |
| `/neighborhoods/{name}/validate-proposal` | POST | Check if development proposal is legal |
| `/neighborhoods/{name}/unit-estimates` | GET | Calculate realistic unit counts for lot |
| `/neighborhoods/{name}/suggest-upzoning` | POST | Recommend zoning changes for target units |

**Example API Call:**
```bash
curl -X POST http://localhost:8000/api/v1/neighborhoods/hayes_valley/validate-proposal \
  -H "Content-Type: application/json" \
  -d '{
    "far": 3.0,
    "height_ft": 55, 
    "lot_area_sf": 3000,
    "num_units": 15
  }'

# Response includes:
# - Legal feasibility (pass/fail)
# - Specific violations with suggestions
# - Inclusionary housing requirements
# - Zoning compliance recommendations
```

---

## 🤖 3-Agent System Architecture

### Agent 1: Interpreter
**Role**: Natural language → Structured planning parameters
- **Input**: *"Add affordable housing near transit in Hayes Valley"*
- **Processing**: 
  - Identify neighborhood (Hayes Valley)
  - Extract intent (housing development)
  - Determine constraints (near transit, affordability focus)
  - Call neighborhood APIs for context
- **Output**: TwistPack with bounded parameters for planning

### Agent 2: Planner  
**Role**: Generate feasible development scenarios
- **Input**: TwistPack from Interpreter
- **Processing**:
  - Generate 3-5 candidate plans using constraint APIs
  - Each plan: specific FAR, height, amenity locations
  - Filter using `/validate-proposal` endpoint
  - Rank by feasibility and policy alignment
- **Output**: Feasible planning alternatives with rationale

### Agent 3: Evaluator
**Role**: Calculate before/after impact analysis  
- **Input**: Candidate plans from Planner
- **Processing**:
  - Use `/unit-estimates` for housing impact
  - Calculate accessibility changes (walk to amenities)
  - Assess equity implications (displacement, affordability)
  - Generate KPI dashboard with spatial metrics
- **Output**: Comprehensive impact analysis with recommendations

---

## 🌍 World Model Strategy

### Hybrid Approach: Real Constraints + Predictive Models

**Level 1: Deterministic (Implemented)**
- Real SF zoning laws (authoritative)
- Spatial calculations (distances, areas)
- Unit estimation based on actual SF development patterns

**Level 2: Lightweight Prediction (Planned)**  
- Pre-computed accessibility isochrones
- Housing market elasticity (price impacts)
- Demographic displacement risk scoring

**Level 3: Dynamic Simulation (Future)**
- Agent-based neighborhood modeling
- Economic gentrification effects
- Long-term spatial development patterns

---

## 🛠️ Technical Stack

### Backend Infrastructure
```yaml
Framework: FastAPI 0.104.1
Database: PostgreSQL 16 + PostGIS 3.4
Caching: Redis 7-alpine
Validation: Pydantic schemas + custom SF rules
Testing: Pytest with async support
Spatial: GeoAlchemy2 for PostGIS integration
```

### Frontend (Planned)
```yaml
Framework: Next.js 14 + TypeScript
UI Components: ShadCN UI + Tailwind CSS
Maps: MapLibre GL JS + SF basemap tiles  
State: React Query + Zustand
Visualization: D3.js for KPI charts
```

### Development Environment  
```yaml
Local Development: Docker + Docker Compose
Database Admin: Supabase Dashboard (production-ready)
API Docs: FastAPI auto-generated (local + deployed)
Code Quality: pytest + black + type checking
```

### Production Deployment
```yaml
Database: Supabase (PostgreSQL + PostGIS + dashboard)
Backend API: Vercel (FastAPI as serverless functions)
Frontend: Vercel (Next.js + ShadCN + MapLibre)
Domain: Custom domain via Vercel
Monitoring: Vercel Analytics + Supabase Logs
```

---

## 📊 Example Use Cases & Outputs

### Scenario 1: Hayes Valley Housing Development
**Input**: *"What if we added 200 affordable units near the Hayes Valley BART station?"*

**System Processing**:
1. **Interpreter**: Hayes Valley → NCT-3 zoning → transit accessibility = excellent
2. **Planner**: Generate plans with FAR 2.5-3.0, height 45-55ft, 20-25% affordable
3. **Evaluator**: Calculate displacement risk, transit load, neighborhood character impact

**Expected Output**:
```json
{
  "scenario": "Hayes Valley Affordable Development",
  "feasible_plans": 3,
  "recommended_plan": {
    "far": 2.8,
    "height_ft": 50,
    "total_units": 185,
    "affordable_units": 46,
    "zoning_compliance": "requires_variance_parking"
  },
  "impacts": {
    "transit_access": "92% within 5-min walk to BART",
    "displacement_risk": "medium - requires community benefits",
    "affordability": "improves 15% affordable housing in neighborhood"
  },
  "recommendations": [
    "Request parking variance due to excellent transit",
    "Include community space in ground floor",
    "Phase development to minimize displacement"
  ]
}
```

### Scenario 2: Marina Climate Resilience  
**Input**: *"How can we make the Marina more walkable while preparing for sea level rise?"*

**Expected Output**: 
- Elevated development recommendations (above flood zones)
- Bike/pedestrian infrastructure that doubles as flood barriers
- Mixed-use zoning suggestions for neighborhood amenities
- Cost-benefit analysis of different resilience strategies

### Scenario 3: Mission Anti-Displacement
**Input**: *"Increase density in the Mission without displacing existing residents"*

**Expected Output**:
- Community land trust development strategies  
- Inclusionary housing maximization (25% in NCT-4)
- Cultural business district preservation zones
- Resident equity ownership models

---

## 🧪 Quality Assurance & Validation

### Constraint Accuracy
- **Real SF Zoning Rules**: All constraints based on actual Planning Code
- **Test Coverage**: 100% of zoning validations tested against known scenarios
- **Ground Truth**: Validated against actual approved developments (pending)

### Spatial Data Quality
- **Source**: SF Open Data Portal (authoritative)
- **Verification**: Cross-referenced with planning documents
- **Updates**: Automated refresh pipeline for data currency

### Agent Reliability
- **Deterministic Core**: Constraint validation always returns consistent results  
- **Bounded Outputs**: All recommendations within feasible parameter ranges
- **Audit Trail**: Complete logging of agent decisions and reasoning

---

## 🗺️ Development Roadmap

### Phase 1: Complete Core System (Current)
- [x] Infrastructure and data pipeline
- [x] Constraint validation system
- [x] API endpoints with SF integration
- [ ] **Agent 1**: Interpreter (natural language processing)
- [ ] **Agent 2**: Planner (scenario generation)
- [ ] **Agent 3**: Evaluator (impact analysis)
- [ ] Agent orchestration and testing

### Phase 2: Interactive Frontend
- [ ] Next.js application with SF neighborhood maps
- [ ] Interactive scenario input forms
- [ ] Real-time constraint validation feedback
- [ ] Before/after map visualizations
- [ ] KPI dashboard with charts and metrics
- [ ] Export functionality (reports, GIS data)

### Phase 3: Production Validation
- [ ] Test against 10 actual SF development precedents
- [ ] Validate recommendations with SF planning professionals
- [ ] Performance optimization for city-scale analysis
- [ ] Error handling and edge case coverage

### Phase 4: Scaling & Enhancement
- [ ] Additional SF neighborhoods (SOMA, Richmond, Sunset)
- [ ] Other Bay Area cities (Oakland, Berkeley)
- [ ] Advanced world modeling (economic impacts)
- [ ] Real-time collaboration features
- [ ] Public deployment and API access

---

## 🚦 Getting Started

### Quick Start (View Current System)
```bash
# 1. Ensure Docker containers are running
docker ps  # Should see postgres and redis

# 2. Start API server
cd backend
source ../venv/bin/activate  
python -m uvicorn app.main:app --reload

# 3. View API documentation
open http://localhost:8000/docs

# 4. Test neighborhood endpoint
curl http://localhost:8000/api/v1/neighborhoods/
```

### Development Setup
```bash
# 1. Clone and setup
git clone [repo-url]
cd urban-infra
python3 -m venv venv
source venv/bin/activate

# 2. Start infrastructure  
docker run -d --name postgres -p 5434:5432 postgis/postgis:latest
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 3. Load SF data
python scripts/test_data_load.py

# 4. Run tests
cd backend && python -m pytest tests/ -v

# 5. Start development server
python -m uvicorn app.main:app --reload
```

### Database Viewing Options
```bash
# Option 1: Drizzle Studio (recommended)
npm install drizzle-kit drizzle-orm
npx drizzle-kit studio  # Opens at localhost:4983

# Option 2: Direct SQL queries
docker exec postgres psql -U postgres -d urban_infra \
  -c "SELECT name, area_type, data->>'zoning' FROM sf_neighborhoods;"

# Option 3: API endpoints
curl http://localhost:8000/api/v1/neighborhoods/ | jq
```

---

## 📈 Success Metrics

### Technical Metrics
- **API Response Time**: <2 seconds for constraint validation
- **Test Coverage**: 100% for constraint validation, 80%+ overall
- **Data Freshness**: SF data updated quarterly
- **System Uptime**: 99.9% availability target

### Planning Quality Metrics  
- **Feasibility Accuracy**: 95%+ of recommendations legally implementable
- **Stakeholder Validation**: Positive feedback from SF planning professionals
- **Real-World Correlation**: Recommendations align with actual approved projects
- **User Satisfaction**: Planning workflows 50%+ faster than traditional methods

---

## 🤝 Contributing & Collaboration

### Code Standards
- Python: Black formatting, type hints, comprehensive docstrings
- JavaScript: Prettier + ESLint, TypeScript strict mode
- SQL: Consistent naming, proper indexing, spatial optimization
- Tests: Pytest for backend, Jest for frontend, >80% coverage

### Planning Domain Expertise
- Urban planning professionals: feedback on recommendation quality
- SF neighborhood advocates: community impact validation  
- GIS specialists: spatial analysis accuracy verification
- Policy experts: zoning compliance and legal feasibility

### Data & Research
- SF Open Data Portal integration and validation
- Academic partnerships for urban planning research
- Community input on neighborhood priorities and constraints

---

## 📚 Technical Documentation

### API Reference
- **OpenAPI Spec**: Available at `/docs` when server running
- **Postman Collection**: Import from `/openapi.json`
- **Example Requests**: See `scripts/test_api_calls.sh`

### Database Schema
- **PostGIS Tables**: SF neighborhoods, zoning, constraints
- **Spatial Indexes**: Optimized for neighborhood queries
- **Migration Scripts**: Alembic for schema versioning

### Agent Implementation
- **CrewAI Integration**: Multi-agent orchestration patterns
- **Tool Calling**: Structured interaction with FastAPI endpoints  
- **State Management**: Scenario persistence and caching strategies

---

## 🔮 Future Vision

**Urban-Infra aims to become the standard tool for AI-assisted urban planning**, enabling planners, developers, and community advocates to:**

- **Rapidly prototype** development scenarios with real constraint validation
- **Understand impacts** before implementation through predictive modeling  
- **Ensure equity** by quantifying displacement and affordability effects
- **Navigate complexity** of zoning laws, environmental constraints, and community priorities
- **Facilitate collaboration** between stakeholders with shared data and analysis

**Long-term goal**: Every major development decision in SF (and beyond) informed by AI-powered impact analysis that balances growth, equity, sustainability, and community needs.

---

## 📞 Contact & Status

**Current Status**: Phase 1 - Core system 70% complete
**Next Milestone**: Working 3-agent system demonstration  
**Timeline**: MVP ready for testing by end of current development cycle

**Project Repository**: [GitHub URL when ready]
**Documentation**: This CLAUDE.md file (maintained as living document)  
**Issues & Feedback**: GitHub Issues or direct collaboration

---

*Last Updated: September 2024*
*Status: Active Development*
*License: [To be determined]*

Avoid redundancy in code! make sure we are succint and efficient in how we write