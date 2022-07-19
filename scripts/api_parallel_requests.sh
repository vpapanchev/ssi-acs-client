#!/bin/bash

REPEAT=1 # How many times to repeat running all the EPOCHS
EPOCHS=1 # 1 Epoch = 10 Requests in parallel

# todo - configure: URL of the SSI-ACS - DID Communication API
server_url=http://localhost:5001/did_comm/inbox/
# todo - configure: Peer DID of the SSI-ACS - DID Communication API
server_did=

BASEDIR=$(pwd)

r1=http://aifb.example.org/degree_science/resources/r1
r2=http://aifb.example.org/degree_arts/resources/r1
r3=http://aifb.example.org/bulgarians/resources/r1
r4=http://aifb.example.org/germans/resources/r1
r5=http://aifb.example.org/vasil/resources/r1
r6=http://aifb.example.org/wassil/resources/r1
r7=http://aifb.example.org/drivers/resources/r1
r8=http://aifb.example.org/vaccinated/resources/r1

# Resources requested by Holder 1
resources_h1=(
  $r1
  $r3
  $r5
  $r7
  $r8
)

# Resources requested by Holder 2
resources_h2=(
  $r2
  $r4
  $r6
  $r7
  $r8
)

# Activate python venv
source ${BASEDIR}/venv/bin/activate

python3 ${BASEDIR}/ssi_client_api.py --server-did $server_did --server-url $server_url &
API_PID=$!

# Wait for the API to initialize
echo "Sleeping 30: Waiting for SSI Client to init"
sleep 30
echo "Woke up"

for (( t=1; t<=$REPEAT; t++ )) do
  wait_pids=()

  start_time_global=$(date +%s.%N)
  for (( i=1; i<=$EPOCHS; i++ )) do

    # Holder Wallet 1
    for r in "${resources_h1[@]}"; do
      # Request the resource in Background and store PID for waiting
      curl -s -X GET "http://localhost:6001/ssi/resources/?resource_url=${r}&holder_id=1" > /dev/null & wait_pids+=($!)
    done

    # Holder Wallet 2
    for r in "${resources_h2[@]}"; do
      # Request the resource in Background and store PID for waiting
      curl -s -X GET "http://localhost:6001/ssi/resources/?resource_url=${r}&holder_id=2" > /dev/null & wait_pids+=($!)
    done

  done

  # Wait for the requests to finish
  wait "${wait_pids[@]}"

  end_time_global=$(date +%s.%N)
  diff_global=$(echo "$end_time_global - $start_time_global" | bc)
  echo "$diff_global,parallel_global,$EPOCHS,$diff_global"

  # Rest some time
  sleep 10

done

# Do not forget to kill the SSI Client API process
kill $API_PID

deactivate

echo "Done"
