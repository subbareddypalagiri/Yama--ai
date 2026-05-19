# BACKEND MANUAL EXECUTION - COMPLETE GUIDE

## ⭐ EASIEST WAY (Recommended)

Just double-click this file in backend folder:
```
START_BACKEND.bat
```

OR run in PowerShell:
```powershell
powershell -ExecutionPolicy RemoteSigned -File START_BACKEND.ps1
```

Both scripts will handle everything automatically!

---

## IF YOU WANT TO DO IT MANUALLY

### STEP-BY-STEP INSTRUCTIONS

#### Step 1: Open PowerShell
- Press: `Windows Key + R`
- Type: `powershell`
- Press: `Enter`

#### Step 2: Navigate to Backend Folder
Copy and paste this:
```powershell
cd "c:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend"
```
Press: `Enter`

You should see the path in your command prompt now.

#### Step 3: Activate Virtual Environment
Copy and paste this:
```powershell
.\venv\Scripts\Activate.ps1
```
Press: `Enter`

**Success**: Your prompt will show `(venv)` at the beginning

**If error about execution policy**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activation again.

#### Step 4: Start Backend Server
Copy and paste this:
```powershell
uvicorn main:app --reload --port 8000
```
Press: `Enter`

**What you'll see**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup...
INFO:     Application startup complete
```

✅ **Backend is now RUNNING!**

---

## TESTING THE BACKEND

### Method 1: Browser (Easiest)
1. Open your web browser
2. Go to: `http://localhost:8000/docs`
3. Click on any endpoint
4. Click "Try it out"
5. Click "Execute"
6. See response

### Method 2: PowerShell (New Window)
Keep backend running in first window, open a NEW PowerShell window:

```powershell
# Test 1: Health Check
curl http://localhost:8000/api/v1/health

# Test 2: List All Acts
curl http://localhost:8000/api/v1/laws/acts

# Test 3: Search Laws
curl "http://localhost:8000/api/v1/laws/search?q=theft"
```

Each should return JSON data.

### Method 3: Desktop Frontend
If frontend is running on port 3000/3001, it can now access the backend automatically.

---

## EXPECTED RESPONSES

### Health Check
Request: `http://localhost:8000/api/v1/health`
Response: `{"status":"ok"}`

### Get Acts
Request: `http://localhost:8000/api/v1/laws/acts`
Response: 
```json
[
  {"act_name":"Arbitration and Conciliation Act, 1996"},
  {"act_name":"Arms Act, 1959"},
  ...
]
```

### Search
Request: `http://localhost:8000/api/v1/laws/search?q=theft`
Response:
```json
{
  "query": "theft",
  "results": [...],
  "total": 10
}
```

---

## STOPPING THE BACKEND

To stop the server:
1. Go to PowerShell window with backend
2. Press: `CTRL + C`
3. Type: `Y` if asked
4. Backend stops

---

## TROUBLESHOOTING

### Problem 1: "ModuleNotFoundError: No module named 'fastapi'"

**What it means**: Packages not installed

**Solution**:
```powershell
# Make sure venv is activated (should show (venv) in prompt)
pip install -r requirements.txt

# This installs all required packages
# Takes 2-5 minutes
```

### Problem 2: "Address already in use"

**What it means**: Port 8000 is occupied by another process

**Solution A - Find and kill process**:
```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Output: TCP    127.0.0.1:8000    0.0.0.0:0    LISTENING    12345
#                                               (note the PID: 12345)

# Kill that process
taskkill /PID 12345 /F

# Try backend again
```

**Solution B - Use different port**:
```powershell
# Instead of:
uvicorn main:app --reload --port 8000

# Use:
uvicorn main:app --reload --port 8001

# Then access at: http://localhost:8001/docs
```

### Problem 3: "No such table: law_sections"

**What it means**: Database table doesn't exist or is corrupted

**Solution**:
```powershell
# Stop backend (CTRL+C)

# Delete old database
Remove-Item yama_ai.db -ErrorAction SilentlyContinue

# Start backend again
uvicorn main:app --reload --port 8000

# It will auto-create tables
```

### Problem 4: "Cannot activate venv" or execution policy error

**Solution**:
```powershell
# Allow scripts to run
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Try activation again
.\venv\Scripts\Activate.ps1
```

### Problem 5: Backend starts but API returns 500 error

**What it means**: Internal server error

