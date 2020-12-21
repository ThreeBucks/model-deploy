FROM harbor.bigo.sg/bigo_ai/icpm/content/auto-deploy-base:latest

COPY tools /tools

COPY src/requirements.txt /evg-ml-auto-deploy/requirements.txt

RUN pip install --no-cache-dir -r /evg-ml-auto-deploy/requirements.txt

COPY . /evg-ml-auto-deploy

WORKDIR /evg-ml-auto-deploy

EXPOSE 5000

ENTRYPOINT ["python3", ""server:app", "-b", "0.0.0.0:5000", "-w", "32""]
