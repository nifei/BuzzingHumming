import subprocess
#rom In
#output = subprocess.call('./input.sh', shell=True)

HorizonLength = 1
Config_Loss_Small_Interval = 5 # collect data every second
# time based on out time

class Packet:
    def __init__(self):
        self.key = None
        pass
    def InMergeOut(self, out):
        self.time_in = self.time
        self.time_out = out.time
        return self
    def OutMergeIn(self, _in):
        self.time_out = self.time
        self.time_in = _in.time
        return self

def ParsePcap(pcap, ip1, ip2):
    cmd_line = 'tshark -r ' + pcap + ' -T fields -e frame.time_epoch -e ip.id -e frame.protocols -e frame.cap_len -R "((ip.src==' + ip1 + '&&ip.dst==' + ip2 + '))" -E separator=";" -E quote=d'
    proc = subprocess.Popen(cmd_line, stdout=subprocess.PIPE, shell=True)
    while True:
        line = proc.stdout.readline()
        if line != '':
            vals = line.split(';')
            vals = [val.rstrip('\n').lstrip('"').rstrip('"') for val in vals]
            packet = Packet()
            ipid = vals[1]
            prot = vals[2]
            cap_len = int(vals[3])
            packet.key = (ipid, prot)#, cap_len)
            packet.id = ipid
            packet.time = float(vals[0])
            packet.length = cap_len
            yield packet
        else:
            break

def MergePcap1(pcap_out, pcap_in, ip_out, ip_in):
    In = ParsePcap(pcap_in, ip_out, ip_in)
    Out = ParsePcap(pcap_out, ip_out, ip_in)
    unmatched_out, unmatched_in = {}, {}
    stop_in = False
    stop_out = False
    out_lead_in = 0
    start_time_out = None
    while ((not stop_in) or (not stop_out)):
        packet_match, packet_out, packet_in = None, None, None
        if not stop_out:
            try:
                packet_out = Out.next()
            except StopIteration:
                stop_out = True
        if (not stop_in):
            try:
                packet_in = In.next()
            except StopIteration:
                stop_in = True
        if packet_out and packet_in and packet_out.key == packet_in.key:
            packet_match = packet_out.OutMergeIn(packet_in)
        else:
            out_key_in_in_dict, in_key_in_out_dict = False, False
            if packet_out:
                if packet_out.key in unmatched_in.keys():
                    if abs(unmatched_in[packet_out.key].time - packet_out.time) < HorizonLength:
                        out_key_in_in_dict = True
                if out_key_in_in_dict:
                    packet_match = packet_out.OutMergeIn(unmatched_in[packet_out.key])
                    unmatched_in.pop(packet_out.key, None)
                    #for key in unmatched_out.keys():
                    #    if packet_match.time_out - unmatched_out[key].time > HorizonLength:
                    #        unmatched_out.pop(key, None)
                else:
                    unmatched_out[packet_out.key] = packet_out
                    pass
            if packet_in:
                if packet_in.key in unmatched_out.keys():
                    if abs(packet_in.time - unmatched_out[packet_in.key].time) < HorizonLength:
                        in_key_in_out_dict = True
                if in_key_in_out_dict:
                    packet_match = packet_in.InMergeOut(unmatched_out[packet_in.key])
                    unmatched_out.pop(packet_in.key, None)
                    #for key in unmatched_in.keys():
                    #    if packet_match.time_in - unmatched_in[key].time > HorizonLength:
                    #        unmatched_in.pop(key, None)
                    pass
                else:
                    unmatched_in[packet_in.key] = packet_in
                    pass

        if packet_match:
            yield {'key':packet_match.key, 'delay':packet_match.time_in - packet_match.time_out, 'out':packet_match.time_out}
            if start_time_out == None or start_time_out - packet_match.time_out > Config_Loss_Small_Interval:
                # clear un found keys
                if start_time_out != None:
                    # summary un received packet in out
                    un_received_packet_in_out = len(unmatched_out)
                    pass #yield loss_rate

                for (key, packet) in unmatched_out.items():
                    if packet_match.time_out - packet.time > Config_Loss_Small_Interval:
                        unmatched_out.pop(key, None)
                for (key, packet) in unmatched_in.items():
                    if packet_match.time_in - packet.time > Config_Loss_Small_Interval:
                        unmatched_in.pop(key, None)
                start_time_out = packet_match.time_out
