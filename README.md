# pycsw-dynamic

A Repository plugin for [pycsw](https://github.com/geopython/pycsw) for creating XML metadata on the fly.  

The XML document is created by merging info from the DB into an ISO19139 template. 


## Installation

### Setup virtualenv

- Create virtualenv

      python3.8 -m venv --prompt CSW-Dyn  /YOUR/VENV/PATH

- Activate venv

      . /YOUR/VENV/PATH/bin/activate

- Upgrade stuff

      pip install --upgrade pip


### Install `pycsw`

- Clone repo
  
      git clone https://github.com/geopython/pycsw.git
      cd pycsw
      git checkout 2.6  

- Install requirements

      pip install -r requirements.txt
      pip install -r requirements-pg.txt
      pip install -r requirements-standalone.txt
 
- Install pycsw

      pip install -e .

  You should get
  ```
  Successfully installed pycsw-2.6.1 
  ```
  
### Install `pycsw-dynamic`

- Clone repo
 
- Install pycsw

      pip install -e .

## Configuration

- Copy `pycsw-config.sample` to `pycsw-config.cfg`
- Edit `pycsw-config.cfg` setting at least:
  - `server.home`
  - `server.url`
  - `repository.database`

### Env variables

Please note that you can use environment variables inside the conf file, e.g.:

    database=${PYCSW_REPO_DATABASE}

## Running `pycsw`

As per pycsw doc, run pycsw locally by issuing:

    PYCSW_CONFIG=/PATH/TO/YOUR/pycsw-config.cfg python pycsw/wsgi.py 

## Build docker image

- Copy `pycsw-config.sample` to `pycsw-config-docker.cfg`
- Edit the config file:
  - Set the proper DB connection in `repository.database` entry
  - Set the URL where pycsw will be called in `server.url` entry
  - Set the required template path in `pycsw-dynamic.iso_template` entry (the one for docker is already there, commented out)
  - Edit any other entry you need 
  - *Remember that you can use [env vars](#env-variables) for setting the various items*
- Build the docker image
 
      docker build . --tag pycsw-dynamic:latest

- Run the container
 
      docker run -p 8000:8000 pycsw-dynamic

# License

```
Copyright 2022, European Union.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
