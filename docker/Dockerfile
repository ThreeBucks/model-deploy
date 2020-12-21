FROM harbor.bigo.sg/bigo_ai/icpm/content/auto-deploy-base:latest

COPY . /evg-ml-auto-deploy

WORKDIR /evg-ml-auto-deploy

RUN pip install --no-cache-dir -r src/requirements.txt

EXPOSE 5000

ENTRYPOINT ["gunicorn", "server:app", "-b", "0.0.0.0:5000", "-w", "4"]
