import docker
import datetime

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

def connect_api(url):
    return docker.APIClient(base_url=url)

def make_row(data):
    print('{0:<30} {1:<20} {2:20} {3:20} {4:20}'
          .format(data['repo'], data['tag'], data['id'], data['created'], data['size']))

def list_images(client):
   header_data = {'repo':'REPOSITORY', 'tag':'TAG', 'id':'ID', 'created':'CREATED', 'size':'SIZE'}
   make_row(header_data)

   for images_info in client.images():
       (repo, tag) = images_info['RepoTags'][0].split(':')
       id = images_info['Id'].split(':')[1][0:12]
       created = calculate_date(images_info['Created'])
       size = convert_bi_size(images_info['Size'])
       image_data = {'repo':repo, 'tag':tag, 'id':id, 'created':created, 'size':size}
       make_row(image_data)

if __name__ == '__main__':
    url = 'unix:///var/run/docker.sock'
    client = connect_api(url)
    list_images(client)
