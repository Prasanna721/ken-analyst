# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ken Analyst is a financial analysis platform consisting of:
- **API** (FastAPI backend) - `/api/`
- **Web** (Next.js frontend) - `/web/`

## Development Commands

### API (FastAPI)
```bash
cd api

# Install dependencies
.venv/bin/pip install -r requirements.txt

# Run development server
.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --reload

# Environment setup
# Create .env file with: API_SECRET=your_secret_here
```

### Web (Next.js)
```bash
cd web

# Install dependencies
npm install

# Setup environment
cp .env.local.example .env.local
# Edit .env.local with:
# - NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
# - NEXT_PUBLIC_HASHED_API_SECRET=<sha256 hash of API_SECRET>

# Generate hashed API secret:
cd ../api && .venv/bin/python -c "import hashlib; print(hashlib.sha256('YOUR_API_SECRET'.encode()).hexdigest())"

# Run development server
npm run dev        # http://localhost:3000

# Production
npm run build      # Build for production
npm start          # Start production server
npm run lint       # Run linter
```

## Architecture

### API Structure
- **Database**: SQLite (`data/ken-analyst.db`) with SQLAlchemy ORM
- **Authentication**: Bearer token (SHA256 hash of API_SECRET from .env)
- **Data Storage**: Workspace folders in `data/{workspace_id}/`

#### Database Schema
- **workspaces**: id, name, ticker, created_at
- **documents**: id, workspace_id, doc_type (10_Q, 10_K, other), file_path, filing_date, reporting_date, doc_id
- **parsed_documents**: id, workspace_id, documents_id, filepath

Cascade deletes: workspace deletion removes all related documents and parsed_documents; document deletion removes related parsed_documents.

#### API Endpoints

**Public Endpoints:**
- `POST /create_workspace` - Create workspace with optional file upload and/or ticker filings
  - Params: workspace_id (optional), ticker (optional), file (optional)
  - Handles zip extraction and flattening
  - Downloads 10-Q and 10-K filings if ticker provided

**Authenticated Endpoints** (require Bearer token):
- `GET /search?q={query}` - Search listed companies from CSV
- `GET /filings?tick={ticker}&inter={quarterly|yearly}` - Download SEC filings

**Database CRUD APIs** (pattern: `/data/{resource}`):
- `GET /data/workspace` - Get all workspaces
- `GET /data/workspace/{workspace_id}` - Get workspace by ID
- `POST /data/workspace` - Create workspace
- `PUT /data/workspace/{workspace_id}` - Update workspace
- `DELETE /data/workspace/{workspace_id}` - Delete workspace
- `GET|POST|PUT|DELETE /data/documents` - Document operations
- `GET|POST|PUT|DELETE /data/parsed_documents` - Parsed document operations

**Key Behaviors:**
- File uploads: Single files copied to workspace folder, zips extracted and flattened
- SEC filings: Downloaded to `data/{workspace_id}/`, dates extracted (YYYYMMDD → YYYY/MM/DD)
- Workspace creation auto-generates 8-char alphanumeric ID if not provided

### Web Structure
- **Framework**: Next.js 15 App Router with TypeScript
- **Styling**: Tailwind CSS with custom theme tokens
- **API Integration**: All API calls go through `apiRequest()` function in `lib/api.ts`
  - Authentication: Pre-hashed API secret sent as Bearer token
  - Environment variables: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_HASHED_API_SECRET`
  - Common request layer handles auth headers automatically for endpoints requiring auth
- **Layout Pattern**: Full-height viewport (`h-screen`), no scrolling beyond viewport
- **Fonts**:
  - Heading: Instrument Serif (`font-heading`) - loaded via next/font
  - Body: Monument Grotesk Mono (`font-sans`) - regular, medium, bold weights

## Design System

### Theme: Light Minimalist
- **Background**: White/light backgrounds
- **Accent**: Light golden hue (#F5E6D3, #D4AF37 family)
- **Typography**: Sharp, clean sans-serif (Monument) with elegant serif accents (Instrument Serif)
- **UI Elements**: Sharp corners (no border-radius), minimal borders, ample whitespace
- **Visual Style**: Clean lines, geometric precision, subtle golden accents for emphasis

### Color Palette
- Primary Background: `#FFFFFF`
- Secondary Background: `#FAFAF9`
- Accent Golden: `#D4AF37` (primary accent)
- Light Golden: `#F5E6D3` (subtle backgrounds/hover states)
- Text Primary: `#1A1A1A`
- Text Secondary: `#737373`
- Border: `#E5E5E5`

### Component Guidelines
- Use sharp corners (no rounded corners)
- Minimal borders, prefer subtle shadows or background changes
- Golden accent for interactive elements, highlights, and CTAs
- Generous padding and spacing
- Clean typography hierarchy with Monument for UI, Instrument Serif for headings

## Important Patterns

### API Service Layer
- Services in `api/services/` handle business logic
- Routers in `api/routers/` handle HTTP endpoints
- Models in `api/models.py` define both SQLAlchemy and Pydantic schemas
- Database session dependency: `db: Session = Depends(get_db)`

### Frontend Data Flow
1. Components call functions from `lib/api.ts`
2. API client handles authentication (SHA-256 hash) and requests
3. Use client components (`"use client"`) for interactive features
4. Components consume API responses and update local state

### File Structure Conventions
- API routes follow RESTful patterns
- Internal database APIs: `/data/{resource_name}`
- Frontend components in `components/`, pages in `app/`
- Shared utilities in `lib/`

## Code Style

- Only add comments if necessary, not changed this or fixed from nothing like that
- Prefer functional components in React
- Use TypeScript strictly
- Follow Next.js App Router patterns
- Sharp corners only (no border-radius) per design system
- Use theme tokens from Tailwind config (golden, text, background, border)
