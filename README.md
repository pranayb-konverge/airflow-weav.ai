# Installation of Airflow on local Ubuntu machine. 

## Installation of Airflow:
### Inside your laptop Ubuntu terminal perform below tasks.
- To up the containers: `docker-compose -f docker-compose_local_executor.yaml up --build -d`
    - To down the containers: `docker-compose -f docker-compose_local_executor.yaml down -v`
- Docker compose to use: https://github.com/pranayb-konverge/airflow-tutorial/blob/main/airflow-local/docker-compose_local_executor.yaml
- The airflow will be running on the port `8080`. Use `http://localhost:8080/home` to access the airflow UI. Credentails will be `airflow`/`airflow`.
- To change the creds goto `docker-compose_local_executor.yaml` file and search `airflow-init`, under `environment`, update the `-airflow` for `_AIRFLOW_WWW_USER_USERNAME` and `_AIRFLOW_WWW_USER_PASSWORD`.

# Noun finder ETL orchestation DAG setup

## Where to do what?
- Place the file `get_me_noun_dag.py` in dags folder, if not present.
- Place the input file in the dage/files folder, if not present.
- Please create Variable in Airflow UI -> Admin -> Variables. Default values:
    - Key: `input_file_path` | Val: `example_text.txt`
    - Key: `output_file_path` | Val: `nouns.csv`
- Create a file connection in Admin -> Connections on Airflow UI. Only this much is needed and save. This is used for FileSensor operator in DAG.
    - Connection Id : `fs_default`
    - Connection Type: `File (path)`
    
## ERROR: 8080 port already in use
- When I run the command `docker-compose -f docker-compose.yaml up -d`, for webserver 
    - I got this error - `Error response from daemon: Ports are not available: exposing port TCP 0.0.0.0:8080 -> 0.0.0.0:0: listen tcp 0.0.0.0:8080: bind: address already in use`
- I check the port access for 8080 - `sudo lsof -t -i:8080` it gave me 2 ports in use `2078, 2084`
- The netstat cmd will give the name of the services these port are running - `sudo netstat -tulpn | grep LISTEN`, Services - `2078/docker-proxy`, `2084/docker-proxy`.
- I killed them using - `sudo kill -9 2078`
- Run the command `docker-compose -f docker-compose.yaml up -d` again.

## Note
- If the dags are not visible please restart the docker containers for webserver and scheduler.
- If you get file operations permission error, run this command in the sandbox: `sudo chmod 777 -R ./dags/ ./logs/`.
