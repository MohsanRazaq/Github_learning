# GitHub Learning Assistant (V2)

## Overview

GitHub Learning Assistant is a modern desktop application built with **Python**, **CustomTkinter**, and **SQLite** that helps students understand GitHub repositories before contributing to open-source projects.

The application analyzes repositories using the GitHub REST API, identifies technologies used, calculates difficulty levels, generates personalized learning roadmaps for more than 18 programming languages, and provides contribution guidance based on repository characteristics.

All analyses are stored locally in a searchable SQLite database for future reference.

---

## Problem Statement

Many students find interesting open-source repositories on GitHub but often struggle to understand:

* What the project does
* Which technologies are used
* Whether the project is beginner-friendly
* What skills are required before contributing

GitHub Learning Assistant simplifies repository exploration and helps learners prepare before making contributions.

---

## Features

### Repository Analysis

* Repository name, owner, and description
* Primary programming language
* All languages used with percentage breakdown
* Stars, forks, and open issues
* License information
* Repository topics/tags
* Default branch
* Last updated date

### Smart Difficulty Prediction

Difficulty is calculated using multiple repository signals:

* Stars
* Forks
* Open Issues
* Repository Size

Difficulty Levels:

* 🟢 Beginner
* 🔵 Intermediate
* 🟠 Advanced
* 🔴 Expert

### Dynamic Learning Roadmaps

* Supports 18+ programming languages
* JSON-based roadmap configuration
* Easy customization through `roadmaps.json`
* Step-by-step learning paths

### Context-Aware Contribution Advice

Provides repository-specific contribution guidance based on:

* Repository popularity
* Open issues
* License availability
* Topics and tags
* Wiki availability

Special detection for:

* Hacktoberfest projects
* Machine Learning / AI repositories
* Web Development projects

### Analysis History

* SQLite-powered local storage
* Search by repository name
* Search by owner
* Search by description
* Filter by language
* Delete records with confirmation
* Duplicate prevention through automatic updates

### Modern User Interface

* Built with CustomTkinter
* Dark mode design
* Card-based layout
* Color-coded difficulty badges
* Responsive and scrollable interface
* Threaded API requests
* Loading indicators

---

## Technology Stack

| Component       | Technology           |
| --------------- | -------------------- |
| Frontend        | Python CustomTkinter |
| Backend         | Python               |
| Database        | SQLite               |
| API             | GitHub REST API      |
| Configuration   | python-dotenv        |
| Version Control | Git & GitHub         |

---

## Installation

### Clone Repository

```bash
git clone https://github.com/MohsanRazaq/Github_learning.git
cd Github_learning
```

### Create Virtual Environment

```bash
python -m venv .venv
```

#### Linux / macOS

```bash
source .venv/bin/activate
```

#### Windows

```bash
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure GitHub Token (Optional)

Create a `.env` file and add:

```env
GITHUB_TOKEN=your_github_token_here
```

Using a GitHub token increases API rate limits.

### Run Application

```bash
python main.py
```

---

## Database Schema

### Table: repositories

| Column        | Type    | Description            |
| ------------- | ------- | ---------------------- |
| id            | INTEGER | Primary Key            |
| repo_name     | TEXT    | Repository Name        |
| owner         | TEXT    | Repository Owner       |
| description   | TEXT    | Repository Description |
| language      | TEXT    | Primary Language       |
| stars         | INTEGER | Star Count             |
| forks         | INTEGER | Fork Count             |
| open_issues   | INTEGER | Open Issue Count       |
| license       | TEXT    | License Type           |
| url           | TEXT    | GitHub Repository URL  |
| analyzed_date | TEXT    | Analysis Timestamp     |

---

## Project Structure

```text
Github_learning/
│
├── main.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
│
├── api/
│   ├── __init__.py
│   └── github_api.py
│
├── database/
│   ├── __init__.py
│   └── db_manager.py
│
├── gui/
│   ├── __init__.py
│   ├── home_screen.py
│   ├── analysis_screen.py
│   └── history_screen.py
│
└── roadmap/
    ├── __init__.py
    ├── roadmaps.json
    ├── roadmap_generator.py
    └── contribution_helper.py
```

---

## Future Scope

* AI Repository Explanation
* README Summarization
* Repository Health Analysis
* Contribution Opportunity Detection
* Security Analysis
* AI Chat Assistant
* Export Reports to PDF
* Export Reports to Markdown

---

## Team Members

### Developers

* Mohsan Razaq
* H. Abdul Rehman

### Supervisor

* Miss Aqsa Afzal

---

## Repository Link

GitHub Repository:

https://github.com/MohsanRazaq/Github_learning

---

## License

This project is developed for educational and learning purposes. Feel free to fork, learn from, and contribute to the project.
