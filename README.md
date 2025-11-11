# Ken

AI helps financial analysts become significantly more productive and effective, allowing them to provide higher-value strategic insights. Instead of spending up to 90% of their time on manual data tasks, AI automates these processes, freeing up analysts to focus on more complex analysis, strategy, and client advisory.

<img width="3360" height="1758" alt="Screenshot 2025-11-10 at 9 27 18 PM" src="https://github.com/user-attachments/assets/6f9370b5-8fb9-4906-8b5f-ddd7bf03ef62" />


## What Ken Does

**Automated Document Analysis**
- Upload financial documents (10-K, 10-Q reports) or fetch them directly by ticker
- AI parses and extracts key data from complex financial statements
- Navigate documents with clickable chunks for instant context

**Intelligent Financial Modeling**
- Chat with Analyst Ken about specific sections of documents
- Get technical analysis of cash flows, balance sheets, and income statements
- Build comprehensive financial models with scenario analysis
- Export analysis and models for further review

**Workspace Organization**
- Organize financial documents by company workspace
- Track analysis activity and version history
- View structured data in Excel-like tables

## How It Works

1. **Create a workspace** - Enter a ticker symbol or upload documents
2. **AI processes documents** - Automatically parses and structures financial data
3. **Analyze with Ken** - Click any section to chat with AI about the content
4. **Export insights** - View models and analysis in familiar formats

## Running the Application

### Backend (API)
```bash
cd api
pip install -r requirements.txt
uvicorn main:app
```

### Frontend (Web)
```bash
cd web
pnpm install
pnpm run dev
```

Access the application at `http://localhost:3000`

---

**Built with FastAPI, Next.js, and Claude AI**
