#!/bin/bash

BASEDIR=$(pwd)

# todo - configure: URL of the SSI-ACS - DID Communication API
server_url=http://localhost:5001/did_comm/inbox/
# todo - configure: Peer DID of the SSI-ACS - DID Communication API
server_did=

r1=http://aifb.example.org/degree_science/resources/r1
r2=http://aifb.example.org/degree_arts/resources/r1
r3=http://aifb.example.org/bulgarians/resources/r1
r4=http://aifb.example.org/germans/resources/r1
r5=http://aifb.example.org/vasil/resources/r1
r6=http://aifb.example.org/wassil/resources/r1
r7=http://aifb.example.org/drivers/resources/r1
r8=http://aifb.example.org/vaccinated/resources/r1

source /home/papanchev/ssi-workspace/ssi_simple_client/venv/bin/activate

start_time=$(date +%s.%N)
for i in {1..1}; do
  python3 ${BASEDIR}/client.py --resource-url $r1 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r3 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r5 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &

  python3 ${BASEDIR}/client.py --resource-url $r2 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r4 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r6 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
done
wait
end_time=$(date +%s.%N)
diff=$(echo "$end_time - $start_time" | bc)
echo "iterations:1,time:$diff"
#
start_time=$(date +%s.%N)
for i in {1..2}; do
  python3 ${BASEDIR}/client.py --resource-url $r1 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r3 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r5 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &

  python3 ${BASEDIR}/client.py --resource-url $r2 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r4 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r6 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
done
wait
end_time=$(date +%s.%N)
diff=$(echo "$end_time - $start_time" | bc)
echo "iterations:2,time:$diff"

start_time=$(date +%s.%N)
for i in {1..3}; do
  python3 ${BASEDIR}/client.py --resource-url $r1 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r3 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r5 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &

  python3 ${BASEDIR}/client.py --resource-url $r2 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r4 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r6 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
done
wait
end_time=$(date +%s.%N)
diff=$(echo "$end_time - $start_time" | bc)
echo "iterations:3,time:$diff"

start_time=$(date +%s.%N)
for i in {1..4}; do
  python3 ${BASEDIR}/client.py --resource-url $r1 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r3 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r5 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &

  python3 ${BASEDIR}/client.py --resource-url $r2 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r4 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r6 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
done
wait
end_time=$(date +%s.%N)
diff=$(echo "$end_time - $start_time" | bc)
echo "iterations:4,time:$diff"

start_time=$(date +%s.%N)
for i in {1..5}; do
  python3 ${BASEDIR}/client.py --resource-url $r1 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r3 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r5 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &

  python3 ${BASEDIR}/client.py --resource-url $r2 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r4 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r6 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
done
wait
end_time=$(date +%s.%N)
diff=$(echo "$end_time - $start_time" | bc)
echo "iterations:5,time:$diff"

start_time=$(date +%s.%N)
for i in {1..10}; do
  python3 ${BASEDIR}/client.py --resource-url $r1 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r3 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r5 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 1 --server-url $server_url --server-did $server_did --http-method GET &

  python3 ${BASEDIR}/client.py --resource-url $r2 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r4 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r6 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r7 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
  python3 ${BASEDIR}/client.py --resource-url $r8 --holder-id 2 --server-url $server_url --server-did $server_did --http-method GET &
done
wait
end_time=$(date +%s.%N)
diff=$(echo "$end_time - $start_time" | bc)
echo "iterations:10,time:$diff"

deactivate
