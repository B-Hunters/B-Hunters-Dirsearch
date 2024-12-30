FROM python:3.10-slim
RUN pip install --no-cache-dir b-hunters==1.1.13 dirsearch
WORKDIR /app/service
COPY dirsearchm /app/service/dirsearchm
CMD [ "python", "-m", "dirsearchm" ]