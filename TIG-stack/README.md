# Description
This TIG stack is an updated version of the one provided by the IoT course. 
It uses `.env` file and updated versions of the images. 

## Steps: 
1. Rename the `change_env.txt`file into `.env`
2. (optional) You can change the values if you want to connect to your own repo or change the user name / passwords to create for the different software
2. Run `docker-compose up` from this repository to start the stack and create the database and user. 
   
**Beware that this repo does not use LoRaWAN and the consumer has been removed from `telegraf.conf` file. Refer to the [original repo](https://github.com/iot-lnu/tig-stack) to retrieve a template.**



## Original repo README
### TIG stack for IoT course, with Docker-compose

- On desktop systems like Docker Desktop for Mac and Windows, Docker Compose is included as part of those desktop installs.
- On Linux systems you need to install docker-compose. Follow the instructions on: https://docs.docker.com/compose/install/

#### First start

Download the folder and go to the directory. Start with ```docker-compose up``` (the old way), or as the updated docker cli ```docker compose up```, in this way you will be able to see all output. You can close with CTRL-C.

If you want to start the stack daemonised ```docker-compose up -d``` or ```docker compose up -d```

A database called "iot" is automatically created when the influxdb instance is started. You can access Grafana with http://localhost:3000, default user is king/arthur. You have to create a datasource in Grafana, choose InfluxDB and write http://influxdb:8086 as the address. The database should be "iot". Press "save and test" and check if it works.
