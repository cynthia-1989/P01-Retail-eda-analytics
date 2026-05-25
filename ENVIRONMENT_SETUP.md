# Environment Setup Guide
## Complete Setup for Windows and Mac

---

## WHICH TERMINAL TO USE

**Windows:** Use the **VS Code integrated terminal set to PowerShell**
**Mac:** Use the **VS Code integrated terminal set to zsh**

Do NOT use Git Bash, Command Prompt, or Anaconda Prompt.
Everything in this course uses the VS Code integrated terminal only.
This works identically on both operating systems.

---

## STEP 1 — Install Python

### Windows
1. Go to python.org/downloads
2. Download Python 3.11 or higher
3. Run the installer
4. **CRITICAL:** Check the box that says **"Add Python to PATH"** before clicking Install
5. Click Install Now

Verify it worked. Open VS Code terminal and run:
```
python --version
```
You should see: `Python 3.11.x` or higher

### Mac
1. Go to python.org/downloads
2. Download Python 3.11 or higher
3. Run the installer (follow the prompts)

Verify it worked. Open VS Code terminal and run:
```
python3 --version
```
You should see: `Python 3.11.x` or higher

---

## STEP 2 — Install VS Code

1. Go to code.visualstudio.com
2. Download for your operating system
3. Install it

Install these VS Code extensions (click the Extensions icon on the left sidebar):
- **Python** (by Microsoft) — required
- **Pylance** (by Microsoft) — recommended
- **GitLens** (by GitKraken) — recommended for Module 04

---

## STEP 3 — Set Up Your Project Folder

### Windows
Open VS Code. Open the terminal (Ctrl + backtick).
Run these commands one at a time:
```
cd C:\
mkdir Darko-Bootcamp
cd Darko-Bootcamp
```

### Mac
Open VS Code. Open the terminal (Cmd + backtick).
Run these commands one at a time:
```
cd ~
mkdir Darko-Bootcamp
cd Darko-Bootcamp
```

---

## STEP 4 — Create a Virtual Environment

A virtual environment is an isolated Python installation for this project.
It keeps packages separate from other Python projects on your computer.
This is how professional engineers work — every project gets its own environment.

### Windows
```
python -m venv .venv
```
Then activate it:
```
.venv\Scripts\activate
```
You will see `(.venv)` appear at the start of your terminal prompt.
This means the virtual environment is active.

### Mac
```
python3 -m venv .venv
```
Then activate it:
```
source .venv/bin/activate
```
You will see `(.venv)` appear at the start of your terminal prompt.

**IMPORTANT:** You must activate the virtual environment every time you open a new terminal.
If you do not see `(.venv)` at the start of your prompt — run the activate command above.

### Tell VS Code to use this environment
1. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Type: `Python: Select Interpreter`
3. Press Enter
4. Choose the option that shows `.venv` in the path

VS Code will now always use the correct environment for this project.

---

## STEP 5 — Install All Packages

Make sure your virtual environment is active (you see `.venv` in the prompt).
Then run:

```
pip install -r requirements.txt
```

This installs everything needed for all 15 modules.
It will take 2-5 minutes. You will see packages downloading.

When it finishes you will see: `Successfully installed ...`

If you see errors about pip being old, run this first:
```
pip install --upgrade pip
```
Then run the requirements command again.

---

## STEP 6 — Create Your .env File

This file stores your database credentials privately.
It must NEVER be shared or committed to GitHub.

In VS Code, create a new file called exactly `.env` in your project folder.
The name is just `.env` — nothing before the dot.

Paste this exactly:
```
DB_URL=postgresql+psycopg2://postgres YOUR_PROJECT_ID:YOUR_PASSWORD@aws-0-us-west-2.pooler.supabase.com:5432/postgres

ANTHROPIC_API_KEY=your_key_here
```

The `ANTHROPIC_API_KEY` line is only needed from Module 11 onwards.
Leave it as `your_key_here` for now — it will not cause any errors.

**Why a .env file?**
Professional engineers never put passwords directly in Python code.
If your code goes to GitHub and it has a password in it, anyone in the world
can read it. The .env file keeps credentials separate. The .gitignore file
tells git to never track the .env file.

---

## STEP 7 — Verify Your Connection

Run this command:
```
python setup/verify_connection.py
```

You should see:
```
OK  Connected to: postgres
OK  bootcamp_data.employees     1,000 rows
OK  bootcamp_data.sales        15,000 rows
... (all tables green)
ALL OK — You are ready to learn
```

