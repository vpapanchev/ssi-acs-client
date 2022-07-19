import asyncio
import json
import sys


def get_or_create_eventloop():
  try:
    return asyncio.get_event_loop()
  except RuntimeError as ex:
    if "There is no current event loop in thread" in str(ex):
      loop = asyncio.new_event_loop()
      asyncio.set_event_loop(loop)
      return asyncio.get_event_loop()


def read_holder_wallet(holder_id):
  with open("wallets.json") as f:
    try:
      wallets = json.load(f)
    except json.decoder.JSONDecodeError:
      print("Error reading wallets.json")
      sys.exit(1)
  return wallets[holder_id]
