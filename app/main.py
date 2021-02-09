# The docker image (tiangolo/meinheld-gunicorn-flask:python3.6-alpine3.8) expects main file as /app/main.py
from app import create_app

app = create_app('prod')

if __name__ == '__main__':
    app.run()
