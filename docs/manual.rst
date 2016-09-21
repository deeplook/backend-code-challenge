Manual
======

This is a sample Python-based implementation of the *Snowdonia* backend code challenge as described in the file ``CHALLENGE.md`` inside this archive. Basically, it's about implementing, deploying and testing a microservice with a simulation of 1000 vehicles, moving in the local area around a chosen city center, and posting their location data regularly to an API endpoint which stores them persistently for later usage. 

.. figure:: sample_trajectory.png
   :width: 90 %
   :align: center

   Example randomized trajectory of a single vehicle (red), plus city center (blue), here: Berlin.


Implementation Overview
-----------------------

For the sake of simplicity (and easier validation on maps) all vehicles start at the same chosen city center (selected here without loss of generality to be the center of Berlin). They have a constant speed (selected randomly from a certain interval), and move in some randomized fashion (building circle-like patterns). They send their GPS data to the API endpoint (``POST /data``) after a fixed 20 second time period if they are within a distance of up to 50 km to the given city center.

The vehicles' data is stored in a single table of a SQLite3 database. Apart from the single API endpoint for posting data there is also a minimal "front-end" which allows to download the database content in CSV format and generate a map for the vehicles' trajectories. This is very helpful during development, but isn't strictly part of the challenge description. Therefore, it's also kept rather simplistic.

The steps in the following sections can be followed one by one to get the system up and running.


Local Project Setup
-------------------

First open the archive named snowdonia.tgz and change into the resulting directory like this:

.. code-block:: bash

    $ tar xfz snowdonia.tgz
    $ cd snowdonia

All further commands should be executed from this directory, unless some reason is given for doing it otherwise.


Install Python
..............

Install a Python3 distribution named Miniconda, shown here for Mac OS X. For other platforms see http://conda.pydata.org/miniconda.html.

.. code-block:: bash

    $ curl -O https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
    $ bash Miniconda3-latest-MacOSX-x86_64.sh -b -f -p ~/mc3
    $ rm Miniconda3-latest-MacOSX-x86_64.sh
    $ ~/mc3/bin/conda install basemap
    $ ~/mc3/bin/pip install -r requirements.txt
    $ ~/mc3/bin/pip install boto3

Since for the real deployments a tool named Fabric will be used (instead of heavier tools like Ansible or Saltstack), which is still not fully migrated to Python3, you need to install a version of Miniconda for Python2 as well:

.. code-block:: bash

    $ curl -O https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh
    $ bash Miniconda2-latest-MacOSX-x86_64.sh -b -f -p ~/mc2
    $ rm Miniconda2-latest-MacOSX-x86_64.sh
    $ ~/mc2/bin/pip install fabric


Configuration
.............

The destination platform for this project is an AWS EC2 server. If you want to replicate the deployment process the following assumptions are made: you have an AWS account with an IAM user. To run any deployments from a local machine you must have these two files, ``~/.aws/credentials`` and ``cat ~/.aws/config``, that contain valid values for your AWS keys and an EC2 region name (below preselected as ``eu-central-1``):

.. code-block:: bash

    $ cat ~/.aws/credentials
    [default]
    aws_access_key_id = <REPLACE-WITH-YOUR-OWN>
    aws_secret_access_key = <REPLACE-WITH-YOUR-OWN>

    $ cat ~/.aws/config
    [default]
    region = eu-central-1

Another config file inside the unpacked archive, named ``config.ini``, contains additional configuration options that you *can* change, but don't have too. Two fields in its AWS section, ``instance_id`` and ``instance_ip``, will be updated dynamically during the deployment process as you create a new instance for deployments. 

.. code-block:: bash

    $ cat config.ini
    [AWS]
    image_id = ami-02724d1f
    instance_type = t2.micro
    instance_tag = Context:snowdonia
    keypair_name = snowdonia
    secgroup_name = snowdonia
    instance_user = admin
    instance_id =
    instance_ip =

    [SERVICE]
    debug = True
    port = 5000
    endpoint = /data
    database = snowdonia.db


Create a Database
-----------------

