# newsworthy-py: nw_connections.py

A Python package for connections to databases and other storages etc in the Newsworthy project.



### Install package

`pip install nw_connections`


### Run tests

`make tests` (run all tests)

`make test file=path/to/test` (run specific test)

### Deploy

To Github:

`make deploy_new_version v=1.0.2 msg="Made some changes"`

The current version is defined in `CURRENT_VERSION.txt`. This file is updated with this make command.

To PyPi:

`python upload_to_pypi.py`
