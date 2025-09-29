# Making the logs more detailed
**Date(s):** 2025-09-28

## Goal
Add more detailed log information such as headers, timing, source port

## Method
- Import time to track time duration
- Add existing information like headers and source port to log function

## Observations
- The new format in access.jsonl looks like:
```json
{
    "ts": "2025-09-29T05:04:27.560910Z", 
    "ip": "127.0.0.1", 
    "src_port": 51044, 
    "method": "GET", 
    "path": "/", 
    "status": 200, 
    "length": 315, 
    "duration_ms": 1.5, 
    "headers": {"Host": "localhost:8000", "Connection": "close"}
}
```

## Next Steps
- 