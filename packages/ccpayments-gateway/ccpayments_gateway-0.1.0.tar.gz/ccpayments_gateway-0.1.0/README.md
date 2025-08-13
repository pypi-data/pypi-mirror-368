# CCPayments Gateway Library

A Python library for interacting with the CCPayments API.

## Installation

```bash
pip install ccpayments-gateway
```

## Usage

### Webhook Verification

```python
from ccpayments_gateway import verify_signature

# Example usage for webhook verification
# This is a simplified example. In a real web framework,
# you would get these values from the request headers and body.
content = '{"some": "payload"}'
signature = "the_signature_from_header"
app_id = "your_app_id"
app_secret = "your_app_secret"
timestamp = "the_timestamp_from_header"

if verify_signature(content, signature, app_id, app_secret, timestamp):
    print("Signature is valid!")
else:
    print("Signature is invalid!")
```

### Resend Webhooks

```python
from ccpayments_gateway import CCPayments
import time

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Resend webhooks from a specific time
start_time = int(time.time()) - 3600 # 1 hour ago
response = client.resend_webhooks(start_timestamp=start_time)
print(response)
```

### Get or Create Deposit Address

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get or create a deposit address
response = client.get_or_create_deposit_address(reference_id="user_123", chain="TRX")
print(response)
```

### Create Order Deposit Address

```python
from ccpayments_gateway import CCPayments
import time

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Create a deposit address for an order
order_id = str(int(time.time()))
response = client.create_order_deposit_address(
    coin_id=1280,
    price="1",
    order_id=order_id,
    chain="POLYGON"
)
print(response)
```

### Get Order Info

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get order information
# Replace with a real order ID
response = client.get_order_info(order_id="1709889675")
print(response)
```

### Create Invoice URL

```python
from ccpayments_gateway import CCPayments
import time

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Create an invoice URL
order_id = str(int(time.time()))
response = client.create_invoice_url(
    order_id=order_id,
    price="1",
    price_coin_id="1280"
)
print(response)
```

### Get Invoice Order Info

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get invoice order information
# Replace with a real order ID
response = client.get_invoice_order_info(order_id="xxxxxxx")
print(response)
```

### Unbind Address

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Unbind an address
response = client.unbind_address(chain="POLYGON", address="0x3720C7f5b352E9da3A102B3b8c49080acAa4ceee")
print(response)
```

### Get Deposit Record

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a deposit record
# Replace with a real record ID
response = client.get_deposit_record(record_id="20250116073333231508600365121536")
print(response)
```

### Get Deposit Record List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a list of deposit records
response = client.get_deposit_record_list()
print(response)
```

### Create Withdrawal Order

```python
from ccpayments_gateway import CCPayments
import time

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Create a withdrawal order
order_id = str(int(time.time() * 1000))
response = client.create_withdrawal_order(
    coin_id=1280,
    address="0xBb9C4e7F3687aca1AE2828c18f9E3ae067F569FE",
    order_id=order_id,
    chain="POLYGON",
    amount="0.001",
)
print(response)
```

### Get Withdrawal Record

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a withdrawal record by order ID
response = client.get_withdrawal_record(order_id="some_order_id")
print(response)

# Get a withdrawal record by record ID
response = client.get_withdrawal_record(record_id="some_record_id")
print(response)
```

### Withdraw to Cwallet

```python
from ccpayments_gateway import CCPayments
import time

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Withdraw to a Cwallet user
order_id = str(int(time.time() * 1000))
response = client.withdraw_to_cwallet(
    coin_id=1280,
    cwallet_user="9558861",
    order_id=order_id,
    amount="1"
)
print(response)
```

### Get Withdrawal Record List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a list of withdrawal records
response = client.get_withdrawal_record_list()
print(response)
```

### Get Swap Quote

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a swap quote
response = client.get_swap_quote(coin_id_in=1280, amount_in="100", coin_id_out=1329)
print(response)
```

### Create Swap

```python
from ccpayments_gateway import CCPayments
import time

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Create a swap
order_id = str(int(time.time() * 1000))
response = client.create_swap(
    order_id=order_id,
    coin_id_in=1280,
    amount_in="1",
    coin_id_out=1329,
)
print(response)
```

### Get Swap Record

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a swap record
response = client.get_swap_record(order_id="xxxxxxxxxxx")
print(response)
```

### Get Swap Record List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a list of swap records
response = client.get_swap_record_list()
print(response)
```

### Get User Asset List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get user asset list
response = client.get_user_asset_list(user_id="1709021102608")
print(response)
```

### Get User Coin Asset

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get user coin asset
response = client.get_user_coin_asset(user_id="1709021102608", coin_id=1280)
print(response)
```

### Get or Create User Deposit Address

```python
from ccpayments_gateway import CCPayments
import time

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get or create a user deposit address
user_id = str(int(time.time() * 1000))
response = client.get_or_create_user_deposit_address(user_id=user_id, chain="BSC")
print(response)
```

### Get User Deposit Record

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a user deposit record
response = client.get_user_deposit_record(record_id="20250116080551231516731711291392")
print(response)
```

