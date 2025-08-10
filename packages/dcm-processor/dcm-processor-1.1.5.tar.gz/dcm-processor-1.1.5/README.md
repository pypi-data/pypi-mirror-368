# DCM PROCESSOR
A dicom processing library setup with docker containers.

## DEPENDENCIES
1. Python (version  >= 3.6)
1. Docker
2. Docker Compose  (you can install with `pip` package manager with the command `pip install docker-compose`)

### NOTES ON DEPENDENCIES
1. Current version of the library supports only unix (linux and macOS). However the library was developed and well tested on Ubuntu 20.04.
2. Current user should have access to execute docker commands without sudo. This can be normally achieved in linux with the command below:  
`sudo usermod -aG docker $USER`
3. You need to make sure you have the current version of `docker-compose` installed.


## INSTALLATION
`pip install dcm-processor`

## CREATE AN APPLICATION
1. Run the command below and follow the prompt.  
`dcm-processor create app`

2. In case you did not select `yes` to initialize the application after creation then run the command below to initialize the application.  
`dcm-processor init app`


## START AN APPLICATION
1. Run the command below and select the application to start it.  
`dcm-processor start app`

## STOP AN APPLICATION
1. Run the command below and select the application to remove it.  
`dcm-processor stop app`


## CREATE A SERVICE TEMPLATE
1. Run command below and follow prompt to create a service template.  
`dcm-processor create service`
2. Fill in the files in `registry` folder and copy your source code into the `module` folder.

### Service entry in the `registry`
- The `settings.json` file can either be an object or an array of objects with the following fields:
    * `jobName` :  [string,required] the name of the job, this should be unique from other service jobs.

    * `worker` : [string,required] name of the function to be run as the worker, this should be a full function name. (see section below for details.).

    * `callback` : [string,required] name of the function which determines if a job should be scheduled for the current dicom processing or not. (see section below for details).

    * `dependsOn` : [string/list of string,optional] name(s) of jobs which the current service job depends on. this will make sure that those jobs run successfully before this job runs.

    * `priority` : [string,optional] the priority level assigned to this job. if not specified a default priority is assigned.

    * `timeout` : [string/number,optional] the RQ queuing timeout default is 1 hour.

    * `params`: [object,optional] this is an object with additional parameters that will be sent to the worker function.

    * `sortPosition` : [number,optional] this is a sorting variable which is used to sort the order in which jobs are scheduled (Note: independent jobs are however scheduled before dependent jobs).

    * `description` : [string,optional] this is a description for this current job. Its not used in any operation but only for third parties to have an idea what your service does.

- The python file `__init__.py` should contain the `callback` function(s) you stated in the `settings.json` file


## INSTALL SERVICE
1. Run command below and follow prompt to install a service.  
`dcm-processor install service`


## REMOVE SERVICE
1. Run command below and follow prompt to remove a service.  
`dcm-processor remove service`


## CREATE WORKER TEMPLATE
1. Run command below and follow prompt to create a worker template.  
`dcm-processor create worker`

2. Fill in the files as follows:  
    - The `settings.json` file can either be an object or an array of objects with the following fields:
        * `name` :  [string,required] the name of the worker, this should be unique from other worker.

        * `scripts` : [list of shell scripts] scripts that are executed `during building of the docker image` to install optional packages etc. defaults `["script.sh"]` pointing to the default script file in the template.

        * `entryScriptPaths` : [list of mounted paths] name of docker mounted path which will contain shell script that are executed at the start of the worker. This can be used to executed dynamic shell scripts `during container runtime`.

        * `baseImage` : [string, required] name of the base docker image to build the container on. defaults ubuntu:20.04.

        * `environments` : [list of objects] a list of virtual environment configurations. Each object contains the fields below:    

            * `name` : [string, required] the name of the virtualenv. Should be unique for all virtualenvs in the current worker.

            * `requirements`: [list of file paths] requirements files with python libraries to be installed in the virtualenv. This is executed `during building of the docker image`.

            * `entryRequirementPaths` : [list of mounted paths] List of docker mounted paths which will contain requirements files which can be used to update the python library dynamically. These are executed at the start of the worker `during runtime`.

            * `channels` : [list of string] this is the list of `service channels` that will be executed with this virtualenv.

            * `pythonVersion` : [string] the version of python to be used for this virtualenv.

    - The `script.sh` can be used to run any shell commands needed to install extra packages like `java, compilers, etc` needed to run the service modules.

    - The `requirements.txt` should be filled with the python libraries needed to run the service modules.


## INSTALL WORKER
1. Run command below and follow prompt to install a worker.  
`dcm-processor install worker`


## REMOVE WORKER
1. Run command below and follow prompt to remove a worker.  
`dcm-processor remove worker`

## TO DOS
1. Add documentation for non-interactive (-o) mode.
2. Add autostart function to start applications at boot time.
3. Support windows environment.
4. Run tests on other linux systems.