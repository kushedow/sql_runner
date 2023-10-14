nohup uvicorn main:app --ssl-certfile /etc/ssl/certificate.crt --ssl-keyfile /etc/ssl/private.key --host 0.0.0.0 --port 443 &
