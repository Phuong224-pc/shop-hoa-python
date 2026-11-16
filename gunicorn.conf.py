import os

# Auto-detect PORT on Render, Railway, Fly, Heroku (default 10000 on Render)
raw_port = os.environ.get("PORT", "10000")
port = raw_port if raw_port.isdigit() else "10000"

bind = f"0.0.0.0:{port}"
workers = 1
threads = 4
timeout = 120
keepalive = 5

# Stream application logs directly to container standard output/error
accesslog = "-"
errorlog = "-"
loglevel = "info"
capture_output = True
enable_stdio_inheritance = True
