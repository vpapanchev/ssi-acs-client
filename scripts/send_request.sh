#!/bin/bash

server_url=http://localhost:5001/did_comm/inbox/
server_did=did:peer:2.Ez6LSjvd7sLwMjrXboNTyF6oeRu4DY4H6T8YfSx66AEu1qLST.Vz6MkjXvCefatD8Vm5bA37XVDf1MsWBYAL8jhVqaFY1nQG9xe.SeyJpZCI6IjNmYzc5N2MyLWY1NGYtNDU4YS04NGQwLWQ2YTk0YzgxZDFmNyIsInQiOiJkbSIsInMiOiJodHRwOi8vaG9zdC5kb2NrZXIuaW50ZXJuYWw6NTAwMS9kaWRfY29tbS9pbmJveC8iLCJhIjpbImRpZGNvbW0vdjIiXX0

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
