import os
import sys

# Auto-detect and switch to virtualenv Python if launched with system Python on Windows
if sys.platform == 'win32' and sys.prefix == getattr(sys, "base_prefix", sys.prefix):
    venv_python = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(venv_python).lower():
        import subprocess
        try:
            sys.exit(subprocess.call([venv_python] + sys.argv))
        except KeyboardInterrupt:
            sys.exit(0)

from app import create_app

# Default configuration
config_name = os.environ.get('FLASK_CONFIG', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    raw_port = os.environ.get('PORT', '5000')
    port = int(raw_port) if raw_port.isdigit() else 5000
    host = os.environ.get('HOST', '127.0.0.1')
    debug_mode = os.environ.get('FLASK_DEBUG', '1').lower() in ['true', '1', 'yes']
    app.run(host=host, port=port, debug=debug_mode)
