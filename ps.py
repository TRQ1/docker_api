import docker
import datetime

def connect_api(url):
    return docker.APIClient(base_url=url)

def calculate_date(created):
    format_type = '%d%m%Y:%H:%M:%S'
    today = datetime.datetime.today().timetuple()
    created_date = datetime.datetime.fromtimestamp(created).timetuple()
    start = '{0}{1}{2}:{3}:{4}:{5}'.format(created_date.tm_mday, created_date.tm_mon, created_date.tm_year,
                             created_date.tm_hour, created_date.tm_min, created_date.tm_sec)
    end = '{0}{1}{2}:{3}:{4}:{5}'.format(today.tm_mday, today.tm_mon, today.tm_year, today.tm_hour, today.tm_min, today.tm_sec)
    start_date = datetime.datetime.strptime(start, format_type)
    end_date = datetime.datetime.strptime(end, format_type)
    subtraction_date = int((end_date - start_date).total_seconds())

    if subtraction_date < 0:
        raise ValueError('This date is worng')
    elif 0 <= subtraction_date <= 60:
        return '{0} seconds ago'.format(subtraction_date)
    elif 60 < subtraction_date <= 3600:
        return '{0} minutes ago'.format(subtraction_date//60)
    elif 3600 < subtraction_date <= 86400:
        return '{0} hours ago'.format(subtraction_date//3600)
    elif 86400 < subtraction_date <= 604800:
        return '{0} days ago'.format(subtraction_date//86400)
    elif 604800 < subtraction_date <= 2419200:
        return '{0} weeks ago'.format(subtraction_date//604800)
    else:
        return '{0} months ago'.format(subtraction_date//2419200)

def make_row(data):
    print('{0:<20} {1:<30} {2:<24} {3:<20} {4:<20} {5:<20} {6:<20}'
          .format(data['container id'], data['image'], data['command'], data['created'], data['status'], data['ports'], data['names']))

def list_container(client):
    header_data = {'container id':'CONTAINER ID', 'image':'IMAGE', 'command':'COMMAND', 'created':'CREATED', 'status':'STATUS',
                   'ports':'PORTS', 'names':'NAMES'}
    make_row(header_data)

    for list_info in client.containers():
        id = list_info['Id'][0:12]
        image = list_info['Image']
        beforecommand = list_info['Command'][0:17]
        command = '{0}{1}{2}{3}'.format('"', beforecommand, '...', '"')
        created = calculate_date(list_info['Created'])
        status = list_info['Status']
        ports = ''.join(list_info['Ports'])
        names = ''.join(list_info['Names']).strip('/')
        list_data = {'container id':id, 'image':image,'command':command, 'created':created,
                     'status':status, 'ports':ports, 'names':names}
        make_row(list_data)
        type(created)

if __name__ == '__main__':
    url = 'unix:///var/run/docker.sock'
    client = connect_api(url)
    list_container(client)
