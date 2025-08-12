# 配置和启动本地 NapCat 服务

import atexit
import json
import os
import platform
import shutil
import subprocess
import time
import traceback
from urllib.parse import urlparse

from ncatbot.adapter.nc.install import check_permission, get_napcat_dir
from ncatbot.utils import WINDOWS_NAPCAT_DIR, config, get_log

LOG = get_log("adapter.nc.start")


def is_napcat_running_linux(target=None):
    process = subprocess.Popen(["bash", "napcat", "status"], stdout=subprocess.PIPE)
    process.wait()
    output = process.stdout.read().decode(encoding="utf-8")
    if target is None:
        return output.find("PID") != -1
    else:
        return output.find(str(target)) != -1


def start_napcat_linux():
    """保证 NapCat 已经安装的前提下, 启动 NapCat 服务"""
    # Linux启动逻辑
    if not is_napcat_running_linux(config.bt_uin):
        if is_napcat_running_linux():
            LOG.warning("NapCat 正在运行, 但运行的不是该 QQ 号")
            rs = input("按 y 强制结束当前 NapCat 进程并继续, 按其他键退出")
            if rs == "y":
                stop_napcat_linux()
            else:
                raise Exception("NapCat 正在运行, 但运行的不是该 QQ 号")
    else:
        LOG.info("NapCat 已启动")
        return
    try:
        # 启动并注册清理函数
        LOG.info("正在启动 NapCat 服务")
        if os.path.exists("napcat"):
            LOG.error(
                "工作目录下存在 napcat 目录, Linux 启动时不应该在工作目录下存在 napcat 目录"
            )
            raise FileExistsError("工作目录下存在 napcat 目录")
        process = subprocess.Popen(
            ["sudo", "bash", "napcat", "start", str(config.bt_uin)],
            stdout=subprocess.PIPE,
        )
        process.wait()
        if process.returncode != 0:
            LOG.error("启动 napcat 失败，请检查日志，napcat cli 可能没有被正确安装")
            raise FileNotFoundError("napcat cli 可能没有被正确安装")
        if config.stop_napcat:
            atexit.register(lambda: stop_napcat_linux(config.bt_uin))
    except Exception as e:
        import traceback

        LOG.error(f"pgrep 命令执行失败, 无法判断 QQ 是否启动, 请检查错误: {e}")
        LOG.info(traceback.format_exc())
        raise e

    if not is_napcat_running_linux(config.bt_uin):
        LOG.error("napcat 启动失败，请检查日志")
        raise Exception("napcat 启动失败")
    else:
        time.sleep(0.5)
        LOG.info("napcat 启动成功")


def stop_napcat_linux():
    try:
        process = subprocess.Popen(["bash", "napcat", "stop"], stdout=subprocess.PIPE)
        process.wait()
        if process.returncode != 0:
            LOG.error("停止 napcat 失败，请检查日志")
            raise Exception("停止 napcat 失败")
        else:
            LOG.info("已成功停止 napcat")
    except Exception as e:
        LOG.error(f"停止 napcat 失败，请检查日志: {e}")
        LOG.info(traceback.format_exc())
        raise e


def is_napcat_running_windows():
    """暂未实现逻辑"""
    return True


