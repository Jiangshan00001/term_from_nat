# coding:utf-8
import base64
import json


def account_to_topic(account, password):
    return '/' + account + '/'



def gen_pkt(payload: str, tk: str) -> bytes:
    try:
        pkt = {'payload': payload, 'tk': tk, 'protocol': 'pty'}
        ret = bytes(json.dumps(pkt), 'utf-8')
        ret_len = len(ret)
        ret_len_str = '{0:08d}'.format(ret_len)
        ret = b'\xaa' + ret_len_str.encode('utf-8') + b'\xab' + ret
    except Exception as e:
        print('gen_pkt error:')
        print(e)
        print(payload)
    return ret

head_len_len=8
HEAD_SIGN=b'\xaa'
HEAD_SIGN2 = b'\xab'

def gen_pkt2(payload: bytes, tk: str) -> bytes:
    try:
        pkt = {'payload':  base64.b64encode(payload).decode('utf-8'), 'tk': tk, 'protocol': 'pty'}
        ret = bytes(json.dumps(pkt), 'utf-8')
        ret_len = len(ret)
        ret_len_str = '{0:08d}'.format(ret_len)
        ret = HEAD_SIGN + ret_len_str.encode('utf-8') + HEAD_SIGN2 + ret
    except Exception as e:
        print('gen_pkt2 error:')
        print(e)
        print(payload)
    return ret

def get_payload2(pkt: bytes, tk: str) -> bytes:
    head_len_len = 8
    try:
        if pkt[0] != 0xaa:
            return b''
        len_str = pkt[1:1+head_len_len].decode('utf-8')
        pkt_len = int(len_str)
        if len(pkt) < (pkt_len + head_len_len + 2):
            return b''
        if len(pkt) > (pkt_len + head_len_len + 2):
            pkt_str = pkt[head_len_len+2:pkt_len +head_len_len+2].decode('utf-8')
            pkt_obj = json.loads(pkt_str)
            pkt_append = get_payload2(pkt[pkt_len + head_len_len+2:], tk)
            return base64.b64decode(pkt_obj['payload']) + pkt_append
        else:
            pkt_str = pkt[head_len_len+2:].decode('utf-8')
            pkt_obj = json.loads(pkt_str)
            return base64.b64decode(pkt_obj['payload'])
    except Exception as e:
        print('get_payload2:error.', e, len(pkt))
        return b''



def get_payload(pkt: bytes, tk: str) -> str:
    try:
        if pkt[0] != 0xaa:
            return ''
        len_str = pkt[1:9].decode('utf-8')
        pkt_len = int(len_str)
        if len(pkt) < (pkt_len + 8 + 2):
            return ''
        if len(pkt) > (pkt_len + 8 + 2):
            pkt_str = pkt[10:pkt_len + 10].decode('utf-8')
            pkt_obj = json.loads(pkt_str)
            pkt_append = get_payload(pkt[pkt_len + 10:], tk)
            return pkt_obj['payload'] + pkt_append
        else:
            pkt_str = pkt[10:].decode('utf-8')
            pkt_obj = json.loads(pkt_str)
            return pkt_obj['payload']
    except Exception as e:
        print('get_payload:json decode error.', e, len(pkt))
        return ''
