FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    nginx \
    curl \
    ca-certificates \
    envsubst \
    && rm -rf /var/lib/apt/lists/*

COPY nginx.conf.template /etc/nginx/sites-available/default

COPY . /app
WORKDIR /app

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/start_xray.sh

EXPOSE 8080

CMD ["/app/entrypoint.sh"]
