import parse

Test = parse.ParsePcap('Logs/in.pcapng', '192.168.91.253', '192.168.91.64')

for item in Test:
    pass#print item
