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
       created = datetime.datetime.fromtimestamp(images_info['Created']).strftime('%d')
       size = convert_bi_size(images_info['Size'])
       image_data = {'repo':repo, 'tag':tag, 'id':id, 'created':created, 'size':size}

       make_row(image_data)

if __name__ == '__main__':
    url = 'unix:///var/run/docker.sock'
    client = connect_api(url)
    list_images(client)
