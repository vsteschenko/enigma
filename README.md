### Load test
1. Launch server, as code is async go with uvicorn uvicorn app.main:app --host 127.0.0.1 --port 8000
2. Launch locust --headless -u 50 -r 5 -t 1m --host http://127.0.0.1:8000
