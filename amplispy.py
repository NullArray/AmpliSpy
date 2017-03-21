#!/usr/bin/env Python2.7

import sys
import argparse
import random
import mechanize
import dns.resolver

from time import sleep
from blessings import Terminal

t = Terminal()

# Input validation, usage
if not len(sys.argv[1:]):
   print t.cyan("""
   _                   _ _ __             
  /_\  _ __ ___  _ __ | (_) _\_ __   _   _ 
 //_\\\| '_ ` _ \| '_ \| | \ \  |'_ \| | | |
/  _  \ | | | | | |_) | | |\ \ |_)  | |_| |
\_/ \_/_| |_| |_| .__/|_|_\__/  .__/ \__, |
                |_|          |_|     |___/ 
   
Welcome to AmpliSpy
   
The purpose of this program is to check a local or remote list of DNS servers
for potential suitability with DNS Amplification attacks. 

The program comes with the option to provide your own custom DNS server list
or to fetch one remotely from public-dns.info.

Type -h or --help to display all options.


Example:
amplispy.py -h
amplispy.py -l /tmp/dns_list.txt --url target.com """)
   
   sys.exit(0)
    
# Handle command line arguments
parser = argparse.ArgumentParser(description="			probe for DNS AMP suitable servers.\n")
group = parser.add_mutually_exclusive_group()

group.add_argument("-l", "--local", help="			select locally saved list of name servers\n")
group.add_argument("-r", "--remote", action="store_true", help="fetch remote list of name servers from public-dns.info\n")
parser.add_argument("-u", "--url", help="			provide the URL for a domain to test against\n")

args = parser.parse_args()

if not args.url:
	print "\n[" + t.red("!") + "]Critical, the '-u' option is mandatory.\n"
	sys.exit(1)

# Random user-agent selector
def select_UA():
	UAs = ["'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'",
		   "'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'",
		   "'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'",
		   "'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'",
		   "'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'",
		   "'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/602.3.12 (KHTML, like Gecko) Version/10.0.2 Safari/602.3.12'",
		   "'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'",
		   "'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'",
		   "'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'",
		   "'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'"
		   ]
	return random.choice(tuple(UAs))

# Fetch list
def mech_ops():
	br = mechanize.Browser()
	br.set_handle_robots(False)
	br.addheaders = [('user-agent', select_UA()), ('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]

	try:
		response = br.open("http://www.public-dns.info/nameservers.txt")
	except Exception as e:
		print "\n[" + t.red("!") + "]Critical, could not open punblic-dns.info"
		print "[" + t.green("+") + "]The following status code was recieved: \n"
		print e
		sys.exit(1)
	
	result = response.read()
	proc = result.rstrip().split('\n')	
	return proc


# If args, read list, else fetch
if args.local:
	RHOSTS = []
	
	print "\n[" + t.green("+") + "]Reading in list from: " + args.local + "\n"	
	
	try:
		with open(args.local, "r") as infile:
			for line in infile:
				RHOSTS.append(line)
								
	except IOError as e:
		print "\n[" + t.red("!") + "]Critical. Unable to read list"
		print "An IO Error was raised with the following error message: "
		print "\n %s" % (e)
            
else:
	RHOSTS = mech_ops()


known_pubs = {"8.8.8.8","8.8.4.4","209.244.0.3","209.244.0.4",
"64.6.64.6","64.6.65.6","84.200.69.80","84.200.70.40","8.26.56.26",
"8.20.247.20","208.67.222.222","208.67.220.220","156.154.70.1",
"156.154.71.1","199.85.126.10","199.85.127.10","81.218.119.11",
"209.88.198.133","195.46.39.39","195.46.39.40","50.116.23.211",
"107.170.95.180","208.76.50.50","208.76.51.51", "216.146.35.35",
"216.146.36.36","37.235.1.174","37.235.1.177","198.101.242.72",
"23.253.163.53","77.88.8.8","77.88.8.1","91.239.100.100",
"74.82.42.42","109.69.8.51"}

R_checked = []


# Validate
def query(address):
    dnsserver = address
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [dnsserver]
   
    try:
        answer = resolver.query(args.url, "A")
        return True
    
    except dns.resolver.NoNameservers:
	return False    
    except dns.resolver.NoAnswer:
        return False
    except dns.resolver.NXDOMAIN:
        return False
    except dns.exception.Timeout:
        return False


# Sort
def start(known_pubs):
	pub = ""
	delay = raw_input("[" + t.magenta("?") + "]Set delay? (default is 0): ")
	
	if delay == "" or delay == "0":
		delay = 0
	else:
		delay = int(delay)
	print "\n[" + t.green("+") + "]Potentially Vulnerable Servers:\n"
	
	for address in RHOSTS:  
		if address in known_pubs:
			pub = True
		else:
			pub = False
		if not pub:
			valid = query(address)
			if valid:
				print address
				R_checked.append(address)
			else:
				continue
		elif pub:
			continue
				
		sleep(delay)

start(known_pubs)

with open("amplispy.log", "w") as outfile:
	for item in R_checked:
		outfile.write("%s\n" % item)
		
print "\n[" + t.green("+") + "]Done. Results saved to %s in the current directory" %  outfile
