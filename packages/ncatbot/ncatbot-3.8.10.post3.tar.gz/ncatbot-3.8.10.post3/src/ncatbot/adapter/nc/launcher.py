"""测试内容
Windows:
 - 纯裸机安装启动(扫码登录)
 - NapCat 安装但未运行启动(快速登录, 需要手机确认)
Linux:
 - 纯裸机安装启动(扫码登录)
 - NapCat 安装但未运行启动(快速登录)
跨平台:
 - 远端模式启动(插件无数据)
 - NapCat 安装且运行启动(插件有数据)
"""

import asyncio
import platform
import time

from ncatbot.adapter.nc.install import install_or_update_napcat
from ncatbot.adapter.nc.login import login, report_login_status
from ncatbot.adapter.nc.start import start_napcat, stop_napcat
from ncatbot.adapter.net import check_websocket
from ncatbot.utils import config, get_log

LOG = get_log("adapter.nc.launcher")


def napcat_service_ok(EXPIRE=0):
    if EXPIRE == 0:
        return asyncio.run(check_websocket(config.ws_uri))
    else:
        MAX_TIME_EXPIRE = time.time() + EXPIRE
        while not napcat_service_ok():
            if time.time() > MAX_TIME_EXPIRE:
                return False
            time.sleep(0.5)


def connect_napcat():
    """启动并尝试连接 napcat 直到成功"""

    def info_windows():
        LOG.info("===请允许终端修改计算机, 并在弹出的另一个终端扫码登录===")
        LOG.info(f"===确认 bot QQ 号 {config.bt_uin} 是否正确===")

    def info(quit=False):
        LOG.info("连接 napcat websocket 服务器超时, 请检查以下内容:")
        if platform.system() == "Windows":
            info_windows()
        elif platform.system() == "Linux":
            pass
        else:
            pass
        LOG.info(f"===websocket url 是否正确: {config.ws_uri}===")
        if quit:
            raise Exception("连接超时")

    MAX_TIME_EXPIRE = time.time() + 60
    # INFO_TIME_EXPIRE = time.time() + 20
    LOG.info("正在连接 napcat websocket 服务器...")
    while not napcat_service_ok():
        time.sleep(0.05)
        if time.time() > MAX_TIME_EXPIRE:
            info(True)

    LOG.info("连接 napcat websocket 服务器成功!")


def napcat_service_remote_start():
    """尝试以远程模式连接到 NapCat 服务"""
    if napcat_service_ok():
        LOG.info(f"napcat 服务器 {config.ws_uri} 在线, 连接中...")
        if not config.enable_webui_interaction:  # 跳过基于 WebUI 交互的检查
            LOG.warning(
                f"跳过基于 WebUI 交互的检查, 请自行确保 NapCat 已经登录了正确的 QQ {config.bt_uin}"
            )
            return True
        status = report_login_status()
        if status == 0:
            return True
        else:
            if status == 3:
                LOG.error("登录状态异常, 请检查远端 NapCat 服务")
                LOG.error("对运行 NapCat 的服务器进行物理重启一般能解决该问题")
                raise Exception("登录状态异常, 请检查远端 NapCat 服务")
            if status == 2:
                LOG.error(
                    f"登录的 QQ 号 {config.bt_uin} 与配置的 QQ 号不匹配, 请检查远端 NapCat 服务"
                )
                raise Exception(
                    "登录的 QQ 号与配置的 QQ 号不匹配, 请检查远端 NapCat 服务"
                )
            if status == 1:
                LOG.error("远端 NapCat 服务未登录, 请完成登录流程")

    LOG.info("NapCat 服务器离线或未登录")
    return False


def launch_napcat_service(*args, **kwargs):
    """
    启动配置中 QQ 对应的 NapCat 服务, 保证 WebSocket 接口可用, 包括以下任务:

    1. 安装或者更新 NapCat
    2. 配置 NapCat
    3. 启动 NapCat 服务
    4. NapCat 登录 QQ
    5. 连接 NapCat 服务
    """
    if config.remote_mode:
        if napcat_service_remote_start():
            return True
        else:
            raise Exception("远端 NapCat 服务异常, 请检查远端 NapCat 服务")
    else:
        if napcat_service_ok():
            if not config.enable_webui_interaction:
                LOG.warning(
                    "跳过基于 WebUI 交互的检查, 请自行确保 NapCat 已经登录了正确的 QQ {config.bt_uin}"
                )
                return True
            else:
                status = report_login_status()
                if status == 0:
                    return True
                elif status == 1:
                    LOG.error("未登录")
                elif status == 2:
                    LOG.error(
                        f"登录的 QQ 号 {config.bt_uin} 与配置的 QQ 号不匹配, 重启服务中..."
                    )
                    stop_napcat()
                    return launch_napcat_service(*args, **kwargs)
                elif status == 3:
                    LOG.error("登录状态异常, 重启服务中...")
                    if platform.system() == "Windows":
                        stop_napcat()
                        return launch_napcat_service(*args, **kwargs)
                    else:
                        LOG.error("非 Windows 系统一般需要进行物理重启解决该问题")
                        raise Exception("登录状态异常, 请物理重启本机")
        else:
            if not install_or_update_napcat():
                return False
            start_napcat()  # 配置、启动 NapCat 服务
        if config.enable_webui_interaction:
            if not napcat_service_ok(3):
                LOG.info("登录中...")
                login(reset=True)  # NapCat 登录 QQ
            else:
                LOG.info("快速登录成功, 跳过登录引导")
        else:
            LOG.warning("禁用了 WEBUI 操作, 请自行完成登录")
        connect_napcat()  # 连接 NapCat 服务
        return True
