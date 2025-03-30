import socket, os
try:
    import pythonping
    allowPing = True
except Exception as exp:
    print(f"Module 'pythonping' import failed ({exp})")
    print("Ping functionality won't work!")
    print("To use ping functionality please install pythonping (python3 -m pip install pythonping)\n")
    allowPing = False
    pass
try:
    from mac_vendor_lookup import MacLookup
    import getmac
    allowMac = True
except Exception as exp:
    print(f"Module 'mac-vendor-lookup' or/and 'get-mac' import failed ({exp})")
    print("Mac look up functionality won't work!")
    print("To use Mac look up functionality please install mac-vendor-lookup and get-mac (python3 -m pip install mac-vendor-lookup get-mac)\n")
    allowMac = False
    pass
import time
import sys

appTimeStart = time.time()
TimeFormatted = time.strftime("%d.%m.%Y_%H-%M-%S",time.localtime())
outputFolder = "portResult/"

if os.path.exists(outputFolder) == False:
    os.makedirs(outputFolder)

outputFile = f"{outputFolder}portCheck.{TimeFormatted}.txt"

outputColor = True
checkHostname = False
printFailed = False
checkMac = False
timeout = float(0.05) #Seconds


def format_seconds_to_hhmmss(seconds):
    hours = seconds // (60*60)
    seconds %= (60*60)
    minutes = seconds // 60
    seconds %= 60
    if hours > 0:
        return str(round(hours)) + "h " + str(int(round(minutes,-1))) + "min"
    elif minutes > 0:
        return str(round(minutes)) + "min"
    else:
        return str(round(seconds)) + "sec"
    #return "%02i:%02i:%02i" % (hours, minutes, seconds)

def avg(inList):
    x = 0
    for i in inList:
        x += i
    try:
        out = x/len(inList)
    except:
        out = 0
    return out

def countAndTrimAverage(inList):
    if len(inList) > 200:
        inList.append(avg(inList))
        inList = inList[5:]
    out = avg(inList)
    return inList,out

def progressBar(current,start,max):
    filledChar = "█" # Same width = better result
    emptyChar = "░"
    lenght = 30 # Characters
    secSize = (max-start)/lenght

    progress = int(round((current-start)/secSize))

    return f"{filledChar*progress}{emptyChar*(int(round(((max-start)/secSize)))-progress)}"


manual = """Manual:
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
[-h] = This manual."""

if len(sys.argv) < 2:
    print(manual + "\n\nThis is a simplified input system that does not support all arguments. Please use command line arguments instead.")
    ipFormatIn = input("Ip (x.x.x.FUZZ) , (FUZZ.FUZZ.FUZZ.FUZZ):")
    ipRange = input("Ip(s) [sep:, or range: x-y] (Default: 1-255):").replace(" ","").split(",")
    ports = input("Port(s) (0 for ping) [sep:, or range: x-y]:").replace(" ","").split(",")
else:
    if ("-h") in sys.argv:
        print(manual)
        exit(0)
    ipRange = [""]
    ipFormatIn, ports = sys.argv[1].split(":")
    ports = ports.replace(" ","").split(",")

    if len(sys.argv) > 2:
        for arg in sys.argv:
            if "-c" in arg:
                ipRange = arg.split("=")[1].replace(" ","").split(",")
            elif "-g" in arg:
                outputColor = False
            elif "-t" in arg:
                timeout = float(arg.split("=")[1])/1000
            elif "-pf" in arg:
                printFailed = True
            elif "-n" in arg:
                checkHostname = True
            elif "-m" in arg:
                checkMac = True
                macInterface = arg.split("=")[1].replace(" ","").replace("_"," ")

ipFormatl = []
fuzes = 0
ipSec = 0
lfI = ipFormatIn.split(".")
lfI.reverse()
for splIp in lfI:
    ipSec += 1
    if splIp.lower() == "fuzz":
        ipsection = "FUZZ" + str(fuzes)
        fuzes += 1
    else:
        ipsection = splIp
    if ipSec != 1:
        ipsection += "."
    ipFormatl.append(ipsection)

ipFormatl.reverse()
ipFormat = ""
for sec in ipFormatl:
    ipFormat += sec

for p in ports:
    if "-" in p:
        ports.remove(p)
        portsList = list(range(int(p.split("-")[0]),int(p.split("-")[1])+1))
        for pL in portsList:
            if str(pL) not in ports:
                ports.append(str(pL))

if ipRange[0] == "":
    ipRangeRes = list(range(1,256))
else:
    ipRangeRes = []
    for i in ipRange:
        if "-" in i:
            ipRange.remove(i)
            ipRangeList = list(range(int(i.split("-")[0]),int(i.split("-")[1])+1))
            for iL in ipRangeList:
                if str(iL) not in ipRange:
                    ipRangeRes.append(iL)
        else:
            ipRangeRes.append(int(i))

f = open(outputFile,"w")
f.write(f"{TimeFormatted}, timeout={str(timeout*1000)}ms, {ipFormatIn}, {ports}\n\n")

count = 0

if outputColor:
    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
else:
    class bcolors:
        HEADER = ''
        OKBLUE = ''
        OKCYAN = ''
        OKGREEN = ''
        WARNING = ''
        FAIL = ''
        ENDC = ''
        BOLD = ''
        UNDERLINE = ''

