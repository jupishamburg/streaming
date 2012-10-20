loadbalancer
============
This thingy is to balance the load between the icecast servers.

Setup
-----
1.  Copy the *json.xsl* into the root of the web-directory of your icecast
2.  Install all requirements of the python-script: `# pip install -r requirements.txt`
3.  Put your servers and max-listeners values into the config-dictionary in the *balancer.py*
4.  Run the *balancer.py* with Python 3: `$ python balancer.py`

Use
---
At the index (*/*) you can find some statistics about your relays.

The loadbalancing is handled by playlists which are reachable by *`/<mountpoint name with file ending>.m3u`*. The order of the servers in this 
playlist 
is ordered by the number of free listener slots.

Credits
-------
*  [Eugene MechanisM][0] for his [json.xsl][1]

[0]: http://mechanism.name/
[1]: https://github.com/MechanisM/jquery-icecast/blob/master/web/json.xsl