This archive contains a sample SQLite3 database in ``snowdonia.db``. You can leave it as-is, but you can also create a new empty database from scratch using ``database.py`` as shown below:

.. code-block:: bash

    $ ~/mc3/bin/python3 database.py
    Usage: database.py create | dump_sql | dump_csv | delete

    $ ~/mc3/bin/python3 database.py delete

    $ ~/mc3/bin/python3 database.py create

    $ ~/mc3/bin/python3 database.py dump_sql
    BEGIN TRANSACTION;
    CREATE TABLE traffic (
                    uid text,
                    type text,
                    timestamp real,
                    longitude real,
                    lattitude real,
                    heading real
                );
    COMMIT;

    $ ~/mc3/bin/python3 database.py dump_csv
    ,uid,type,timestamp,longitude,lattitude,heading

You can populate this database, adding randomized data using ``simulate.py``.

.. code-block:: bash

    $ ~/mc3/bin/python3 simulate.py -h
    usage: simulate.py [-h] [--live] [--store MODE] num dur

    Simulate vehicles moving and sending data.

    positional arguments:
      num           Number of vehicles to create.
      dur           Duration in seconds to run the simulation.

    optional arguments:
      -h, --help    show this help message and exit
      --live        Run in real-time mode (waiting for time to pass)
      --store MODE  Data storage mode, either "database" (default) or "api".

Run this to add trajectories for two vehicles and 40 seconds directly into the database. The output shows two vehicles in their start states and, after a blank line, additional states after moving to their next locations. The columns are: UID, Timestamp, Lattitude, Longitude and Heading:

.. code-block:: bash

    $ ~/mc3/bin/python3 simulate.py --store database 2 40
    44391310-212c-4bc3-b31d-68bb71033be7 1473009221.873277 52.516667 13.383333 84.47983062861165
    e7698142-3a16-4a58-a7f4-44d9aeab663d 1473009221.873366 52.516667 13.383333 223.81197720171508

    44391310-212c-4bc3-b31d-68bb71033be7 1473009241.873277 52.516772644306116 13.385125096966247 88.77983062861165
    44391310-212c-4bc3-b31d-68bb71033be7 1473009261.873277 52.516796019466554 13.386925136392584 84.37983062861164
    e7698142-3a16-4a58-a7f4-44d9aeab663d 1473009241.873366 52.51544206823732 13.381406744095392 233.6119772017151
    e7698142-3a16-4a58-a7f4-44d9aeab663d 1473009261.873366 52.51443502552337 13.379166893952485 242.4119772017151

Now you can have a look at the database:

.. code-block:: bash

    $ ~/mc3/bin/python3 database.py dump_csv
    ,uid,type,timestamp,longitude,lattitude,heading
    0,44391310-212c-4bc3-b31d-68bb71033be7,car,1473009241.873277,13.385125096966247,52.516772644306116,88.77983062861165
    1,44391310-212c-4bc3-b31d-68bb71033be7,car,1473009261.873277,13.386925136392584,52.516796019466554,84.37983062861164
    2,e7698142-3a16-4a58-a7f4-44d9aeab663d,car,1473009241.873366,13.381406744095392,52.51544206823732,233.6119772017151
    3,e7698142-3a16-4a58-a7f4-44d9aeab663d,car,1473009261.873366,13.379166893952485,52.51443502552337,242.4119772017151

If you use the ``--live`` flag the data is saved in "real-time" as it would be created by the simulated vehicles (which can take a while). This is implemented using asynchronous coroutines, which is not strictly necessary. Threads would do here as well, but this was something like a little challenge inside the real challenge.

If you use the ``--mode api`` option the data is posted to the database via the API endpoint of the microservice implemented in this code challenge. But first, the microservice needs to be started, as shown in the next section.


Run a Local Server
------------------

Running a local server simply means executing the command ``python3 serve.py``:

.. code-block:: bash

    $ ~/mc3/bin/python3 serve.py
     * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger pin code: 227-187-639

