import json
import time
import hmac
import hashlib
import binascii
import requests
from typing import List, Optional

class CCPayments:
    BASE_URL = "https://ccpayment.com/ccpayment/v2"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret

    def _create_signature(self, timestamp: str, payload: str = "") -> str:
        if payload:
            sign_text = f"{self.app_id}{timestamp}{payload}"
        else:
            sign_text = f"{self.app_id}{timestamp}"
        
        h = hmac.new(self.app_secret.encode('utf-8'), sign_text.encode('utf-8'), hashlib.sha256)
        return binascii.hexlify(h.digest()).decode('utf-8')

    def resend_webhooks(
        self,
        start_timestamp: int,
        end_timestamp: Optional[int] = None,
        record_ids: Optional[List[str]] = None,
        webhook_result: Optional[str] = None,
        transaction_type: Optional[str] = None,
    ):
        """
        Resend webhooks for transactions within a specified time period.

        :param start_timestamp: Resend webhooks for all transactions created after this start time.
        :param end_timestamp: Resend webhooks for all transactions created before this start time.
        :param record_ids: Specify the record IDs to resend the webhook.
        :param webhook_result: 'Failed' or 'AllResult'.
        :param transaction_type: 'AllType', 'ApiDeposit', 'DirectDeposit', 'ApiWithdrawal', 'UserDeposit', 'UserWithdrawal'.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/webhook/resend"
        timestamp = str(int(time.time()))
        
        content = {"startTimestamp": start_timestamp}
        if end_timestamp:
            content["endTimestamp"] = end_timestamp
        if record_ids:
            content["recordIds"] = record_ids
        if webhook_result:
            content["webhookResult"] = webhook_result
        if transaction_type:
            content["transactionType"] = transaction_type
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_cwallet_user_info(self, cwallet_user_id: str):
        """
        Get Cwallet user information.

        :param cwallet_user_id: Cwallet user ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getCwalletUserId"
        timestamp = str(int(time.time()))
        
        content = {"cwalletUserId": cwallet_user_id}
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def check_withdrawal_address_validity(self, chain: str, address: str):
        """
        Check if a withdrawal address is valid.

        :param chain: Symbol of the network.
        :param address: Receiving address of withdrawal.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/checkWithdrawalAddressValidity"
        timestamp = str(int(time.time()))
        
        content = {
            "chain": chain,
            "address": address,
        }
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_withdrawal_network_fee(self, coin_id: int, chain: str):
        """
        Get withdrawal network fee for a given token.

        :param coin_id: Coin ID.
        :param chain: Symbol of the chain.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getWithdrawFee"
        timestamp = str(int(time.time()))
        
        content = {
            "coinId": coin_id,
            "chain": chain,
        }
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_fiat_list(self):
        """
        Get the list of fiat information.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getFiatList"
        timestamp = str(int(time.time()))
        
        body = ""
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_swap_coin_list(self):
        """
        Get the list of all coins available for swap.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getSwapCoinList"
        timestamp = str(int(time.time()))
        
        body = ""
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_chain_list(self, chains: Optional[List[str]] = None):
        """
        Get the current network statuses for all supported chains.

        :param chains: List of chain symbols.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getChainList"
        timestamp = str(int(time.time()))
        
        content = {}
        if chains:
            content["chains"] = chains
            
        body = json.dumps(content) if content else ""
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_balance_list(self):
        """
        Get all balance in the merchant account.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getAppCoinAssetList"
        timestamp = str(int(time.time()))
        
        body = ""
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_coin_balance(self, coin_id: int):
        """
        Get the balance of one provided coin.

        :param coin_id: Coin ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getAppCoinAsset"
        timestamp = str(int(time.time()))
        
        content = {"coinId": coin_id}
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def rescan_lost_transaction(self, chain: str, to_address: str, tx_id: str, memo: Optional[str] = None):
        """
        Trigger a rescan for a deposit transaction.

        :param chain: Chain symbol.
        :param to_address: Receiving address of deposit.
        :param tx_id: TXID.
        :param memo: Memo for memo-required coins.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/rescanLostTransaction"
        timestamp = str(int(time.time()))
        
        content = {
            "chain": chain,
            "toAddress": to_address,
            "txId": tx_id,
        }
        if memo:
            content["memo"] = memo
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_token_list(self):
        """
        Get all details of tokens you've enabled for your business.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getCoinList"
        timestamp = str(int(time.time()))
        
        body = ""
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_token_info(self, coin_id: int):
        """
        Get the detailed information of one specific token.

        :param coin_id: Coin ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getCoin"
        timestamp = str(int(time.time()))
        
        content = {"coinId": coin_id}
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_token_price(self, coin_ids: List[int]):
        """
        Get the equivalent USDT value of coins.

        :param coin_ids: Array of coin IDs.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getCoinUSDTPrice"
        timestamp = str(int(time.time()))
        
        content = {"coinIds": coin_ids}
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def create_internal_transaction(
        self,
        from_user_id: str,
        to_user_id: str,
        coin_id: int,
        amount: str,
        order_id: str,
        remark: Optional[str] = None,
    ):
        """
        Create an internal transaction between users.

        :param from_user_id: From User ID.
        :param to_user_id: To User ID.
        :param coin_id: Coin ID.
        :param amount: Withdrawal amount.
        :param order_id: Withdrawal order ID.
        :param remark: Transaction note.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/userTransfer"
        timestamp = str(int(time.time()))

        content = {
            "fromUserId": from_user_id,
            "toUserId": to_user_id,
            "coinId": coin_id,
            "amount": amount,
            "orderId": order_id,
        }
        if remark:
            content["remark"] = remark

        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_user_internal_transaction_record(
        self, record_id: Optional[str] = None, order_id: Optional[str] = None
    ):
        """
        Get the user's internal transaction record.

        :param record_id: CCPayment unique ID for a transaction.
        :param order_id: Withdrawal order ID.
        :return: The JSON response from the API.
        """
        if not record_id and not order_id:
            raise ValueError("Either record_id or order_id must be provided.")

        url = f"{self.BASE_URL}/getUserTransferRecord"
        timestamp = str(int(time.time()))
        
        content = {}
        if record_id:
            content["recordId"] = record_id
        if order_id:
            content["orderId"] = order_id
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_user_internal_transaction_record_list(
        self,
        from_user_id: str,
        to_user_id: Optional[str] = None,
        coin_id: Optional[int] = None,
        start_at: Optional[int] = None,
        end_at: Optional[int] = None,
        next_id: Optional[str] = None,
    ):
        """
        Get the user's internal transaction record list.

        :param from_user_id: From User ID.
        :param to_user_id: To User ID.
        :param coin_id: Coin ID.
        :param start_at: Retrieve all transaction records starting from the specified startAt timestamp.
        :param end_at: Retrieve all transaction records up to the specified endAt timestamp.
        :param next_id: Next ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getUserTransferRecordList"
        timestamp = str(int(time.time()))
        
        content = {"fromUserId": from_user_id}
        if to_user_id:
            content["toUserId"] = to_user_id
        if coin_id:
            content["coinId"] = coin_id
        if start_at:
            content["startAt"] = start_at
        if end_at:
            content["endAt"] = end_at
        if next_id:
            content["nextId"] = next_id
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def user_withdraw_to_network(
        self,
        user_id: str,
        coin_id: int,
        chain: str,
        address: str,
        order_id: str,
        amount: str,
        memo: Optional[str] = None,
    ):
        """
        Create a user withdrawal order to a blockchain address.

        :param user_id: User ID.
        :param coin_id: Coin ID.
        :param chain: Symbol of the chain.
        :param address: Withdrawal destination address.
        :param order_id: Withdrawal order ID.
        :param amount: Withdrawal amount.
        :param memo: Memo of the withdrawal address.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/applyUserWithdrawToNetwork"
        timestamp = str(int(time.time()))

        content = {
            "userId": user_id,
            "coinId": coin_id,
            "chain": chain,
            "address": address,
            "orderId": order_id,
            "amount": amount,
        }
        if memo:
            content["memo"] = memo

        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def user_withdraw_to_cwallet(
        self,
        user_id: str,
        coin_id: int,
        cwallet_user: str,
        order_id: str,
        amount: str,
    ):
        """
        Create a user withdrawal order to a Cwallet account.

        :param user_id: User ID.
        :param coin_id: Coin ID.
        :param cwallet_user: Cwallet user ID or email.
        :param order_id: Withdrawal order ID.
        :param amount: Withdrawal amount.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/applyUserWithdrawToCwallet"
        timestamp = str(int(time.time()))

        content = {
            "userId": user_id,
            "coinId": coin_id,
            "cwalletUser": cwallet_user,
            "orderId": order_id,
            "amount": amount,
        }
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_user_withdrawal_record(self, record_id: Optional[str] = None, order_id: Optional[str] = None):
        """
        Get the detailed information of a specific user withdrawal record ID.

        :param record_id: CCPayment unique ID for a transaction.
        :param order_id: The order ID of the withdrawal.
        :return: The JSON response from the API.
        """
        if not record_id and not order_id:
            raise ValueError("Either record_id or order_id must be provided.")

        url = f"{self.BASE_URL}/getUserWithdrawRecord"
        timestamp = str(int(time.time()))
        
        content = {}
        if record_id:
            content["recordId"] = record_id
        if order_id:
            content["orderId"] = order_id
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_user_withdrawal_record_list(
        self,
        user_id: str,
        coin_id: Optional[int] = None,
        to_address: Optional[str] = None,
        chain: Optional[str] = None,
        start_at: Optional[int] = None,
        end_at: Optional[int] = None,
        next_id: Optional[str] = None,
    ):
        """
        Get a list of user withdrawal records.

        :param user_id: User ID.
        :param coin_id: Coin ID.
        :param to_address: Destination address.
        :param chain: Symbol of the chain.
        :param start_at: Retrieve all transaction records starting from the specified startAt timestamp.
        :param end_at: Retrieve all transaction records up to the specified endAt timestamp.
        :param next_id: Next ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getUserWithdrawRecordList"
        timestamp = str(int(time.time()))
        
        content = {"userId": user_id}
        if coin_id:
            content["coinId"] = coin_id
        if to_address:
            content["toAddress"] = to_address
        if chain:
            content["chain"] = chain
        if start_at:
            content["startAt"] = start_at
        if end_at:
            content["endAt"] = end_at
        if next_id:
            content["nextId"] = next_id
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_user_deposit_record(self, record_id: str):
        """
        Get the detailed information of a specific user deposit record ID.

        :param record_id: CCPayment unique ID for a transaction.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getUserDepositRecord"
        timestamp = str(int(time.time()))
        
        content = {"recordId": record_id}
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_user_deposit_record_list(
        self,
        user_id: str,
        coin_id: Optional[int] = None,
        chain: Optional[str] = None,
        start_at: Optional[int] = None,
        end_at: Optional[int] = None,
        next_id: Optional[str] = None,
    ):
        """
        Get a list of user deposits records within a specific time range.

        :param user_id: User ID.
        :param coin_id: Coin ID.
        :param chain: Symbol of the chain.
        :param start_at: Retrieve all transaction records starting from the specified startAt timestamp.
        :param end_at: Retrieve all transaction records up to the specified endAt timestamp.
        :param next_id: Next ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getUserDepositRecordList"
        timestamp = str(int(time.time()))
        
        content = {"userId": user_id}
        if coin_id:
            content["coinId"] = coin_id
        if chain:
            content["chain"] = chain
        if start_at:
            content["startAt"] = start_at
        if end_at:
            content["endAt"] = end_at
        if next_id:
            content["nextId"] = next_id
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_or_create_user_deposit_address(self, user_id: str, chain: str):
        """
        Create or get the permanent deposit address of the user.

        :param user_id: User ID.
        :param chain: Symbol of the chain.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getOrCreateUserDepositAddress"
        timestamp = str(int(time.time()))
        
        content = {
            "userId": user_id,
            "chain": chain,
        }
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_user_asset_list(self, user_id: str):
        """
        Get the balance list of a user.

        :param user_id: User ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getUserCoinAssetList"
        timestamp = str(int(time.time()))
        
        content = {"userId": user_id}
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_user_coin_asset(self, user_id: str, coin_id: int):
        """
        Get specific coin balance of a user.

        :param user_id: User ID.
        :param coin_id: Coin ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getUserCoinAsset"
        timestamp = str(int(time.time()))
        
        content = {
            "userId": user_id,
            "coinId": coin_id,
        }
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_swap_quote(self, coin_id_in: int, amount_in: str, coin_id_out: int, extra_fee_rate: Optional[str] = None):
        """
        Get a swap quote.

        :param coin_id_in: ID of the input coin.
        :param amount_in: Amount of input coin.
        :param coin_id_out: ID of the output coin.
        :param extra_fee_rate: Percentage rate you want to charge for this transaction as your service fee.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/estimate"
        timestamp = str(int(time.time()))
        
        content = {
            "coinIdIn": coin_id_in,
            "amountIn": amount_in,
            "coinIdOut": coin_id_out,
        }
        if extra_fee_rate:
            content["extraFeeRate"] = extra_fee_rate
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def user_create_swap(
        self,
        order_id: str,
        user_id: str,
        coin_id_in: int,
        amount_in: str,
        coin_id_out: int,
        extra_fee_rate: Optional[str] = None,
        amount_out_minimum: Optional[str] = None,
    ):
        """
        Create and fulfill a user swap order.

        :param order_id: Swap order ID.
        :param user_id: User ID.
        :param coin_id_in: ID of the input coin.
        :param amount_in: Amount of input coin.
        :param coin_id_out: ID of the output coin.
        :param extra_fee_rate: Percentage rate you want to charge for this transaction as your service fee.
        :param amount_out_minimum: The minimum amount of the output coin.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/userSwap"
        timestamp = str(int(time.time()))
        
        content = {
            "orderId": order_id,
            "userId": user_id,
            "coinIdIn": coin_id_in,
            "amountIn": amount_in,
            "coinIdOut": coin_id_out,
        }
        if extra_fee_rate:
            content["extraFeeRate"] = extra_fee_rate
        if amount_out_minimum:
            content["amountOutMinimum"] = amount_out_minimum
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_user_swap_record(self, record_id: Optional[str] = None, order_id: Optional[str] = None):
        """
        Get the details of a specific user swap order.

        :param record_id: CCPayment unique ID for a transaction.
        :param order_id: Swap order ID.
        :return: The JSON response from the API.
        """
        if not record_id and not order_id:
            raise ValueError("Either record_id or order_id must be provided.")

        url = f"{self.BASE_URL}/getUserSwapRecord"
        timestamp = str(int(time.time()))
        
        content = {}
        if record_id:
            content["recordId"] = record_id
        if order_id:
            content["orderId"] = order_id
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_user_swap_record_list(
        self,
        record_ids: Optional[List[str]] = None,
        order_ids: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        coin_id_in: Optional[int] = None,
        coin_id_out: Optional[int] = None,
        start_at: Optional[int] = None,
        end_at: Optional[int] = None,
        next_id: Optional[str] = None,
    ):
        """
        Get the details of a list of user swap orders.

        :param record_ids: List of record IDs.
        :param order_ids: List of order IDs.
        :param user_id: User ID.
        :param coin_id_in: ID of the input coin.
        :param coin_id_out: ID of the output coin.
        :param start_at: Retrieve all transaction records starting from the specified startAt timestamp.
        :param end_at: Retrieve all transaction records up to the specified endAt timestamp.
        :param next_id: Next ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getUserSwapRecordList"
        timestamp = str(int(time.time()))
        
        content = {}
        if record_ids:
            content["recordIds"] = record_ids
        if order_ids:
            content["orderIds"] = order_ids
        if user_id:
            content["userId"] = user_id
        if coin_id_in:
            content["coinIdIn"] = coin_id_in
        if coin_id_out:
            content["coinIdOut"] = coin_id_out
        if start_at:
            content["startAt"] = start_at
        if end_at:
            content["endAt"] = end_at
        if next_id:
            content["nextId"] = next_id
            
        body = json.dumps(content) if content else ""
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def create_swap(
        self,
        order_id: str,
        coin_id_in: int,
        amount_in: str,
        coin_id_out: int,
        amount_out_minimum: Optional[str] = None,
    ):
        """
        Create and fulfill a swap order.

        :param order_id: Swap order ID.
        :param coin_id_in: ID of the input coin.
        :param amount_in: Amount of input coin.
        :param coin_id_out: ID of the output coin.
        :param amount_out_minimum: The minimum amount of the output coin.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/swap"
        timestamp = str(int(time.time()))
        
        content = {
            "orderId": order_id,
            "coinIdIn": coin_id_in,
            "amountIn": amount_in,
            "coinIdOut": coin_id_out,
        }
        if amount_out_minimum:
            content["amountOutMinimum"] = amount_out_minimum
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_swap_record(self, record_id: Optional[str] = None, order_id: Optional[str] = None):
        """
        Get the details of a specific swap order.

        :param record_id: CCPayment unique ID for a transaction.
        :param order_id: Swap order ID.
        :return: The JSON response from the API.
        """
        if not record_id and not order_id:
            raise ValueError("Either record_id or order_id must be provided.")

        url = f"{self.BASE_URL}/getSwapRecord"
        timestamp = str(int(time.time()))
        
        content = {}
        if record_id:
            content["recordId"] = record_id
        if order_id:
            content["orderId"] = order_id
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_swap_record_list(
        self,
        record_ids: Optional[List[str]] = None,
        order_ids: Optional[List[str]] = None,
        coin_id_in: Optional[int] = None,
        coin_id_out: Optional[int] = None,
        start_at: Optional[int] = None,
        end_at: Optional[int] = None,
        next_id: Optional[str] = None,
    ):
        """
        Get the details of a list of swap orders.

        :param record_ids: List of record IDs.
        :param order_ids: List of order IDs.
        :param coin_id_in: ID of the input coin.
        :param coin_id_out: ID of the output coin.
        :param start_at: Retrieve all transaction records starting from the specified startAt timestamp.
        :param end_at: Retrieve all transaction records up to the specified endAt timestamp.
        :param next_id: Next ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getSwapRecordList"
        timestamp = str(int(time.time()))
        
        content = {}
        if record_ids:
            content["recordIds"] = record_ids
        if order_ids:
            content["orderIds"] = order_ids
        if coin_id_in:
            content["coinIdIn"] = coin_id_in
        if coin_id_out:
            content["coinIdOut"] = coin_id_out
        if start_at:
            content["startAt"] = start_at
        if end_at:
            content["endAt"] = end_at
        if next_id:
            content["nextId"] = next_id
            
        body = json.dumps(content) if content else ""
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def create_withdrawal_order(
        self,
        coin_id: int,
        chain: str,
        address: str,
        order_id: str,
        amount: str,
        memo: Optional[str] = None,
        merchant_pay_network_fee: Optional[bool] = None,
    ):
        """
        Create a withdrawal order to a blockchain address.

        :param coin_id: Coin ID.
        :param chain: Symbol of the chain.
        :param address: Withdrawal destination address.
        :param order_id: Withdrawal order ID.
        :param amount: Withdrawal amount.
        :param memo: Memo of the withdrawal address.
        :param merchant_pay_network_fee: Whether merchants pay network fee.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/applyAppWithdrawToNetwork"
        timestamp = str(int(time.time()))

        content = {
            "coinId": coin_id,
            "chain": chain,
            "address": address,
            "orderId": order_id,
            "amount": amount,
        }
        if memo:
            content["memo"] = memo
        if merchant_pay_network_fee is not None:
            content["merchantPayNetworkFee"] = merchant_pay_network_fee

        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        retry_count = 3
        timeout = 15

        while retry_count > 0:
            try:
                res = requests.post(url, headers=headers, data=body, timeout=timeout)
                res.raise_for_status()
                return res.json()
            except requests.exceptions.Timeout:
                retry_count -= 1
                time.sleep(0.2)
                if retry_count == 0:
                    return self.get_withdrawal_record(order_id=order_id)
            except Exception as e:
                raise e

    def withdraw_to_cwallet(self, coin_id: int, cwallet_user: str, order_id: str, amount: str):
        """
        Create a withdrawal order to a Cwallet account.

        :param coin_id: Coin ID.
        :param cwallet_user: Cwallet user ID or email.
        :param order_id: Withdrawal order ID.
        :param amount: Withdrawal amount.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/applyAppWithdrawToCwallet"
        timestamp = str(int(time.time()))

        content = {
            "coinId": coin_id,
            "cwalletUser": cwallet_user,
            "orderId": order_id,
            "amount": amount,
        }
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_withdrawal_record(self, record_id: Optional[str] = None, order_id: Optional[str] = None):
        """
        Get the detailed information of a specific withdrawal record ID.

        :param record_id: CCPayment unique ID for a transaction.
        :param order_id: The order ID of the withdrawal.
        :return: The JSON response from the API.
        """
        if not record_id and not order_id:
            raise ValueError("Either record_id or order_id must be provided.")

        url = f"{self.BASE_URL}/getAppWithdrawRecord"
        timestamp = str(int(time.time()))
        
        content = {}
        if record_id:
            content["recordId"] = record_id
        if order_id:
            content["orderId"] = order_id
            
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_withdrawal_record_list(
        self,
        coin_id: Optional[int] = None,
        order_ids: Optional[List[str]] = None,
        chain: Optional[str] = None,
        start_at: Optional[int] = None,
        end_at: Optional[int] = None,
        next_id: Optional[str] = None,
    ):
        """
        Get a list of withdrawals records.

        :param coin_id: Coin ID.
        :param order_ids: List of order IDs.
        :param chain: Symbol of the chain.
        :param start_at: Retrieve all transaction records starting from the specified startAt timestamp.
        :param end_at: Retrieve all transaction records up to the specified endAt timestamp.
        :param next_id: Next ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getAppWithdrawRecordList"
        timestamp = str(int(time.time()))
        
        content = {}
        if coin_id:
            content["coinId"] = coin_id
        if order_ids:
            content["orderIds"] = order_ids
        if chain:
            content["chain"] = chain
        if start_at:
            content["startAt"] = start_at
        if end_at:
            content["endAt"] = end_at
        if next_id:
            content["nextId"] = next_id
            
        body = json.dumps(content) if content else ""
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_deposit_record(self, record_id: str):
        """
        Get the detailed information of a specific record ID.

        :param record_id: CCPayment unique ID for a transaction.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getAppDepositRecord"
        timestamp = str(int(time.time()))
        
        content = {"recordId": record_id}
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_deposit_record_list(
        self,
        coin_id: Optional[int] = None,
        reference_id: Optional[str] = None,
        order_id: Optional[str] = None,
        chain: Optional[str] = None,
        start_at: Optional[int] = None,
        end_at: Optional[int] = None,
        next_id: Optional[str] = None,
    ):
        """
        Get a list of deposits records within a specific time range.

        :param coin_id: Coin ID.
        :param reference_id: Unique reference ID for the user in your system.
        :param order_id: Order ID.
        :param chain: Symbol of the chain.
        :param start_at: Retrieve all transaction records starting from the specified startAt timestamp.
        :param end_at: Retrieve all transaction records up to the specified endAt timestamp.
        :param next_id: Next ID.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getAppDepositRecordList"
        timestamp = str(int(time.time()))
        
        content = {}
        if coin_id:
            content["coinId"] = coin_id
        if reference_id:
            content["referenceId"] = reference_id
        if order_id:
            content["orderId"] = order_id
        if chain:
            content["chain"] = chain
        if start_at:
            content["startAt"] = start_at
        if end_at:
            content["endAt"] = end_at
        if next_id:
            content["nextId"] = next_id
            
        body = json.dumps(content) if content else ""
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def unbind_address(self, chain: str, address: str):
        """
        Unbind a deposit address from a userID/referenceID.

        :param chain: Chain symbol of the address to be unbound.
        :param address: Address to be unbound.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/addressUnbinding"
        timestamp = str(int(time.time()))
        
        content = {
            "chain": chain,
            "address": address,
        }
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_invoice_order_info(self, order_id: str):
        """
        Get invoice order information and all deposit records associated with the provided Order ID.

        :param order_id: Unique ID for the order.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getInvoiceOrderInfo"
        timestamp = str(int(time.time()))
        
        content = {"orderId": order_id}
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def create_invoice_url(
        self,
        order_id: str,
        price: str,
        product: Optional[str] = None,
        return_url: Optional[str] = None,
        close_url: Optional[str] = None,
        price_fiat_id: Optional[str] = None,
        price_coin_id: Optional[str] = None,
        expired_at: Optional[int] = None,
        buyer_email: Optional[str] = None,
    ):
        """
        Create a checkout page URL where the customer can select currencies.

        :param order_id: Order ID created by merchant.
        :param price: The price of the product.
        :param product: Product name.
        :param return_url: URL to which the user will be redirected after completing the payment.
        :param close_url: URL to which the user will be redirected after clicking 'leave page'.
        :param price_fiat_id: ID for the fiat currency in which the price is denominated.
        :param price_coin_id: ID for the cryptocurrency in which the price is denominated.
        :param expired_at: A 10-digit timestamp.
        :param buyer_email: Email address of the buyer.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/createInvoiceUrl"
        timestamp = str(int(time.time()))

        content = {
            "orderId": order_id,
            "price": price,
        }
        if product:
            content["product"] = product
        if return_url:
            content["returnUrl"] = return_url
        if close_url:
            content["closeUrl"] = close_url
        if price_fiat_id:
            content["priceFiatId"] = price_fiat_id
        if price_coin_id:
            content["priceCoinId"] = price_coin_id
        if expired_at:
            content["expiredAt"] = expired_at
        if buyer_email:
            content["buyerEmail"] = buyer_email

        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_order_info(self, order_id: str):
        """
        Get order information and all deposit records associated with the provided Order ID.

        :param order_id: Unique ID for the order in your system.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getAppOrderInfo"
        timestamp = str(int(time.time()))
        
        content = {"orderId": order_id}
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def create_order_deposit_address(
        self,
        coin_id: int,
        price: str,
        order_id: str,
        chain: str,
        fiat_id: Optional[int] = None,
        expired_at: Optional[int] = None,
        buyer_email: Optional[str] = None,
        generate_checkout_url: Optional[bool] = None,
        product: Optional[str] = None,
        return_url: Optional[str] = None,
        close_url: Optional[str] = None,
    ):
        """
        Create a deposit address for an order.

        :param coin_id: Coin ID of the coin to pay.
        :param price: Product price.
        :param order_id: Order ID.
        :param chain: Symbol of the chain.
        :param fiat_id: Fiat ID.
        :param expired_at: A 10-digit timestamp.
        :param buyer_email: Buyer's email address.
        :param generate_checkout_url: Whether to create a checkout URL.
        :param product: The product name.
        :param return_url: The next URL after successful payment.
        :param close_url: The next URL after the buyer clicks 'leave page'.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/createAppOrderDepositAddress"
        timestamp = str(int(time.time()))

        content = {
            "coinId": coin_id,
            "price": price,
            "orderId": order_id,
            "chain": chain,
        }
        if fiat_id:
            content["fiatId"] = fiat_id
        if expired_at:
            content["expiredAt"] = expired_at
        if buyer_email:
            content["buyerEmail"] = buyer_email
        if generate_checkout_url:
            content["generateCheckoutURL"] = generate_checkout_url
        if product:
            content["product"] = product
        if return_url:
            content["returnUrl"] = return_url
        if close_url:
            content["closeUrl"] = close_url

        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()

    def get_or_create_deposit_address(self, reference_id: str, chain: str):
        """
        Get or create a permanent deposit address.

        :param reference_id: Unique reference ID for the user in your system.
        :param chain: Symbol of the chain.
        :return: The JSON response from the API.
        """
        url = f"{self.BASE_URL}/getOrCreateAppDepositAddress"
        timestamp = str(int(time.time()))
        
        content = {
            "referenceId": reference_id,
            "chain": chain,
        }
        body = json.dumps(content)
        signature = self._create_signature(timestamp, body)

        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Appid": self.app_id,
            "Sign": signature,
            "Timestamp": timestamp,
        }

        res = requests.post(url, headers=headers, data=body)
        return res.json()