If you see any errors — read the error message carefully and check Steps 4-6.
Post the exact error message in Discord and we will help you fix it.

---

## STEP 8 — Choose Your Industry (Day 1 Activity)

You have access to 11 datasets:

| Schema | Industry | Tables |
|--------|----------|--------|
| `bootcamp_data` | GlobalTech (used in instructor demos) | employees, sales, products, customers... |
| `healthcare` | Hospital management, patients, billing | 5 tables |
| `banking` | Accounts, loans, fraud detection | 5 tables |
| `education` | Students, courses, grades | 5 tables |
| `logistics` | Shipments, drivers, warehouses | 5 tables |
| `retail` | Stores, inventory, sales | 5 tables |
| `real_estate` | Properties, agents, listings | 4 tables |
| `ecommerce` | Orders, sellers, reviews | 5 tables |
| `insurance` | Policies, claims, risk | 5 tables |
| `hospitality` | Hotels, bookings, guests | 5 tables |
| `manufacturing` | Production, quality, equipment | 6 tables |

**Pick one industry that interests you most.**
You will use it for all your take-home projects throughout the course.

In every lesson and project file you will see this at the top:
```python
# ── CHOOSE YOUR INDUSTRY ──────────────────────────────────────
# Change this to your chosen industry schema
# Options: healthcare, banking, education, logistics, retail,
#          real_estate, ecommerce, insurance, hospitality, manufacturing
# Leave as bootcamp_data to follow along with the instructor demo

INDUSTRY = "bootcamp_data"
```

Just change `"bootcamp_data"` to your chosen industry.
That single line routes all your queries to the right dataset.

You can switch industries at any time — just change that one line.

---

## DAILY WORKFLOW

Every time you sit down to work:

1. Open VS Code
2. Open your project folder (File → Open Folder → Darko-Bootcamp)
3. Open the terminal (Ctrl + backtick or Cmd + backtick)
4. Activate your virtual environment:
   - **Windows:** `.venv\Scripts\activate`
   - **Mac:** `source .venv/bin/activate`
5. Check you see `(.venv)` in the prompt
6. Open the lesson file and start working

---

## COMMON ERRORS AND FIXES

**"python is not recognized" (Windows)**
Fix: Python was not added to PATH during installation.
Uninstall Python and reinstall, making sure to check "Add Python to PATH".

**"No module named pandas" or similar**
Fix: Your virtual environment is not active.
Run the activate command for your OS (Step 4) and try again.

**"DB_URL not found" or connection errors**
Fix: Your .env file is either missing or in the wrong folder.
The .env file must be in the same folder where you run Python from.
Run `ls -la` (Mac) or `dir` (Windows) and check .env is listed.

**"password authentication failed"**
Fix: The password in your DB_URL is wrong.
Ask your instructor for the correct DB_URL.

**"ModuleNotFoundError: No module named 'dotenv'"**
Fix: Run `pip install python-dotenv` with your virtual environment active.

**Virtual environment not activating on Windows PowerShell**
Fix: Run this once in PowerShell as administrator:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again.

---

## THE STANDARD CONNECTION PATTERN

Every Python file in this course starts with these same lines.
Learn this pattern — you will type it hundreds of times:

```python
import os                              # built into Python -- reads environment variables
import pandas as pd                    # data manipulation
from sqlalchemy import create_engine   # connects Python to PostgreSQL
from dotenv import load_dotenv         # reads your .env file

load_dotenv()                          # loads DB_URL from .env into memory

engine = create_engine(                # creates the database connection
    os.getenv("DB_URL"),               # reads the DB_URL from your .env file
    pool_pre_ping=True                 # tests the connection before using it
)

# ── CHOOSE YOUR INDUSTRY ──────────────────────────────────────
INDUSTRY = "bootcamp_data"             # change this to your chosen industry

# Example query -- change the table to match your industry
df = pd.read_sql(f"SELECT * FROM {INDUSTRY}.employees LIMIT 10", engine)
print(df)
```

---

## GETTING HELP

If something is not working:
1. Read the exact error message carefully
2. Check the Common Errors section above
3. Post the exact error in Discord (copy and paste it -- do not take a photo)
4. Include which step you are on and what OS you are using

We fix things together. Do not spend more than 10 minutes stuck on setup
before asking for help.
