## This docker file contains deployment related commands and filenames which can be used for installation at any system or machine.

# Importing Airflow Image, building it and using in docker compose file
FROM apache/airflow

# ENV PYTHONPATH $PYTHONPATH:$AIRFLOW_HOME/dags
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm
