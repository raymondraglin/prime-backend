# Task Queue Setup Guide

## Windows Setup (Recommended: Memurai)

Redis doesn't officially support Windows. Use **Memurai** (Redis-compatible) instead.

### Option 1: Memurai (Easiest for Windows)

1. **Download Memurai:**
   - Go to [https://www.memurai.com/get-memurai](https://www.memurai.com/get-memurai)
   - Download Memurai Developer Edition (free)
   - Install it (default port 6379)

2. **Verify Memurai is running:**
   ```powershell
   # Check if service is running
   Get-Service Memurai
   ```

3. **Add to .env (optional — defaults to localhost:6379):**
   ```bash
   REDIS_URL=redis://localhost:6379/0
   ```

4. **Install Celery in your venv:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **Start Celery worker:**
   ```powershell
   python -m celery -A app.prime.tasks.celery_app worker --loglevel=info --pool=solo
   ```

### Option 2: Redis via WSL2

If you have WSL2 installed:

```bash
# Inside WSL2
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

Then in Windows .env:
```bash
REDIS_URL=redis://localhost:6379/0
```

### Option 3: Skip Celery (Synchronous Mode)

If you don't need async tasks yet, you can skip Redis/Celery entirely. The API will work fine without it — long-running operations will just block the request instead of running in the background.

**To disable task queue:**
- Don't start the Celery worker
- Use synchronous endpoints instead:
  - `/prime/research/` (sync) instead of `/prime/tasks/research` (async)
  - `/prime/academic/embed` (sync) instead of `/prime/tasks/embed/corpus` (async)

---

## Starting the Stack

### With Task Queue (Async)

**Terminal 1 — API Server:**
```powershell
uvicorn app.main:app --reload --port 8001
```

**Terminal 2 — Celery Worker:**
```powershell
python -m celery -A app.prime.tasks.celery_app worker --loglevel=info --pool=solo
```

### Without Task Queue (Sync Only)

**Terminal 1 — API Server:**
```powershell
uvicorn app.main:app --reload --port 8001
```

That's it. Use sync endpoints only.

---

## Testing Task Queue

**1. Launch a research task:**
```powershell
curl -X POST http://localhost:8001/prime/tasks/research `
  -H "Content-Type: application/json" `
  -d '{"query": "explain quantum computing", "depth": "standard"}'
```

Returns:
```json
{
  "task_id": "abc-123-def",
  "status": "PENDING",
  "message": "Research task launched. Poll /prime/tasks/status/{task_id} for progress."
}
```

**2. Poll status:**
```powershell
curl http://localhost:8001/prime/tasks/status/abc-123-def
```

Returns:
```json
{
  "task_id": "abc-123-def",
  "status": "STARTED",
  "message": "Task is running.",
  "meta": {"stage": "conducting", "progress": 50}
}
```

**3. Get result when complete:**
```powershell
curl http://localhost:8001/prime/tasks/result/abc-123-def
```

---

## Troubleshooting

### Celery not found
```powershell
pip install celery redis
```

### Connection refused to Redis
- Check Memurai service: `Get-Service Memurai`
- If stopped: `Start-Service Memurai`
- Or restart: `Restart-Service Memurai`

### Celery worker crashes on Windows
- Always use `--pool=solo` flag on Windows
- Full command: `python -m celery -A app.prime.tasks.celery_app worker --loglevel=info --pool=solo`

### Task stays PENDING forever
- Worker not running — start it in a separate terminal
- Check worker logs for errors

---

## Production Deployment

For Railway/Render/Heroku:

1. **Add Redis addon** (most platforms have one-click Redis)
2. **Set REDIS_URL** in environment variables (auto-set by addon)
3. **Deploy two services:**
   - Web: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Worker: `celery -A app.prime.tasks.celery_app worker --loglevel=info`

**Railway example:**
- Web service: uses `Procfile` or railway.toml startCommand
- Worker service: separate service with command `celery -A app.prime.tasks.celery_app worker --loglevel=info`
