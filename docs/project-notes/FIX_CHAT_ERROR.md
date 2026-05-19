# YAMA AI - Fix Chat Error (LLM_PROVIDER=none)

## STEP 1: Stop Current Backend

In your backend PowerShell window, press:
```
CTRL + C
```

You should see:
```
KeyboardInterrupt
```

The backend will stop.

---

## STEP 2: Create .env File

In backend folder, create a file named `.env`

Add this line:
```
LLM_PROVIDER=none
```

Save the file.

---

## STEP 3: Restart Backend

In the SAME PowerShell window, paste:

```powershell
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ Backend is running with LLM_PROVIDER=none

---

## STEP 4: Test Chat

Open frontend in browser and try:
- Click chat input box
- Type: "hello"
- Press Enter

You should get a response now!

If you get error again, wait 30 seconds and try again.

---

## IF STILL NOT WORKING

Check backend console for error messages (red text).

Try this instead:

```powershell
# Stop backend: CTRL+C

# Use this command (sets environment variable):
$env:LLM_PROVIDER="none"; uvicorn main:app --reload --port 8000
```

---

## WHAT THIS DOES

- `LLM_PROVIDER=none` tells backend to NOT use external AI
- Uses built-in templates and logic instead
- Faster response
- No API keys needed
- Works immediately

---

## EXPECTED BEHAVIOR

User types: "What is theft?"
Backend responds: "Based on your question..." (with relevant laws)

All chat features work with template-based responses!

---

Done! Chat should now work! 🎉
