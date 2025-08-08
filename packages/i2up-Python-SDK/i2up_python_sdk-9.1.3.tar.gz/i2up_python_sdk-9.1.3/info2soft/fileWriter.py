import os
import json


def write(information, module, method, body=None):
    path = os.getcwd()
    print(path)
    file = open(path + '/{0}TestResults.txt'.format(module), mode='a', encoding='UTF-8')
    file.write('<START-----------------------------------------------------------\n')
    file.write('Method: ' + method + '\n')
    file.write('body: ' + json.dumps(body, indent=1))
    file.write('\n')
    file.write('response: ' + json.dumps(information, indent=1) + '\n')
    file.write('-----------------------------------------------------------END>\n')
    file.write('\n')
    file.close()
