import os
os.environ['no_proxy'] = '10.11.20.251'
os.environ['NO_PROXY'] = '10.11.20.251'

from stormshield.sns.sslclient import SSLClient

c = SSLClient(
    host='10.11.20.251',
    user='admin',
    password='Azerty01!',
    sslverifypeer=False,
    sslverifyhost=False
)
ret = c.send_command('CONFIG OBJECT HOST NEW update=1 name=TEST_ANSIBLE ip=1.2.3.4 comment="test"')
print(ret)
c.disconnect()
