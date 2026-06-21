# Money Track

A personal finance tracker built with Django.

## Root project structure

- `moneytrack/` - Django project folder
- `node_modules/` - frontend or dependency folder
- `venv/` - local Python virtual environment (ignored)
- `.gitignore` - ignored files and folders
- `README.md` - project overview and setup

## Setup

1. Activate your virtual environment:
   ```bash
   .\venv\Scripts\activate
   ```
2. Install Python dependencies:
   ```bash
   python -m pip install -r moneytrack\requirements.txt
   ```
3. Run Django migrations:
   ```bash
   python moneytrack\manage.py migrate
   ```
4. Start the development server:
   ```bash
   python moneytrack\manage.py runserver
   ```

## Git guidance

- Keep source code and migrations committed
- Ignore local environment files and runtime artifacts
- Do not commit `venv/`, `node_modules/`, or `ngrok.exe`
