一个小脚本，可以用于不同内网之间的linux之间terminal共享。

在待共享的机器A上运行：
pip install term_from_nat
python3 -m term_from_nat


会显示另一方B需要输入的命令，例如：
python3 -m term_from_nat -s -t  378885 

 
另一方B机器上输入：
pip install term_from_nat
python3 -m term_from_nat -s -t  378885   

B机器就可以输入命令，操作A机器的窗口了。（A机器窗口已经不可以在本地操作，只能在B机器上操作，类似于远程协助）
