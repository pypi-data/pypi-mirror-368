import http.client
import json

def get_app_version():
    return '0.23.5'

def check_app_is_latest():
    pass
    # contact API to examine version

    # This is slow, which will make the CLI annoying to use. This means
    # we need an approach that can try to do this in the background and then
    # caches somewhere so that the user is notified on the next run

    # api_url = 'zn5boqqk60.execute-api.us-east-1.amazonaws.com'

    # connection = http.client.HTTPSConnection(api_url)
    # headers = {'Content-type': 'application/json'}
    # body = json.dumps({'hello': 'hello'}).encode('utf-8')
    # connection.request('POST', '/test', body, headers)
    # response = connection.getresponse()
    # if response.status != 200:
    #     print('response had status code {}'.format(response))
    # print('{}'.format(response.read().decode('utf-8')))