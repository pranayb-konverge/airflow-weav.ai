# python imports
import os
from os.path import exists
import logging
from datetime import datetime, timedelta
import csv

# airflow imports
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.exceptions import AirflowSensorTimeout

# lib import
import spacy

logger = logging.getLogger()

# globle variables
output_file_path = "./dags/files/" + Variable.get("output_file_path") # By default: "./dags/files/nouns.csv"
input_file_path = "./dags/files/" + Variable.get("input_file_path")  # By default: "./dags/files/example_text.txt"


"""
    Check if output file are avaialble, if not create a new one.
"""

def check_output_file():
    try:
        output_file_exists = exists(output_file_path)
        # If output file does not exist create a new one
        if not output_file_exists:
            file = open(output_file_path, "a")
            file.close()
            return "Outupt CSV file created."
        else:
            return "Outupt CSV file is available."
    except Exception as e:
        logger.error(f"Exception while creating nouns.csv file. Error:{str(e)}")
        return str(e)
# end of check_output_file method


"""
    This method will read the lines from the file and 
    for each line it will check the NOUNs using spacy module.
    Then it will save the line with nouns in the output csv file.
"""

def noun_finder_etl():
    line_number = 1
    nouns = []
    try:
        # Documentation: 
        # spacy.load() is a convenience wrapper that reads the pipeline's config.cfg, 
        # uses the language and pipeline information to construct a Language object, 
        # loads in the model data and weights, and returns it.
        nlp = spacy.load("en_core_web_sm")
        input_file = open(input_file_path, "r")
        lines = input_file.readlines()
        # iterate over each line
        for line in lines:
            logger.info(f"Line number {line_number}, readed: {line}")
            # the nlp object will analyse the line and construct a spacy.tokens.doc.Doc class,
            # this doc is iterable.         
            doc = nlp(line)
            for token in doc:
                # we will only search for the `NOUN` POS and get the text out of it.
                if token.pos_ == "NOUN":
                    nouns.append(token.text)                    
            # We will construst the csv_line to be saved in output file with line number
            all_nouns_of_the_line_in_str = ",".join(nouns)
            csv_line = f"{line_number}. {all_nouns_of_the_line_in_str}"
            with open(output_file_path,'a') as output_file:
                output_file.write(csv_line)
                output_file.write("\n")               
            nouns.clear()
            line_number += 1
            logger.info(f"List of Noun found at line: {csv_line}")
        return "Operation completed!"
    except Exception as e:
        logger.error(str(e))
        return str(e)
                
# end of read_file_and_save_to_csv method

def _failure_callback(context):
    if isinstance(context['exception'], AirflowSensorTimeout):
        logger.info("Sensor timed out %s \n", context)
# end of _failure_callback method

default_args = {
    'owner': 'Airflow-Test1.0',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'trigger_rule': 'none_failed_or_skipped'
}

with DAG('get_me_noun_dag', 
        default_args=default_args, 
        start_date=datetime(2022, 9, 28), 
        schedule_interval='@hourly',
        catchup=False) as dag:
    
    """ 
        This task is to check if the input file is available or not. 
        If not then the task will retry as per  poke_interval.
    """
    check_input_file_task_1 = FileSensor(
        task_id='check_input_file_task_1',
        poke_interval=30, # time in sec that the job should wait in bwtween each tries
        timeout=60 * 30, # need to timeout as poke_interval is only 30 sec.
        mode="reschedule", # worker task will relase the file for other intervals.
        on_failure_callback=_failure_callback, # if failed log the event
        filepath= os.path.join(os.getcwd(), input_file_path[2:]), 
        # create a file connection in Admin > Connections on Airflow UI. No need to give any task to the connection.
        fs_conn_id='fs_default'
    )
    
    """
        Check if output file are avaialble, if not create a new one.
    """
    check_output_file_task_2 = PythonOperator(
        task_id='check_output_file_task_2',
        provide_context=True,
        python_callable=check_output_file
    )
    
    """
        This method will read the lines from the file and 
        for each line it will check the NOUNs using spacy module.
        Then it will save the line with nouns in the output csv file.
    """
    find_noun_task_3 = PythonOperator(
        task_id='find_noun_task_3',
        provide_context=True,
        python_callable=noun_finder_etl
    )
    
    
    """
        Execution path of the tasks
    """
    check_input_file_task_1 >> check_output_file_task_2 >> find_noun_task_3
    
