import docker
from xlsxwriter import *

def connect_api(url):
    return docker.APIClient(base_url=url)

def convert_bi_size(size):
    byte = size
    kb = 1000
    mb = kb ** 2  # 1,000,000
    gb = kb ** 3  # 1,000,000,000

    if byte < kb:
        return '{0} {1}'.format(byte, 'Bytes' if 0 == byte > 1 else 'Byte')
    elif kb <= byte < mb:
        return '{0:.2f} KB'.format(byte / kb)
    elif mb <= byte < gb:
        return '{0:.2f} MB'.format(byte / mb)
    elif gb:
        return '{0:.2f} GB'.format(byte / gb)

def get_cpu_percentage_linux(id):
   # Get CPU Usage in percentage
    constat = client.stats(id, stream=False)
    prestats = constat['precpu_stats']
    cpustats = constat['cpu_stats']

   # print(cpustats)
   # cpuDelta = res.cpu_stats.cpu_usage.total_usage -  res.precpu_stats.cpu_usage.total_usage;
   # systemDelta = res.cpu_stats.system_cpu_usage - res.precpu_stats.system_cpu_usage;
   # var RESULT_CPU_USAGE = cpuDelta / systemDelta * 100;
   # CPUStats.CPUUsage.PercpuUsage

    prestats_totalusage = prestats['cpu_usage']['total_usage']
    stats_totalusage = cpustats['cpu_usage']['total_usage']
#    num_of_cpu_core = len(cpustats['cpu_usage']['percpu_usage'])
    num_of_cpu_core = cpustats['online_cpus']
    prestats_syscpu = prestats['system_cpu_usage']
    stats_syscpu = cpustats['system_cpu_usage']

    cpuDelta = stats_totalusage - prestats_totalusage
    systemDelta = stats_syscpu - prestats_syscpu

    if cpuDelta > 0 and systemDelta > 0:
        cpupercentage = ((cpuDelta / systemDelta) * num_of_cpu_core) * 100.0
    return '{0:.2f}%'.format(cpupercentage)

def get_mem_percentage_linux(id):
    constat = client.stats(id, stream=False)
    memstats = constat['memory_stats']
    max_usage = memstats['limit']
    mem_usage = memstats['usage']
    mem_percentage = (mem_usage / max_usage) * 100.0
    mem_data = [convert_bi_size(mem_usage), convert_bi_size(max_usage), '{0:.2f}%'.format(mem_percentage)]
    return mem_data

def get_networks_linx(id):
    constat = client.stats(id, stream=False)
#   will make some check point where is network interface
#    network_info = constat['networks']
#    if 'eth0' in network_info: >> after check
    rx_bytest = constat['networks']['eth0']['rx_bytes']
    tx_bytest = constat['networks']['eth0']['tx_bytes']
    networks_data = [convert_bi_size(rx_bytest), convert_bi_size(tx_bytest)]
    return networks_data


def get_block_linux(id):
    constat = client.stats(id, stream=False)
    blk_stats = constat['blkio_stats']['io_service_bytes_recursive']
    blk_read_stats = blk_stats[0]['value']
    blk_wirte_stats = blk_stats[1]['value']
    blk_data = [convert_bi_size(blk_read_stats), convert_bi_size(blk_wirte_stats)]
    return blk_data

def get_pid_linux(id):
    constat = client.stats(id, stream=False)
    pid_stats = constat['pids_stats']['current']
    return pid_stats

def make_row(data):
    print('{0:<20} {1:<20} {2:20} {3:20} {4:20} {5:20} {6}'
          .format(data['container id'], data['cpu%'], data['mem useage / limit'], data['mem%'],
                  data['net i/o'], data['block i/o'], data['pids']))

if __name__ == '__main__':
    url = 'unix:///var/run/docker.sock'
    client = connect_api(url)
    header_data = {'container id': 'CONTAINER ID', 'cpu%': 'CPU %', 'mem useage / limit': 'MEM USAGE / LIMIT',
                   'mem%': 'MEM %', 'net i/o': 'NET I/O', 'block i/o': 'BLOCK I/O', 'pids': 'PIDS'}
    make_row(header_data)
    for container_info in client.containers():
        container_id = container_info['Id'][0:12]
        cpu_percentage = get_cpu_percentage_linux(container_id)
        mem_info = get_mem_percentage_linux(container_id)
        net_info = get_networks_linx(container_id)
        block_info = get_block_linux(container_id)
        pids_info = get_pid_linux(container_id)

        list_data = {'container id': container_id, 'cpu%': cpu_percentage, 'mem useage / limit': '{0} / {1}'.format(mem_info[0], mem_info[1]),
                     'mem%': '{0}'.format(mem_info[2]), 'net i/o': '{0} / {1}'.format(net_info[0], net_info[1]),
                     'block i/o': '{0} / {1}'.format(block_info[0], block_info[1]), 'pids': pids_info}
        make_row(list_data)

        workbook = workbook('stats.xlsx')
        worksheet = worksheet.add_wrosheet()
        rows = make_row(list_data)

        columns = rows.split()
        for col_inx, col in enumerate(columns):
            worksheet.write(0, col_inx, col)

        workbook.close()
