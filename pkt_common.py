#coding:utf-8
import json


def gen_pkt(payload:str, tk:str)->bytes:
    try:
        pkt = {'payload':payload, 'tk':tk,'protocol':'pty'}
        ret = bytes(json.dumps(pkt), 'utf-8')
        ret_len=len(ret)
        ret_len_str='{0:05d}'.format(ret_len)
        ret=b'\xaa' +ret_len_str.encode('utf-8')+  b'\xab'+ret
    except Exception as e:
        print(e)
        print(payload)
    return ret

def get_payload(pkt:bytes, tk:str)->str:
    try:
        if pkt[0]!=0xaa:
            return ''
        len_str = pkt[1:6].decode('utf-8')
        pkt_len=int(len_str)
        if len(pkt)<(pkt_len+5+2):
            return ''
        if len(pkt)>(pkt_len+5+2):
            pkt_str = pkt[7:pkt_len+7].decode('utf-8')
            pkt_obj = json.loads(pkt_str)
            pkt_append=get_payload(pkt[pkt_len+7:], tk)
            return pkt_obj['payload']+pkt_append
        else:
            pkt_str = pkt[7:].decode('utf-8')
            pkt_obj = json.loads(pkt_str)
            return pkt_obj['payload']
    except Exception as e:
        print('get_payload:json decode error.', e,pkt)
        return ''

