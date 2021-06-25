#!/bin/bash
set -e

git clone https://github.com/igor-davidyuk/openfl.git
cd openfl
git checkout model-proto-ll
python3.7 -m pip install --upgrade pip
python3.7 -m pip install virtualenv
python3.7 -m virtualenv --python=python3.7 env-openfl
source ./env-openfl/bin/activate
pip install -e .
pip install torchvision
cd openfl-tutorials/interactive_api_tutorials_experimental/director_kvasir/

# jupyter notebook --ip=0.0.0.0 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''

get best model
envoy registry - remove envoy
remove experiment workspace on envoy side in case of fail (demo error)
directors API registry
logs streaming 
remove pickling
shard descriptor `get_item` from validation set
return error to API if collaborator fails
passing envoy node info, choosing devices
assigner
send model
adding tests
workspace should be unpacked by CollaboratorManager component but not by the grpc client
we do not need to deconstruct model proto on director side, just pass it to the aggregator