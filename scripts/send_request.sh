#!/bin/bash

# todo - configure: URL of the SSI-ACS - DID Communication API
server_url=http://localhost:5001/did_comm/inbox/
# todo - configure: Peer DID of the SSI-ACS - DID Communication API
server_did=

BASEDIR=$(pwd)

r1=http://aifb.example.org/degree_science/resources/r1

# Activate python venv
source ${BASEDIR}/venv/bin/activate

# Run the SSI Client API as a separate process
python3 ${BASEDIR}/ssi_client_api.py --server-did $server_did --server-url $server_url &
API_PID=$!

# Wait for the API to initialize
echo "Sleeping 30: Waiting for SSI Client to init"
sleep 30
echo "Woke up"

start_time=$(date +%s.%N)

curl -s -X GET "http://localhost:6001/ssi/resources/?resource_url=${r1}&holder_id=1" > /dev/null

end_time=$(date +%s.%N)
diff=$(echo "$end_time - $start_time" | bc)
echo "Elapsed time: $diff_global"

# Do not forget to kill the SSI Client API process
kill $API_PID

deactivate

echo "Done"
