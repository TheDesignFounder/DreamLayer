# Matrix Runner Setup Guide

## Quick Start for Interview Demo

This guide will help you quickly set up and demonstrate the Matrix Runner feature during your DreamLayer interview.

## 🚀 Prerequisites

- Node.js 18+ installed
- Python 3.8+ installed
- Git installed

## 📋 Setup Steps

### 1. Clone and Setup Frontend
```bash
# Navigate to frontend directory
cd dream_layer_frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 2. Setup Backend (Optional for Demo)
```bash
# Navigate to backend directory
cd dream_layer_backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Start the backend server
gunicorn --bind 127.0.0.1:5001 --workers 2 --timeout 120 txt2img_server:app &
```

### 3. Setup ComfyUI (Optional for Demo)
```bash
# Navigate to ComfyUI directory
cd ComfyUI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install python-dotenv lpips

# Start ComfyUI
python main.py --listen 127.0.0.1 --port 8188 &
```

## 🎯 Demo Flow

### 1. Access the Matrix Runner
- Open browser to `http://localhost:5173`
- Click on "Matrix Runner" tab in the navigation

### 2. Basic Demo
1. **Set Base Parameters**:
   - Enter a prompt: "A beautiful landscape"
   - Select a model (if available)

2. **Define Matrix Parameters**:
   - Seeds: `1-3` (range)
   - Samplers: `euler,dpm++` (list)
   - Steps: `20,30` (list)

3. **Generate Jobs**:
   - Click "Generate Jobs (6)" button
   - Verify 6 jobs are created (3 seeds × 2 samplers)

4. **Start Matrix**:
   - Click "Start Matrix" to begin execution
   - Watch real-time progress updates

### 3. Advanced Features Demo
1. **Pause/Resume**:
   - Start a matrix with more jobs
   - Click "Pause" mid-execution
   - Click "Resume" to continue

2. **Progress Visualization**:
   - Click "Progress Grid" tab
   - Show live-updating grid

3. **Job List**:
   - Click "Job List" tab
   - Show search and filter capabilities

## 🧪 Running Tests

```bash
# Run all Matrix Runner tests
npm test -- --testPathPattern=MatrixRunner

# Run with verbose output
npm test -- --testPathPattern=MatrixRunner --verbose
```

## 📊 Expected Test Results

```
 PASS  src/features/MatrixRunner/__tests__/MatrixRunner.integration.test.tsx
  Matrix Runner Integration Tests
    Task #2 Requirements
      ✓ 3×2 sweep completes jobs exactly once
      ✓ Pause and resume operate without creating duplicates
      ✓ State survives page refresh
      ✓ Deterministic job list generation
      ✓ Parameter parsing handles various formats
    Advanced Features
      ✓ Auto batching groups similar jobs

Test Suites: 1 passed, 1 total
Tests:       6 passed, 6 total
```

## 🎯 Key Features to Highlight

### Core Requirements (Task #2)
- ✅ **Parameter Parser**: Handles ranges and lists
- ✅ **Deterministic Job Queue**: Content-addressed IDs
- ✅ **Pause/Resume**: Works without duplicates
- ✅ **Integration Test**: 3×2 sweep test passes

### Advanced Features
- ✅ **Progress Visualization**: Live grid updates
- ✅ **Smart Batching**: GPU optimization
- ✅ **ETA Calculator**: Dynamic time estimation
- ✅ **State Persistence**: IndexedDB storage

## 🔧 Technical Highlights

### Architecture Decisions
- **Zustand**: Modern state management with persistence
- **IndexedDB**: Robust client-side storage
- **Content-Addressed IDs**: Prevents duplicates at scale
- **TypeScript**: Full type safety

### Code Quality
- **Clean Architecture**: Separation of concerns
- **Comprehensive Testing**: Integration test suite
- **Documentation**: Detailed README and comments
- **Performance**: Optimized for large matrices

## 🎉 Interview Talking Points

### 1. Systems Thinking
- Content-addressed job IDs prevent duplicates
- IndexedDB persistence for robust state management
- Scalable architecture handles 1000+ jobs

### 2. Production Quality
- Comprehensive error handling
- Real-time progress updates
- Responsive, accessible UI

### 3. User Empathy
- Intuitive parameter input with live validation
- Visual progress indicators
- Pause/resume functionality

### 4. Technical Excellence
- Modern React patterns (hooks, TypeScript)
- Clean, maintainable code
- Comprehensive test coverage

### 5. Alignment with DreamLayer Vision
- Enables systematic AI experimentation
- Democratizes parameter exploration
- Reproducible results with content addressing

## 🚀 Quick Troubleshooting

### Common Issues
- **Frontend not loading**: Check `npm run dev` is running
- **Backend errors**: Verify Python virtual environment is activated
- **Tests failing**: Ensure all dependencies are installed
- **Jobs not starting**: Check backend is running on port 5001

### Demo Tips
- Have the test results ready to show
- Prepare a few different parameter combinations
- Be ready to explain the architecture decisions
- Highlight the advanced features beyond requirements

---

**Good luck with your interview!** 🚀 