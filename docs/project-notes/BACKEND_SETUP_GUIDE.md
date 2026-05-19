# YAMA AI BACKEND - MANUAL SETUP & EXECUTION GUIDE

## Step 1: Navigate to Backend Directory

Open PowerShell or Command Prompt and run:

```powershell
cd "c:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend"
```

Expected output: You should see the command prompt change to show the backend path

---

## Step 2: Check Python Installation

Verify Python is installed:

```powershell
python --version
```

Expected output: Should show Python 3.12.x or higher

If this fails:
- Download Python from https://www.python.org
- Install with "Add Python to PATH" checked
- Restart PowerShell

---

## Step 3: Check Virtual Environment

List files in the backend directory:

```powershell
Get-ChildItem
```

You should see:
- `venv` folder (virtual environment)
- `requirements.txt`
- `main.py`
- `app` folder
- `retrieval_engine` folder

---

## Step 4: Activate Virtual Environment

This is CRITICAL! Run:

```powershell
.\venv\Scripts\Activate.ps1
```

Expected output:
- Command prompt will show `(venv)` at the beginning
- Example: `(venv) PS C:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend>`

If you get an error about execution policy, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try Activate again.

---

## Step 5: Verify Required Packages

Check if all packages are installed:

```powershell
pip list
```

You should see:
- fastapi
- uvicorn
- sqlalchemy
- chromadb
- sentence-transformers
- (and others)

If packages are missing, run:

```powershell
pip install -r requirements.txt
```

This will take 2-5 minutes to complete.

---

## Step 6: Start the Backend Server

Run this command:

```powershell
uvicorn main:app --reload --port 8000
```

### What You Should See:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup...
INFO:     Application startup complete
```

### This means:
✅ Backend is running successfully
✅ Server is listening on port 8000
✅ Ready to accept requests

---

## Step 7: Test the Backend (In New PowerShell Window)

Keep the backend running in the first window. Open a NEW PowerShell window:

```powershell
# Test 1: Health Check
curl http://localhost:8000/api/v1/health

# Test 2: Get Acts
curl http://localhost:8000/api/v1/laws/acts

# Test 3: Search Laws
curl "http://localhost:8000/api/v1/laws/search?q=theft"
```

Expected output: JSON responses with data

---

## Step 8: Access API Documentation

Open your browser and go to:

```
http://localhost:8000/docs
```

You should see:
- Swagger UI documentation
- All available endpoints listed
- Interactive testing interface

---

## TROUBLESHOOTING

### Problem 1: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```powershell
# Make sure you activated venv first!
.\venv\Scripts\Activate.ps1

# Then install packages
pip install -r requirements.txt
```

---

### Problem 2: "Address already in use"

This means port 8000 is occupied.

**Solution:**
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace XXXX with PID from above)
taskkill /PID XXXX /F

# Then start backend again
uvicorn main:app --reload --port 8000
```

Or use a different port:
```powershell
uvicorn main:app --reload --port 8001
```

---

### Problem 3: "Cannot find database yama_ai.db"

The database will be created automatically.

**If still failing:**
```powershell
# Check if yama_ai.db exists
Get-ChildItem yama_ai.db

# If not found, it will be created on first run
# Just start the backend again
```

---

### Problem 4: Backend starts but no response from API

**Check 1: Verify port is correct**
```powershell
# In new PowerShell:
curl http://localhost:8000
# Should show HTML response
```

**Check 2: Check if backend is running**
- Look at original PowerShell window
- Should show "Application startup complete"

**Check 3: Wait a bit**
- First startup can take 10-30 seconds
- Loading ML models takes time
- Try again after 30 seconds

**Check 4: Check for errors in console**
- Look at the PowerShell window with backend
- Any red text indicates errors
- Copy error and search online

---

## COMPLETE STEP-BY-STEP EXAMPLE

Here's a complete working example:

### Window 1: Start Backend

```powershell
# Step 1: Navigate to backend
cd "c:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend"

# Step 2: Activate virtual environment
.\venv\Scripts\Activate.ps1

# Step 3: Start backend server
uvicorn main:app --reload --port 8000

# Output should show:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
# Keep this window open!
```

