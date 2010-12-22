#!/usr/bin/env python
'''
This module sets the parameter of an openvz container.

Copyright: ego2dot0
License: GPLv3
'''

if __name__ == '__main__':
    pass

from optparse import OptionParser
import sys
import re
import os

usage = "usage: %prog [options]"
version = "0.0.2"

parser = OptionParser(usage=usage, version=version)
parser.add_option('-i', '--vzid', dest='vzid', help="<veid>")
parser.add_option('-m', '--memory', dest='memory', help="Memory in MiB")
parser.add_option('-d', '--diskspace', dest='diskspace', help="Diskspace in GiB")
parser.add_option('-p', '--numproc', dest="numproc", help="Maximal number of processes (~500)")
parser.add_option('-t', '--numtcpsock', dest="numtcpsock", help="Maximal number of tcp sock connections (~550)")
parser.add_option('-o', '--numothersock', dest="numothersock", help="Maximal number of non tcp sock connection (~400)")


(options, args) = parser.parse_args()

number_pattern = re.compile("^[1-9][0-9]*$")

vzid = options.vzid
if vzid == None or not number_pattern.match(vzid):
    parser.error("VZ ID is not valid")

if options.diskspace == None or not number_pattern.match(options.diskspace):
    parser.error("Invalid diskspace parameter")

if options.memory == None or not number_pattern.match(options.memory):
    parser.error("Invalid memory parameter")

if options.numproc == None or not number_pattern.match(options.numproc):
    parser.error("Invalid numproc parameter")

if options.numtcpsock == None or not number_pattern.match(options.numtcpsock):
    parser.error("Invalid numtcpsock parameter")
    
if options.numothersock == None or not number_pattern.match(options.numothersock):
    parser.error("Invalid numothersock parameter")    

MAX_ULONG = str(sys.maxint)

diskspace = int(options.diskspace)*1024
diskspace_limit = diskspace * 110 / 100

inodes = diskspace * 64
inodes_limit = inodes * 110 / 100

numproc = int(options.numproc)           # barrier and limit
numtcpsock = int(options.numtcpsock)        # barrier and limit
numothersock = int(options.numothersock)      # barrier and limit
vmguarpages = int(options.memory)*1024/4    # Speicher in 4KB Seiten limit to MAX_ULONG = 9223372036854775807 

avgnumproc = numproc # Upper limit

numfile = avgnumproc * 32 * 110 / 100 # Documentation says 32
dcachesize = numfile * 384 * 110 / 100 # 
dcachesize_limit = dcachesize * 110 / 100

privvmpages = vmguarpages * 2 # It must be much less than 60% of host memory
privvmpages_limit = privvmpages * 110 / 100 

# Hosteurope sets it to MAX_ULONG
oomguarpages = privvmpages # limit = MAX_ULONG

lockedpages = avgnumproc * 4 # barrier and limit
shmpages = vmguarpages / 4      # barrier and limit
physpages = 0 # limit = MAX_ULONG

numflock = avgnumproc * 2 
numflock_limit = numflock * 110 / 100

numpty = 64 # barrier and limit

numsiginfo = 1024 # barrier and limit // may be reduced

numiptent = 300 # barrier and limit

tcpsndbuf = numtcpsock * 9600
tcpsndbuf_limit = tcpsndbuf + numtcpsock * 3840 

tcprcvbuf = numtcpsock * 9600
tcprcvbuf_limit = tcprcvbuf + numtcpsock * 3840 

othersockbuf = numothersock * 9600
othersockbuf_limit = othersockbuf + numothersock * 3840  

dgramrcvbuf = numothersock * 8960

kmemsize =  40*1024 * avgnumproc + dcachesize_limit + tcpsndbuf_limit + tcprcvbuf_limit + othersockbuf_limit + dgramrcvbuf
kmemsize_limit = kmemsize * 110 / 100


cmd = "vzctl set " + vzid 
cmd += " --numproc " + str(numproc) + ":" + str(numproc)
cmd += " --numtcpsock " + str(numtcpsock) + ":" + str(numtcpsock)
cmd += " --numothersock " + str(numothersock) + ":" + str(numothersock)
cmd += " --vmguarpages " + str(vmguarpages) + ":" + MAX_ULONG

cmd += " --kmemsize " + str(kmemsize) + ":" + str(kmemsize_limit)
cmd += " --tcpsndbuf " + str(tcpsndbuf) + ":" + str(tcpsndbuf_limit)
cmd += " --tcprcvbuf " + str(tcprcvbuf) + ":" + str(tcprcvbuf_limit)
cmd += " --othersockbuf " + str(othersockbuf) + ":" + str(othersockbuf_limit)
cmd += " --dgramrcvbuf " + str(dgramrcvbuf) + ":" + str(dgramrcvbuf)
cmd += " --oomguarpages " + str(oomguarpages) + ":" + MAX_ULONG
cmd += " --privvmpages " + str(privvmpages) + ":" + str(privvmpages_limit)

shmpages
cmd += " --lockedpages " + str(lockedpages) + ":" + str(lockedpages)
cmd += " --shmpages " + str(shmpages) + ":" + str(shmpages)
cmd += " --physpages " + "0" + ":" + MAX_ULONG
cmd += " --numfile " + str(numfile) + ":" + str(numfile)
cmd += " --numflock " + str(numflock) + ":" + str(numflock_limit)
cmd += " --numpty " + str(numpty) + ":" + str(numpty)
cmd += " --numsiginfo " + str(numsiginfo) + ":" + str(numsiginfo)
cmd += " --dcachesize " + str(dcachesize) + ":" + str(dcachesize_limit)
cmd += " --numiptent " + str(numiptent) + ":" + str(numiptent)

cmd += " --diskspace " + str(diskspace) + "M:" + str(diskspace_limit) + "M"

cmd += " --save"

cmd_quota = "vzctl set " + vzid 
cmd_quota += " --diskspace " + str(diskspace) + "M:" + str(diskspace_limit) + "M"
cmd_quota += " --diskinodes " + str(inodes) + ":" + str(inodes_limit)
cmd_quota += " --save"

error = os.system(cmd)
if error != 0:
    print("Could not update parameters")
    sys.exit(1)

error = os.system(cmd_quota)
if error != 0:
    print("Could not update inode limit")
    sys.exit(1)

sys.exit(0)