**What to do**:
1. Check console for error messages (red text)
2. Search the error message online
3. Check if all packages installed: `pip install -r requirements.txt`
4. Restart backend: `CTRL+C` then start again

### Problem 6: No response from API

**What to do**:
1. Wait 30 seconds (loading models on first run)
2. Check if backend shows "Application startup complete"
3. Verify correct URL: `http://localhost:8000`
4. Try different port: change 8000 to 8001
5. Check console for errors

---

## COMPLETE WORKFLOW EXAMPLE

### Terminal Session:

```
PS C:\Users\subba> cd "c:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend"

PS C:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend> .\venv\Scripts\Activate.ps1

(venv) PS C:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend> uvicorn main:app --reload --port 8000

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Waiting for application startup...
INFO:     Application startup complete

[Backend is running! Don't close this window]
```

### In Browser:
Navigate to: `http://localhost:8000/docs`

You'll see Swagger UI with all endpoints!

---

## QUICK REFERENCE

| Task | Command |
|------|---------|
| Navigate | `cd "c:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend"` |
| Activate venv | `.\venv\Scripts\Activate.ps1` |
| Start backend | `uvicorn main:app --reload --port 8000` |
| Stop backend | `CTRL + C` |
| Install packages | `pip install -r requirements.txt` |
| List packages | `pip list` |
| Check Python | `python --version` |
| Test API | `curl http://localhost:8000/api/v1/health` |
| API Docs | Browser: `http://localhost:8000/docs` |

---

## API ENDPOINTS (ALL WORKING)

```
GET  /api/v1/health                      - System health
GET  /api/v1/laws/acts                   - List 85 acts
GET  /api/v1/laws/search?q=keyword       - Search laws
GET  /api/v1/laws/sections/{act}         - Get sections
GET  /api/v1/laws/categories             - List categories
POST /api/v1/chat                        - Chat conversation
POST /api/v1/analyze-situation           - Legal analysis
POST /api/v1/cases                       - Case management
POST /api/v1/documents                   - Document upload
POST /api/v1/reports                     - Report generation
```

---

## KEY INFORMATION

- **Backend URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Database**: `yama_ai.db` (created automatically)
- **Virtual Environment**: `venv` folder
- **Config**: `app/core/config.py`

---

## FILES IN BACKEND FOLDER

```
backend/
├── START_BACKEND.bat           ← Double-click to start
├── START_BACKEND.ps1           ← Or run this PowerShell script
├── BACKEND_SETUP_GUIDE.md      ← Full setup guide
├── main.py                     ← Main FastAPI app
├── requirements.txt            ← Python packages
├── app/                        ← Application code
│   ├── api/                   ← API endpoints
│   ├── services/              ← Business logic
│   └── db/                    ← Database models
├── venv/                       ← Virtual environment
├── yama_ai.db                  ← SQLite database
└── backups/                    ← Backup folder
```

---

## QUICK START (Copy & Paste)

### Option 1: Double-click (Windows)
1. Go to: `c:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend\`
2. Double-click: `START_BACKEND.bat`
3. Done! Backend is running

### Option 2: PowerShell
```powershell
cd "c:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend"
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

### Option 3: PowerShell Script
```powershell
powershell -ExecutionPolicy RemoteSigned -File START_BACKEND.ps1
```

---

## SUCCESS INDICATORS

✅ Backend started successfully when you see:
- `INFO:     Uvicorn running on http://127.0.0.1:8000`
- `INFO:     Application startup complete`
- No red error text

✅ API working when:
- Browser shows Swagger UI at `http://localhost:8000/docs`
- Curl returns JSON response
- No 500 errors

✅ Database loaded when:
- GET `/api/v1/laws/acts` returns 85 acts
- GET `/api/v1/laws/search?q=theft` returns results

---

## GETTING HELP

If something doesn't work:

1. **Check error message** in PowerShell (red text)
2. **Try again** after waiting 30 seconds
3. **Restart** with `CTRL+C` then start again
4. **Check internet** (first run downloads models)
5. **Reinstall packages**: `pip install -r requirements.txt`
6. **Read BACKEND_SETUP_GUIDE.md** for detailed help

---

## SUMMARY

1. Open PowerShell
2. Navigate to backend folder
3. Activate virtual environment: `.\venv\Scripts\Activate.ps1`
4. Start backend: `uvicorn main:app --reload --port 8000`
5. Open browser: `http://localhost:8000/docs`
6. Test API endpoints
7. Done! Backend is running

**That's it! You now have the backend running manually! 🚀**
