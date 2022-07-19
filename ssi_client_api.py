import argparse
import logging

from flask import Flask, request

import api_utils

flask_app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

init_data = {}


@flask_app.route('/-system/liveness')
def check_system_liveness():
  print("System is running!")
  return 'ok', 200


@flask_app.route('/ssi/resources/', methods=['GET'])
def get_resource():
  """
  Runs the entire procedure for requesting a resource from the SSI Access Control System.
  :return:
  """
  resource_url = request.args.get('resource_url')
  holder_id = request.args.get('holder_id')
  if not resource_url or not holder_id:
    return 'Bad Request: Missing parameters', 400

  return api_utils.request_resource(init_data, holder_id, resource_url)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--server-url', required=True,
                      help='URL of the SSI Server')
  parser.add_argument('--server-did', required=True,
                      help='Peer-DID of the SSI Server')
  args = parser.parse_args()

  # Initialize DIDComm Object and Parse Credentials as RDF Graphs
  init_data = api_utils.initialize_ssi_client(args.server_url, args.server_did)
  print("SSI Client initialized successfully!")

  # Start the API
  flask_app.run(debug=False, port=6001, host='localhost')
