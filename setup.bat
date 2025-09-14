@echo off
echo 🚀 Setting up Agent Builder Development Environment...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3 is required but not installed.
    echo Please install Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is required but not installed.
    echo Please install Node.js from: https://nodejs.org/
    pause
    exit /b 1
)

:: Check if PostgreSQL is available
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  PostgreSQL not found. Please ensure PostgreSQL is installed and running.
    echo You can install it from: https://www.postgresql.org/download/
)

echo ✅ Prerequisites check completed

:: Setup Backend
echo.
echo 🔧 Setting up Backend...
cd backend

:: Create virtual environment
python -m venv venv
call venv\Scripts\activate

:: Install Python dependencies
pip install -r requirements.txt

:: Copy environment file
if not exist .env (
    copy .env.example .env
    echo 📝 Created .env file. Please update with your API keys and database URL.
)

:: Setup database
echo 🗄️  Setting up database...
python -m alembic upgrade head

echo ✅ Backend setup completed

:: Setup Frontend
echo.
echo 🎨 Setting up Frontend...
cd ..\frontend

:: Install Node dependencies
npm install

:: Copy environment file
if not exist .env.local (
    copy .env.example .env.local
    echo 📝 Created .env.local file for frontend.
)

echo ✅ Frontend setup completed

:: Final instructions
echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Update backend\.env with your API keys:
echo    - OPENAI_API_KEY
echo    - GOOGLE_API_KEY
echo    - SERPAPI_KEY
echo    - DATABASE_URL
echo.
echo 2. Start the backend server:
echo    cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload
echo.
echo 3. Start the frontend server:
echo    cd frontend ^&^& npm run dev
echo.
echo 4. Access the application at http://localhost:3000
echo.
echo 📖 For more information, see README.md

pause