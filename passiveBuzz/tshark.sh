#tshark -r Logs/out.pcapng -T fields -e frame.time_epoch -e ip.id -e udp.port -e tcp.port -R '((ip.src==192.168.91.253&&ip.dst==192.168.91.64)||(ip.src==192.168.91.64&&ip.dst==192.168.91.253))' -E separator=',' -E quote=d
tshark -r Logs/in.pcapng -T fields -e frame.time_epoch -e ip.id -e udp.port -e tcp.port -R '(udp&&(ip.src==192.168.91.253&&ip.dst==192.168.91.64)||(ip.src==192.168.91.64&&ip.dst==192.168.91.253))' -E separator=',' -E quote=d
