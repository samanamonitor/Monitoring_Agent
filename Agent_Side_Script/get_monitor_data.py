#! /usr/bin/python
import argparse, urllib2, json
from helpers import mean, getCPUAvg
from datetime import datetime, timedelta

# Setup command line arguments for script
parser = argparse.ArgumentParser(description='Get data from monitor about servers with agents.')

# Define script arguments with descriptions
parser.add_argument('-ID', metavar='<id>', help='The hash code associated with the server for which you would like data for.', type=str, nargs=1)
parser.add_argument('-m', metavar='<data>', help='The data value you would like.', choices=['uptime', 'cpu', 'ram'], type=str, nargs=1)
parser.add_argument('-w', metavar='<warningThreshold>', help='The threshold value that would have to be exceeded to issue a warning.', type=float, nargs=1)
parser.add_argument('-c', metavar='<criticalThreshold>', help='The threshold value that would have to be exceeded to issue a critical warning (should be greater than or equal to <warningThreshold>).', type=float, nargs=1)
parser.add_argument('-u', metavar='<url>', help='URL of monitor', type=str, nargs=1)

# Obtain arguments
args = parser.parse_args()

url = args.u[0] + '/' + args.ID[0]

try:
    # Attempt to retrieve data. Then, load it.
    try:
        res = urllib2.urlopen(url)
    except:
        raise Exception("Connection problem. Check network connection, URL, or ID.")
    data = json.load(res)

    # Make sure that the monitor is up to date.
    if datetime.fromtimestamp(data['post']['UploadTime']) < datetime.now() + timedelta(minutes=-5):
        raise Exception("Monitor data out of date. Check on monitor.")

    if args.m[0] == 'uptime':
        uptime = data['post']['SystemInfo']['Uptime']
        if uptime < args.w[0]:
            print 'OK - Uptime is {}'.format(uptime)
            exit(0)
        elif uptime >= args.w[0] and uptime < args.c[0]:
            print 'WARNING - Uptime is {}'.format(uptime)
            exit(1)
        elif uptime >= args.c[0]:
            print 'CRITICAL - Uptime is {}'.format(uptime)
            exit(2)
    elif args.m[0] == 'cpu':
        cpu = getCPUAvg(data['post']['CPUData'])
        if cpu < args.w[0]:
            print 'OK - CPU usage is {:.2f}%'.format(cpu*100)
            exit(0)
        elif cpu >= args.w[0] and cpu < args.c[0]:
            print 'WARNING - CPU usage is {:.2f}%'.format(cpu*100)
            exit(1)
        elif cpu >= args.c[0]:
            print 'CRITICAL - CPU usage is {:.2f}%'.format(cpu*100)
            exit(2)
    elif args.m[0] == 'ram':
        totalPhysical = float(data['post']['Memory']['TotalPhysical'])
        availablePhysical = float(data['post']['Memory']['AvailablePhysical'])
        ram = (totalPhysical - availablePhysical)/totalPhysical * 100
        if ram < args.w[0]:
            print 'OK - RAM usage is {:.2f}%'.format(ram)
            exit(0)
        elif ram >= args.w[0] and ram < args.c[0]:
            print 'WARNING - RAM usage is {:.2f}%'.format(ram)
            exit(1)
        elif ram >= args.c[0]:
            print 'CRITICAL - RAM usage is {:.2f}%'.format(ram)
            exit(2)
except Exception as e:
    print 'UNKNOWN - ' + str(e)
    exit(3)