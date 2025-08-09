"""
Utility functions for BSV blockchain operations
"""
import logging
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional
from bsv import PrivateKey, P2PKH
from bsv.script.script import ScriptChunk
from bsv import Script, OpCode

logger = logging.getLogger('bsv_integration')


async def fetch_utxos(address: str, network: str = 'main') -> List[Dict]:
    """
    Fetch UTXOs for a given address from WhatsOnChain
    
    Args:
        address: BSV address
        network: 'main' or 'test'
    
    Returns:
        List of UTXO dictionaries
    """
    async with aiohttp.ClientSession() as session:
        url = f"https://api.whatsonchain.com/v1/bsv/{network}/address/{address}/unspent"
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            return []


async def fetch_transaction_hex(txid: str, network: str = 'main') -> str:
    """
    Fetch raw transaction hex from WhatsOnChain
    
    Args:
        txid: Transaction ID
        network: 'main' or 'test'
    
    Returns:
        Raw transaction hex string
    """
    async with aiohttp.ClientSession() as session:
        url = f"https://api.whatsonchain.com/v1/bsv/{network}/tx/{txid}/hex"
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            raise ValueError(f"Failed to fetch transaction hex for {txid}")


def create_op_return_script(data: bytes) -> Script:
    """
    Create an OP_RETURN script with the given data
    
    Args:
        data: Data to include in OP_RETURN
        
    Returns:
        Script object
    """
    chunks = [
        ScriptChunk(OpCode.OP_FALSE),
        ScriptChunk(OpCode.OP_RETURN),
        ScriptChunk(None, data)
    ]
    return Script.from_chunks(chunks)


def create_b_protocol_script(binary_data: bytes, content_type: str, filename: str) -> Script:
    """
    Create B:// protocol OP_RETURN script for file storage
    
    Args:
        binary_data: File binary data
        content_type: MIME type (e.g., 'image/jpeg')
        filename: Original filename
        
    Returns:
        Script object following B:// protocol
    """
    chunks = [
        ScriptChunk(OpCode.OP_FALSE),
        ScriptChunk(OpCode.OP_RETURN),
        ScriptChunk(None, b'19HxigV4QyBv3tHpQVcUEQyq1pzZVdoAut'),  # B:// protocol prefix
        ScriptChunk(None, binary_data),
        ScriptChunk(None, content_type.encode('utf-8')),
        ScriptChunk(None, b'binary'),
        ScriptChunk(None, filename.encode('utf-8'))
    ]
    return Script.from_chunks(chunks)


def create_1sat_ordinal_script(recipient_address: str, content_type: str, binary_data: bytes) -> Script:
    """
    Create a 1sat ordinal inscription script
    
    Args:
        recipient_address: Address to send the ordinal to
        content_type: MIME type of the content
        binary_data: Binary content data
        
    Returns:
        Script object for 1sat ordinal
    """
    # Create standard P2PKH output
    p2pkh_output = P2PKH().lock(recipient_address)
    
    # Add ordinal inscription data
    chunks = p2pkh_output.chunks + [
        ScriptChunk(OpCode.OP_FALSE),
        ScriptChunk(OpCode.OP_IF),
        ScriptChunk(None, b'ord'),
        ScriptChunk(OpCode.OP_1),
        ScriptChunk(None, content_type.encode()),
        ScriptChunk(OpCode.OP_0),
        ScriptChunk(None, binary_data),
        ScriptChunk(OpCode.OP_ENDIF)
    ] + p2pkh_output.chunks
    
    return Script.from_chunks(chunks)


def generate_wallet_keys(network: str = 'mainnet') -> Dict[str, str]:
    """
    Generate new wallet keys
    
    Args:
        network: 'mainnet' or 'testnet'
        
    Returns:
        Dictionary with private_key, public_key, and address
    """
    # Generate private key
    private_key = PrivateKey()
    
    # Get public key and address
    public_key = private_key.public_key()
    address = public_key.address()
    
    return {
        'private_key': str(private_key),
        'public_key': str(public_key),
        'address': str(address)
    }


def validate_bsv_address(address: str) -> bool:
    """
    Validate a BSV address format
    
    Args:
        address: BSV address to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Basic validation - BSV addresses start with 1 or 3 and are 26-35 chars
        if not address or len(address) < 26 or len(address) > 35:
            return False
            
        if not address.startswith(('1', '3')):
            return False
            
        # Additional validation could be added here
        return True
    except Exception:
        return False


def satoshis_to_bsv(satoshis: int) -> float:
    """
    Convert satoshis to BSV
    
    Args:
        satoshis: Amount in satoshis
        
    Returns:
        Amount in BSV
    """
    return satoshis / 100000000


def bsv_to_satoshis(bsv: float) -> int:
    """
    Convert BSV to satoshis
    
    Args:
        bsv: Amount in BSV
        
    Returns:
        Amount in satoshis
    """
    return int(bsv * 100000000)


class BSVNetworkUtils:
    """
    Utility class for BSV network operations
    """
    
    @staticmethod
    def get_network_string(network: str) -> str:
        """Convert network name to API format"""
        return 'test' if network == 'testnet' else 'main'
    
    @staticmethod
    async def check_transaction_status(txid: str, network: str = 'main') -> Dict[str, Any]:
        """
        Check transaction status on the blockchain
        
        Args:
            txid: Transaction ID
            network: 'main' or 'test'
            
        Returns:
            Transaction data dictionary
        """
        async with aiohttp.ClientSession() as session:
            url = f"https://api.whatsonchain.com/v1/bsv/{network}/tx/{txid}"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return {}
    
    @staticmethod
    async def get_address_balance(address: str, network: str = 'main') -> Dict[str, int]:
        """
        Get address balance from blockchain
        
        Args:
            address: BSV address
            network: 'main' or 'test'
            
        Returns:
            Balance data dictionary
        """
        async with aiohttp.ClientSession() as session:
            url = f"https://api.whatsonchain.com/v1/bsv/{network}/address/{address}/balance"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return {'confirmed': 0, 'unconfirmed': 0}


class OrdinalUtils:
    """
    Utility class for ordinal operations
    """
    
    @staticmethod
    def verify_ordinal_inscription(txid: str) -> Dict[str, Any]:
        """
        Verify ordinal inscription using GorillaPool API
        
        Args:
            txid: Transaction ID containing the ordinal
            
        Returns:
            Ordinal data dictionary
        """
        import requests
        api_url = f"https://ordinals.gorillapool.io/api/inscriptions/tx/{txid}"
        try:
            response = requests.get(api_url)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logger.error(f"Error verifying ordinal: {e}")
            return {}
    
    @staticmethod
    def get_address_ordinals(address: str) -> Dict[str, Any]:
        """
        Get all ordinals for an address
        
        Args:
            address: BSV address
            
        Returns:
            Ordinals data dictionary
        """
        import requests
        api_url = f"https://ordinals.gorillapool.io/api/inscriptions/address/{address}"
        try:
            response = requests.get(api_url)
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            logger.error(f"Error fetching ordinals: {e}")
            return {}
