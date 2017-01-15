import memcache
import redis
import telnetlib
from .li_tabulate import tabulate
from tools.config import get_config_data
from tools.utils import bcolors


def run_service(service, key):

    print((
        "\n{}{}>> Chaves do {}".format(
            bcolors.BOLD,
            bcolors.WARNING,
            service.upper())))
    print(("********************{}\n".format(bcolors.ENDC)))

    data = get_config_data()
    if not data:
        return False

    if service == "redis":
        key_list = get_all_redis_keys(data, key)
    else:
        key_list = get_all_memcached_keys(data, key)

    print((tabulate(
        key_list,
        headers=["Chave", "Valor"]
    )))


def get_all_redis_keys(data, key):
    conn = redis.StrictRedis(
        host=data['redis_host'],
        port=data['redis_port'],
        db=data['redis_db']
    )
    pattern = "*{}*".format(key) if key else "*"
    all_keys = set()
    for k in conn.scan_iter(pattern):
        if k not in all_keys:
            all_keys.add(k)
    all_keys = sorted(list(all_keys))

    key_list = []
    for k in all_keys:
        try:
            value = conn.get(k)
            if value:
                value = value.decode('utf-8')
            else:
                value = '--'
        except:
            chave = k.decode('utf-8')
            if '_kombu' in chave:
                value = '--'
            else:
                value = "Erro ao tentar recuperar o valor"
        key_list.append((k, value))

    return key_list


def get_all_memcached_keys(data, k):
    t = telnetlib.Telnet(
        data['memcached_host'],
        int(data['memcached_port']))
    t.write('stats items STAT items:0:number 0 END\n'.encode('ascii'))
    items = t.read_until('END'.encode('ascii')).split('\r\n'.encode('ascii'))
    keys = set()
    for item in items:
        item = item.decode('ascii')
        parts = item.split(':')
        if not len(parts) >= 3:
            continue
        slab = parts[1]
        t.write('stats cachedump {} 200000 ITEM '
                'views.decorators.cache.cache_header..cc7d9 '
                '[6 b; 1256056128 s] END\n'.format(
                    slab).encode('ascii'))
        cachelines = t.read_until(
            'END'.encode('ascii')).split(
            '\r\n'.encode('ascii'))
        for line in cachelines:
            line = line.decode('ascii')
            parts = line.split(' ')
            if not len(parts) >= 3:
                continue
            if not k or k in parts[1]:
                keys.add(parts[1])
    t.close()
    all_keys = sorted(list(keys))

    mc = memcache.Client(
        [
            '{}:{}'.format(data['memcached_host'], data['memcached_port'])
        ], debug=0
    )

    key_list = []
    for ky in all_keys:
        try:
            value = mc.get(ky) or '--'
        except:
            value = "Erro ao tentar recuperar o valor"
        key_list.append((ky, value))

    return key_list
