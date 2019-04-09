#!/usr/bin/env python3
import time
import requests
import json
import os

path = os.path.split(os.path.realpath(__file__))[0] + os.path.sep  # 脚本根目录


def log(level, message):
    with open(path + "log.txt", "a") as file:
        file.write("%s %s: %s\n" % (
            "[INFO]" if level == 0 else "[WARN]",
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            message))
        print("%s %s" % ("[INFO]" if level == 0 else "[WARN]", message))


def config_reader():
    if os.path.exists(path + "config.json"):
        try:
            with open(path + "config.json", "r") as file:
                config = json.load(file)
                return config
        except Exception as exception:
            log(-1, repr(exception))
            exit(0)
    log(-1, "`config.json` not found")
    exit(-1)


def config_writer(config):
    try:
        with open(path + "config.json", "w") as file:
            file.write(json.dumps(config, indent=4))
            log(0, "IP updated: %s" % config['ip_current'])
    except Exception as exception:
        log(-1, repr(exception))
        exit(-1)


def request_dnspod(config):
    json_response = requests.api.post('https://dnsapi.cn/Record.Ddns', data={
        'login_token': "%s,%s" % (config['ID'], config['token']),
        'format': 'json',
        'domain_id': config['domain_id'],
        'record_id': config['record_id'],
        'sub_domain': config['sub_domain'],
        'record_line': "默认",
        'value': config['ip_current']
    }).json()
    message = json_response['status']['message']
    log(0, "Message from DNSPOD: " + message)
    return message == "Action completed successful"


def get_ip():
    address = "http://lan.upc.edu.cn/eportal/InterFace.do?method=getOnlineUserInfo"  # 有线
    # address = "http://wlan.upc.edu.cn/eportal/InterFace.do?method=getOnlineUserInfo"  #无线
    return requests.api.get(address).json()['userIp']


if __name__ == '__main__':
    try:
        config = config_reader()
        log(0, "IP from `config.json`: %s" % config['ip_current'])
        ip_eportal = get_ip()
        log(0, "IP from ePortal: " + ip_eportal)
        if config['ip_current'] != ip_eportal:
            config['ip_current'] = ip_eportal
            if request_dnspod(config):
                config_writer(config)
            else:
                log(-1, "Something Wrong, please see the log.txt file at: %s" % path + "log.txt")
        else:
            log(0, "Nothing different with IP from `config.json` and ePortal")
    except Exception as exception:
        log(-1, repr(exception))
        exit(-1)
