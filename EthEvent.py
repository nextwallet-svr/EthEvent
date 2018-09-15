from web3 import Web3, HTTPProvider, IPCProvider
import json
import time
import datetime
import eth_utils
import hexbytes
from web3.contract import ConciseContract
from ServerError import *
from LogUtil import *
from EthUtils import *

######################################################################
g_event_handler_dict = {}
g_event_filter_map = {}

def getContract(contract_address, _abi):
    try:
        contract = getWeb3().eth.contract(address=contract_address, abi=_abi)
        if contract is None:
            error('contract none, contract_address: %s', contract_address)
            raise(Exception('WEB3_DISCONNECT'))
        return contract
    except (Exception) as e:
        error('getContract, contract_address: %s, e: %s', contract_address, e)
        raise (e)
    return None

def getEventNames():
    global g_event_handler_dict

    event_names = []
    for k in g_event_handler_dict.keys():
        event_names.append(k)

    return event_names

def callEventHandle(event_name, contract, event):
    global g_event_handler_dict

    if (not event_name in g_event_handler_dict):
        error('invalid event_name: %s', event_name)
        return False

    return g_event_handler_dict[event_name](contract, event)

def regEventHandler(event_name, handler):
    global g_event_handler_dict
    g_event_handler_dict[event_name] = handler
    return True

def createEventFilters(_abi, from_block, to_block = 0, confirm_block_num = 0):
    global g_event_filter_map

    try:
        if (type(from_block) == str and from_block != 'latest'):
            error('invalid args, from_block: %s', from_block)
            raise(Exception('SERVER_INTERNAL_ERR'))

        # if (type(from_block) == int):
        #     if (type(to_block) != int):
        #         error('invalid args, from_block: %s, to_block: %s', from_block, to_block)
        #         raise(Exception('SERVER_INTERNAL_ERR'))

        contract = getWeb3().eth.contract(abi=_abi)
        if (contract is None):
            error('contract none')
            raise(Exception('SERVER_INTERNAL_ERR'))
    except (Exception) as e:
        error('createEventFilters, e: %s', e)
        raise(e)

    for name in getEventNames():
        try:
            f = getattr(contract.events, name)
            if (f is None):
                error('f none')
                continue

            event_filter = None
            if (from_block == 'latest'):
                event_filter = f.createFilter(fromBlock=from_block)

            if (type(from_block) == int and to_block == 0):
                event_filter = f.createFilter(fromBlock=from_block - confirm_block_num)

            if (type(from_block) == int and to_block >= from_block):
                event_filter = f.createFilter(fromBlock=from_block - confirm_block_num, toBlock=to_block)

            if (event_filter is None):
                error('createEventFilters, createFilter none, name: %s, from_block: %d, to_block: %d, confirm_block_num: %d', 
                        name, from_block, to_block, confirm_block_num)
                raise(Exception('createFilter fail'))

            #filter绑定name
            g_event_filter_map[name] = event_filter
        except (Exception) as e:
            error('%s： createEventFilters, e: %s, from_block: %d, to_block: %d, confirm_block_num: %d', 
                    name, e, from_block, to_block, confirm_block_num)
            raise(e)
    info('g_event_filter_map: %s', g_event_filter_map)
    return g_event_filter_map

def destroyEventFilters():
    global g_event_filter_map
    if (g_event_filter_map is None):
        return

    for k, v in g_event_filter_map.items():
        try:
            getWeb3().eth.uninstallFilter(v.filter_id)
        except Exception as e:
            error('uninstallFilter fail, e: %s, name: %s, v: %s, filter_id: %s', 
                    e, k, v, v.filter_id)
            continue

def callEventHandlers(_abi):
    try:
        for name, event_filter in g_event_filter_map.items():
            events = event_filter.get_new_entries()

            if (events is None or len(events) == 0):
                debug('events empty, name: %s', name)
                continue

            for e in events:
                info('get name: %s, evn: %s', name, e)

                if (e is None):
                    debug('None evn: %s, events: %s, name: %s', e, events, name)
                    continue

                event = dict(e)
                info('event: %s, name: %s, contract_address: %s', event, name, event['address'])

                contract_address = event['address']
                new_contract = getContract(contract_address, _abi)
                callEventHandle(event['event'], new_contract, event)
    except Exception as e:
        error('callEventHandlers fail, e: %s', e)
