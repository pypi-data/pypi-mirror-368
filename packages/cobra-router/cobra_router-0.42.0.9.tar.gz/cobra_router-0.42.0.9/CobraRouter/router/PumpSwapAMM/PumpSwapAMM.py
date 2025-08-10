import asyncio
import traceback
from typing import Optional
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts, TokenAccountOpts
from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit # type: ignore
from solders.keypair import Keypair # type: ignore
from solders.pubkey import Pubkey # type: ignore
from solders.transaction import VersionedTransaction # type: ignore
from solders.message import MessageV0 # type: ignore
from solana.rpc.commitment import Processed, Confirmed
from spl.token.instructions import (
    get_associated_token_address,
    create_associated_token_account,
    sync_native,
    SyncNativeParams,
    close_account,
    CloseAccountParams,
)
from construct import Struct as cStruct, Byte, Int16ul, Int64ul, Bytes
try:
    from fetch_reserves import fetch_pool_base_price
except:
    from .fetch_reserves import fetch_pool_base_price

import logging

def compute_unit_price_from_total_fee(
    total_lams: int,
    compute_units: int = 120_000
) -> int:
    lamports_per_cu = total_lams / float(compute_units)
    micro_lamports_per_cu = lamports_per_cu * 1_000_000
    return int(micro_lamports_per_cu)

POOL_COMPUTE_BUDGET = 200_000
UNIT_COMPUTE_BUDGET = 200_000

WSOL_MINT           = Pubkey.from_string("So11111111111111111111111111111111111111112")
PUMPSWAP_PROGRAM_ID = Pubkey.from_string("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA")
TOKEN_PROGRAM_PUB   = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN    = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM_PROGRAM_ID   = Pubkey.from_string("11111111111111111111111111111111")
EVENT_AUTHORITY     = Pubkey.from_string("GS4CU59F31iL7aR2Q8zVS8DRrcRnXX1yjQ66TqNVQnaR")
GLOBAL_VOLUME_ACCUMULATOR = Pubkey.from_string("C2aFPdENg4A2HQsmrd5rTw5TaYBX5Ku887cWjbFKtZpw")

GLOBAL_CONFIG_PUB   = Pubkey.from_string("ADyA8hdefvWN2dbGGWFotbzWxrAvLW83WG6QCVXvJKqw")
PROTOCOL_FEE_RECIP  = Pubkey.from_string("7VtfL8fvgNfhz17qKRMjzQEXgbdpnHHHQRh54R9jP2RJ")
TOKEN_2022_PROGRAM_PUB = Pubkey.from_string(
    "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb"
)
CREATE_POOL_DISCRIM = b"\xe9\x92\xd1\x8e\xcf\x68\x40\xbc"
BUY_INSTR_DISCRIM = b'\x66\x06\x3d\x12\x01\xda\xeb\xea'
SELL_INSTR_DISCRIM = b"\x33\xe6\x85\xa4\x01\x7f\x83\xad"
WITHDRAW_INSTR_DISCRIM = b"\xb7\x12\x46\x9c\x94\x6d\xa1\x22"
DEPOSIT_INSTR_DISCRIM = b"\xf2\x23\xc6\x89\x52\xe1\xf2\xb6"
LAMPORTS_PER_SOL = 1_000_000_000

def _get_price(base_balance_tokens: float, quote_balance_sol: float, reversed: bool = False) -> float:
    if base_balance_tokens <= 0:
        return float("inf")
    if reversed:
        return base_balance_tokens / quote_balance_sol
    return quote_balance_sol / base_balance_tokens

CREATOR_VAULT_SEED  = b"creator_vault"

def derive_creator_vault(creator: Pubkey, quote_mint: Pubkey) -> tuple[Pubkey, Pubkey]:
    vault_auth, bump = Pubkey.find_program_address(
        [CREATOR_VAULT_SEED, bytes(creator)],
        PUMPSWAP_PROGRAM_ID
    )
    vault_ata = get_associated_token_address(vault_auth, quote_mint)
    return vault_ata, vault_auth

def convert_sol_to_base_tokens(
    sol_amount: float,
    base_balance_tokens: float,
    quote_balance_sol: float,
    decimals_base: int,
    decimals_quote: int = 0, # specify when using `reversed` functions
    slippage_pct: float = 0.01,
    reversed: bool = False,
):
    price = _get_price(base_balance_tokens, quote_balance_sol, reversed)
    raw_tokens = sol_amount / price 
    base_amount_out = int(raw_tokens * (10**decimals_base)) if not reversed else int(raw_tokens * (10**decimals_quote))

    max_sol = sol_amount * (float("1." + str(slippage_pct)))
    max_quote_in_lamports = int(max_sol * LAMPORTS_PER_SOL)
    return (base_amount_out, max_quote_in_lamports)

def convert_base_tokens_to_sol(
    token_amount_user: float,
    base_balance_tokens: float,
    quote_balance_sol: float,
    decimals_base: int,
    slippage_pct: float = 0.01,
):
    price = _get_price(base_balance_tokens, quote_balance_sol)

    base_amount_out = int(token_amount_user * (10**decimals_base))

    needed_sol = token_amount_user * price
    max_needed_sol = needed_sol * (1 + slippage_pct)
    max_quote_in_lamports = int(max_needed_sol * LAMPORTS_PER_SOL)
    return (base_amount_out, max_quote_in_lamports)

class Exceptions:
    class PoolReversed(Exception):
        pass

PumpSwapPoolStateNew = cStruct(
    "pool_bump" / Byte,
    "index" / Int16ul,
    "creator" / Bytes(32),
    "base_mint" / Bytes(32),
    "quote_mint" / Bytes(32),
    "lp_mint" / Bytes(32),
    "pool_base_token_account" / Bytes(32),
    "pool_quote_token_account" / Bytes(32),
    "lp_supply" / Int64ul,
    "coin_creator" / Bytes(32),
)
PumpSwapPoolStateOld = cStruct(
    "pool_bump" / Byte,
    "index" / Int16ul,
    "creator" / Bytes(32),
    "base_mint" / Bytes(32),
    "quote_mint" / Bytes(32),
    "lp_mint" / Bytes(32),
    "pool_base_token_account" / Bytes(32),
    "pool_quote_token_account" / Bytes(32),
    "lp_supply" / Int64ul,
)

NEW_POOL_TYPE = "NEW"
OLD_POOL_TYPE = "OLD"

def convert_pool_keys(container, pool_type):
    return {
        "pool_bump": container.pool_bump,
        "index": container.index,
        "creator": str(Pubkey.from_bytes(container.creator)),
        "base_mint": str(Pubkey.from_bytes(container.base_mint)),
        "quote_mint": str(Pubkey.from_bytes(container.quote_mint)),
        "lp_mint": str(Pubkey.from_bytes(container.lp_mint)),
        "pool_base_token_account": str(Pubkey.from_bytes(container.pool_base_token_account)),
        "pool_quote_token_account": str(Pubkey.from_bytes(container.pool_quote_token_account)),
        "lp_supply": container.lp_supply,
        "coin_creator": str(Pubkey.from_bytes(container.coin_creator)),
    } if pool_type == NEW_POOL_TYPE else {
        "pool_bump": container.pool_bump,
        "index": container.index,
        "creator": str(Pubkey.from_bytes(container.creator)),
        "base_mint": str(Pubkey.from_bytes(container.base_mint)),
        "quote_mint": str(Pubkey.from_bytes(container.quote_mint)),
        "lp_mint": str(Pubkey.from_bytes(container.lp_mint)),
        "pool_base_token_account": str(Pubkey.from_bytes(container.pool_base_token_account)),
        "pool_quote_token_account": str(Pubkey.from_bytes(container.pool_quote_token_account)),
        "lp_supply": container.lp_supply
    }

