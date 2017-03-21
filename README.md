# AmpliSpy
Check local or remote list of DNS servers for suitability in DNS Amplification DoS.

AmpliSpy checks a list of name server IPs and to see if a server responds for a zone for which it is none authoritative. You can provide the program with a local list of name server IPs or you can set the `--remote` option to fetch a list of name servers from public-dns.info.

## Usage

Cloning the repo.

```
git clone https://github.com/NullArray/AmpliSpy.git
cd AmpliSpy
python amplispy.py
```
The options for the program are as follows.

```
-h, --help                show this help message and exit
-l LOCAL, --local LOCAL   select locally saved list of name servers
-r, --remote              fetch remote list of name servers from public-dns.info
-u URL, --url URL         provide the URL for a domain to test against
```

Please also see some examples for clarity below.

```
amplispy.py -h
amplispy.py -l /tmp/dns_list.txt --url target.com 
```

Once the program is done it will save the results to a file called amplispy.log for further processing when desired.

### Dependencies

The mechanize lib is used to fetch the remote list of name servers and I used the blessings module in this script for formatting purposes, should you find you don't have these installed please use `pip` with the following commands to install it.

```
pip install blessings`
pip install mechanize
```
