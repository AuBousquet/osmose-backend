# Tutorial: add an SQL analyser

## Installation
Install locally the Osmose backend, after cloning this repository.

Create a virtual environment and install the dependencies inside.
```bash
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Install the needed packages.
```bash
sudo apt install build-essential python3-dev python3-virtualenv libpq-dev protobuf-compiler libprotobuf-dev
sudo apt install g++ libboost-python-dev libosmpbf-dev make pkg-config python3-dev
```

Compile the C++ sources.
```bash
cd modules/osm_pbf_parser/
make
```

Create a production database. 
```bash
sudo -u postgres psql
create user osmose;
alter user osmose password '-osmose-';
create database osmose owner osmose;
\c osmose;
create extension hstore; 
create extension fuzzystrmatch; 
create extension unaccent; 
create extension postgis;
```

Create a test database.
```bash
sudo -u postgres psql
create database osmose_test;
\c osmose_test;
create extension hstore; 
create extension fuzzystrmatch; 
create extension unaccent; 
create extension postgis;
grant select, update, delete on table spatial_ref_sys TO osmose;
grant select, update, delete, insert on table geometry_columns TO osmose;
```

Fill the `.pgpass` file with the following lines:
```bash
localhost:5432:osmose:osmose;-osmose-
localhost:5432:osmose_test:osmose;-osmose-
```

## Launch of the analyses

Change:
- the `db_host` parameter in the `osmose_config.py` file to `localhost` ;
- the `dir_work` parameter in the `modules/config.py` file to a place where you are allowed to write.

Launch Python script at the root folder of the project:
```bash
python ./osmose_run.py --no-clean --country=france_bretagne_cotes_d_armor --skip-upload
```

The following options can be used:
- `--no-clean`: don’t remove extract and database after analyses;
- `--country=monaco`: charge the data on this area (Monaco), you can list the available countries or regions with `python osmose_run.py --list-country`;
- `--skip-download`: do not download OSM extract again;
- `--skipupload`: do not upload the analysis to the frontend at the end;
- `--skip-init`: do not initialize the database;
- `--result-format`: result format, xml (default), csv or geojson.

## What is done

This command will do the following tasks.

| Logger message | Task |
|----------------|------|
| `loading analyses` | Load analysers as python modules |
| `check database` | Check if database contains all necessary extensions |
| `run osmosis replication` | Check if database needs to be synchronized with the OSM server |
| `import osmosis schema` | Create schema to store data for the chosen area |
| `import osmosis data` | Fills tables `nodes.txt`, `ways.txt`, `way_nodes.txt`, `relations.txt`, `relation_members.txt`, `users.txt`, as defined in `osmose_config.py` by `osmosis_import_scripts`|
| `import osmosis post scripts` | Executes scripts defined in `osmose_config.py` by `osmosis_post_scripts` variable (creates index on tags, creates functions usefull for analysers) |
| `import post scripts` | Executes scripts defined in `osmose_config.py` by `sql_post_scripts` variable (added to geo datasets) |
| `country : analyser` | Executes each analyser |
| `cleaning` | Cleans database and .pbf files |

The results are stored in the folder pointed by the `dir_work` parameter of `modules/config.py` file.

## Download OSM extract data in the database

To download a PBF file containing the OSM extract in the PostgreSQL-PostGIS database, you must use the following command:
```shell
python ./osmose_run.py --no-clean --country=france_bretagne_cotes_d_armor --skip-analyser --skip-upload
```

## Add new analysers

There are 5 source tables :
- `zone_elligibilite_rip`;
- `cable_fttx_rip`;
- `parcours_fttx_rip`;
- `pf_rip`;
- `site_support_rip`.

### Add a new merge analyser

To load data from the `merge_data` local folder, you have to define a shape source in the initialisation of you herited class from `Analyser_Merge`, like in that example:
```python
    parser=SHP(
            Source(
                attribution="Orange",
                millesime="2024",
                encoding="iso-8859-1",
                file="cable_fttx_rip.zip"
            ),
        zip="cable_fttx_rip.shp",
        srid=4326
    )
```

Once your merge analyser is defined, launch it with the following command:
```shell
python ./osmose_run.py --no-clean --country=france_bretagne_cotes_d_armor --analyser merge_orange_fttx_cable_FR --skip-upload --result-format csv
```

If you want to relaunch it, without having to download the PBF file and to create the database again, add the following options:
```shell
--skip-init --skip-download 
```


### Add a new osmosis SQL analyser

You have to define to which item the error you want to identify belongs to. You can either use the Osmose classical issue numbering (see [wiki](https://wiki.openstreetmap.org/wiki/Osmose/issues)) or define your own item id, if it is not already referenced.

We have chosen to add specific items codes for Orange data verifications:
- a code for internet infrastructure integration: 8393;
- a code for internet network structure related problems: 1400;
    - Class 1: the begining point of the geometry of the FTTX cable does not correspond to the geometry of the associated site;
    - Class 2: the end point of the geometry of the FTTX cable does not correspond to the geometry of the associated site.

To launch an `osmosis_analyser`, you have to use this type of command:
```shell
python ./osmose_run.py --no-clean --country=france_bretagne_cotes_d_armor --analyser osmosis_powerline --skip-init --skip-download --skip-upload
```