def start_napcat_windows():
    # Windows启动逻辑
    def get_launcher_name():
        """获取对应系统的launcher名称"""
        is_server = "Server" in platform.release()
        if is_server:
            version = platform.release()
            if "2016" in version:
                LOG.info("当前操作系统为: Windows Server 2016")
                return "launcher-win10.bat"
            elif "2019" in version:
                LOG.info("当前操作系统为: Windows Server 2019")
                return "launcher-win10.bat"
            elif "2022" in version:
                LOG.info("当前操作系统为: Windows Server 2022")
                return "launcher-win10.bat"
            elif "2025" in version:
                LOG.info("当前操作系统为：Windows Server 2025")
                return "launcher.bat"
            else:
                LOG.error(
                    f"不支持的的 Windows Server 版本: {version}，将按照 Windows 10 内核启动"
                )
                return "launcher-win10.bat"

        if platform.release() == "10":
            LOG.info("当前操作系统为: Windows 10")
            return "launcher-win10.bat"

        if platform.release() == "11":
            LOG.info("当前操作系统为: Windows 11")
            return "launcher.bat"

        return "launcher-win10.bat"

    launcher = get_launcher_name()
    napcat_dir = os.path.abspath(WINDOWS_NAPCAT_DIR)
    launcher_path = os.path.join(napcat_dir, launcher)

    if not os.path.exists(launcher_path):
        LOG.error(f"找不到启动文件: {launcher_path}")
        raise FileNotFoundError(f"找不到启动文件: {launcher_path}")

    LOG.info(f"正在启动QQ, 启动器路径: {launcher_path}")
    subprocess.Popen(
        f'"{launcher_path}" {config.bt_uin}',
        shell=True,
        cwd=napcat_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop_napcat_windows():
    """停止 NapCat 服务: 在 Windows 上强制结束 QQ.exe 进程"""
    try:
        # 使用 taskkill 强制结束 QQ.exe 进程
        subprocess.run(
            ["taskkill", "/F", "/IM", "QQ.exe"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        LOG.info("已成功停止 QQ.exe 进程（NapCat 服务）")
    except subprocess.CalledProcessError as e:
        # 如果 taskkill 命令执行失败，记录错误并抛出异常
        stdout = e.stdout.decode(errors="ignore") if e.stdout else ""
        stderr = e.stderr.decode(errors="ignore") if e.stderr else ""
        LOG.error(f"停止 NapCat 服务失败: {stderr or stdout}")
        raise RuntimeError(f"无法停止 QQ.exe 进程: {stderr or stdout}")


def is_napcat_running():
    if platform.system() == "Linux":
        return is_napcat_running_linux()
    elif platform.system() == "Windows":
        return is_napcat_running_windows()
    else:
        LOG.warning("不提供官方支持的系统, 默认 NapCat 正在运行")
        return True


def stop_napcat():
    """本地停止 NapCat 服务"""
    LOG.info("正在停止 NapCat 服务")
    if platform.system() == "Linux":
        stop_napcat_linux()
    elif platform.system() == "Windows":
        stop_napcat_windows()
    else:
        LOG.warning("不提供官方支持的系统, 默认 NapCat 未启动")


def start_napcat():
    """本地配置并启动 NapCat 服务"""
    config_napcat()
    if platform.system() == "Linux":
        start_napcat_linux()
    elif platform.system() == "Windows":
        start_napcat_windows()
    else:
        LOG.warning("不提供官方支持的系统, 默认 NapCat 已启动")


def config_napcat():
    """配置 napcat 服务器, 保证 napcat_dir 存在且被正确配置"""
    napcat_dir = get_napcat_dir()

    def config_onebot11():
        if os.path.exists(
            os.path.join(
                napcat_dir, "config", "onebot11_" + str(config.bt_uin) + ".json"
            )
        ):
            original_data = json.load(
                open(
                    os.path.join(
                        napcat_dir, "config", "onebot11_" + str(config.bt_uin) + ".json"
                    ),
                    "r",
                    encoding="utf-8",
                )
            )
        else:
            original_data = {
                "network": {
                    "websocketServers": [],
                },
                "musicSignUrl": "",
                "enableLocalFile2Url": False,
                "parseMultMsg": False,
            }

        expected_server_config = {
            "name": "WsServer",
            "enable": True,
            "host": config.ws_listen_ip,
            "port": int(urlparse(config.ws_uri).port),
            "messagePostFormat": "array",
            "reportSelfMessage": config.report_self_message,
            "token": (str(config.ws_token) if config.ws_token is not None else ""),
            "enableForcePushEvent": True,
            "debug": False,
            "heartInterval": 30000,
        }
        if expected_server_config in original_data["network"]["websocketServers"]:
            pass
        else:
            for server_config in original_data["network"]["websocketServers"]:
                if server_config["port"] == int(urlparse(config.ws_uri).port):
                    LOG.error(
                        f"原配置对应的端口 {server_config['port']} 已经存在, 请更改端口"
                    )
                    raise ValueError(
                        f"原配置对应的端口 {server_config['port']} 已经存在, 请更改端口"
                    )
            original_data["network"]["websocketServers"].append(expected_server_config)

        try:
            with open(
                os.path.join(
                    napcat_dir,
                    "config",
                    "onebot11_" + str(config.bt_uin) + ".json",
                ),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(original_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            LOG.error("配置 onebot 失败: " + str(e))
            if not check_permission():
                LOG.info("请使用 root 权限运行 ncatbot")
                raise Exception("请使用 root 权限运行 ncatbot")

    def config_quick_login():
        ori = os.path.join(napcat_dir, "quickLoginExample.bat")
        dst = os.path.join(napcat_dir, f"{config.bt_uin}_quickLogin.bat")
        shutil.copy(ori, dst)

    def read_webui_config():
        # 确定 webui 路径
        webui_config_path = os.path.join(napcat_dir, "config", "webui.json")
        try:
            with open(webui_config_path, "r") as f:
                webui_config = json.load(f)
                port = webui_config.get("port", 6099)
                token = webui_config.get("token", "")
            if token != config.webui_token:
                LOG.warning(
                    "WebUI 令牌和 webui 配置文件不匹配, 将自动和配置文件同步, 请注意核对！！"
                )
                LOG.info(webui_config_path)
            if port != config.webui_port:
                LOG.warning(
                    "WebUI 端口和 webui 配置文件不匹配, 将自动和配置文件同步, 请注意核对！！"
                )
                LOG.info(webui_config_path)

            LOG.info("Token: " + token + ", Webui port: " + str(port))
            config.webui_token = token
            config.webui_port = port

        except FileNotFoundError:
            LOG.warning("无法读取 WebUI 配置, 将使用默认配置")

    config_onebot11()
    config_quick_login()
    read_webui_config()
