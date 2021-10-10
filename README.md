# term_from_nat

=========================

connect a terminal inside a nat. 
used when you want somebody to help you, but he could not connect to your linux because your computer is inside a nat.

it is somehow like the ssh, the different is that:

the **ssh** is: client connect to server. **do something in the server computer.**

this **term_from_nat** is: client connect to server. **do something in the client computer.**


used when:
----------------

```
1 when you want somebody to do something in you linux computer
2 but he could not connect to your linux because your computer is inside a nat
```

how to use:
-----------------------------
```
COMPUTER1(one nat):
1. pip install term_from_nat
2. python3 -m term_from_nat  or just type: term_from_nat
will show some tips:
client started, use: 
python3 -m term_from_nat -s -t  378885 
 to start the server
 
COMPUTER2(another nat):
1. pip install term_from_nat
2. python3 -m term_from_nat -s -t  378885   
     or just: term_from_nat -s -t  378885

that's all.

```




```
old/deprecated usage:
normal usage uses a bridge to connect each-other.
if you have a public ip server, then, you could run this, connect each other without bridge.
1 COMPUTER1: run python3 server_lite.py  {server_port} on one computer that has a public ip.
2 COMPUTER2: run python3 client_lite.py {server_ip} {server_port} on the computer that inside a nat
3 COMPUTER1: type you command.
```
