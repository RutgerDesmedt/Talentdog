#!/bin/bash

# TalentDog Quick Start Script
# This script sets up the complete TalentDog application

set -e  # Exit on error

echo "🚀 TalentDog Quick Start"
echo "======================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Setup Backend
echo -e "${BLUE}Setting up Backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit backend/.env and add your API keys${NC}"
fi

# Initialize database
echo "Initializing database..."
python3 -c "from main import init_database; init_database()"

# Seed database with sample data
echo "Seeding database with 100 sample profiles..."
python3 seed_database.py

echo -e "${GREEN}✅ Backend setup complete${NC}"
echo ""

# Setup Frontend
echo -e "${BLUE}Setting up Frontend...${NC}"
cd ../frontend

# Install Node dependencies
echo "Installing Node dependencies..."
npm install --silent

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    echo "REACT_APP_API_URL=http://localhost:8000" > .env
fi

echo -e "${GREEN}✅ Frontend setup complete${NC}"
echo ""

# Create launcher script
cd ..
cat > start.sh << 'EOF'
#!/bin/bash

# TalentDog Launcher
echo "🚀 Starting TalentDog..."
echo ""

# Start backend in background
echo "Starting backend on http://localhost:8000..."
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 3

# Start frontend
echo "Starting frontend on http://localhost:3000..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ TalentDog is running!"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF

chmod +x start.sh

echo ""
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ TalentDog Setup Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "To start TalentDog, run:"
echo ""
echo -e "  ${BLUE}./start.sh${NC}"
echo ""
echo "Or manually:"
echo ""
echo -e "  ${BLUE}# Terminal 1 (Backend)${NC}"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo -e "  ${BLUE}# Terminal 2 (Frontend)${NC}"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "Then open: http://localhost:3000"
echo ""
echo -e "${YELLOW}⚠️  Don't forget to configure API keys in backend/.env${NC}"
echo ""
