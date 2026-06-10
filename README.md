# GitHub Learning Assistant (V2)

## Overview

GitHub Learning Assistant is a modern desktop application developed using Python and CustomTkinter that helps students understand GitHub repositories before contributing to open-source projects.

The application retrieves comprehensive repository information using the GitHub REST API, identifies all technologies used, generates intelligent learning roadmaps for 18+ programming languages, calculates multi-signal difficulty scores, and provides context-aware contribution advice — all stored in a searchable SQLite history.

---

## Problem Statement

Many students discover interesting open-source repositories on GitHub but struggle to understand:

* What the project does
* Which technologies are used
* Whether the project is beginner-friendly
* What skills are required before contributing

This project simplifies repository exploration and learning.

---

## Features

### Repository Analysis
* Repository name, owner, description
* Primary language & all languages used (with percentage breakdown)
* Stars, forks, open issues, license, default branch
* Topics/tags detection
* Last updated date

### Smart Difficulty Prediction
* Multi-signal scoring using stars, forks, open issues, and repository size
* Four-tier classification: Beginner → Intermediate → Advanced → Expert
* Color-coded difficulty badges

### Dynamic Learning Roadmaps
* 18 language-specific learning paths loaded from JSON config
* Easily extensible — just edit `roadmap/roadmaps.json`
* Visual step-by-step numbered roadmap display

### Context-Aware Contribution Advice
* Advice based on stars, forks, open issues, license, wiki, and topics
* Detects Hacktoberfest, ML/AI, and web projects for targeted tips
* License validation and safety warnings

### Analysis History
* Searchable by name, owner, or description
* Filterable by programming language
* Delete with confirmation
* Duplicate prevention (updates existing records)

### Modern UI
* Beautiful dark theme with CustomTkinter
* Card-based layout with color-coded badges
* Threaded API calls with loading indicators
* Scrollable analysis view
* Responsive design

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Python CustomTkinter |
| Backend | Python |
| Database | SQLite |
| API | GitHub REST API |
| Config | python-dotenv |
| Version Control | Git + GitHub |

---

## Setup

```bash
# Clone the repository
git clone https://github.com/MohsanRazaq/Github_learning.git
cd Github_learning

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# (Optional) Add your GitHub token for higher API rate limits
# Edit .env and add: GITHUB_TOKEN=your_token_here

# Run the application
python main.py
```

---

## Database Schema

**repositories**

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (auto-increment) |
| repo_name | TEXT | Repository name |
| owner | TEXT | Repository owner |
| description | TEXT | Repository description |
| language | TEXT | Primary language |
| stars | INTEGER | Star count |
| forks | INTEGER | Fork count |
| open_issues | INTEGER | Open issue count |
| license | TEXT | License type |
| url | TEXT | GitHub URL (unique) |
| analyzed_date | TEXT | Analysis timestamp |

---

## Project Structure

```
Github_learning/
├── main.py                    # Application entry point
├── config.py                  # Central configuration (env, colors)
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (not committed)
├── .gitignore
├── api/
│   ├── __init__.py
│   └── github_api.py          # GitHub API integration
├── database/
│   ├── __init__.py
│   └── db_manager.py          # SQLite database operations
├── gui/
│   ├── __init__.py
│   ├── home_screen.py         # Main application window
│   ├── analysis_screen.py     # Repository analysis display
│   └── history_screen.py      # Saved analysis history
└── roadmap/
    ├── __init__.py
    ├── roadmaps.json           # Language roadmap configs (18 languages)
    ├── roadmap_generator.py    # Roadmap & difficulty calculation
    └── contribution_helper.py  # Contribution advice engine
```

---

## Future Scope

* AI Repository Explanation (LLM integration)
* README Summarization
* Repository Health Analysis
* Contribution Opportunity Detection
* Security Analysis
* AI Chat Assistant
* Export to PDF / Markdown

---

## Team Members

* Mohsan Razaq
* H. Abdul Rehman

---

## Supervisor

Miss Aqsa Afzal
