import json
import logging

from typing import Optional

from didcomm.common.resolvers import ResolversConfig
from didcomm.common.types import DID, VerificationMethodType, VerificationMaterial, VerificationMaterialFormat
from didcomm.core.utils import id_generator_default, get_did
from didcomm.did_doc.did_doc import DIDDoc, VerificationMethod, DIDCommService
from didcomm.did_doc.did_resolver import DIDResolver
from didcomm.message import Message, Attachment
from didcomm.pack_encrypted import pack_encrypted, PackEncryptedConfig
from didcomm.secrets.secrets_util import generate_x25519_keys_as_jwk_dict, generate_ed25519_keys_as_jwk_dict, \
  jwk_to_secret
from didcomm.unpack import unpack as unpack_didcomm
from didcomm.errors import DIDCommError

from peerdid import peer_did
from peerdid.core.did_doc_types import DIDCommServicePeerDID
from peerdid.did_doc import DIDDocPeerDID
from peerdid.types import VerificationMaterialFormatPeerDID, VerificationMaterialAgreement, \
  VerificationMethodTypeAgreement, VerificationMaterialAuthentication, VerificationMethodTypeAuthentication
from peerdid.errors import PeerDIDError

from utilities import utils


class DIDCommAPIError(Exception):
  """ Base exception class for all DID Comm API errors """
  pass


class MyDIDCommError(DIDCommAPIError):
  """ Base exception class for errors when using the DID Comm Implementation """
  pass


class DIDResolverPeerDID(DIDResolver):

  async def resolve(self, did: DID) -> Optional[DIDDoc]:
    # request DID Doc in JWK format
    did_doc_json = peer_did.resolve_peer_did(did, format=VerificationMaterialFormatPeerDID.JWK)
    did_doc = DIDDocPeerDID.from_json(did_doc_json)

    return DIDDoc(
      did=did_doc.did,
      key_agreement_kids=did_doc.agreement_kids,
      authentication_kids=did_doc.auth_kids,
      verification_methods=[
        VerificationMethod(
          id=m.id,
          type=VerificationMethodType.JSON_WEB_KEY_2020,
          controller=m.controller,
          verification_material=VerificationMaterial(
            format=VerificationMaterialFormat.JWK,
            value=json.dumps(m.ver_material.value)
          )
        )
        for m in did_doc.authentication + did_doc.key_agreement
      ],
      didcomm_services=[
        DIDCommService(
          id=s.id,
          service_endpoint=s.service_endpoint,
          routing_keys=s.routing_keys,
          accept=s.accept
        )
        for s in did_doc.service
        if isinstance(s, DIDCommServicePeerDID)
      ] if did_doc.service else []
    )


class DIDComm:

  def __init__(self, secret_resolver):
    self.secrets_resolver = secret_resolver
    self.resolvers_config = ResolversConfig(
      secrets_resolver=self.secrets_resolver,
      did_resolver=DIDResolverPeerDID()
    )

  def create_peer_did(self, service_endpoint):
    # 1. generate keys in JWK format
    agreement_key = generate_x25519_keys_as_jwk_dict()
    auth_key = generate_ed25519_keys_as_jwk_dict()

    # 2. prepare the keys for peer DID lib
    agreement_keys_peer_did = [
      VerificationMaterialAgreement(
        type=VerificationMethodTypeAgreement.JSON_WEB_KEY_2020,
        format=VerificationMaterialFormatPeerDID.JWK,
        value=agreement_key[1],
      )
    ]
    auth_keys_peer_did = [
      VerificationMaterialAuthentication(
        type=VerificationMethodTypeAuthentication.JSON_WEB_KEY_2020,
        format=VerificationMaterialFormatPeerDID.JWK,
        value=auth_key[1],
      )
    ]

    # 3. generate service
    service = json.dumps(
      DIDCommServicePeerDID(
        id=id_generator_default(),
        service_endpoint=service_endpoint, routing_keys=[],
        accept=["didcomm/v2"]
      ).to_dict()
    )

    # 4. Create DID with the Peer DID library
    did = peer_did.create_peer_did_numalgo_2(
      encryption_keys=agreement_keys_peer_did,
      signing_keys=auth_keys_peer_did,
      service=service,
    )

    # 5. Store private keys in the Secret Resolver using the KIDs from the DID DOC
    did_doc = DIDDocPeerDID.from_json(peer_did.resolve_peer_did(did))

    auth_private_key = auth_key[0]
    auth_private_key["kid"] = did_doc.auth_kids[0]
    utils.get_or_create_eventloop().run_until_complete(
      self.secrets_resolver.add_key(jwk_to_secret(auth_private_key))
    )

    agreement_private_key = agreement_key[0]
    agreement_private_key["kid"] = did_doc.agreement_kids[0]
    utils.get_or_create_eventloop().run_until_complete(
      self.secrets_resolver.add_key(jwk_to_secret(agreement_private_key))
    )

    return did

  @staticmethod
  def resolve_peer_did(did):
    try:
      did_doc_json_string = peer_did.resolve_peer_did(did, format=VerificationMaterialFormatPeerDID.JWK)
    except PeerDIDError as error:
      logging.warning("Encountered PeerDIDError while resolving peer did: {}".format(str(error)))
      raise MyDIDCommError("Got PeerDID Error when resolving peer did")
    return json.loads(did_doc_json_string)
    # return peer_did.resolve_peer_did(did, format=VerificationMaterialFormatPeerDID.JWK)

  def pack(self, msg_body, to, frm, msg_type, msg_id=None, attachments=None):
    if not msg_id:
      msg_id = id_generator_default()
    attachments_objects = []
    if attachments:
      for attachment_dict in attachments:
        attachments_objects.append(Attachment.from_dict(attachment_dict))
    message = Message(
      body=msg_body,
      id=msg_id,
      type=msg_type,
      frm=frm,
      to=[to],
      attachments=attachments_objects
    )
    pack_config = PackEncryptedConfig()
    pack_config.forward = False

    # Authenticated Encryption without the unnecessary additional signatures:
    try:
      message_pack_encrypted = utils.get_or_create_eventloop().run_until_complete(
        pack_encrypted(
          resolvers_config=self.resolvers_config,
          message=message,
          frm=frm,
          to=to,
          sign_frm=None,
          pack_config=pack_config
        )
      )
    except DIDCommError as error:
      logging.error("Encountered DIDCommError: {}".format(str(error)))
      raise MyDIDCommError("Unsuccessful packing of message")

    return message_pack_encrypted.packed_msg

  def unpack(self, packed_msg):
    try:
      res = utils.get_or_create_eventloop().run_until_complete(
        unpack_didcomm(
          resolvers_config=self.resolvers_config,
          packed_msg=packed_msg
        )
      )
    except DIDCommError as error:
      logging.warning("Encountered DIDComm Error when unpacking message: {}".format(str(error)))
      raise MyDIDCommError("Unsuccessful unpacking of message")
    if not res.metadata.encrypted or not res.metadata.authenticated:
      logging.warning("Received unencrypted or unauthenticated message")
      MyDIDCommError("Unsuccessful unpacking of message")

    frm = get_did(res.metadata.encrypted_from) if res.metadata.encrypted_from else None
    to = get_did(res.metadata.encrypted_to[0])
    attachments = []
    if res.message.attachments:
      for attachment in res.message.attachments:
        attachments.append(attachment.as_dict())

    return {
      'frm': frm,
      'to': to,
      'msg_id': res.message.id,
      'msg_type': res.message.type,
      'msg_body': res.message.body,
      'attachments': attachments
    }
