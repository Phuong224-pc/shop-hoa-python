import os
import sys

from app import create_app

# Default to production config for cloud deployments (Render, Railway, Fly, Heroku)
config_name = os.environ.get('FLASK_CONFIG', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    # Auto-detect and switch to virtualenv Python if launched directly with system Python on Windows
    if sys.prefix == getattr(sys, "base_prefix", sys.prefix):
        venv_python = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "python.exe")
        if os.path.exists(venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(venv_python).lower():
            import subprocess
            try:
                sys.exit(subprocess.call([venv_python] + sys.argv))
            except KeyboardInterrupt:
                sys.exit(0)

    raw_port = os.environ.get('PORT', '5000')
    port = int(raw_port) if raw_port.isdigit() else 5000
    host = os.environ.get('HOST', '0.0.0.0')
    debug_mode = os.environ.get('FLASK_DEBUG', '0').lower() in ['true', '1', 'yes']
    app.run(host=host, port=port, debug=debug_mode)
