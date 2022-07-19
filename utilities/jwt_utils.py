import base58
import jwt
import datetime
import random

from dateutil.relativedelta import relativedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def create_presentation(credentials, holder_sign_key, holder_verify_kid, holder_did, nonce, domain):
  presentation_id = random.randint(1000000000000000, 10000000000000000)
  payload = {
    'iss': holder_did,
    'jti': presentation_id,
    'vp': {
      '@context': ["https://www.w3.org/2018/credentials/v1"],
      'type': ["VerifiablePresentation"],
      'verifiableCredential': credentials,
      'nonce': nonce,
      'domain': domain
    }
  }

  vp = create_jwt_with_b58_ed25519_with_kid(payload, holder_sign_key, holder_verify_kid)
  return vp


def create_jwt_with_b58_ed25519_with_kid(payload, sign_key_b58, kid):
  sign_key_pem = signing_key_ed25519_b58_to_pem(sign_key_b58)

  payload['nbf'] = datetime.datetime.now().timestamp()

  d = datetime.datetime.now()
  d2 = d + relativedelta(months=6)
  payload['exp'] = d2.timestamp()
  return jwt.encode(payload, sign_key_pem, algorithm='EdDSA', headers={'kid': kid})


def verify_key_ed25519_b58_to_pem(verify_key_b58):
  # Get Ed25519PublicKey object
  ver_key_bytes = bytes(verify_key_b58, "ascii")
  ver_key_raw = base58.b58decode(ver_key_bytes)
  ed25519_pk = Ed25519PublicKey.from_public_bytes(ver_key_raw)

  # Use cryptography library to get key in PEM format
  ver_key_pem_bytes = ed25519_pk.public_bytes(
    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
  ver_key_pem = ver_key_pem_bytes.decode("ascii")

  return ver_key_pem


def signing_key_ed25519_b58_to_pem(signing_key_b58):
  sign_key_bytes = bytes(signing_key_b58, "ascii")
  sign_key_raw = base58.b58decode(sign_key_bytes)
  sign_key_raw = sign_key_raw[:32]

  sign_key_obj = Ed25519PrivateKey.from_private_bytes(sign_key_raw)
  sign_key_pem_bytes = sign_key_obj.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
  )
  sign_key_pem = sign_key_pem_bytes.decode("ascii")

  return sign_key_pem


def verify_jwt_with_b58_ed25519(jwt_credential, ver_key_b58):
  ver_key_pem = verify_key_ed25519_b58_to_pem(ver_key_b58)
  try:
    return jwt.decode(jwt_credential, ver_key_pem, algorithms=["EdDSA"])
  except jwt.exceptions.InvalidSignatureError:
    print('Signature verification failed')
  except jwt.exceptions.ExpiredSignatureError:
    print('Invalid Credential: Credential is expired')
  except jwt.exceptions.InvalidIssuedAtError:
    print('Invalid Credential: Credential issuance date is in the future.')
  except jwt.exceptions.ImmatureSignatureError:
    print('Invalid Credential: Credential nbf date is in the future')
  except jwt.exceptions.InvalidKeyError as err:
    print('Invalid Format of Public Key.')
    print(err)
  except jwt.exceptions.InvalidAlgorithmError:
    print('Credential Proof Algorithm not supported')
  except jwt.exceptions.InvalidTokenError as err:
    print(err)
  return None
