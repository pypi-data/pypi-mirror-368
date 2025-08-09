"""
BSV Wallet and Transaction models for Django integration
"""
from django.db import models
from django.conf import settings
import json
from django.core.cache import cache
from django.utils import timezone
from decimal import Decimal
import logging
import aiohttp
import asyncio
from typing import Optional, Dict, Any
import requests

# BSV SDK imports
try:
    # Try new bsv-sdk package first
    from bsv_sdk import PrivateKey, P2PKH, Transaction, TransactionInput, TransactionOutput
    from bsv_sdk import Script, OpCode
    from bsv_sdk.script import ScriptChunk
    BSVTransactionLib = Transaction
    WhatsOnChainBroadcaster = None  # Will use direct API calls
except ImportError:
    # Fallback to older bsv package
    from bsv import ( 
        PrivateKey,
        P2PKH,
        P2PK, 
        Transaction as BSVTransactionLib,
        Transaction,
        TransactionInput,
        TransactionOutput, 
        WhatsOnChainBroadcaster,
        BroadcastFailure, 
        Script, 
        OpCode,
        OpReturn
    )
    from bsv.script.script import ScriptChunk
    from bsv.utils import encode_pushdata
from yenpoint_1satordinals.core import OneSatOrdinal
from whatsonchain.api import Whatsonchain
from asgiref.sync import sync_to_async

logger = logging.getLogger('bsv_integration')


