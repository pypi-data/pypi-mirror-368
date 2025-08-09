import os
import json
import re
from typing import Dict, Any, Optional, Union, TypedDict
from enum import Enum
import httpx


API_PORT = os.getenv('API_PORT', '3140')
if os.getenv('ENV') == 'production':
    API_PATH = 'shade-agent-api'
else:
    API_PATH = 'localhost'


class AgentAccountIdResponse(TypedDict):
    """Response type for agent account ID."""
    accountId: str


class AgentInfoResponse(TypedDict):
    """Response type for agent info."""
    codehash: str
    checksum: str


class SignatureKeyType(Enum):
    """Enum for signature key types."""
    EDDSA = 'Eddsa'
    ECDSA = 'Ecdsa'
    
    @classmethod
    def from_string(cls, value: str) -> 'SignatureKeyType':
        """Create enum from string value (case insensitive)."""
        value_lower = value.lower()
        if value_lower == 'eddsa':
            return cls.EDDSA
        elif value_lower == 'ecdsa':
            return cls.ECDSA
        else:
            raise ValueError(f"Invalid signature key type: {value}. Must be 'Eddsa' or 'Ecdsa'")


async def agent(method_name: str, args: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Calls a method on the agent account instance inside the API

    Args:
        method_name: The name of the agent method to call
        args: Arguments to pass to the agent account method

    Returns:
        The result of the agent method call
    """
    if args is None:
        args = {}
    
    url = f"http://{API_PATH}:{API_PORT}/api/agent/{method_name}"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=args)
        response.raise_for_status()
        return response.json()


async def agent_account_id() -> AgentAccountIdResponse:
    """
    Retrieves the account ID of the agent.

    Returns:
        A dictionary containing the agent's account ID
    """
    return await agent('getAccountId')


async def agent_info() -> AgentInfoResponse:
    """
    Retrieves the agent's record from the agent contract

    Returns:
        A dictionary containing the agent's codehash and checksum
    """
    account_id = (await agent_account_id())['accountId']
    return await agent('view', {
        'methodName': 'get_agent',
        'args': {'account_id': account_id}
    })


async def agent_view(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Contract view from agent account inside the API

    Args:
        args: The arguments for the contract view method

    Returns:
        The result of the view method
    """
    return await agent('view', args)


async def agent_call(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Contract call from agent account inside the API

    Args:
        args: The arguments for the contract call method

    Returns:
        The result of the call method
    """
    return await agent('call', args)


async def request_signature(
    path: str,
    payload: str,
    key_type: Union[SignatureKeyType, str] = SignatureKeyType.ECDSA
) -> Dict[str, Any]:
    """
    Requests a signature from the agent for a given payload and path.

    Args:
        path: The path associated with the signature request
        payload: The payload to be signed
        key_type: The type of key to use for signing (default is ECDSA)

    Returns:
        The result of the signature request
    """
    # Handle string input
    if isinstance(key_type, str):
        key_type = SignatureKeyType.from_string(key_type)
    
    return await agent('call', {
        'methodName': 'request_signature',
        'args': {
            'path': path,
            'payload': payload,
            'key_type': key_type.value
        }
    })
