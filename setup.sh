#!/bin/bash

echo "🚀 Setting up Agent Builder Development Environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check if PostgreSQL is available
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. Please ensure PostgreSQL is installed and running."
    echo "   You can install it from: https://www.postgresql.org/download/"
fi

echo "✅ Prerequisites check completed"

# Setup Backend
echo ""
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Created .env file. Please update with your API keys and database URL."
fi

# Setup database
echo "🗄️  Setting up database..."
python -m alembic upgrade head

echo "✅ Backend setup completed"

# Setup Frontend
echo ""
echo "🎨 Setting up Frontend..."
cd ../frontend

# Install Node dependencies
npm install

# Copy environment file
if [ ! -f .env.local ]; then
    cp .env.example .env.local
    echo "📝 Created .env.local file for frontend."
fi

echo "✅ Frontend setup completed"

# Final instructions
echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update backend/.env with your API keys:"
echo "   - OPENAI_API_KEY"
echo "   - GOOGLE_API_KEY" 
echo "   - SERPAPI_KEY"
echo "   - DATABASE_URL"
echo ""
echo "2. Start the backend server:"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "3. Start the frontend server:"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Access the application at http://localhost:3000"
echo ""
echo "📖 For more information, see README.md"