### Window 2: Test Backend (Open NEW PowerShell)

```powershell
# Test 1: Simple health check
curl http://localhost:8000/api/v1/health

# Test 2: Get all acts
curl http://localhost:8000/api/v1/laws/acts

# Test 3: Search for laws
curl "http://localhost:8000/api/v1/laws/search?q=theft" -Headers @{"Content-Type"="application/json"}

# Test 4: Create a case
$body = @{
    title = "Test Case"
    description = "Test description"
    category = "criminal"
    client_name = "Test User"
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/cases `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

---

## STOPPING THE BACKEND

When you want to stop the server:

1. Go to the PowerShell window with the backend
2. Press: `CTRL + C`
3. Press `Y` if asked to confirm

The backend will shut down.

---

## COMMON COMMANDS REFERENCE

```powershell
# Navigate to backend
cd "c:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Deactivate virtual environment
deactivate

# Start backend (default port 8000)
uvicorn main:app --reload --port 8000

# Start backend (different port)
uvicorn main:app --reload --port 8001

# Install packages
pip install -r requirements.txt

# List installed packages
pip list

# Check Python version
python --version

# Stop backend
CTRL + C
```

---

## API ENDPOINTS TO TEST

### 1. Health Check
```powershell
curl http://localhost:8000/api/v1/health
```
Response: `{"status":"ok"}`

### 2. List All Acts
```powershell
curl http://localhost:8000/api/v1/laws/acts
```
Response: Array of 85 acts

### 3. Search Laws
```powershell
curl "http://localhost:8000/api/v1/laws/search?q=theft"
```
Response: Search results with relevance

### 4. Get Act Sections
```powershell
curl "http://localhost:8000/api/v1/laws/sections/Indian%20Penal%20Code,%201860"
```
Response: All sections of IPC

### 5. Create Case
```powershell
$body = @{
    title = "My Case"
    description = "Case description"
    category = "criminal"
    client_name = "Your Name"
} | ConvertTo-Json

curl -X POST http://localhost:8000/api/v1/cases `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```
Response: Case created with UUID

---

## INTERACTIVE TESTING WITH SWAGGER UI

1. Backend must be running
2. Open browser: http://localhost:8000/docs
3. Click on any endpoint
4. Click "Try it out"
5. Fill in parameters
6. Click "Execute"
7. See response below

---

## ENVIRONMENT VARIABLES (Optional)

If you want to use advanced features, create `.env` file in backend folder:

```
LLM_PROVIDER=none
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
```

Then start backend normally.

---

## MONITORING BACKEND PERFORMANCE

While backend is running, you can see:

1. **Request logs**: Every API call is logged in PowerShell
2. **Response time**: Shown for each request
3. **Errors**: Any errors appear in red
4. **Hot reload**: Changes to code auto-reload (if using --reload)

Example log entry:
```
INFO:     127.0.0.1:12345 - "GET /api/v1/laws/acts HTTP/1.1" 200 OK
```

---

## NEXT STEPS AFTER BACKEND IS RUNNING

1. ✅ Backend running on http://localhost:8000
2. ✅ API docs available at http://localhost:8000/docs
3. ✅ Database loaded with 398 documents
4. ✅ Ready to test endpoints
5. ✅ Ready to integrate with frontend

---

## GETTING HELP

If something goes wrong:

1. **Check console**: Look for error messages in PowerShell
2. **Check port**: Make sure port 8000 is free
3. **Check venv**: Make sure virtual environment is activated
4. **Check requirements**: Make sure all packages are installed
5. **Restart**: Stop and start the backend fresh

---

## SUMMARY

### Quick Start (Every Time):
```powershell
# 1. Open PowerShell
# 2. Navigate to backend
cd "c:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend"

# 3. Activate environment
.\venv\Scripts\Activate.ps1

# 4. Start server
uvicorn main:app --reload --port 8000

# 5. In new PowerShell window, test:
curl http://localhost:8000/api/v1/health

# 6. Open browser:
# http://localhost:8000/docs
```

That's it! Backend is running and ready to use! 🚀
