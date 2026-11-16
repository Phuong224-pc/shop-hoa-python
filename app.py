import os
from app import create_app

# WSGI entrypoint for cloud hosting (Render, Railway, Vercel, Gunicorn, Waitress)
config_name = os.environ.get('FLASK_CONFIG', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    raw_port = os.environ.get('PORT', '5000')
    port = int(raw_port) if raw_port.isdigit() else 5000
    host = os.environ.get('HOST', '0.0.0.0')
    debug_mode = os.environ.get('FLASK_DEBUG', '0').lower() in ['true', '1', 'yes']
    app.run(host=host, port=port, debug=debug_mode)
