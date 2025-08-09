from ..functions.api_request import api_request
from typing import Optional

async def create_simulated_transaction(institution: str, billId: str, forwardTransferRef: str, api_key: str = None):
  api_response = await api_request("POST", "/simulated-transactions", "", {"institution": institution, "billId": billId, "forwardTransferRef": forwardTransferRef}, api_key)
  return api_response

async def get_simulated_transaction(transaction_id: str, api_key: str = None):
  api_response = await api_request("GET", "/simulated-transactions/" + transaction_id, "", None, api_key)
  return api_response

async def list_simulated_transactions(param: Optional[dict] = None, api_key: Optional[str] = None):
    if param is None:
      param = {}

    if hasattr(param, 'dict'):
      param = param.dict()

    api_response = await api_request("GET", "/simulated-transactions", param, None, api_key)
    return api_response