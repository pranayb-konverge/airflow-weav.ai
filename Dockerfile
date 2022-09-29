## This docker file contains deployment related commands and filenames which can be used for installation at any system or machine.

# Importing Airflow Image, building it and using in docker compose file
FROM apache/airflow

# The airflow user should have the same UID as the user running docker on the host system.
# ARG DOCKER_UID
# RUN \
#     : "${DOCKER_UID:?Build argument DOCKER_UID needs to be set and non-empty. Use 'make build' to set it automatically.}" \
#     && usermod -u ${DOCKER_UID} airflow \
#     && echo "Set airflow's uid to ${DOCKER_UID}"

# USER airflow

# ENV PYTHONPATH $PYTHONPATH:$AIRFLOW_HOME/dags
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm
