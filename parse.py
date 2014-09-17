import subprocess
#rom In
#output = subprocess.call('./input.sh', shell=True)

HorizonLength = 0.001

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
            ipid = int(vals[1], 16) if vals[1].startswith('0x') else int(vals[1], 10)
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
    timestamp_out = 0
    stop_in = False
    stop_out = False
    lead_in = 0 
    lead_out = 0
    match_case = 'Sync'
    first = True
    while ((not stop_in) and (not stop_out)):
        new_case = match_case
        packet_match, packet_out, packet_in = None, None, None
        if not stop_out and match_case !='OutLead':
            try:
                packet_out = Out.next()
                lead_in = lead_in - 1
            except StopIteration:
                stop_out = True
        if (not stop_in) and match_case!='InLead':
            try:
                packet_in = In.next()
                lead_out = lead_out - 1
            except StopIteration:
                stop_in = True
        if packet_out and packet_in and packet_out.key == packet_in.key:
            packet_match = packet_out.OutMergeIn(packet_in)
            new_case = 'Sync'
        else:
            if packet_out and packet_out.key in unmatched_in.keys():
                packet_match = packet_out.OutMergeIn(unmatched_in[packet_out.key])
                unmatched_in.pop(packet_out.key, None)
                current_time = packet_match.time_out
                for key in unmatched_out.keys():
                    if current_time - unmatched_out[key].time > HorizonLength:
                        unmatched_out.pop(key, None)
                new_case = 'InLead'
            elif packet_out:
                unmatched_out[packet_out.key] = packet_out
            if packet_in and packet_in.key in unmatched_out.keys():
                packet_match = packet_in.InMergeOut(unmatched_out[packet_in.key])
                unmatched_out.pop(packet_in.key, None)
                current_time = packet_match.time_in
                for key in unmatched_in.keys():
                    if current_time - unmatched_in[key].time > HorizonLength:
                        unmatched_in.pop(key, None)
                new_case = 'OutLead'
            elif packet_in:
                unmatched_in[packet_in.key] = packet_in
            lead_in = len(unmatched_in)
            lead_out = len(unmatched_out)
            if new_case == 'InLead' and lead_in == 0:
                new_case = 'Sync'
            if new_case == 'OutLead' and lead_out == 0:
                new_case = 'Sync'

        if packet_match:
            yield {'key':packet_match.key, 'delay':packet_match.time_in - packet_match.time_out, 'out':packet_match.time_out}
        if new_case != match_case:
            print match_case + '->' + new_case
            match_case = new_case