if fuzes > 0:
    ipRangeRes0 = ipRangeRes
else:
    ipRangeRes0 = [-1]
if fuzes > 1:
    ipRangeRes1 = ipRangeRes
else:
    ipRangeRes1 = [-1]
if fuzes > 2:
    ipRangeRes2 = ipRangeRes
else:
    ipRangeRes2 = [-1]
if fuzes > 3:
    ipRangeRes3 = ipRangeRes
else:
    ipRangeRes3 = [-1]



max = (len(ipRangeRes)**fuzes)*len(ports)

averageVals = []
average = 0
first = True
countMshLen = 0
startTime = time.time()

for ipSuf3 in ipRangeRes3:
    for ipSuf2 in ipRangeRes2:
        for ipSuf1 in ipRangeRes1:
            for ipSuf0 in ipRangeRes0:
                successPorts = []
                failPorts = []
                hostname = ""
                MacVendor = " "*100
                hasHostname = False
                hasMac = False
                hasBeenPinged = False

                for port in ports:

                    averageVals,average = countAndTrimAverage(averageVals)
                    ipAddr = ipFormat.replace("FUZZ0",str(ipSuf0)).replace("FUZZ1",str(ipSuf1)).replace("FUZZ2",str(ipSuf2)).replace("FUZZ3",str(ipSuf3))
                    ip = (ipAddr,int(port))
                    if str(port) == "0":
                        ip = (ipAddr, "PNG")
                    countMsg = f"{bcolors.WARNING}[*]{bcolors.ENDC}: {str(ip).replace("(","").replace(")","").replace("'","").replace(",",":").replace(" ","")} "
                    if first:
                        countMshLen = len(countMsg)+6 # lenght of visual stabilizer
                        first = False
                    waitSec = average*(max-count)
                    print(countMsg + "-"*(abs(len(countMsg) - countMshLen)) + f" {bcolors.UNDERLINE}[{progressBar(count,0,max)}] ~{format_seconds_to_hhmmss(waitSec)} ({round(average,3)}) -> [{str(count)}/{str(max)}]{bcolors.ENDC}" + " "*20,end="\r",flush=True)

                    count += 1

                    if str(port) != "0":

                        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        
                        sock.settimeout(timeout)
                        try:
                            sock.connect(ip)
                            try:
                                if checkHostname:
                                    if hasHostname == False:
                                        hasHostname = True
                                        hostname = " | " + str(socket.gethostbyaddr(ipAddr)[0])
                            except Exception as exp:
                                #hostname = str(exp)
                                pass
                            if checkMac:
                                if hasMac == False:
                                    hasMac = True
                                    try:
                                        macAddr = getmac.get_mac_address(macInterface,ipAddr)
                                        try:
                                            MacVendor = f" | [{macAddr}] " + str(MacLookup().lookup(macAddr)) + " "*40
                                        except:
                                            MacVendor = f" | [{macAddr}]" + " "*70
                                    except:
                                        pass
                            successPorts.append(int(port))
                            sock.close()
                        except:
                            failPorts.append(int(port))
                            pass
                    elif allowPing:
                        try:
                            pingResp = pythonping.ping(ipFormat.replace("FUZZ0",str(ipSuf0)).replace("FUZZ1",str(ipSuf1)).replace("FUZZ2",str(ipSuf2)).replace("FUZZ3",str(ipSuf3)),timeout=timeout,count=1)
                            if pingResp.success():
                                successPorts.append(f"<{round(pingResp.rtt_max_ms)}ms>")
                                if checkHostname:
                                    if hasHostname == False:
                                        hasHostname = True
                                        try:
                                            hostname = " | " + str(socket.gethostbyaddr(ipAddr)[0])
                                        except:
                                            pass
                                if checkMac:
                                    if hasMac == False:
                                        hasMac = True
                                        try:
                                            macAddr = getmac.get_mac_address(macInterface,ipAddr)
                                            try:
                                                MacVendor = f" | [{macAddr}] " + str(MacLookup().lookup(macAddr)) + " "*40
                                            except:
                                                MacVendor = f" | [{macAddr}]" + " "*70
                                        except Exception as exp:
                                            #print(exp)
                                            pass
                        except Exception as exp:
                            #print(exp)
                            pass
                    
                    averageVals.append(time.time()-startTime)
                    startTime = time.time()

                if len(successPorts) > 0:
                    print(f"{bcolors.OKGREEN}[+]{bcolors.ENDC}: " + ipAddr + ":" + f"{bcolors.OKBLUE}{str(successPorts).replace("[","").replace("]",",").replace(" ","").replace("'","")[:-1]}{bcolors.ENDC}" + hostname + MacVendor)
                    f.write(f"[+]: " + ipAddr + ":" + f"{str(successPorts).replace("[","").replace("]",",").replace(" ","").replace("'","")[:-1]}" + hostname + MacVendor + "\n")
                elif printFailed:
                    print(f"{bcolors.FAIL}[-]{bcolors.ENDC}: " + ipAddr + f" | No given ports open.")
                    f.write(f"[-]: " + ipAddr + "\n")



print(f"Scanned a total of {str(count)} ports in {format_seconds_to_hhmmss(time.time()-appTimeStart)}." + " "*150,end="\r",flush=True)
print(f"{bcolors.ENDC}\n")

