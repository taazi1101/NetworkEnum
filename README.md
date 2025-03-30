# NetworkEnum
A python portscanner and network scanner built together.

Input: portCheck.py [Ip Address]:[Ports] [Other args]
Example: portCheck.py 192.168.1.fuzz:0,20,21,30-50 -c=10-200 -t=200

Ip address and ports must be first argument!

[Ip Address] = Ip (x.x.x.FUZZ) , (FUZZ.FUZZ.FUZZ.FUZZ) | Sets ip address base and parts to fuzz.
[Ports] = Port(s) (0 for ping) [sep:, or range: x-y] | Sets ports to scan or ping (Ping might require root/admin because it send raw ip packets.).
[-c] = Ip(s) [sep:, or range: x-y] (Default: 1-255) | Sets what adresses fuzz produces.
[-n] = Tries to find hostname. In case no hostname can be found, this wastes a lot of time.
[-m] = Tries to resolve vendor and mac address. | (-m=Wi-Fi) select network interface to use. (Replace possible spaces with '_')
[-t] = Sets timeout in ms (default 50ms)
[-g] = Disables output color. If you see random bytes, your terminal probably doesen't support color.
[-pf] = Prints all failed connections. | This is not recommended as it will flood your results.

// Coming soon...
