import argparse
import sys
import requests
import json

from base64 import urlsafe_b64decode

import constants as const
from utilities import utils, rdf_utils, jwt_utils
from utilities.did_comm import DIDComm
from utilities.secret_resolver import SecretsResolverLocal


# DIDComm User Request Message Types
DIDCOMM_INITIAL_REQUEST_MSG_TYPE = const.DIDCOMM_INITIAL_REQUEST_MSG_TYPE
DIDCOMM_REQUEST_PRESENTATION_MSG_TYPE = const.DIDCOMM_REQUEST_PRESENTATION_MSG_TYPE
DIDCOMM_PRESENTATION_MSG_TYPE = const.DIDCOMM_PRESENTATION_MSG_TYPE
DIDCOMM_ERROR_MSG_TYPE = const.DIDCOMM_ERROR_MSG_TYPE
DIDCOMM_AUTHORIZATION_DECISION_MSG_TYPE = const.DIDCOMM_AUTHORIZATION_DECISION_MSG_TYPE

# Attachment formats:
PRESENTATION_REQUEST_ATTACHMENT_FORMAT_PE_DEFINITION = const.PRESENTATION_REQUEST_ATTACHMENT_FORMAT_PE_DEFINITION
PRESENTATION_REQUEST_ATTACHMENT_FORMAT_SHACL = const.PRESENTATION_REQUEST_ATTACHMENT_FORMAT_SHACL
PRESENTATION_ATTACHMENT_FORMAT_SHACL = const.PRESENTATION_ATTACHMENT_FORMAT_SHACL


def main(holder_id, server_url, server_peer_did, resource_url, http_method):
  """
  Simple procedure emulating an SSI Client requesting a resource, parsing a Presentation Request,
  creating and sending a Verifiable Presentation.

  Workflow:
  1. Generate a fresh Peer-DID
  2. Send Initial Request to the Access Control System
  3. Receive Presentation_Request (PR)
  4. Parse PR and get required_credentials
  5. Get the credentials of holder. (using local storage and holder_id)
  6. Select credentials based on the required_credentials
  7. Create a Verifiable Presentation (VP)
  8. Send a Secondary Request to the Access Control System

  :param holder_id: ID of Holder
  :param server_url: URL of the Access Control System
  :param server_peer_did: Peer DID of the Access Control System
  :param resource_url: URL of requested resource
  :param http_method: HTTP Method of the sent requests
  :return:
  """

  # Create DIDComm Object
  secret_resolver = SecretsResolverLocal()
  did_comm_obj = DIDComm(secret_resolver)

  # Create a new Peer DID for communication with the Access Control System
  my_peer_did = did_comm_obj.create_peer_did("http://fake.service.endpoint")

  # Send Initial Request
  http_response = __send_initial_request(
    did_comm_obj, server_peer_did, server_url, my_peer_did, resource_url, http_method)

  if 'error' in http_response:
    print(f"Initial_Request Response Error:{http_response['error']}")
    sys.exit(1)

  # Find the AIFB-SHACL VP Request
  response_msg = __unpack_http_didcomm_message(did_comm_obj, http_response)
  if response_msg['msg_type'] == DIDCOMM_ERROR_MSG_TYPE:
    print(f"Initial_Request Response Error:{response_msg['msg_body']['error']}")
    sys.exit(1)
  if response_msg['msg_type'] != DIDCOMM_REQUEST_PRESENTATION_MSG_TYPE:
    print("Unexpected Initial Request Response DIDComm Message Type")
    sys.exit(1)
  vp_request = __get_presentation_request(response_msg['msg_body'])

  # Create Verifiable Presentation
  vp = __create_verifiable_presentation(holder_id, vp_request)
  vp_message = __create_presentation_message(resource_url, vp)

  http_response = __send_secondary_request(
    did_comm_obj, server_peer_did, server_url, my_peer_did, vp_message, http_method)
  response_msg = __unpack_http_didcomm_message(did_comm_obj, http_response)
  msg_body = response_msg['msg_body']
  print(f"Resource: {resource_url} Authorization result: {msg_body}")


def __unpack_http_didcomm_message(did_comm_obj, http_response):
  did_comm_msg_encrypted = http_response['didcomm_msg']
  return did_comm_obj.unpack(did_comm_msg_encrypted)


def __send_initial_request(did_comm_obj, server_peer_did, server_url, my_peer_did, resource_url, http_method):
  # Create initial request
  msg_type = DIDCOMM_INITIAL_REQUEST_MSG_TYPE
  initial_request_body = {
    'resource_url': resource_url
  }
  did_comm_message = did_comm_obj.pack(
    msg_body=initial_request_body,
    to=server_peer_did,
    frm=my_peer_did,
    msg_type=msg_type,
    attachments=[]
  )
  request_data = {
    'didcomm_msg': did_comm_message
  }
  if http_method == 'GET':
    response = requests.get(server_url, data=request_data)
  elif http_method == 'POST':
    response = requests.post(server_url, data=request_data)
  elif http_method == 'PUT':
    response = requests.put(server_url, data=request_data)
  elif http_method == 'DELETE':
    response = requests.delete(server_url, data=request_data)
  else:
    print(f'ERROR: Unexpected HTTP Method: {http_method}')
    sys.exit(1)

  return response.json()