Then you can open your favourite webbrowser and enter some of the following addresses. Make sure you adapt the port number or vehicle UID if you change the configuration or create your own vehicles:

    - http://0.0.0.0:5000/
    - http://0.0.0.0:5000/data.csv
    - http://0.0.0.0:5000/data.csv?uid=44391310-212c-4bc3-b31d-68bb71033be7
    - http://0.0.0.0:5000/data.csv?type=bus&duration=PT1H

The vehicle ``type`` filter can be used to show only some type of vehicles (here: bus, taxi, train, tram). And the ``duration`` filter can be used to show vehicle locations taken with timestamps between now and the given duration back in time. Durations must be given in ISO 8601 format, see https://en.wikipedia.org/wiki/ISO_8601#Durations. "PT1H" means one hour. The returned CSV file will be the same like the one returned by the command ``python3 database.py dump_csv``. 

If the server is running you can also add other vehicle entries via the dedicated POST API endpoint when using ``simulate.py`` from the command-line. In this case the vehicles added are of type "tram" and are added in real-time, so the simulation does actually take 40 seconds:

.. code-block:: bash

    $ ~/mc3/bin/python3 simulate.py --store api --type tram --live 2 40
    2fa74786-ccc7-4673-9fbb-34a1f147c02d 1473013327.619334 52.516667 13.383333 306.85073628462925
    56dc239a-57d7-4bf9-9ba6-8c5dd8c17ebe 1473013327.61942 52.516667 13.383333 212.5634918116318

    56dc239a-57d7-4bf9-9ba6-8c5dd8c17ebe 1473013347.625095 52.51477352263088 13.381350918876912 214.9634918116318
    2fa74786-ccc7-4673-9fbb-34a1f147c02d 1473013347.652002 52.51813410833846 13.380124027631766 307.4507362846293
    56dc239a-57d7-4bf9-9ba6-8c5dd8c17ebe 1473013367.657075 52.512932340202866 13.379240697238707 214.1634918116318
    2fa74786-ccc7-4673-9fbb-34a1f147c02d 1473013367.670516 52.51962163574963 13.376940308884501 312.65073628462926


Test on a Local Server
----------------------

For this challenge testing does not include the usual unit-testing, but means "only" testing the performance of the API endpoint for posting location data. The document named ``testing.rst`` describes using a dedicated tool to conduct this kind of performance tests in a systematic and reproducible way.

The following example shows only a very simple way to do this kind of testing during development using a tool like ``curl`` (the tested endpoint returns the plain text "saved", if successful): 

.. code-block:: bash

    $ curl -X POST "http://localhost:5000/data" --data "uid=76b1b23a-9763-41e8-9727-a63955cb5daf&type=bus&timestamp=1472716308.602317&longitude=13.383333&lattitude=52.516667&heading=123"
    saved


Deployment
----------

Deployments are performed on temporary remote AWS EC2 instances. These can be managed using the ``remote.py`` intended to create, list and delete an instance and its security group and keypair file. The following interaction shows a full cycle from creating to deleting such a remote instance.

This tool tries to be idempotent when performing its actions, but there might be little issues to solve, especially about timing (when waiting for an instance to be fully ready or terminated). So in these cases, but also in general, it makes a lot of sense to watch your AWS management console to verify what is going on and, mabye, perform some action manually, if really needed.

.. code-block:: bash

    $ ~/mc3/bin/python3 remote.py create
    created AWS key pair named "snowdonia"
    created file "snowdonia.pem"
    chmod to 400 for file "snowdonia.pem"
    found my public IP: "77.179.222.43"
    created security group named "snowdonia"
    created inbound access rules for security group named "snowdonia"
    created instance with id "i-3fdc8583"
    tagged instance "i-3fdc8583" with tag "{'Key': 'Context', 'Value': 'snowdonia'}"
    instance "i-3fdc8583" has public IP "52.28.92.85"
    created instance has public IP: 52.28.92.85

    $ ~/mc3/bin/python3 remote.py list
    found AWS key pair named "snowdonia"
    found AWS security group named "snowdonia"
    found instance i-3fdc8583 t2.micro
    instance "i-3fdc8583" has public IP "52.28.92.85"
    instance has public IP: 52.28.92.85
    use this command to login via ssh: ssh -i snowdonia.pem admin@52.28.92.85

    $ ~/mc3/bin/python3 remote.py delete # might be slightly buggy

