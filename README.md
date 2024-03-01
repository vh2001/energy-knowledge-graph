# Energy Knowledge Graph

The projects builds knowledge graph for energy consumption.[TODO expand add pipeline image?]

# File structure

- `data` - contains the raw datasets and their metadata and later preprocessed data
- `scripts` - contains the scripts for preprocessing the data and populating the database
- `notebooks` - contains notebooks for data exploration and model training(TODO may remove)
- `src` - contains model training and evaluation code and some helper scripts
- `requirements.txt` - contains the python dependencies for the project without tensorflow
- `requirements.tensorflow.txt` - contains the python dependencies for tensorflow



## Installation / Use

If PostgresML is already deployed on remote machine, go to step 3. If database is already populated with the data, go to step 10.

The scripts are described in more detail in the [scripts README](./scripts/README.md).


1. Clone PostgresML [repository](https://github.com/postgresml/postgresml) `git clone https://github.com/postgresml/postgresml`
2. Navigate to postgresml directory `cd ./postgresml` and run `docker-compose up --build`
3. Start separate terminal and clone this [repository](https://github.com/sensorlab/energy-knowledge-graph) `git clone https://github.com/sensorlab/energy-knowledge-graph`
4. Navigate into energy-knowledge-graph directory, enter conda or virtualenv, and install dependecies with `pip install -r requirements.txt` and `pip install -r requirements.tensorflow.txt` if you want to use InceptionTime
5. Unzip the `data_dump_full.tar.gz` file in the data directory using `tar -xvf data_dump_full.tar.gz -C data`, optionally you can use only the data_sample.tar.gz file `tar -xvf data_sample.tar.gz -C data` instead 
5. Make sure that `./data/`folder contains contains required datasets and metadata data folder should be of structure `./data/metadata/` containing metadata and `./data/raw/` containing raw datasets
6. Create an .env file in the [scripts](./scripts/) directory with the following content:
    ```bash
    DATABASE_USER=<username to access PostgreSQL database>
    DATABASE_PASSWORD=<password to access PostgreSQL database>
    ```
7. Check [pipeline_config.py](./scripts/pipeline_config.py) for the configuration of the pipeline leave as is for default configuration
7. Run `python scripts/process_data.py` by default this will preprocess the data and store it in the database, 
8. Access PostgreSQL at port `:5433`, PostgresML dashboard at port `:8000`, and PostgresML documentation at port `:8001`




## Detailed pipeline script usage

The pipeline can be customized by changing the configuration in the [pipeline_config](./scripts/pipeline_config.py) file.

In the [pipeline_config.py](./scripts/pipeline_config.py) file you can set the following parameters:





- `STEPS` - list of data processsing steps to be executed
- `DATASETS` - list of datasets to be preprocessed
- `TRAINING_DATASETS` - list of datasets to be used to generate the training data
- `PREDICT_DATASETS` - list of unlabelled datasets to run the pretrained model on
- various paths for where to store the data and where to read the data from this is explained in    more detail in the [pipeline_config](./scripts/pipeline_config.py) file


The pipeline contains the following data processing steps:

1. [parse](./scripts/run_parsers.py) - This script runs the parsers for the datasets and stores the parsed datasets in pickle files
2. [loadprofiles](./scripts/loadprofiles.py) - This script calcualtes the load profiles for the households
3. [metadata](./scripts/generate_metadata.py) - This script generates metadata for the households and stores it in a dataframe as a parquet file
4. [consumption-data](./scripts/consumption_data.py) - This script calculates the electrictiy consumption data for the households and their appliances
5. [db-reset](./scripts/db_reset.py) - This script resets and populates the database with the households metadata, load profiles and consumption data
6. [training-data](./scripts/generate_training_data.py) - This script generates the training data for on/off appliance classification from the training datasets

and the following steps for predicting devices using a pretrained model (requires tensorflow):

1. [predict-devices](./scripts/label_datasets.py) - This script predicts the devices for the households using a pretrained model
2. [add_predicted_devices](./scripts/add_predicted_devices.py) - This script adds the predicted devices to the knowledge graph



[TODO add bibtex reference for paper]