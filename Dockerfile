FROM python:3.7-slim

LABEL name="ansible-runner"

ARG APP_USER=appuser
RUN groupadd -r ${APP_USER} && useradd --no-log-init -r -g ${APP_USER} ${APP_USER}

RUN mkdir -p /.ansible/ && \ 
    chgrp -R 0 /.ansible/ && \
    chmod -R g=u /.ansible/

ADD requirements.txt requirements.txt 

RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential \
&& pip3 install --no-cache-dir -r requirements.txt \
&& pip3 install --no-cache-dir ansible psutil ansible-runner \
&& apt-get purge -y --auto-remove gcc build-essential 


WORKDIR /app
COPY . /app

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]