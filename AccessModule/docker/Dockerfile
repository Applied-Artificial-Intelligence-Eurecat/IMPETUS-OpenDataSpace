FROM python:3.12
ENV PG_USERNAME=postgres
ENV PG_PASSWORD=p455w0rdD3v3l0p
ENV PG_HOSTNAME=host.docker.internal
ENV PG_PORT=5432
ENV PG_DATABASE=postgres
ENV ORION_URL=http://localhost:1026
ENV ORION_CONTEXT=http://host.docker.internal:8000/context/impetus.json
ENV FIWARE_FILES_PATH=/app/files
ENV FIWARE_CONTEXT_PATH=/app/context
ENV QUANTUM_LEAD_NOTIFY=http://quantumleap:8668/v2/notify
ENV HOSTNAME=accessmodule
WORKDIR /app
COPY ./requirements.txt .
RUN python3 -m pip install -r requirements.txt
COPY ./context /app/context
COPY ./src .
EXPOSE 80/tcp
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:80", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "4", "--timeout", "300"]