import nonebot
from os import path
from qbotor import config


def start(_host):
    nonebot.init(config)
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'plugins'),
        'qbotor.plugins'
    )
    nonebot.run(host=_host, port=5700)


if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_plugins(
        path.join(path.dirname(__file__), 'plugins'),
        'qbotor.plugins'
    )

    nonebot.run(host='10.0.0.2', port=5700)