class BSVWallet(models.Model):
    """
    BSV Wallet model with full blockchain integration
    """
    # Basic wallet fields
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='bsv_wallets'
    )
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    public_key = models.CharField(max_length=100)
    private_key = models.CharField(max_length=100)
    network = models.CharField(max_length=10, default='mainnet')
    is_primary = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    
    # Balance and timestamps
    balance = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_balance_update = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "BSV Wallet"
        verbose_name_plural = "BSV Wallets"

    def __str__(self):
        return f"{self.name} - {self.address}"

    @property
    def display_name(self):
        return f"{self.name} (Balance: {self.balance} BSV)"

    def get_network(self):
        """Get the appropriate network string for WhatsOnChain API"""
        return 'test' if self.network == 'testnet' else 'main'

    async def get_utxos(self):
        """Get fresh UTXOs for the wallet"""
        network = self.get_network()
        async with aiohttp.ClientSession() as session:
            url = f"https://api.whatsonchain.com/v1/bsv/{network}/address/{self.address}/unspent"
            async with session.get(url) as response:
                if response.status == 200:
                    utxos = await response.json()
                    return sorted(utxos, key=lambda x: x['value'], reverse=True) if utxos else []
        return []

    async def get_fresh_utxos(self):
        """Get fresh UTXOs for the wallet (filtering out dust)"""
        utxos = await self.get_utxos()
        filtered_utxos = [utx for utx in utxos if utx['value'] > 1000]
        return sorted(filtered_utxos, key=lambda x: x['value'], reverse=True) if filtered_utxos else []

    async def get_transaction_hex(self, txid: str) -> str:
        """Get raw transaction hex from WhatsOnChain"""
        network = self.get_network()
        url = f"https://api.whatsonchain.com/v1/bsv/{network}/tx/{txid}/hex"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                raise ValueError(f"Failed to get transaction hex for {txid}")

    async def send_transaction(self, recipient_address, amount, op_return_message=None, image=None):
        """
        Send BSV transaction with optional OP_RETURN message and image
        """
        logger.info(f"\n=== Starting BSV Transaction ===")
        logger.info(f"From: {self.address}")
        logger.info(f"To: {recipient_address}")
        logger.info(f"Amount: {amount} satoshis")
        
        try:
            # Get UTXOs
            fresh_utxos = await self.get_fresh_utxos()
            if not fresh_utxos:
                raise ValueError("No valid UTXOs available")

            selected_utxo = fresh_utxos[0]
            priv_key = PrivateKey(self.private_key)

            # Get source transaction
            source_tx_hex = await self.get_transaction_hex(selected_utxo['tx_hash'])
            source_tx = Transaction.from_hex(source_tx_hex)
            
            # Create input
            tx_input = TransactionInput(
                source_transaction=source_tx,
                source_txid=selected_utxo['tx_hash'],
                source_output_index=selected_utxo['tx_pos'],
                unlocking_script_template=P2PKH().unlock(priv_key)
            )

            tx = BSVTransactionLib([tx_input])

            # Add image as 1sat ordinal if provided
            if image:
                try:
                    image_data = image.read() if hasattr(image, 'read') else image
                    content_type = getattr(image, 'content_type', 'image/jpeg')

                    logger.info(f"Processing image: {getattr(image, 'name', 'unknown')}")
                    logger.info(f"Image size: {len(image_data)} bytes")
                    logger.info(f"Content type: {content_type}")

                    if not image_data:
                        raise ValueError("Image data is empty")

                    ordinal_script = self.create_1sat_ordinal_script(
                        recipient_address,
                        content_type,
                        image_data
                    )

                    tx.add_output(TransactionOutput(
                        locking_script=ordinal_script,
                        satoshis=1
                    ))
                    logger.info("1sat ordinal output added to transaction")

                except Exception as e:
                    logger.error(f"Error processing image: {str(e)}")
                    raise

            # Add OP_RETURN message if provided
            if op_return_message:
                message_chunks = [
                    ScriptChunk(OpCode.OP_FALSE),
                    ScriptChunk(OpCode.OP_RETURN),
                    ScriptChunk(None, op_return_message.encode())
                ]
                tx.add_output(TransactionOutput(
                    satoshis=0,
                    locking_script=Script.from_chunks(message_chunks)
                ))

            # Add change output
            change_amount = selected_utxo['value'] - amount - 1000  # Basic fee
            if change_amount > 546:  # Dust limit
                tx.add_output(TransactionOutput(
                    satoshis=change_amount,
                    locking_script=P2PKH().lock(self.address)
                ))

            # Sign and broadcast
            tx.sign()
            broadcaster = WhatsOnChainBroadcaster()
            await broadcaster.broadcast(tx)
            txid = tx.txid()
            
            # Create transaction record
            transaction = await sync_to_async(BSVTransaction.objects.create)(
                wallet=self,
                txid=txid,
                amount=Decimal(amount) / Decimal('100000000'),  # Convert to BSV
                recipient_address=recipient_address,
                op_return_message=op_return_message,
                transaction_type='ordinal' if image else 'transfer'
            )
            
            logger.info(f"Transaction broadcast successfully: {txid}")
            return {
                'success': True,
                'txid': txid,
                'hex': tx.hex(),
                'transaction': transaction
            }

        except Exception as e:
            logger.error(f"Send transaction failed: {str(e)}")
            raise

    def create_1sat_ordinal_script(self, recipient_address, content_type, binary_data):
        """Create script for 1sat ordinal inscription"""
        logger.info(f"\n=== Creating 1sat Ordinal Script ===")
        logger.info(f"Content type: {content_type}")
        logger.info(f"Binary data length: {len(binary_data)} bytes")
        
        try:
            # Create standard P2PKH output first
            p2pkh_output = P2PKH().lock(recipient_address)
            logger.info(f"P2PKH script created for address: {recipient_address}")

            # Add ordinal data with correct OP codes
            chunks = p2pkh_output.chunks + [
                ScriptChunk(OpCode.OP_FALSE),
                ScriptChunk(OpCode.OP_IF),
                ScriptChunk(None, b'ord'),
                ScriptChunk(OpCode.OP_1),           # Required before content type
                ScriptChunk(None, content_type.encode()),
                ScriptChunk(OpCode.OP_0),           # Required before content
                ScriptChunk(None, binary_data),
                ScriptChunk(OpCode.OP_ENDIF)
            ] + p2pkh_output.chunks  # Add locking script at the end

            script = Script.from_chunks(chunks)
            logger.info(f"1sat ordinal script created, length: {len(script.hex()) // 2} bytes")
            return script
            
        except Exception as e:
            logger.error(f"1sat ordinal script creation failed: {str(e)}")
            raise

    def update_balance(self, force_refresh=False):
        """Update wallet balance from blockchain"""
        logger.info(f"\n=== Updating Balance for {self.address} ===")
        try:
            # Throttle with cache, unless force_refresh is True
            last_checked = cache.get(f"wallet_checked_{self.id}")
            if not force_refresh and last_checked and (timezone.now() - last_checked).seconds < 300:
                logger.info("Balance check skipped (cached)")
                return self.balance

            network = self.get_network()
            
            # Try WhatsOnChain first
            try:
                woc_url = f"https://api.whatsonchain.com/v1/bsv/{network}/address/{self.address}/balance"
                response = requests.get(woc_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    confirmed = data.get("confirmed", 0)
                    
                    # Convert to BSV
                    self.balance = Decimal(confirmed) / Decimal("100000000")
                    self.save()
                    cache.set(f"wallet_checked_{self.id}", timezone.now())
                    logger.info(f"Balance updated (WhatsOnChain): {self.balance} BSV")
                    return self.balance
            except Exception as e:
                logger.warning(f"WhatsOnChain error: {e}")

            # Fallback to GorillaPool
            try:
                gp_url = f"https://api.gorillapool.io/api/v1/address/{self.address}/balance"
                response = requests.get(gp_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    confirmed = data.get("confirmed", 0)
                    
                    self.balance = Decimal(confirmed) / Decimal("100000000")
                    self.save()
                    cache.set(f"wallet_checked_{self.id}", timezone.now())
                    logger.info(f"Balance updated (GorillaPool): {self.balance} BSV")
                    return self.balance
            except Exception as e:
                logger.error(f"GorillaPool error: {e}")

        except Exception as e:
            logger.error(f"Balance update failed: {str(e)}")
            return self.balance

    def verify_ordinal(self, txid: str) -> Dict[str, Any]:
        """Verify ordinal inscription using GorillaPool API"""
        api_url = f"https://ordinals.gorillapool.io/api/inscriptions/tx/{txid}"
        response = requests.get(api_url)
        return response.json()

    def get_ordinal_history(self, address: str) -> Dict[str, Any]:
        """Get ordinal history for an address"""
        api_url = f"https://ordinals.gorillapool.io/api/inscriptions/address/{address}"
        response = requests.get(api_url)
        return response.json()


class BSVTransaction(models.Model):
    """
    Model to track BSV transactions
    """
    TRANSACTION_TYPES = [
        ('transfer', 'Regular Transfer'),
        ('ordinal', '1Sat Ordinal'),
        ('image', 'Image Transaction'),
    ]

    wallet = models.ForeignKey(BSVWallet, on_delete=models.CASCADE)
    txid = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    recipient_address = models.CharField(max_length=100)
    op_return_message = models.TextField(null=True, blank=True)
    fee = models.DecimalField(max_digits=18, decimal_places=8, default=0.0001)
    created_at = models.DateTimeField(auto_now_add=True)

    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPES,
        default='transfer'
    )
    content_type = models.CharField(max_length=100, null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Transaction {self.txid[:8]}..."

    class Meta:
        verbose_name = "BSV Transaction"
        verbose_name_plural = "BSV Transactions"
        ordering = ['-created_at']