def __get_presentation_request(presentation_request_message):
  attachment_id = None
  for attachment_format in presentation_request_message['formats']:
    if attachment_format['format'] == PRESENTATION_REQUEST_ATTACHMENT_FORMAT_SHACL:
      attachment_id = attachment_format['attach_id']
  if not attachment_id:
    print(f'Error: Did not find a {PRESENTATION_REQUEST_ATTACHMENT_FORMAT_SHACL} Presentation Request')
    sys.exit(1)
  vp_request_base64 = None
  for attachment in presentation_request_message['request_presentations~attach']:
    if attachment['@id'] == attachment_id:
      vp_request_base64 = attachment['data']['base64']
  if not vp_request_base64:
    print('ERROR: Missing attachment in VP Request')
    sys.exit(1)

  vp_request_base64_decoded = urlsafe_b64decode(vp_request_base64.encode('utf-8')).decode('utf-8')
  return json.loads(vp_request_base64_decoded)


def __create_verifiable_presentation(holder_id, presentation_request):
  """
  1. Get all credentials of this Holder
  2. Get Required Credentials from the presentation_request
  3. For each required credential: find a credential that satisfies it
  4. Get Holder DID and Keys and create the VP

  Currently, the first credential that satisfy a requirement is provided.
  In a real scenario, the SSI Client would have to ask the User whether and which credentials to provide.

  :param holder_id:
  :param presentation_request:
  :return:
  """
  holder_wallet = utils.read_holder_wallet(holder_id)

  nonce = presentation_request['options']['challenge']
  domain = presentation_request['options']['domain']
  required_credentials_graphs_ttl = presentation_request['required_credentials']

  # Parse Required Credential SHACL Definitions as RDF Graphs
  required_creds_graphs = []
  for required_credential_shacl_graph_ttl in required_credentials_graphs_ttl:
    required_creds_graphs.append(rdf_utils.parse_ttl_graph(required_credential_shacl_graph_ttl))

  # Parse credentials as RDF Graphs
  import time
  s = time.time()
  stored_credentials = []
  for credential_infos in holder_wallet['credentials']:
    stored_credentials.append({
      'name': credential_infos['name'],
      'jwt': credential_infos['jwt'],
      'graph': rdf_utils.parse_ld_credential_dict(credential_infos['w3c_payload'])
    })
  print(f"Parsing Credentials: {time.time() - s} seconds")

  vp_credentials = []
  added_credentials = []
  for required_cred_graph in required_creds_graphs:
    satisfied = False
    for credential in stored_credentials:
      if rdf_utils.is_credential_compliant_graphs(credential['graph'], required_cred_graph):
        satisfied = True
        if credential['name'] not in added_credentials:
          added_credentials.append(credential['name'])
          vp_credentials.append(credential['jwt'])
        break
    if not satisfied:
      print("Warning: Cannot fulfil all required credentials")

  print(f"Sending credentials: {added_credentials}")
  return jwt_utils.create_presentation(
    vp_credentials,
    holder_wallet['holder_signing_key'],
    holder_wallet['holder_verify_key_id'],
    holder_wallet['holder_did'],
    nonce,
    domain
  )


def __create_presentation_message(resource_url, verifiable_presentation):
  return {
    "resource_url": resource_url,
    "last_presentation": True,
    "formats": [
      {
        "attach_id": "attachment_1",
        "format": "dif/presentation-exchange/submission@v1.0",
      },
      {
        "attach_id": "attachment_2",
        "format": PRESENTATION_ATTACHMENT_FORMAT_SHACL,
      }
    ],
    "presentations~attach": [
      {
        "@id": "attachment_1",
        "mime-type": "application/json",
        "data": {
          "json": "UNSUPPORTED"
        }
      },
      {
        "@id": "attachment_2",
        "mime-type": "application/json",
        "data": {
          "json": {
            "jwt": verifiable_presentation
          }
        }
      }
    ]
  }


def __send_secondary_request(
  did_comm_obj, server_peer_did, server_url, my_peer_did, presentation_message, http_method):
  did_comm_message = did_comm_obj.pack(
    msg_body=presentation_message,
    to=server_peer_did,
    frm=my_peer_did,
    msg_type=DIDCOMM_PRESENTATION_MSG_TYPE,
    attachments=[]
  )
  request_data = {
    'didcomm_msg': did_comm_message
  }
  if http_method == 'GET':
    response = requests.get(server_url, data=request_data)
  elif http_method == 'POST':
    response = requests.post(server_url, data=request_data)
  elif http_method == 'PUT':
    response = requests.put(server_url, data=request_data)
  elif http_method == 'DELETE':
    response = requests.delete(server_url, data=request_data)
  else:
    print(f'ERROR: Unexpected HTTP Method: {http_method}')
    sys.exit(1)

  return response.json()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--holder-id', required=True,
                      help='The ID of the holder. Used for accessing the local wallets')
  parser.add_argument('--server-url', required=True,
                      help='URL of the SSI Server')
  parser.add_argument('--server-did', required=True,
                      help='Peer-DID of the SSI Server')
  parser.add_argument('--resource-url', required=True,
                      help='Resource URL to request')
  parser.add_argument('--http-method', required=True, help='What HTTP Request to send')
  args = parser.parse_args()
  main(args.holder_id, args.server_url, args.server_did, args.resource_url, args.http_method)
