Expense tracking application built on the CubicWeb framework.
=============================================================

Developping with docker
=======================

Assuming you have a postgresql running on your machine where you can connect
with peer authentication, run "make dev" it will spawn an interactive shell
inside a docker container with the code mounted in develop mode. It mean you
can edit the code locally and run it in the container.

Some useful commands:

- ``cubicweb-ctl db-create -a fresh`` will create and initialize the database

- ``cubicweb-ctl pyramid -D -l info fresh`` will start the instance on
  http://localhost:8080


Deploying on kubernetes
=======================

The file `deployment.yaml` contains several containers split in several
deployments:

- `nginx` to serve static files directly

- `fresh` to run the application (and compile the latest translation)

- an *initContainers* `upgrade` before `fresh` that upgrade the database schema
  if there is a new `fresh` version.

- `fresh-scheduler` to have the scheduler running.


To create the initial database from an existing empty database::

   kubectl run -it fresh-dbcreate \
      --env CW_DB_HOST=db \
      --env CW_DB_USER=user \
      --env CW_DB_PASSWORD=pass \
      --env CW_DB_NAME=fresh \
      --image=hub.extranet.logilab.fr/logilab/fresh --command -- \
      cubicweb-ctl db-create --automatic --create-db=n fresh
   kubectl delete deployment fresh-dbcreate


Then generate a secret named "fresh" from where environment variables are set::

   kubectl create secret generic fresh-env \
      --from-literal CW_DB_HOST=db
      --from-literal CW_DB_USER=user \
      --from-literal CW_DB_PASSWORD=pass \
      --from-literal CW_DB_NAME=fresh \
      --from-literal CW_BASE_URL=https://fresh.example.com


You need to mount a cwclientlib configuration file to make
CWClientLibDataFeedParser. If you don't use this feature, just create an empty
file.

Create a file named cwclientlibrc and run::

   kubectl create secret generic fresh-cwclientlibrc --from-file=./cwclientlibrc


Create a persistent volume for bfss data::

   kubectl apply -f deploy/pvc.yaml


Then deploy fresh with::

   kubectl apply -f deploy/deployment.yaml
