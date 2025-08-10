# Security Policy


## Reporting a Vulnerability

Send an email or submit an github issue if you see a vulnerability that **SHOULD** be addressed.

## Security Information

I advocate for better and [simple security](simplifysecurity.nocomplexity.com), so this tool is reviewed to identify potential vulnerabilities.

Result of scan with [Bandit](https://bandit.readthedocs.io/):
```
blacklist: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
Test ID: B310
Severity: MEDIUM
Confidence: HIGH
```
For details on `B310` see this [page in the Bandit manual](https://bandit.readthedocs.io/en/1.8.3/blacklists/blacklist_calls.html#b310-urllib-urlopen).


Checking the status of an URL requires using a construct like:
```python
request = Request(url, headers=nocxheaders)
	            with urlopen(request, timeout=nocxtimeout) as response:
	                return url, response.status
```

Mitigation to your judgement:
* Content of URLs is not processed.
* Only the DNS or HTTP status of an URL is verified.
* Use of external libraries, like `requests` or `aiohttp` is deliberately avoided.

