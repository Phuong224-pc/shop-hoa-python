import os
import sys

# Auto-detect and switch to virtualenv Python if launched with system Python
if sys.prefix == getattr(sys, "base_prefix", sys.prefix):
    venv_python = os.path.join(os.path.dirname(__file__), "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(venv_python).lower():
        import subprocess
        try:
            sys.exit(subprocess.call([venv_python] + sys.argv))
        except KeyboardInterrupt:
            sys.exit(0)

from app import create_app

app = create_app(os.environ.get('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
