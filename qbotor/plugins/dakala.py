from aiocqhttp import MessageSegment
from nonebot import on_command, CommandSession
import userdb
import json
from daka import async_dakala
from os import path

father_path = path.abspath(path.dirname(__file__) + path.sep + ".." + path.sep + "..")
IMAGE_LOCATION = path.join(father_path, "static", "vc_images")


def check_register_info(stuinfo) -> bool:
    if len(stuinfo) != 2:
        return False
    return True


def get_image_uri(stuid) -> str:
    print(f'{IMAGE_LOCATION}/{stuid}_img.png')
    return f'{IMAGE_LOCATION}/{stuid}_img.png'


# on_command 装饰器将函数声明为一个命令处理器
# 这里 weather 为命令的名字，同时允许使用别名「天气」「天气预报」「查天气」
@on_command('daka_exec', aliases=('疫情打卡', '打卡'))
async def daka_command(session: CommandSession):
    # 从会话状态（session.state）中获取城市名称（city），如果当前不存在，则询问用户
    # session.get('')
    stripped_arg = session.current_arg_text.strip()
    session.state[session.current_key] = stripped_arg
    qqid = str(session.ctx['user_id'])
    _target = userdb.db_get_user_qq_id(qqid)
    if _target is not None:
        flag = await daka_worker(_target,"/Users/yulinfeng/Docker/coolq/data/image")
        stuid = _target['stuid']
        if flag:
            message = f"{stuid} - 打卡成功"
        else:
            message = f"{stuid} - 打卡失败"
    else:
        message = "请私聊机器人以格式\n\n 打卡注册  学号#密码 \n\n进行注册打卡"

    # city = session.get('city', prompt=f'你想查询哪个城市的天气呢？{qqnum}')
    # 获取城市的天气预报
    # 向用户发送天气预报

    await session.send(message)


async def daka_worker(student,coolq_image_location) -> bool:
    return await async_dakala(student, config=None,image_location=coolq_image_location)


@on_command('daka_register', aliases=('打卡注册', '疫情打卡注册'))
async def daka_register(session: CommandSession):
    info = session.get('info', prompt='请继续以格式\n\n 学号#密码 \n\n发送您的信息～')
    print(info)
    stuinfo = info.split("#")
    if check_register_info(stuinfo):
        qqid = str(session.ctx['user_id'])
        userdb.db_put_user_qq_id(qqid, stuinfo)
    else:
        message = "注册失败"
        await session.send(message)

    await session.send(json.dumps({
        'stuid': stuinfo[0],
        'password': stuinfo[1]
    }))


@on_command('daka_delete', aliases=('删除打卡信息', '删除信息'))
async def daka_delete(session: CommandSession):
    qqid = str(session.ctx['user_id'])
    userdb.db_delete_user_qq_id(qqid)
    await session.send("删除成功")


# daka_register.args_parser 装饰器将函数声明为 weather 命令的参数解析器
# 命令解析器用于将用户输入的参数解析成命令真正需要的数据
@daka_register.args_parser
async def _daka_register_before(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将城市名跟在命令名后面，作为参数传入
            # 例如用户可能发送了：天气 南京
            session.state['info'] = stripped_arg
        return

    if not stripped_arg:
        # 用户没有发送有效的城市名称（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('请输入注册信息')

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg
