FROM python:3.12.2-slim

ENV USER=digeiz-user \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install --no-install-recommends -y \
    dumb-init \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system $USER && adduser --system --group $USER

ENV APP_DIR=/home/$USER/src

WORKDIR $APP_DIR

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY /src $APP_DIR

ENV PYTHONPATH=$APP_DIR

RUN chown -R "$USER":"$USER" $APP_DIR
USER $USER

CMD ["dumb-init", "gunicorn", "--config", "gunicorn_config.py", "drivers.rest.main:create_app()"]