async def fetch_pool_state(pool: str | Pubkey, async_client: AsyncClient):
    """
        Returns:
            dict: Pool data:
                pool_bump: int
                index: int
                creator: str
                base_mint: str
                quote_mint: str
                lp_mint: str
                pool_base_token_account: str
                pool_quote_token_account: str
                lp_supply: int
                coin_creator: str [Optional]
    """
    pool = pool if isinstance(pool, Pubkey) else Pubkey.from_string(pool)

    resp = await async_client.get_account_info_json_parsed(pool, commitment=Processed)
    if not resp or not resp.value or not resp.value.data:
        raise Exception("Invalid account response")

    raw_data = resp.value.data
    pool_type = NEW_POOL_TYPE
    try:
        parsed = PumpSwapPoolStateNew.parse(raw_data[8:])
    except Exception as e:
        try:
            parsed = PumpSwapPoolStateOld.parse(raw_data[8:])
            pool_type = OLD_POOL_TYPE
        except Exception as e:
            traceback.print_exc()
            return (None, None)
        
    parsed = convert_pool_keys(parsed, pool_type=pool_type)

    return (parsed, pool_type)

class PumpSwap:
    def __init__(self, async_client: AsyncClient):
        self.async_client = async_client
    
    async def close(self):
        await self.async_client.close()

    def _derive_uva_pda(self, user: Pubkey):
        user_acc, _ = Pubkey.find_program_address(
            [b"user_volume_accumulator", bytes(user)],
            PUMPSWAP_PROGRAM_ID
        )
        return user_acc

    async def fetch_pool_base_price(self, pool: str | Pubkey):
        """
        Fetch the base price of the pool.
        Args:
            pool (str): Pool address.
        Returns:
            tuple: (base_price, base_balance_tokens, quote_balance_sol)
        """
        pool = pool if isinstance(pool, Pubkey) else Pubkey.from_string(pool)
        pool_keys, _ = await fetch_pool_state(pool, self.async_client)
        base_price, base_balance_tokens, quote_balance_sol = await fetch_pool_base_price(pool_keys, self.async_client)
        return base_price, base_balance_tokens, quote_balance_sol

    async def create_ata_if_needed(self, owner: Pubkey, mint: Pubkey):
        """
        If there's no associated token account for (owner, mint), return an
        instruction to create it. Otherwise return None.
        """
        ata = get_associated_token_address(owner, mint)
        resp = await self.async_client.get_account_info(ata)
        if resp.value is None:
            # means ATA does not exist
            return create_associated_token_account(
                payer=owner,
                owner=owner,
                mint=mint
            )
        return None

    async def _create_ata_if_needed_for_owner(
        self, payer: Pubkey, owner: Pubkey, mint: Pubkey, token_program: Pubkey = TOKEN_PROGRAM_PUB
    ):
        ata = get_associated_token_address(owner, mint, token_program)
        resp = await self.async_client.get_account_info(ata)
        if resp.value is None:
            return create_associated_token_account(
                payer=payer,
                owner=owner,
                mint=mint,
                token_program_id=token_program
            )
        return None

    async def buy(
        self,
        pool_data: dict,
        sol_amount: float,      # e.g. 0.001
        keypair: Keypair,
        pool_type: str = NEW_POOL_TYPE,
        slippage_pct: float = 10,    # e.g. 1.0 => 1%
        fee_sol: float = 0.00001,         # total priority fee user wants to pay, e.g. 0.0005
        debug_prints: bool = False,
        return_instructions: bool = False,
    ):
        """
            Args:
                pool_data: dict
                sol_amount: float
                slippage_pct: float
                fee_sol: float
            Returns:
                tuple: (confirmed: bool, tx_sig: str, pool_type: (str)OLD | (str)NEW, (float)mint_amount_we_bought)
        """
        user_pubkey = keypair.pubkey()
        base_balance_tokens = pool_data['base_balance_tokens']
        quote_balance_sol   = pool_data['quote_balance_sol']
        decimals_base       = pool_data['decimals_base']

        token_base = pool_data['token_base']
        token_quote = pool_data['token_quote']
        if token_base == WSOL_MINT:
            raise Exceptions.PoolReversed("PumpSwap | Pool is reversed, which means you buy WSOL and sell TOKEN")

        if pool_type == NEW_POOL_TYPE:
            coin_creator  = pool_data["coin_creator"]
            vault_ata, vault_auth = derive_creator_vault(coin_creator, token_quote)

        (base_amount_out, max_quote_amount_in) = convert_sol_to_base_tokens(
            sol_amount, base_balance_tokens, quote_balance_sol,
            decimals_base, slippage_pct=slippage_pct
        )

        instructions = []

        if not return_instructions:
            lamports_fee = int(fee_sol * LAMPORTS_PER_SOL)
            micro_lamports = compute_unit_price_from_total_fee(
                lamports_fee,
                compute_units=UNIT_COMPUTE_BUDGET
            )

            instructions.append(set_compute_unit_limit(UNIT_COMPUTE_BUDGET))
            instructions.append(set_compute_unit_price(micro_lamports))

        wsol_ata_ix = await self.create_ata_if_needed(user_pubkey, token_quote)
        if wsol_ata_ix:
            instructions.append(wsol_ata_ix)

        wsol_ata = get_associated_token_address(user_pubkey, token_quote)
        system_transfer_ix = self._build_system_transfer_ix(
            from_pubkey=user_pubkey,
            to_pubkey=wsol_ata,
            lamports=max_quote_amount_in
        )
        instructions.append(system_transfer_ix)

        base_ata_ix = await self.create_ata_if_needed(user_pubkey, token_base)
        if base_ata_ix:
            instructions.append(base_ata_ix)

        instructions.append(sync_native(SyncNativeParams(program_id=TOKEN_PROGRAM_PUB, account=wsol_ata)))

        if pool_type == NEW_POOL_TYPE:
            buy_ix = self._build_new_pumpswap_buy_ix(
                pool_pubkey = pool_data['pool_pubkey'],
                user_pubkey = user_pubkey,
                global_config = GLOBAL_CONFIG_PUB,
                base_mint    = token_base,
                quote_mint   = token_quote,
                user_base_token_ata  = get_associated_token_address(user_pubkey, token_base),
                user_quote_token_ata = get_associated_token_address(user_pubkey, token_quote),
                pool_base_token_account  = Pubkey.from_string(pool_data['pool_base_token_account']),
                pool_quote_token_account = Pubkey.from_string(pool_data['pool_quote_token_account']),
                protocol_fee_recipient   = PROTOCOL_FEE_RECIP,
                protocol_fee_recipient_ata = get_associated_token_address(PROTOCOL_FEE_RECIP, token_quote),
                base_amount_out = base_amount_out,
                max_quote_amount_in = max_quote_amount_in,
                vault_auth = vault_auth,
                vault_ata = vault_ata,
            )
        elif pool_type == OLD_POOL_TYPE:
            buy_ix = self._build_old_pumpswap_buy_ix(
                pool_pubkey = pool_data['pool_pubkey'],
                user_pubkey = user_pubkey,
                global_config = GLOBAL_CONFIG_PUB,
                base_mint    = token_base,
                quote_mint   = token_quote,
                user_base_token_ata  = get_associated_token_address(user_pubkey, token_base),
                user_quote_token_ata = get_associated_token_address(user_pubkey, token_quote),
                pool_base_token_account  = Pubkey.from_string(pool_data['pool_base_token_account']),
                pool_quote_token_account = Pubkey.from_string(pool_data['pool_quote_token_account']),
                protocol_fee_recipient   = PROTOCOL_FEE_RECIP,
                protocol_fee_recipient_ata = get_associated_token_address(PROTOCOL_FEE_RECIP, token_quote),
                base_amount_out = base_amount_out,
                max_quote_amount_in = max_quote_amount_in
            )
        instructions.append(buy_ix)

        instructions.append(
            close_account(
                CloseAccountParams(
                    program_id=TOKEN_PROGRAM_PUB,
                    account=wsol_ata,
                    dest=user_pubkey,
                    owner=user_pubkey
                )
            )
        )

        if return_instructions:
            return instructions

        latest_blockhash = await self.async_client.get_latest_blockhash()
        compiled_msg = MessageV0.try_compile(
            payer=user_pubkey,
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=latest_blockhash.value.blockhash,
        )
        transaction = VersionedTransaction(compiled_msg, [keypair])

        opts = TxOpts(skip_preflight=True, max_retries=0)
        send_resp = await self.async_client.send_transaction(transaction, opts=opts)
        if debug_prints:
            logging.info(f"Transaction sent: https://solscan.io/tx/{send_resp.value}")

        # Confirm
        confirmed = await self._await_confirm_transaction(send_resp.value)
        if debug_prints:
            logging.info(f"Success: {confirmed}")
        return (confirmed, str(send_resp.value), pool_type, base_amount_out)

    def _build_system_transfer_ix(self, from_pubkey: Pubkey, to_pubkey: Pubkey, lamports: int):
        from solders.system_program import TransferParams, transfer
        return transfer(
            TransferParams(
                from_pubkey=from_pubkey,
                to_pubkey=to_pubkey,
                lamports=lamports
            )
        )
    
    async def reversed_sell(
        self,
        pool_data: dict,
        sell_pct: float,
        keypair: Keypair,
        pool_type: str = NEW_POOL_TYPE,
        slippage_pct: float = 10, # slippage works differently here, we can't apply slippage because we spend all the tokens, so only way is to sell less, set slippage to as low as possible to sell as much WSOL
        fee_sol: float = 0.00001,         # total priority fee user wants to pay, e.g. 0.0005
        debug_prints: bool = False,
        return_instructions: bool = False,
    ):
        """
            Use this when pool is reversed, e.g. WSOL - Token.
            This function is used to buy WSOL and sell TOKEN.
            Don't mistake it for buying Token and selling WSOL.

            Args:
                pool_data: dict
                sol_amount: float
                pool_type: str
                slippage_pct: float
                fee_sol: float
            Returns:
                tuple: (confirmed: bool, tx_sig: str, pool_type: (str)OLD | (str)NEW, (float)mint_amount_we_bought)
        """
        user_pubkey = keypair.pubkey()
        base_balance_tokens = pool_data['base_balance_tokens'] # WSOL
        quote_balance_sol   = pool_data['quote_balance_sol'] # TOKEN
        decimals_quote      = pool_data['decimals_quote'] # TOKEN == X

        token_base = pool_data['token_base'] # WSOL
        token_quote = pool_data['token_quote'] # TOKEN

        user_base_balance_f = await self._fetch_user_token_balance(keypair, str(token_quote))
        if not user_base_balance_f or user_base_balance_f <= 0:
            if debug_prints:
                logging.info("No base token balance, can't sell.")
            return (False, None, pool_type)
        
        to_sell_amount_f = user_base_balance_f * (sell_pct / 100.0)
        if to_sell_amount_f <= 0:
            if debug_prints:
                logging.info("Nothing to sell after applying percentage.")
            return (False, None, pool_type)

        if pool_type == NEW_POOL_TYPE:
            coin_creator  = pool_data["coin_creator"]
            vault_ata, vault_auth = derive_creator_vault(coin_creator, token_quote)

        quote_token_in_amount = int(to_sell_amount_f * (10 ** decimals_quote))
        logging.info(f"quote_token_in_amount: {quote_token_in_amount} | to_sell_amount_f: {to_sell_amount_f}")
        
        base_balance_tokens = pool_data['base_balance_tokens']
        quote_balance_sol   = pool_data['quote_balance_sol']
        
        price = _get_price(base_balance_tokens, quote_balance_sol, reversed=True)
        logging.info(price)
        raw_sol = to_sell_amount_f * price
        # we can't apply slippage because we spend all the tokens, so only way is to sell less
        min_sol_out = raw_sol * (1 - slippage_pct/100.0)
        base_amount_out = int(min_sol_out * LAMPORTS_PER_SOL)
        logging.info(f"base_amount_out: {base_amount_out}")
        if base_amount_out <= 0:
            if debug_prints:
                logging.info("min_quote_amount_out <= 0. Slippage too big or no liquidity.")
            return (False, None, pool_type)

        instructions = []

        if not return_instructions:
            lamports_fee = int(fee_sol * LAMPORTS_PER_SOL)
            micro_lamports = compute_unit_price_from_total_fee(
                lamports_fee,
                compute_units=UNIT_COMPUTE_BUDGET
            )

            instructions.append(set_compute_unit_limit(UNIT_COMPUTE_BUDGET))
            instructions.append(set_compute_unit_price(micro_lamports))

        wsol_ata_ix = await self.create_ata_if_needed(user_pubkey, token_base)
        if wsol_ata_ix:
            instructions.append(wsol_ata_ix)

        wsol_ata = get_associated_token_address(user_pubkey, token_base)

        if pool_type == NEW_POOL_TYPE:
            buy_ix = self._build_new_pumpswap_buy_ix(
                pool_pubkey = pool_data['pool_pubkey'],
                user_pubkey = user_pubkey,
                global_config = GLOBAL_CONFIG_PUB,
                base_mint    = token_base,
                quote_mint   = token_quote,
                user_base_token_ata  = get_associated_token_address(user_pubkey, token_base),
                user_quote_token_ata = get_associated_token_address(user_pubkey, token_quote),
                pool_base_token_account  = Pubkey.from_string(pool_data['pool_base_token_account']),
                pool_quote_token_account = Pubkey.from_string(pool_data['pool_quote_token_account']),
                protocol_fee_recipient   = PROTOCOL_FEE_RECIP,
                protocol_fee_recipient_ata = get_associated_token_address(PROTOCOL_FEE_RECIP, token_quote),
                base_amount_out = base_amount_out,
                max_quote_amount_in = quote_token_in_amount,
                vault_auth = vault_auth,
                vault_ata = vault_ata,
            )
        elif pool_type == OLD_POOL_TYPE:
            buy_ix = self._build_old_pumpswap_buy_ix(
                pool_pubkey = pool_data['pool_pubkey'],
                user_pubkey = user_pubkey,
                global_config = GLOBAL_CONFIG_PUB,
                base_mint    = token_base,
                quote_mint   = token_quote,
                user_base_token_ata  = get_associated_token_address(user_pubkey, token_base),
                user_quote_token_ata = get_associated_token_address(user_pubkey, token_quote),
                pool_base_token_account  = Pubkey.from_string(pool_data['pool_base_token_account']),
                pool_quote_token_account = Pubkey.from_string(pool_data['pool_quote_token_account']),
                protocol_fee_recipient   = PROTOCOL_FEE_RECIP,
                protocol_fee_recipient_ata = get_associated_token_address(PROTOCOL_FEE_RECIP, token_quote),
                base_amount_out = base_amount_out,
                max_quote_amount_in = quote_token_in_amount
            )
        instructions.append(buy_ix)

        instructions.append(
            close_account(
                CloseAccountParams(
                    program_id=TOKEN_PROGRAM_PUB,
                    account=wsol_ata,
                    dest=user_pubkey,
                    owner=user_pubkey
                )
            )
        )

        if return_instructions:
            return instructions

        latest_blockhash = await self.async_client.get_latest_blockhash()
        compiled_msg = MessageV0.try_compile(
            payer=user_pubkey,
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=latest_blockhash.value.blockhash,
        )
        transaction = VersionedTransaction(compiled_msg, [keypair])

        opts = TxOpts(skip_preflight=True, max_retries=0)
        send_resp = await self.async_client.send_transaction(transaction, opts=opts)
        if debug_prints:
            logging.info(f"Transaction sent: https://solscan.io/tx/{send_resp.value}")

        # Confirm
        confirmed = await self._await_confirm_transaction(send_resp.value)
        if debug_prints:
            logging.info(f"Success: {confirmed}")
        return (confirmed, str(send_resp.value), pool_type, base_amount_out)

    def _build_old_pumpswap_buy_ix(
        self,
        pool_pubkey: Pubkey,
        user_pubkey: Pubkey,
        global_config: Pubkey,
        base_mint: Pubkey,
        quote_mint: Pubkey,
        user_base_token_ata: Pubkey,
        user_quote_token_ata: Pubkey,
        pool_base_token_account: Pubkey,
        pool_quote_token_account: Pubkey,
        protocol_fee_recipient: Pubkey,
        protocol_fee_recipient_ata: Pubkey,
        base_amount_out: int,
        max_quote_amount_in: int
    ):
        """
          #1 Pool
          #2 User
          #3 Global Config
          #4 Base Mint
          #5 Quote Mint
          #6 User Base ATA
          #7 User Quote ATA
          #8 Pool Base ATA
          #9 Pool Quote ATA
          #10 Protocol Fee Recipient
          #11 Protocol Fee Recipient Token Account
          #12 Base Token Program
          #13 Quote Token Program
          #14 System Program
          #15 Associated Token Program
          #16 Event Authority
          #17 PumpSwap Program
        
          {
            base_amount_out:  u64,
            max_quote_amount_in: u64
          }
        plus an 8-byte Anchor discriminator at the front. 
        """
        from solders.instruction import AccountMeta, Instruction # type: ignore
        from solders.pubkey import Pubkey as SPubkey  # type: ignore
        import struct

        data = BUY_INSTR_DISCRIM + struct.pack("<QQ", base_amount_out, max_quote_amount_in)

        accs = [
            AccountMeta(pubkey=SPubkey.from_string(str(pool_pubkey)),  is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(user_pubkey)),  is_signer=True,  is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(global_config)),is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(base_mint)),    is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(quote_mint)),   is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(user_base_token_ata)),  is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(user_quote_token_ata)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_base_token_account)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_quote_token_account)),is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(protocol_fee_recipient)),   is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(protocol_fee_recipient_ata)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(TOKEN_PROGRAM_PUB)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(TOKEN_PROGRAM_PUB)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(SYSTEM_PROGRAM_ID)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(ASSOCIATED_TOKEN)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(EVENT_AUTHORITY)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(PUMPSWAP_PROGRAM_ID)), is_signer=False, is_writable=False),
        ]

        ix = Instruction(
            program_id=SPubkey.from_string(str(PUMPSWAP_PROGRAM_ID)),
            data=data,
            accounts=accs
        )
        return ix
    
    def _build_new_pumpswap_buy_ix(
        self,
        pool_pubkey: Pubkey,
        user_pubkey: Pubkey,
        global_config: Pubkey,
        base_mint: Pubkey,
        quote_mint: Pubkey,
        user_base_token_ata: Pubkey,
        user_quote_token_ata: Pubkey,
        pool_base_token_account: Pubkey,
        pool_quote_token_account: Pubkey,
        protocol_fee_recipient: Pubkey,
        protocol_fee_recipient_ata: Pubkey,
        base_amount_out: int,
        max_quote_amount_in: int,
        vault_auth: Pubkey,
        vault_ata: Pubkey
    ):
        """
          #1 Pool
          #2 User
          #3 Global Config
          #4 Base Mint
          #5 Quote Mint
          #6 User Base ATA
          #7 User Quote ATA
          #8 Pool Base ATA
          #9 Pool Quote ATA
          #10 Protocol Fee Recipient
          #11 Protocol Fee Recipient Token Account
          #12 Base Token Program
          #13 Quote Token Program
          #14 System Program
          #15 Associated Token Program
          #16 Event Authority
          #17 PumpSwap Program
        
          {
            base_amount_out:  u64,
            max_quote_amount_in: u64
          }
        plus an 8-byte Anchor discriminator at the front. 
        """
        from solders.instruction import AccountMeta, Instruction # type: ignore
        from solders.pubkey import Pubkey as SPubkey  # type: ignore
        import struct

        data = BUY_INSTR_DISCRIM + struct.pack("<QQ", base_amount_out, max_quote_amount_in)

        accs = [
            AccountMeta(pubkey=SPubkey.from_string(str(pool_pubkey)),  is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(user_pubkey)),  is_signer=True,  is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(global_config)),is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(base_mint)),    is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(quote_mint)),   is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(user_base_token_ata)),  is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(user_quote_token_ata)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_base_token_account)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_quote_token_account)),is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(protocol_fee_recipient)),   is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(protocol_fee_recipient_ata)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(TOKEN_PROGRAM_PUB)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(TOKEN_PROGRAM_PUB)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(SYSTEM_PROGRAM_ID)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(ASSOCIATED_TOKEN)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(EVENT_AUTHORITY)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(PUMPSWAP_PROGRAM_ID)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(vault_ata)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(vault_auth)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(GLOBAL_VOLUME_ACCUMULATOR)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(self._derive_uva_pda(user_pubkey))), is_signer=False, is_writable=True),
        ]

        ix = Instruction(
            program_id=SPubkey.from_string(str(PUMPSWAP_PROGRAM_ID)),
            data=data,
            accounts=accs
        )
        return ix

    async def sell(
        self,
        pool_data: dict,
        sell_pct: float,
        keypair: Keypair,
        pool_type: str = NEW_POOL_TYPE,
        slippage_pct: float = 10, 
        fee_sol: float = 0.00001,
        debug_prints: bool = False,
        return_instructions: bool = False,
    ):
        """
            Args:
                pool_data: dict
                sell_pct: float
                pool_type: str
                slippage_pct: float
                fee_sol: float
            Returns:
                tuple: (confirmed: bool, tx_sig: str, pool_type: (str)OLD | (str)NEW, (float)mint_amount_we_sold)
        """
        user_pubkey = keypair.pubkey()
        token_base = pool_data['token_base']
        token_quote = pool_data['token_quote']
        if token_base == WSOL_MINT:
            raise Exceptions.PoolReversed("PumpSwap | Pool is reversed, which means you sell WSOL and get TOKEN")
        
        user_base_balance_f = await self._fetch_user_token_balance(keypair, str(token_base))
        if user_base_balance_f <= 0:
            if debug_prints:
                logging.info("No base token balance, can't sell.")
            return (False, None, pool_type)
        
        to_sell_amount_f = user_base_balance_f * (sell_pct / 100.0)
        if to_sell_amount_f <= 0:
            if debug_prints:
                logging.info("Nothing to sell after applying percentage.")
            return (False, None, pool_type)

        if pool_type == NEW_POOL_TYPE:
            coin_creator  = pool_data["coin_creator"]
            vault_ata, vault_auth = derive_creator_vault(coin_creator, token_quote)

        decimals_base = pool_data['decimals_base']
        base_amount_in = int(to_sell_amount_f * (10 ** decimals_base))
        
        base_balance_tokens = pool_data['base_balance_tokens']
        quote_balance_sol   = pool_data['quote_balance_sol']
        
        price = _get_price(base_balance_tokens, quote_balance_sol)
        raw_sol = to_sell_amount_f * price
        
        min_sol_out = raw_sol * (1 - slippage_pct/100.0)
        min_quote_amount_out = int(min_sol_out * LAMPORTS_PER_SOL)
        if min_quote_amount_out <= 0:
            if debug_prints:
                logging.info("min_quote_amount_out <= 0. Slippage too big or no liquidity.")
            return (False, None, pool_type)
        
        instructions = []
        
        if not return_instructions:
            lamports_fee = int(fee_sol * LAMPORTS_PER_SOL)
            micro_lamports = compute_unit_price_from_total_fee(
                lamports_fee,
                compute_units=UNIT_COMPUTE_BUDGET
            )
        
            instructions.append(set_compute_unit_limit(UNIT_COMPUTE_BUDGET))
            instructions.append(set_compute_unit_price(micro_lamports))
        
        wsol_ata_ix = await self.create_ata_if_needed(user_pubkey, token_quote)
        if wsol_ata_ix:
            instructions.append(wsol_ata_ix)
        
        if pool_type == NEW_POOL_TYPE:
            sell_ix = self._build_new_pumpswap_sell_ix(
                user_pubkey = user_pubkey,
                pool_data = pool_data,
                base_amount_in = base_amount_in,
                min_quote_amount_out = min_quote_amount_out,
                protocol_fee_recipient   = PROTOCOL_FEE_RECIP,
                protocol_fee_recipient_ata = get_associated_token_address(PROTOCOL_FEE_RECIP, token_quote),
                vault_auth = vault_auth,
                vault_ata = vault_ata,
            )
        else:
            sell_ix = self._build_old_pumpswap_sell_ix(
                user_pubkey = user_pubkey,
                pool_data = pool_data,
                base_amount_in = base_amount_in,
                min_quote_amount_out = min_quote_amount_out,
                protocol_fee_recipient   = PROTOCOL_FEE_RECIP,
                protocol_fee_recipient_ata = get_associated_token_address(PROTOCOL_FEE_RECIP, token_quote),
            )
        instructions.append(sell_ix)
        
        wsol_ata = get_associated_token_address(user_pubkey, token_quote)
        close_ix = close_account(
            CloseAccountParams(
                program_id = TOKEN_PROGRAM_PUB,
                account = wsol_ata,
                dest = user_pubkey,
                owner = user_pubkey
            )
        )
        instructions.append(close_ix)
        
        if return_instructions:
            return instructions

        latest_blockhash = await self.async_client.get_latest_blockhash()
        compiled_msg = MessageV0.try_compile(
            payer=user_pubkey,
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=latest_blockhash.value.blockhash
        )
        transaction = VersionedTransaction(compiled_msg, [keypair])
        
        opts = TxOpts(skip_preflight=True, max_retries=0)
        send_resp = await self.async_client.send_transaction(transaction, opts=opts)
        if debug_prints:
            logging.info(f"Transaction sent: https://solscan.io/tx/{send_resp.value}")
        
        confirmed = await self._await_confirm_transaction(send_resp.value)
        if debug_prints:
            logging.info(f"Success: {confirmed}")
        return (confirmed, send_resp.value, pool_type, min_sol_out)

    async def reversed_buy(
        self,
        pool_data: dict,
        sol_amount: float,
        keypair: Keypair,
        pool_type: str = NEW_POOL_TYPE,
        slippage_pct: float = 10,
        fee_sol: float = 0.00001,
        debug_prints: bool = False,
        return_instructions: bool = False,
    ):
        """
            Args:
                pool_data: dict
                sol_amount: float
                pool_type: str
                slippage_pct: float
                fee_sol: float
        """
        user_pubkey = keypair.pubkey()
        base_balance_tokens = pool_data['base_balance_tokens'] # WSOL
        quote_balance_sol   = pool_data['quote_balance_sol'] # TOKEN
        decimals_base       = pool_data['decimals_base'] # WSOL == 9
        decimals_quote      = pool_data['decimals_quote'] # TOKEN == X

        token_base = pool_data['token_base'] # WSOL
        token_quote = pool_data['token_quote'] # TOKEN

        if pool_type == NEW_POOL_TYPE:
            coin_creator  = pool_data["coin_creator"]
            vault_ata, vault_auth = derive_creator_vault(coin_creator, token_quote)

        (base_amount_out, max_quote_amount_in) = convert_sol_to_base_tokens(
            sol_amount, base_balance_tokens, quote_balance_sol,
            decimals_base, decimals_quote, slippage_pct=slippage_pct,
            reversed=True
        )
        logging.info(f"base_amount_out: {base_amount_out} | max_quote_amount_in: {max_quote_amount_in}")
        if base_amount_out <= 0:
            if debug_prints:
                logging.info("base_amount_out <= 0. Slippage too big or no liquidity.")
            return (False, None, pool_type)

        instructions = []
        
        if not return_instructions:
            lamports_fee = int(fee_sol * LAMPORTS_PER_SOL)
            micro_lamports = compute_unit_price_from_total_fee(
                lamports_fee,
                compute_units=UNIT_COMPUTE_BUDGET
            )
        
            instructions.append(set_compute_unit_limit(UNIT_COMPUTE_BUDGET))
            instructions.append(set_compute_unit_price(micro_lamports))
        
        wsol_ata_ix = await self.create_ata_if_needed(user_pubkey, token_base)
        if wsol_ata_ix:
            instructions.append(wsol_ata_ix)

        wsol_ata = get_associated_token_address(user_pubkey, token_base)
        system_transfer_ix = self._build_system_transfer_ix(
            from_pubkey=user_pubkey,
            to_pubkey=wsol_ata,
            lamports=max_quote_amount_in
        )
        instructions.append(system_transfer_ix)

        base_ata_ix = await self.create_ata_if_needed(user_pubkey, token_quote)
        if base_ata_ix:
            instructions.append(base_ata_ix)

        instructions.append(sync_native(SyncNativeParams(program_id=TOKEN_PROGRAM_PUB, account=wsol_ata)))
        
        if pool_type == NEW_POOL_TYPE:
            sell_ix = self._build_new_pumpswap_sell_ix(
                user_pubkey = user_pubkey,
                pool_data = pool_data,
                base_amount_in = max_quote_amount_in,
                min_quote_amount_out = base_amount_out,
                protocol_fee_recipient   = PROTOCOL_FEE_RECIP,
                protocol_fee_recipient_ata = get_associated_token_address(PROTOCOL_FEE_RECIP, token_quote),
                vault_auth = vault_auth,
                vault_ata = vault_ata,
            )
        else:
            sell_ix = self._build_old_pumpswap_sell_ix(
                user_pubkey = user_pubkey,
                pool_data = pool_data,
                base_amount_in = max_quote_amount_in,
                min_quote_amount_out = base_amount_out,
                protocol_fee_recipient   = PROTOCOL_FEE_RECIP,
                protocol_fee_recipient_ata = get_associated_token_address(PROTOCOL_FEE_RECIP, token_quote),
            )
        instructions.append(sell_ix)
        
        close_ix = close_account(
            CloseAccountParams(
                program_id = TOKEN_PROGRAM_PUB,
                account = wsol_ata,
                dest = user_pubkey,
                owner = user_pubkey
            )
        )
        instructions.append(close_ix)
        
        if return_instructions:
            return instructions

        latest_blockhash = await self.async_client.get_latest_blockhash()
        compiled_msg = MessageV0.try_compile(
            payer=user_pubkey,
            instructions=instructions,
            address_lookup_table_accounts=[],
            recent_blockhash=latest_blockhash.value.blockhash
        )
        transaction = VersionedTransaction(compiled_msg, [keypair])
        
        opts = TxOpts(skip_preflight=True, max_retries=0)
        send_resp = await self.async_client.send_transaction(transaction, opts=opts)
        if debug_prints:
            logging.info(f"Transaction sent: https://solscan.io/tx/{send_resp.value}")
        
        confirmed = await self._await_confirm_transaction(send_resp.value)
        if debug_prints:
            logging.info(f"Success: {confirmed}")
        return (confirmed, send_resp.value, pool_type, base_amount_out)


    def _build_new_pumpswap_sell_ix(
        self,
        user_pubkey: Pubkey,
        pool_data: dict,
        base_amount_in: int,
        min_quote_amount_out: int,
        protocol_fee_recipient: Pubkey,
        protocol_fee_recipient_ata: Pubkey,
        vault_auth: Pubkey,
        vault_ata: Pubkey
    ):
        """
        Accounts (17 total):
          #1  Pool
          #2  User
          #3  Global Config
          #4  Base Mint
          #5  Quote Mint
          #6  User Base Token Account
          #7  User Quote Token Account (WSOL ATA)
          #8  Pool Base Token Account
          #9  Pool Quote Token Account
          #10 Protocol Fee Recipient
          #11 Protocol Fee Recipient Token Account
          #12 Base Token Program
          #13 Quote Token Program
          #14 System Program
          #15 Associated Token Program
          #16 Event Authority
          #17 Program

        Data:
          sell_discriminator (8 bytes) + struct.pack("<QQ", base_amount_in, min_quote_amount_out)
        """
        from solders.instruction import AccountMeta, Instruction # type: ignore
        from solders.pubkey import Pubkey as SPubkey # type: ignore
        import struct

        data = SELL_INSTR_DISCRIM + struct.pack("<QQ", base_amount_in, min_quote_amount_out)

        accs = [
            AccountMeta(pubkey=SPubkey.from_string(str(pool_data["pool_pubkey"])),  is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(user_pubkey)),  is_signer=True,  is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(GLOBAL_CONFIG_PUB)),is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_data["token_base"])), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_data["token_quote"])), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(get_associated_token_address(user_pubkey, pool_data["token_base"]))),
                        is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(get_associated_token_address(user_pubkey, pool_data["token_quote"]))),
                        is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_data["pool_base_token_account"])),  is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_data["pool_quote_token_account"])), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(protocol_fee_recipient)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(protocol_fee_recipient_ata)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(TOKEN_PROGRAM_PUB)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(TOKEN_PROGRAM_PUB)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(SYSTEM_PROGRAM_ID)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(ASSOCIATED_TOKEN)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(EVENT_AUTHORITY)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(PUMPSWAP_PROGRAM_ID)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(vault_ata)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(vault_auth)), is_signer=False, is_writable=True),
        ]

        return Instruction(
            program_id=SPubkey.from_string(str(PUMPSWAP_PROGRAM_ID)),
            data=data,
            accounts=accs
        )

    def _build_old_pumpswap_sell_ix(
        self,
        user_pubkey: Pubkey,
        pool_data: dict,
        base_amount_in: int,
        min_quote_amount_out: int,
        protocol_fee_recipient: Pubkey,
        protocol_fee_recipient_ata: Pubkey
    ):
        """
        Accounts (17 total):
          #1  Pool
          #2  User
          #3  Global Config
          #4  Base Mint
          #5  Quote Mint
          #6  User Base Token Account
          #7  User Quote Token Account (WSOL ATA)
          #8  Pool Base Token Account
          #9  Pool Quote Token Account
          #10 Protocol Fee Recipient
          #11 Protocol Fee Recipient Token Account
          #12 Base Token Program
          #13 Quote Token Program
          #14 System Program
          #15 Associated Token Program
          #16 Event Authority
          #17 Program

        Data:
          sell_discriminator (8 bytes) + struct.pack("<QQ", base_amount_in, min_quote_amount_out)
        """
        from solders.instruction import AccountMeta, Instruction # type: ignore
        from solders.pubkey import Pubkey as SPubkey # type: ignore
        import struct

        data = SELL_INSTR_DISCRIM + struct.pack("<QQ", base_amount_in, min_quote_amount_out)

        accs = [
            AccountMeta(pubkey=SPubkey.from_string(str(pool_data["pool_pubkey"])),  is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(user_pubkey)),  is_signer=True,  is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(GLOBAL_CONFIG_PUB)),is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_data["token_base"])), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_data["token_quote"])), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(get_associated_token_address(user_pubkey, pool_data["token_base"]))),
                        is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(get_associated_token_address(user_pubkey, pool_data["token_quote"]))),
                        is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_data["pool_base_token_account"])),  is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(pool_data["pool_quote_token_account"])), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(protocol_fee_recipient)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(protocol_fee_recipient_ata)), is_signer=False, is_writable=True),
            AccountMeta(pubkey=SPubkey.from_string(str(TOKEN_PROGRAM_PUB)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(TOKEN_PROGRAM_PUB)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(SYSTEM_PROGRAM_ID)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(ASSOCIATED_TOKEN)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(EVENT_AUTHORITY)), is_signer=False, is_writable=False),
            AccountMeta(pubkey=SPubkey.from_string(str(PUMPSWAP_PROGRAM_ID)), is_signer=False, is_writable=False),
        ]

        return Instruction(
            program_id=SPubkey.from_string(str(PUMPSWAP_PROGRAM_ID)),
            data=data,
            accounts=accs
        )

    async def _fetch_user_token_balance(self, keypair: Keypair, mint_pubkey_str: str) -> Optional[float]:
        response = await self.async_client.get_token_accounts_by_owner_json_parsed(
            keypair.pubkey(),
            TokenAccountOpts(mint=Pubkey.from_string(mint_pubkey_str)),
            commitment=Processed
        )
        if response.value:
            accounts = response.value
            if accounts:
                balance = accounts[0].account.data.parsed['info']['tokenAmount']['uiAmount']
                if balance is not None:
                    return float(balance)
        return None

    async def _await_confirm_transaction(self, tx_sig: str, max_attempts=20, delay=2.0):
        """
        Simple helper to poll getTransaction until we get a success/fail.
        """
        for i in range(max_attempts):
            resp = await self.async_client.get_transaction(tx_sig, commitment=Confirmed, max_supported_transaction_version=0)
            if resp.value:
                maybe_err = resp.value.transaction.meta.err
                if maybe_err is None:
                    return True
                else:
                    return False
            await asyncio.sleep(delay)
        return False
    
    def _build_pumpswap_create_pool_ix(
        self,
        *,
        pool_pda: Pubkey,
        creator: Pubkey,
        base_mint: Pubkey,
        quote_mint: Pubkey,
        lp_mint_pda: Pubkey,
        user_base_ata: Pubkey,
        user_quote_ata: Pubkey,
        user_lp_ata: Pubkey,
        pool_base_ata: Pubkey,
        pool_quote_ata: Pubkey,
        index: int,
        base_amount_in: int,
        quote_amount_in: int,
    ):
        from solders.instruction import AccountMeta, Instruction # type: ignore
        import struct

        data = CREATE_POOL_DISCRIM + struct.pack(
            "<HQQ", index, base_amount_in, quote_amount_in
        )

        am = AccountMeta
        accs = [
            am(pool_pda,               False, True),
            am(GLOBAL_CONFIG_PUB,      False, False),
            am(creator,                True,  True),
            am(base_mint,              False, False),
            am(quote_mint,             False, False),
            am(lp_mint_pda,            False, True),
            am(user_base_ata,          False, True),
            am(user_quote_ata,         False, True),
            am(user_lp_ata,            False, True),
            am(pool_base_ata,          False, True),
            am(pool_quote_ata,         False, True),
            am(SYSTEM_PROGRAM_ID,      False, False),
            am(TOKEN_2022_PROGRAM_PUB, False, False),
            am(TOKEN_PROGRAM_PUB,      False, False),  # base_token_program
            am(TOKEN_PROGRAM_PUB,      False, False),  # quote_token_program
            am(ASSOCIATED_TOKEN,       False, False),
            am(EVENT_AUTHORITY,        False, False),
            am(PUMPSWAP_PROGRAM_ID,    False, False),
        ]

        return Instruction(
            program_id=PUMPSWAP_PROGRAM_ID,
            accounts=accs,
            data=data,
        )

    async def create_pool(
        self,
        base_mint: Pubkey,
        base_amount_tokens: float,  # e.g. 2e8 == 200 000 000
        quote_amount_sol: float,    # e.g. 15  (WSOL to deposit)
        keypair: Keypair,
        decimals_base: int = 6,
        index: int = 0,
        fee_sol: float = 0.0005,
        debug_prints: bool = False,
    ) -> bool:
        """
        Initialise a brand‑new PumpSwap pool (a.k.a. “Add Liquidity” on pump.fun).
        the calling wallet becomes the creator & initial LP holder

        Returns:
            str: Pool PDA if successful, None otherwise
        """
        user = keypair.pubkey()
        quote_mint = WSOL_MINT

        base_amount_in  = int(base_amount_tokens * 10 ** decimals_base)
        quote_amount_in = int(quote_amount_sol * LAMPORTS_PER_SOL)

        pool_seed_prefix = b"pool"
        pool_pda, _ = Pubkey.find_program_address(
            [
                pool_seed_prefix,
                index.to_bytes(2, "little"),
                bytes(user),
                bytes(base_mint),
                bytes(quote_mint),
            ],
            PUMPSWAP_PROGRAM_ID,
        )
        lp_mint_pda, _ = Pubkey.find_program_address(
            [b"pool_lp_mint", bytes(pool_pda)],
            PUMPSWAP_PROGRAM_ID,
        )

        pool_base_ata  = get_associated_token_address(pool_pda,  base_mint)
        pool_quote_ata = get_associated_token_address(pool_pda,  quote_mint)
        user_base_ata  = get_associated_token_address(user,      base_mint)
        user_quote_ata = get_associated_token_address(user,      quote_mint)
        user_lp_ata    = get_associated_token_address(
            user, lp_mint_pda, token_program_id=TOKEN_2022_PROGRAM_PUB
        )

        lamports_fee     = int(fee_sol * LAMPORTS_PER_SOL)
        micro_lamports   = compute_unit_price_from_total_fee(
            lamports_fee, POOL_COMPUTE_BUDGET
        )

        ix: list = [
            set_compute_unit_limit(POOL_COMPUTE_BUDGET),
            set_compute_unit_price(micro_lamports),
        ]

        maybe_create_wsol = await self.create_ata_if_needed(user, quote_mint)
        if maybe_create_wsol:
            ix.append(maybe_create_wsol)

        ix.append(
            self._build_system_transfer_ix(
                from_pubkey=user, to_pubkey=user_quote_ata, lamports=quote_amount_in
            )
        )
        ix.append(
            sync_native(
                SyncNativeParams(
                    program_id=TOKEN_PROGRAM_PUB,
                    account=user_quote_ata,
                )
            )
        )

        for mint, ata in (
            (base_mint, pool_base_ata),
            (quote_mint, pool_quote_ata),
        ):
            maybe_ix = await self._create_ata_if_needed_for_owner(
                payer=user, owner=pool_pda, mint=mint
            )
            if maybe_ix:
                ix.append(maybe_ix)

        ix.append(
            self._build_pumpswap_create_pool_ix(
                pool_pda=pool_pda,
                creator=user,
                base_mint=base_mint,
                quote_mint=quote_mint,
                lp_mint_pda=lp_mint_pda,
                user_base_ata=user_base_ata,
                user_quote_ata=user_quote_ata,
                user_lp_ata=user_lp_ata,
                pool_base_ata=pool_base_ata,
                pool_quote_ata=pool_quote_ata,
                index=index,
                base_amount_in=base_amount_in,
                quote_amount_in=quote_amount_in,
            )
        )

        ix.append(
            close_account(
                CloseAccountParams(
                    program_id=TOKEN_PROGRAM_PUB,
                    account=user_quote_ata,
                    dest=user,
                    owner=user,
                )
            )
        )

        bh = await self.async_client.get_latest_blockhash()
        msg = MessageV0.try_compile(
            payer=user,
            instructions=ix,
            address_lookup_table_accounts=[],
            recent_blockhash=bh.value.blockhash,
        )
        tx = VersionedTransaction(msg, [keypair])
        ok_sim = await self._simulate_and_show(tx, debug_prints)
        if not ok_sim:
            return False   # bail early – no fee wasted
        sig = (await self.async_client.send_transaction(
            tx, opts=TxOpts(skip_preflight=True, max_retries=0)
        )).value

        if debug_prints:
            logging.info(f"Tx submitted: https://solscan.io/tx/{sig}")

        ok = await self._await_confirm_transaction(sig)

        if debug_prints:
            logging.info(f"Success: {ok}")

        return str(pool_pda) if ok else None
    
    def _build_pumpswap_withdraw_ix(
        self,
        *,
        pool_pubkey: Pubkey,
        user_pubkey: Pubkey,
        base_mint: Pubkey,
        quote_mint: Pubkey,
        lp_mint: Pubkey,
        user_base_ata: Pubkey,
        user_quote_ata: Pubkey,
        user_lp_ata: Pubkey,
        pool_base_ata: Pubkey,
        pool_quote_ata: Pubkey,
        lp_token_amount_in: int,
        min_base_amount_out: int,
        min_quote_amount_out: int,
    ):
        from solders.instruction import AccountMeta, Instruction # type: ignore
        import struct

        data = WITHDRAW_INSTR_DISCRIM + struct.pack(
            "<QQQ",
            lp_token_amount_in,
            min_base_amount_out,
            min_quote_amount_out,
        )

        am = AccountMeta
        accs = [
            am(pool_pubkey,            False, True),
            am(GLOBAL_CONFIG_PUB,      False, False),
            am(user_pubkey,            True,  True),
            am(base_mint,              False, False),
            am(quote_mint,             False, False),
            am(lp_mint,                False, True),
            am(user_base_ata,          False, True),
            am(user_quote_ata,         False, True),
            am(user_lp_ata,            False, True),
            am(pool_base_ata,          False, True),
            am(pool_quote_ata,         False, True),
            am(TOKEN_PROGRAM_PUB,      False, False),
            am(TOKEN_2022_PROGRAM_PUB, False, False),
            am(EVENT_AUTHORITY,        False, False),
            am(PUMPSWAP_PROGRAM_ID,    False, False),
        ]

        return Instruction(
            program_id=PUMPSWAP_PROGRAM_ID, data=data, accounts=accs
        )
    
    async def withdraw(
        self,
        pool_data: dict,
        withdraw_pct: float,          # 100 = max
        fee_sol: float = 0.0003,
        debug_prints: bool = False,
        keypair: Keypair = None,
    ):
        """
            Withdraw deposited liquidity from a PumpSwap pool (creating a pool counts as deposit).
        """
        user         = keypair.pubkey()
        lp_mint      = Pubkey.from_string(pool_data["lp_mint"])
        base_mint    = pool_data["token_base"]
        quote_mint   = pool_data["token_quote"]

        lp_balance_f = await self._fetch_user_token_balance(str(lp_mint))
        if not lp_balance_f or lp_balance_f == 0:
            if debug_prints:
                logging.info("No LP tokens, nothing to withdraw")
            return False

        lp_in_f      = lp_balance_f * withdraw_pct / 100.0
        lp_amount_in = int(lp_in_f * 10**9)            # lp-mint is 9-dec

        # (0 → skip slippage checks)
        min_base_out  = 0
        min_quote_out = 0

        lamports_fee = int(fee_sol * LAMPORTS_PER_SOL)
        micro_lamports = compute_unit_price_from_total_fee(
            lamports_fee, UNIT_COMPUTE_BUDGET
        )

        ix: list = [
            set_compute_unit_limit(UNIT_COMPUTE_BUDGET),
            set_compute_unit_price(micro_lamports),
        ]

        wsol_create = await self.create_ata_if_needed(user, quote_mint)
        if wsol_create:
            ix.append(wsol_create)
        user_quote_ata = get_associated_token_address(user, quote_mint)

        ix.append(
            self._build_pumpswap_withdraw_ix(
                pool_pubkey             = pool_data["pool_pubkey"],
                user_pubkey             = user,
                base_mint               = base_mint,
                quote_mint              = quote_mint,
                lp_mint                 = Pubkey.from_string(pool_data["lp_mint"]),
                user_base_ata           = get_associated_token_address(user, base_mint),
                user_quote_ata          = user_quote_ata,
                user_lp_ata             = get_associated_token_address(user, lp_mint, token_program_id=TOKEN_2022_PROGRAM_PUB),
                pool_base_ata           = Pubkey.from_string(pool_data["pool_base_token_account"]),
                pool_quote_ata          = Pubkey.from_string(pool_data["pool_quote_token_account"]),
                lp_token_amount_in      = lp_amount_in,
                min_base_amount_out     = min_base_out,
                min_quote_amount_out    = min_quote_out,
            )
        )

        ix.append(
            close_account(
                CloseAccountParams(
                    program_id = TOKEN_PROGRAM_PUB,
                    account    = user_quote_ata,
                    dest       = user,
                    owner      = user,
                )
            )
        )

        blockhash  = (await self.async_client.get_latest_blockhash()).value.blockhash
        msg        = MessageV0.try_compile(
            payer=user, instructions=ix, address_lookup_table_accounts=[],
            recent_blockhash=blockhash,
        )
        tx         = VersionedTransaction(msg, [keypair])
        if not await self._simulate_and_show(tx, debug_prints): return False

        sig = (await self.async_client.send_transaction(
            tx, opts=TxOpts(skip_preflight=True, max_retries=0)
        )).value

        if debug_prints:
            logging.info(f"Tx: {sig}")

        ok  = await self._await_confirm_transaction(sig)

        if debug_prints:
            logging.info(f"Success: {ok}")

        return ok

    def _build_pumpswap_deposit_ix(
        self,
        *,
        pool_pubkey: Pubkey,
        user_pubkey: Pubkey,
        base_mint: Pubkey,
        quote_mint: Pubkey,
        lp_mint: Pubkey,
        user_base_ata: Pubkey,
        user_quote_ata: Pubkey,
        user_lp_ata: Pubkey,
        pool_base_ata: Pubkey,
        pool_quote_ata: Pubkey,
        lp_token_amount_out: int,
        max_base_amount_in: int,
        max_quote_amount_in: int,
    ):
        from solders.instruction import AccountMeta, Instruction # type: ignore
        import struct

        data = DEPOSIT_INSTR_DISCRIM + struct.pack(
            "<QQQ",
            lp_token_amount_out,
            max_base_amount_in,
            max_quote_amount_in,
        )

        am = AccountMeta
        accs = [
            am(pool_pubkey,            False, True),
            am(GLOBAL_CONFIG_PUB,      False, False),
            am(user_pubkey,            True,  True),
            am(base_mint,              False, False),
            am(quote_mint,             False, False),
            am(lp_mint,                False, True),
            am(user_base_ata,          False, True),
            am(user_quote_ata,         False, True),
            am(user_lp_ata,            False, True),
            am(pool_base_ata,          False, True),
            am(pool_quote_ata,         False, True),
            am(TOKEN_PROGRAM_PUB,      False, False),
            am(TOKEN_2022_PROGRAM_PUB, False, False),
            am(EVENT_AUTHORITY,        False, False),
            am(PUMPSWAP_PROGRAM_ID,    False, False),
        ]

        return Instruction(
            program_id=PUMPSWAP_PROGRAM_ID, data=data, accounts=accs
        )
    
    async def deposit(
        self,
        pool_data         : dict,
        base_amount_tokens: float,     # UI amount of base-tokens you want to add
        keypair: Keypair,
        slippage_pct      : float = 1.0,
        fee_sol           : float = 0.0003,
        sol_cap           : float | None = None,
        debug_prints      : bool = False,
    ):
        """
            Deposit tokens into a PumpSwap pool.
        """
        user        = keypair.pubkey()
        base_mint   = pool_data["token_base"]
        quote_mint  = pool_data["token_quote"]
        lp_mint     = Pubkey.from_string(pool_data["lp_mint"])
        dec_base    = pool_data["decimals_base"]

        base_in_raw = int(base_amount_tokens * 10**dec_base)

        base_res_raw  = int((await self.async_client.get_token_account_balance(
                            Pubkey.from_string(pool_data["pool_base_token_account"])
                            )).value.amount)
        quote_res_raw = int((await self.async_client.get_token_account_balance(
                            Pubkey.from_string(pool_data["pool_quote_token_account"])
                            )).value.amount)
        if base_res_raw == 0 or quote_res_raw == 0:
            if debug_prints:
                logging.info("Pool reserves are zero – can’t deposit proportionally.")
            return False

        quote_needed_lamports = base_in_raw * quote_res_raw // base_res_raw

        if sol_cap is not None:
            cap_lamports = int(sol_cap * LAMPORTS_PER_SOL)
            if quote_needed_lamports > cap_lamports:
                if debug_prints:
                    logging.info(
                    f"Deposit aborted: would need {quote_needed_lamports/1e9:.6f} SOL "
                    f"but cap is {sol_cap:.6f} SOL."
                    )
                return False

        max_base_in  = int(base_in_raw  * (1 + slippage_pct / 100))
        max_quote_in = int(quote_needed_lamports * (1 + slippage_pct / 100))

        lp_supply_raw = max(
            int((await self.async_client.get_token_supply(lp_mint)).value.amount) - 100,
            1,
        )
        lp_est_raw = base_in_raw * lp_supply_raw // base_res_raw
        min_lp_out = max(int(lp_est_raw * (1 - slippage_pct / 100)), 1)

        ui_bal_resp = await self.async_client.get_token_accounts_by_owner_json_parsed(
            user, TokenAccountOpts(mint=base_mint), commitment=Processed
        )
        have_base_raw = int(
            ui_bal_resp.value[0].account.data.parsed["info"]["tokenAmount"]["amount"]
        ) if ui_bal_resp.value else 0
        if have_base_raw < base_in_raw:
            if debug_prints:
                logging.info("Not enough base tokens in wallet.")
            return False
        # SOL balance
        sol_balance = (await self.async_client.get_balance(user)).value
        if sol_balance < quote_needed_lamports + int(0.002 * LAMPORTS_PER_SOL):
            if debug_prints:
                logging.info("Not enough SOL to wrap.")
            return False

        ix = [
            set_compute_unit_limit(UNIT_COMPUTE_BUDGET),
            set_compute_unit_price(
                compute_unit_price_from_total_fee(
                    int(fee_sol * LAMPORTS_PER_SOL), UNIT_COMPUTE_BUDGET
                )
            ),
        ]

        if (wsol_ix := await self.create_ata_if_needed(user, quote_mint)):
            ix.append(wsol_ix)
        if (base_ix := await self.create_ata_if_needed(user, base_mint)):
            ix.append(base_ix)

        user_base_ata  = get_associated_token_address(user, base_mint)
        user_quote_ata = get_associated_token_address(user, quote_mint)

        ix += [
            self._build_system_transfer_ix(user, user_quote_ata, quote_needed_lamports),
            sync_native(SyncNativeParams(program_id=TOKEN_PROGRAM_PUB,
                                         account=user_quote_ata)),
        ]

        ix.append(
            self._build_pumpswap_deposit_ix(
                pool_pubkey          = pool_data["pool_pubkey"],
                user_pubkey          = user,
                base_mint            = base_mint,
                quote_mint           = quote_mint,
                lp_mint              = lp_mint,
                user_base_ata        = user_base_ata,
                user_quote_ata       = user_quote_ata,
                user_lp_ata          = get_associated_token_address(
                                           user, lp_mint,
                                           token_program_id=TOKEN_2022_PROGRAM_PUB),
                pool_base_ata        = Pubkey.from_string(pool_data["pool_base_token_account"]),
                pool_quote_ata       = Pubkey.from_string(pool_data["pool_quote_token_account"]),
                lp_token_amount_out  = min_lp_out,
                max_base_amount_in   = max_base_in,
                max_quote_amount_in  = max_quote_in,
            )
        )

        ix.append(
            close_account(
                CloseAccountParams(program_id=TOKEN_PROGRAM_PUB,
                                   account=user_quote_ata,
                                   dest=user,
                                   owner=user))
        )

        bh  = (await self.async_client.get_latest_blockhash()).value.blockhash
        msg = MessageV0.try_compile(payer=user, instructions=ix,
                                    address_lookup_table_accounts=[],
                                    recent_blockhash=bh)
        tx  = VersionedTransaction(msg, [keypair])

        if not await self._simulate_and_show(tx, debug_prints):
            return False
        sig = (await self.async_client.send_transaction(
            tx, opts=TxOpts(skip_preflight=True, max_retries=0)
        )).value
        if debug_prints:
            logging.info(f"Tx: {sig}")
        ok  = await self._await_confirm_transaction(sig)
        if debug_prints:
            logging.info(f"Success: {ok}")
        return ok

    @staticmethod
    def derive_pool_address(creator: Pubkey, base_mint: Pubkey,
                            quote_mint: Pubkey, index: int = 0) -> Pubkey:
        seed = [
            b"pool",
            index.to_bytes(2, "little"),
            bytes(creator),
            bytes(base_mint),
            bytes(quote_mint),
        ]
        return Pubkey.find_program_address(seed, PUMPSWAP_PROGRAM_ID)[0]

    async def _simulate_and_show(self, tx: VersionedTransaction, debug_prints: bool = False):
        sim = await self.async_client.simulate_transaction(
            tx, sig_verify=False, commitment=Processed,

        )
        if debug_prints:
            if sim.value.err:
                logging.info("── Simulation failed ──────────────────────────────────────────")
            else:
                logging.info("── Simulation succeeded ────────────────────────────────────────")
            for l in sim.value.logs:
                logging.info(l)
            logging.info("────────────────────────────────────────────────────────────────")
        return sim.value.err is None