### Get User Deposit Record List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a list of user deposit records
response = client.get_user_deposit_record_list(user_id="1737014581861")
print(response)
```

### User Withdraw to Network

```python
from ccpayments_gateway import CCPayments
import time

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# User withdraw to network
order_id = str(int(time.time() * 1000))
response = client.user_withdraw_to_network(
    user_id="1709021102608",
    coin_id=1280,
    address="0x12438F04093EBc87f0Ba629bbe93F2451711d967",
    order_id=order_id,
    chain="POLYGON",
    amount="0.001",
)
print(response)
```

### User Withdraw to Cwallet

```python
from ccpayments_gateway import CCPayments
import time

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# User withdraw to Cwallet
order_id = str(int(time.time() * 1000))
response = client.user_withdraw_to_cwallet(
    user_id="1709021102608",
    coin_id=1280,
    cwallet_user="9558861",
    order_id=order_id,
    amount="0.01"
)
print(response)
```

### Get User Withdrawal Record

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a user withdrawal record
response = client.get_user_withdrawal_record(record_id="202403010604081763445093768892416")
print(response)
```

### Get User Withdrawal Record List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a list of user withdrawal records
response = client.get_user_withdrawal_record_list(user_id="1709021102608")
print(response)
```

### Create Internal Transaction

```python
from ccpayments_gateway import CCPayments
import time

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Create an internal transaction
order_id = str(int(time.time() * 1000))
response = client.create_internal_transaction(
    from_user_id="1709021102608",
    to_user_id="1709021101247",
    coin_id=1280,
    amount="0.005",
    order_id=order_id,
)
print(response)
```

### Get User Internal Transaction Record

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a user internal transaction record
response = client.get_user_internal_transaction_record(record_id="202403010610541763446796748591104")
print(response)
```

### Get User Internal Transaction Record List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a list of user internal transaction records
response = client.get_user_internal_transaction_record_list(from_user_id="1709021102608")
print(response)
```

### User Get Swap Quote

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a user swap quote
response = client.get_swap_quote(coin_id_in=1280, amount_in="100", coin_id_out=1482, extra_fee_rate="0.01")
print(response)
```

### User Create Swap

```python
from ccpayments_gateway import CCPayments
import time

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Create a user swap
order_id = str(int(time.time() * 1000))
response = client.user_create_swap(
    order_id=order_id,
    user_id="user-swap1",
    coin_id_in=1280,
    amount_in="100",
    coin_id_out=1329,
)
print(response)
```

### Get User Swap Record

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a user swap record
response = client.get_user_swap_record(record_id="20240722021342166923068583059456")
print(response)
```

### Get User Swap Record List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get a list of user swap records
response = client.get_user_swap_record_list()
print(response)
```

### Get Token List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get token list
response = client.get_token_list()
print(response)
```

### Get Token Info

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get token info
response = client.get_token_info(coin_id=1280)
print(response)
```

### Get Token Price

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get token price
response = client.get_token_price(coin_ids=[1329])
print(response)
```

### Get Balance List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get balance list
response = client.get_balance_list()
print(response)
```

### Get Coin Balance

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get coin balance
response = client.get_coin_balance(coin_id=1280)
print(response)
```

### Rescan Lost Transaction

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Rescan a lost transaction
response = client.rescan_lost_transaction(
    chain="XLM",
    to_address="GBSCAK4DTAS4TUNZJUQ5QO5FCJBEXVH7JSMZNZLRTSIZGIDS3H7CWE7O",
    tx_id="9f1597024ca2fabdef4048c4b203fbc2ee2cda1ba2504f184f3a8304d97c1487",
    memo="109"
)
print(response)
```

### Get Cwallet User Info

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get Cwallet user info
response = client.get_cwallet_user_info(cwallet_user_id="9558861")
print(response)
```

### Check Withdrawal Address Validity

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Check withdrawal address validity
response = client.check_withdrawal_address_validity(chain="POLYGON", address="0x43fEeF6879286BBAC5082f17AD3dA55EE456B934")
print(response)
```

### Get Withdrawal Network Fee

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get withdrawal network fee
response = client.get_withdrawal_network_fee(coin_id=1280, chain="POLYGON")
print(response)
```

### Get Fiat List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get fiat list
response = client.get_fiat_list()
print(response)
```

### Get Swap Coin List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get swap coin list
response = client.get_swap_coin_list()
print(response)
```

### Get Chain List

```python
from ccpayments_gateway import CCPayments

client = CCPayments(app_id="your_app_id", app_secret="your_app_secret")

# Get chain list
response = client.get_chain_list(chains=["ETH", "POLYGON"])
print(response)
