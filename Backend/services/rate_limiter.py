from datetime import datetime, timedelta
from fastapi import HTTPException
from collections import defaultdict

# In-memory store
# { "ip_address": [timestamp1, timestamp2, ...] }
request_log = defaultdict(list)

# Config — safe for Groq free tier
MAX_REQUESTS_PER_MINUTE = 2      # Groq token limit = ~2 full requests/min
MAX_REQUESTS_PER_DAY = 20        # Conservative daily limit per IP

def check_rate_limit(client_ip: str):
    now = datetime.utcnow()
    one_minute_ago = now - timedelta(minutes=1)
    one_day_ago = now - timedelta(hours=24)

    # Clean old timestamps
    request_log[client_ip] = [
        t for t in request_log[client_ip]
        if t > one_day_ago
    ]

    recent = [t for t in request_log[client_ip] if t > one_minute_ago]

    # Check per-minute limit
    if len(recent) >= MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. You can make 2 requests per minute. Please wait."
        )

    # Check per-day limit
    if len(request_log[client_ip]) >= MAX_REQUESTS_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail="Daily limit reached. Maximum 20 requests per day per user."
        )

    # Log this request
    request_log[client_ip].append(now)