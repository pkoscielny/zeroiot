FROM tiangolo/meinheld-gunicorn-flask:python3.6-alpine3.8

RUN apk update && apk add sqlite
COPY ./ /app
WORKDIR /app
RUN pip install --upgrade pip && pip install -r configs/requirements.txt

# By default is prod.
ENV FLASK_ENV = 'prod'

EXPOSE 3000

# docker build -t zeroiot -f configs/Dockerfile ./
# docker run --rm -d -p 3000:80 zeroiot
# curl http://localhost:3000/air_state
# docker ps -a
# docker exec -it <CONTAINER_ID> /bin/sh
# docker <stop|start|rm> <CONTAINER_ID>
