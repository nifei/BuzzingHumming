import parse

Test = parse.ParsePcap('/home/dejavu/git/BuzzingHumming/Logs/out.pcap', '192.168.91.253', '192.168.91.64')

for item in Test:
    print item
