import os
import platform

from twisted.internet import defer

from . import data
from p2pool.util import math, pack
from operator import *

def get_subsidy(nCap, nMaxSubsidy, bnTarget):
    bnLowerBound = 0.01
    bnUpperBound = bnSubsidyLimit = nMaxSubsidy
    bnTargetLimit = 0x00000fffff000000000000000000000000000000000000000000000000000000

    while bnLowerBound + 0.01 <= bnUpperBound:
        bnMidValue = (bnLowerBound + bnUpperBound) / 2
        if pow(bnMidValue, nCap) * bnTargetLimit > pow(bnSubsidyLimit, nCap) * bnTarget:
            bnUpperBound = bnMidValue
        else:
            bnLowerBound = bnMidValue

    nSubsidy = round(bnUpperBound, 6)

    if nSubsidy > bnUpperBound:
        nSubsidy = nSubsidy - 0.000001

    return int(nSubsidy * 1000000)

nets = dict(
    bitbar=math.Object(
        P2P_PREFIX='e4e8e9e5'.decode('hex'),
        P2P_PORT=19944,
        ADDRESS_VERSION=25,
        RPC_PORT=9344,
        RPC_CHECK=defer.inlineCallbacks(lambda bitcoind: defer.returnValue(
            'bitbaraddress' in (yield bitcoind.rpc_help()) and
            not (yield bitcoind.rpc_getinfo())['testnet']
        )),
        SUBSIDY_FUNC=lambda target: get_subsidy(6, 1, target),
        BLOCKHASH_FUNC=lambda data: pack.IntType(256).unpack(__import__('ltc_scrypt').getPoWHash(data)),
        POW_FUNC=lambda data: pack.IntType(256).unpack(__import__('ltc_scrypt').getPoWHash(data)),
        BLOCK_PERIOD=600, # s
        SYMBOL='BTB',
        CONF_FILE_FUNC=lambda: os.path.join(os.path.join(os.environ['APPDATA'], 'BitBar') if platform.system() == 'Windows' else os.path.expanduser('~/Library/Application Support/BitBar/') if platform.system() == 'Darwin' else os.path.expanduser('~/.bitbar'), 'bitbar.conf'),
        BLOCK_EXPLORER_URL_PREFIX='http://btb.cryptocoinexplorer.com/block?block=',
        ADDRESS_EXPLORER_URL_PREFIX='http://btb.cryptocoinexplorer.com/address?address=',
        TX_EXPLORER_URL_PREFIX='http://btb.cryptocoinexplorer.com/transaction?transaction=',
        SANE_TARGET_RANGE=(2**256//100000000 - 1, 2**256//1000 - 1),
        DUMB_SCRYPT_DIFF=2**16,
        DUST_THRESHOLD=1e8,
    ),

)
for net_name, net in nets.iteritems():
    net.NAME = net_name
