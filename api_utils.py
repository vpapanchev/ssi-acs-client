import sys
import requests
import json

from base64 import urlsafe_b64decode

import constants as const
from utilities import utils, rdf_utils, jwt_utils
from utilities.did_comm import DIDComm
from utilities.secret_resolver import SecretsResolverLocal


def initialize_ssi_client(server_url, server_peer_did):
  # Create DIDComm Object
  secret_resolver = SecretsResolverLocal()
  did_comm_obj = DIDComm(secret_resolver)

  # Load Credentials
  h1_wallet = utils.read_holder_wallet("1")
  h1_credentials = []
  for credential_infos in h1_wallet['credentials']:
    h1_credentials.append({
      'name': credential_infos['name'],
      'jwt': credential_infos['jwt'],
      'graph': rdf_utils.parse_ld_credential_dict(credential_infos['w3c_payload'])
    })

  # Load Credentials
  h2_wallet = utils.read_holder_wallet("2")
  h2_credentials = []
  for credential_infos in h2_wallet['credentials']:
    h2_credentials.append({
      'name': credential_infos['name'],
      'jwt': credential_infos['jwt'],
      'graph': rdf_utils.parse_ld_credential_dict(credential_infos['w3c_payload'])
    })

  return {
    'server_url': server_url,
    'server_peer_did': server_peer_did,
    'did_comm_obj': did_comm_obj,
    'holders': {
      '1': {
        'wallet': h1_wallet,
        'credentials': h1_credentials
      },
      '2': {
        'wallet': h2_wallet,
        'credentials': h2_credentials
      }
    }
  }


def request_resource(init_data, holder_id, resource_url):
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

  :param init_data: Initialization Data of the SSI Client. (see initialize_ssi_client)
  :param holder_id: ID of Holder ('1' or '2' - see wallets.json)
  :param resource_url: URL of requested resource
  :return:
  """
  did_comm_obj = init_data['did_comm_obj']
  server_peer_did = init_data['server_peer_did']
  server_url = init_data['server_url']
  holder_wallet = init_data['holders'][holder_id]['wallet']
  holder_credentials = init_data['holders'][holder_id]['credentials']

  # Create a new Peer DID for communication with the Access Control System
  my_peer_did = did_comm_obj.create_peer_did("http://fake.service.endpoint")

  # Send Initial Request
  http_response = __send_initial_request(
    did_comm_obj, server_peer_did, server_url, my_peer_did, resource_url, "GET")

  if 'error' in http_response:
    print(f"Initial_Request Response Error:{http_response['error']}")
    return f"Initial_Request Response Error:{http_response['error']}", 400

  # Find the AIFB-SHACL VP Request
  response_msg = __unpack_http_didcomm_message(did_comm_obj, http_response)
  if response_msg['msg_type'] == const.DIDCOMM_ERROR_MSG_TYPE:
    print(f"Initial_Request Response Error:{response_msg['msg_body']['error']}")
    return f"Initial_Request Response Error:{response_msg['msg_body']['error']}", 400
  if response_msg['msg_type'] != const.DIDCOMM_REQUEST_PRESENTATION_MSG_TYPE:
    print("Unexpected Initial Request Response DIDComm Message Type")
    return "Unexpected Initial Request Response DIDComm Message Type", 400
  vp_request = __get_presentation_request(response_msg['msg_body'])

  # Create Verifiable Presentation
  vp = __create_verifiable_presentation(vp_request, holder_wallet, holder_credentials)
  vp_message = __create_presentation_message(resource_url, vp)

  http_response = __send_secondary_request(
    did_comm_obj, server_peer_did, server_url, my_peer_did, vp_message, "GET")
  response_msg = __unpack_http_didcomm_message(did_comm_obj, http_response)
  msg_body = response_msg['msg_body']

  print(f"Resource: {resource_url} Authorization result: {msg_body}")
  return f"Resource: {resource_url} Authorization result: {msg_body}", 200


def __unpack_http_didcomm_message(did_comm_obj, http_response):
  did_comm_msg_encrypted = http_response['didcomm_msg']
  return did_comm_obj.unpack(did_comm_msg_encrypted)


def __send_initial_request(did_comm_obj, server_peer_did, server_url, my_peer_did, resource_url, http_method):
  # Create initial request
  msg_type = const.DIDCOMM_INITIAL_REQUEST_MSG_TYPE
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
    if attachment_format['format'] == const.PRESENTATION_REQUEST_ATTACHMENT_FORMAT_SHACL:
      attachment_id = attachment_format['attach_id']
  if not attachment_id:
    print(f'Error: Did not find a {const.PRESENTATION_REQUEST_ATTACHMENT_FORMAT_SHACL} Presentation Request')
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


def __create_verifiable_presentation(presentation_request, holder_wallet, holder_credentials):
  """
  1. Get all credentials of this Holder
  2. Get Required Credentials from the presentation_request
  3. For each required credential: find a credential that satisfies it
  4. Get Holder DID and Keys and create the VP

  Currently, the first credential that satisfy a requirement is provided.
  In a real scenario, the SSI Client would have to ask the User whether and which credentials to provide.

  :param presentation_request:
  :param holder_wallet:
  :param holder_credentials:
  :return:
  """

  nonce = presentation_request['options']['challenge']
  domain = presentation_request['options']['domain']
  required_credentials_graphs_ttl = presentation_request['required_credentials']

  # Parse Required Credential SHACL Definitions as RDF Graphs
  required_creds_graphs = []
  for required_credential_shacl_graph_ttl in required_credentials_graphs_ttl:
    required_creds_graphs.append(rdf_utils.parse_ttl_graph(required_credential_shacl_graph_ttl))

  vp_credentials = []
  added_credentials = []
  for required_cred_graph in required_creds_graphs:
    satisfied = False
    for credential in holder_credentials:
      if rdf_utils.is_credential_compliant_graphs(credential['graph'], required_cred_graph):
        satisfied = True
        if credential['name'] not in added_credentials:
          added_credentials.append(credential['name'])
          vp_credentials.append(credential['jwt'])
        break
    if not satisfied:
      print("Warning: Cannot fulfil all required credentials")

  #print(f"Sending credentials: {added_credentials}")
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
        "format": const.PRESENTATION_ATTACHMENT_FORMAT_SHACL,
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
    msg_type=const.DIDCOMM_PRESENTATION_MSG_TYPE,
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
