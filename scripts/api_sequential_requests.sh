#!/bin/bash

EPOCHS=2 # How many epochs to run
server_url=http://localhost:5001/did_comm/inbox/
server_did=did:peer:2.Ez6LSbtGaSqNJiDz8VyPQ2VcKjYrP6Z1zgLP9QvQtWpJgM5hd.Vz6MkqL8CQi6hKCGZCHohs4RESySGo32z8jgR7UaYNmYLN74w.SeyJpZCI6IjlhNzU2ZmM1LTUzNmUtNDcwZC1iNjZhLWFkMzU3ZDgwNmJhNiIsInQiOiJkbSIsInMiOiJodHRwOi8vaG9zdC5kb2NrZXIuaW50ZXJuYWw6NTAwMS9kaWRfY29tbS9pbmJveC8iLCJhIjpbImRpZGNvbW0vdjIiXX0

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

# Run the SSI Client API as a separate process
python3 ${BASEDIR}/ssi_client_api.py --server-did $server_did --server-url $server_url &
API_PID=$!

# Wait for the API to initialize
echo "Sleeping 30: Waiting for SSI Client to init"
sleep 30
echo "Woke up"

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
    # schema = sequential_local,<resource_url>,<ethr or indy DIDs>,<time>
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
    # schema = sequential_local,<resource_url>,<ethr or indy DIDs>,<time>
    echo "$diff_local,sequential_local,$r,indy,$diff_local"
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
