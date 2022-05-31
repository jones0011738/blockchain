import os
from solcx import compile_standard, install_solc
import json
from web3 import Web3

# visual studio installer and install windows sdx
from dotenv import load_dotenv

load_dotenv()  # loading from env use pip install python-dotenv
with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = json.loads(
    compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]

# For connecting to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address = "0x862932b08d2749E5249378cd2E8bc140a17883C0"
private_key = os.getenv("PRIVATE_KEY")

# create contract in python

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# build
# sign
# send a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# send signed transaction
print("deploying contract")
tx_hash = w3.eth.send_raw_transaction(
    signed_txn.rawTransaction
)  # sending transaction to blockchain
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("deployed contract")
# working with contract
# contract address
# contract abi
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# interracting with contract is through a call(simulate making the call and getting a return value(no state change to the blockchain))
# or transact(actually make state change build and send a transaction)
# initial value of favouritenumber
print(simple_storage.functions.retrieve().call())
print("updating contract")
# creating the transaction
greeting_transaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_greeting_txn = w3.eth.account.sign_transaction(
    greeting_transaction, private_key=private_key
)
tx_greeting_hash = w3.eth.send_raw_transaction(signed_greeting_txn.rawTransaction)
print("Updating stored Value...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greeting_hash)
print("updated contract")
print(simple_storage.functions.retrieve().call())
