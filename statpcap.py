import parse

Config_Stat_Interval = 5
Config_Stat_Small_Interval = 1

def StatPcap0(pcap_out, pcap_in, ip_out, ip_in):
    delay_list_small_interval = []
    delay_count_small_interval = 0
    last_stat_time = None
    delay_sum_small_interval = 0
    for item in parse.MergePcap(pcap_out, pcap_in, ip_out, ip_in):
        if 'delay' in item.keys():
            time = item['out']
            delay = item ['delay']
            if last_stat_time == None:
                last_stat_time = time
                delay_sum_small_interval = delay
                delay_count_small_interval = 1
                last_stat_time = time
            elif time - last_stat_time > Config_Stat_Small_Interval:
                delay_list_small_interval.append({'time':time, 'delay_sum_small_interval':delay_sum_small_interval, 'delay_count_small_interval':delay_count_small_interval})
                average_delay = float(delay_sum_small_interval) / float(delay_count_small_interval)
#                print time, average_delay
                yield {'out':time, 'delay':average_delay}
                delay_sum_small_interval = delay
                delay_count_small_interval = 1
                last_stat_time = time
            else:
                delay_sum_small_interval = delay_sum_small_interval + delay
                delay_count_small_interval = delay_count_small_interval + 1
        else:
            yield item
StatPcap = StatPcap0

















