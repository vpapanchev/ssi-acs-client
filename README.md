# Self-Sovereign Identity (SSI) Client

## Description

A simple implementation of an SSI-Client as a user of the [Interoperable SSI-based Access Control System](https://github.com/vpapanchev/ssi-acs).

The SSI-Client is implemented as a Python project using the Flask framework. \
The Flask API is initialized with the URL and Peer-DID of the Access Control System (ACS) and provides a single HTTP API used to request a resource from the ACS.

The Workflow of the SSI-Client is as follows:
  1. Generate a fresh Peer-DID.
  2. Send Initial Request to the ACS.
  3. Receive Presentation_Request (PR) from the ACS.
  4. Parse the requested credentials from the PR.
  5. Get the credentials of the holder. (using the local wallet)
  6. Select credentials based on the requested credentials.
  7. Create a Verifiable Presentation (VP) in a JWT format.
  8. Send a Secondary Request containing the VP to the Access Control System

## Communication with the ACS

The communication between the SSI-Client and the ACS is secured using the DIDComm Messaging Protocol in combination with freshly-generated Peer-DIDs.\
The DIDComm Messages are embedded in HTTP Requests and Responses. For more information see the [DID Communication API](https://github.com/vpapanchev/did-comm-api) service of the ACS.

## Used DIDs and VCs

The project contains a local wallet (a simple wallets.json file) containing: 
  - Holder Ethr-DIDs on the test Ropsten Ethereum network (private keys are included).
  (can be used freely)
  - Holder Indy-DIDs on a local instance of the VON Network
  (usage would require to deploy a local VON network and register the DIDs manually)
  - Multiple Verifiable Credentials in JSON-LD + JWT format, i.e., VCs expressed as JWTs

The contained DIDs and VCs are used merely for test purposes and do not hold any actual value.

## How to use

Multiple automated scripts are provided which can be used to send a single request, multiple requests sequentially or multiple requests in parallel and to  evaluate the End-to-End latency of the authorization process.

1. Create and activate a new virtual environment:\
`python3 -m venv ./venv`\
`source venv/bin/activate`
2. Install the project requirements\
`pip3 install -r requirements.txt`
3. Configure the URL and Peer-DID of the ACS (and other constants if needed) in the automated script you wish to execute.
4. Execute the selected automated script, for example\
`./scripts/send_request.sh`
