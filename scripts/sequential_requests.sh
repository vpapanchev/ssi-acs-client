#!/bin/bash

# todo - configure: URL of the SSI-ACS - DID Communication API
server_url=http://localhost:5001/did_comm/inbox/
# todo - configure: Peer DID of the SSI-ACS - DID Communication API
server_did=

EPOCHS=2

BASEDIR=$(pwd)

r1=http://aifb.example.org/degree_science/resources/r1
r2=http://aifb.example.org/degree_arts/resources/r1
r3=http://aifb.example.org/bulgarians/resources/r1
r4=http://aifb.example.org/germans/resources/r1
r5=http://aifb.example.org/vasil/resources/r1
r6=http://aifb.example.org/wassil/resources/r1
r7=http://aifb.example.org/drivers/resources/r1
r8=http://aifb.example.org/vaccinated/resources/r1

# Activate python venv
source ${BASEDIR}/venv/bin/activate

resources_h1=(
  $r1
  $r3
  $r5
  $r7
  $r8
)

resources_h2=(
  $r2
  $r4
  $r6
  $r7
  $r8
)

start_time_global=$(date +%s.%N)
for (( i=1; i<=$EPOCHS; i++ )) do

  # Holder Wallet 1
  for r in "${resources_h1[@]}"; do
    start_time_local=$(date +%s.%N)
    python3 ${BASEDIR}/client.py --resource-url $r --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET
    end_time_local=$(date +%s.%N)
    diff_local=$(echo "$end_time_local - $start_time_local" | bc)
    echo "sequential_local,$r,ethr,$diff_local"
  done

  # Holder Wallet 2
  for r in "${resources_h2[@]}"; do
    start_time_local=$(date +%s.%N)
    python3 ${BASEDIR}/client.py --resource-url $r --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET
    end_time_local=$(date +%s.%N)
    diff_local=$(echo "$end_time_local - $start_time_local" | bc)
    # schema = sequential_local,<resource_url>,<ethr or indy DIDs>,<time>
    echo "sequential_local,$r,indy,$diff_local"
  done

done
end_time_global=$(date +%s.%N)
diff_global=$(echo "$end_time_global - $start_time_global" | bc)
echo "sequential_global,$EPOCHS,$diff_global"

# Deactivate python venv
deactivate