With the ``ssh`` command listed by ``python3 remote.py list`` you can connect to the fresh instance and do whatever you like, but the idea is, of course, to provision it automatically, deploy the microservice on it, and run it from your local development machine.

As mentioned above this is done with Fabric are done using Python2. After installing Fabric (shown above in section *Install Python*), you have a tool named ``fab`` which operates on the local file named ``fabfile.py`` which contains deployment functions:

.. code-block:: bash

    $ ~/mc2/bin/fab -l

    This is used for server provisioning, deploying and starting the service.

    Provisioning is done in this case to some AWS EC2 server. And deployment
    consists of copying a local development folder to the remote server.

    This uses Fabric, since it is simpler than Ansible or Saltstack. Notice
    that Fabric currently is still recommended to be used on Python 2! You
    can install Fabric with ``pip install fabric``.

    Examples:

        fab -l
        fab -h
        fab -i snowdonia.pem -u admin -H 52.57.6.142 provision
        fab -R aws provision

    Available commands:

        dependencies  Install dependencies on remote server.
        deploy        Deploy code to remote server.
        provision     Provision remote server.
        serve         Run remote service (until you quit this command!).

You can find out more about ``fab`` by calling ``fab -h``. To fully prepare an instance with all code needed (including the Python microservice implementation for this challenge) you can run this sequence, using ``-R aws`` (R for role) for automatically picking the correct public IP of your instance from ``config.ini`` and run commands over ``ssh`` (output removed for brevity):

.. code-block:: bash

    $ ~/mc2/bin/fab -R aws provision
    ...

    $ ~/mc2/bin/fab -R aws dependencies
    ...

    $ ~/mc2/bin/fab -R aws deploy
    ...

To start the service on the remote instance you can execute the following command:

.. code-block:: bash

    $ ~/mc2/bin/fab -R aws serve
    [admin@52.57.27.69] Executing task 'serve'
    ** When this is ready you can open http://52.57.27.69:5000/ in a webbrowser!
    [admin@52.57.27.69] run: /home/admin/miniconda3/bin/python serve.py
    [admin@52.57.27.69] out:  * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
    [admin@52.57.27.69] out:  * Restarting with stat
    [admin@52.57.27.69] out:  * Debugger is active!
    [admin@52.57.27.69] out:  * Debugger pin code: 151-953-816
    [admin@52.57.27.69] out:

Notice the hint on the URL to open in a webbrowser to verify that your service is running (your instance IP will be, very likely, a different one)!


Test on a Remote Server
-----------------------

Again, you can post a vehicle location to the dedicated API endpoint, now on the remote server, and you will get the same "saved" response if everything works as expected. The following shows this with a slightly funky UID:

.. code-block:: bash

    $ curl -X POST "http://52.57.27.69:5000/data" --data "uid=11111111-1111-1111-1111-111111111111&type=bus&timestamp=1472716308.602317&longitude=13.383333&lattitude=52.516667&heading=42"
    saved

    $ curl -X GET "http://52.57.27.69:5000/data.csv?uid=11111111-1111-1111-1111-111111111111"
    ,uid,type,timestamp,longitude,lattitude,heading
    0,11111111-1111-1111-1111-111111111111,bus,1472716308.602317,13.383333,52.516667,42.0

The document named ``testing.rst`` describes many more detailed tests conducted via a dedicated tool.


Maps
----

When developping this code it was very helpful to be able to "see" a visual representation of the whole set of vehicles and their movements across some territory. Therefore there is an endpoint to generate maps showing the location of the vehicles in the database (see figure below). You can also provide a UID as a query parameter to plot the trajectory of only that one vehicle with this UID:

- http://0.0.0.0:5000/map/traffic
- http://0.0.0.0:5000/map/traffic?uid=<UID>

.. figure:: all_trajectories.png
   :width: 90 %
   :align: center

   All trajectories (red) in a fresh database with 10 vehicles moving for 10 minutes from the city center (blue).
