#!/bin/bash

EPOCHS=1 # How many epochs to run

# todo - configure: URL of the SSI-ACS - DID Communication API
server_url=http://localhost:5001/did_comm/inbox/
# todo - configure: Peer DID of the SSI-ACS - DID Communication API
server_did=

BASEDIR=$(pwd)

h1_r1=http://aifb.example.org/degree_science/resources/r1
h1_r2=http://aifb.example.org/degree_science/resources/r1
h1_r3=http://aifb.example.org/bulgarians/resources/r1
h1_r4=http://aifb.example.org/vasil/resources/r1
h1_r5=http://aifb.example.org/vaccinated/resources/r1

h2_r1=http://aifb.example.org/degree_arts/resources/r1
h2_r2=http://aifb.example.org/degree_arts/resources/r1
h2_r3=http://aifb.example.org/germans/resources/r1
h2_r4=http://aifb.example.org/wassil/resources/r1
h2_r5=http://aifb.example.org/vaccinated/resources/r1

h3_r1=http://aifb.example.org/degree_science/resources/r1
h3_r2=http://aifb.example.org/degree_science/resources/r1
h3_r3=http://aifb.example.org/bulgarians/resources/r1
h3_r4=http://aifb.example.org/alice/resources/r1
h3_r5=http://aifb.example.org/vaccinated/resources/r1

# Do not use. LD context not found
#http://aifb.example.org/drivers/resources/r1

# Resources requested by Holder 1
resources_h1=(
  $h1_r1
  $h1_r2
  $h1_r3
  $h1_r4
  $h1_r5
)

# Resources requested by Holder 2
resources_h2=(
  $h2_r1
  $h2_r2
  $h2_r3
  $h2_r4
  $h2_r5
)

# Resources requested by Holder 3
resources_h3=(
  $h3_r1
  $h3_r2
  $h3_r3
  $h3_r4
  $h3_r5
)

# Activate python venv
source ${BASEDIR}/venv/bin/activate

# Run the SSI Client API as a separate process
python3 ${BASEDIR}/ssi_client_api.py --server-did $server_did --server-url $server_url &
API_PID=$!

# Wait for the API to initialize
echo "Initializing SSI Client..."
sleep 30
echo "Initialization completed."

start_time_global=$(date +%s.%N)
for (( i=1; i<=$EPOCHS; i++ )) do

  # Holder Wallet 1
  for r in "${resources_h1[@]}"; do
    echo ""
    start_time_local=$(date +%s.%N)
    # This is how we run the client:
    curl -s -X GET "http://localhost:6001/ssi/resources/?resource_url=${r}&holder_id=1" > /dev/null
    end_time_local=$(date +%s.%N)
    diff_local=$(echo "$end_time_local - $start_time_local" | bc)
    # schema = sequential_local,<resource_url>,<ethr or indy or web DIDs>,<time>
    echo "$diff_local,sequential_local,$r,ethr,$diff_local"
    # Wait 1 second
    sleep 1
  done

  # Holder Wallet 2
  for r in "${resources_h2[@]}"; do
    echo ""
    start_time_local=$(date +%s.%N)
    curl -s -X GET "http://localhost:6001/ssi/resources/?resource_url=${r}&holder_id=2" > /dev/null
    end_time_local=$(date +%s.%N)
    diff_local=$(echo "$end_time_local - $start_time_local" | bc)
    # schema = sequential_local,<resource_url>,<ethr or indy or web DIDs>,<time>
    echo "$diff_local,sequential_local,$r,indy,$diff_local"
    # Wait 1 second
    sleep 1
  done

  # Holder Wallet 3
  for r in "${resources_h3[@]}"; do
    echo ""
    start_time_local=$(date +%s.%N)
    curl -s -X GET "http://localhost:6001/ssi/resources/?resource_url=${r}&holder_id=3" > /dev/null
    end_time_local=$(date +%s.%N)
    diff_local=$(echo "$end_time_local - $start_time_local" | bc)
    # schema = sequential_local,<resource_url>,<ethr or indy or web DIDs>,<time>
    echo "$diff_local,sequential_local,$r,web,$diff_local"
    # Wait 1 second
    sleep 1
  done

done
end_time_global=$(date +%s.%N)
diff_global=$(echo "$end_time_global - $start_time_global" | bc)
echo "$diff_global,sequential_global,$EPOCHS,$diff_global"

# Do not forget to kill the SSI Client API process
kill $API_PID

deactivate

echo "Done"
