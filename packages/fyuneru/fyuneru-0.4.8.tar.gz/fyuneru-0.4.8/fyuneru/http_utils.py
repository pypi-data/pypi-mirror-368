"""
http工具类
"""

import random
import socket
import ssl
from collections import defaultdict
from functools import wraps
from pathlib import Path
from urllib.parse import urlparse

import requests
from joblib import Parallel, delayed
from loguru import logger
from requests.adapters import HTTPAdapter, PoolManager


def handle_exception(func):
    """异常处理包装类"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            logger.error(f"请求失败，状态码: {e.response.status_code}")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"请求超时: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"发生错误: {e}")
            return None
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"发生错误: {e}")
            return None

    return wrapper


def __get_headers(token: str) -> dict[str, str]:
    return {
        "Access-Token": token,
    }


@handle_exception
def get_json(url: str, session: requests.Session | None = None, proxies=None):
    """获取json"""
    response = (session or requests).get(url, proxies=proxies)
    response.raise_for_status()
    if response.status_code != 200:
        return None
    return response.json()


@handle_exception
def get_content(
    url: str,
    session: requests.Session | None = None,
    proxies: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
) -> bytes:
    """获取内容"""
    response = (session or requests).get(url, proxies=proxies, headers=headers)
    response.raise_for_status()
    return response.content


class SSLAdapter(HTTPAdapter):
    """AI生成的 SSL 适配器"""

    def __init__(self, server_hostname: str, **kwargs):
        self.server_hostname = server_hostname
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        kwargs["ssl_context"] = context
        # 手动设置目标 SNI 域名
        self.poolmanager = PoolManager(
            *args,
            server_hostname=self.server_hostname,  # 关键点
            assert_hostname=self.server_hostname,  # 确保证书匹配
            **kwargs,
        )


def write_content(
    url: str,
    path: Path,
    session: requests.Session | None = None,
    proxies: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
):
    """写入内容"""
    if path.exists():
        logger.debug(f"文件已存在: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    while (
        content := get_content(
            url=url, session=session, proxies=proxies, headers=headers
        )
    ) is None:
        continue
    with path.open("wb") as f:
        f.write(content)


def batch_download(
    path_url: dict[Path, str],
    sessions: list[requests.Session] | None = None,
    proxies: dict[str, str] | None = None,
    session_num: int = 8,
    n_jobs: int = 16,
):
    """批量下载"""
    if not sessions:
        sessions = [requests.Session() for _ in range(session_num)]
    host_grouped_path_url = defaultdict(list)
    for write_path, url in path_url.items():
        host_grouped_path_url[urlparse(url).hostname].append((write_path, url))
    for idx, (host, path_urls) in enumerate(host_grouped_path_url.items()):
        logger.info(f"[{idx}/{len(host_grouped_path_url)}] batch downloading...")
        for session in sessions:
            session.mount("https://", SSLAdapter(server_hostname=host))
        ip = socket.gethostbyname(host)

        def count_wrapper(
            url: str,
            write_path: Path,
            session: requests.Session,
            proxies: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
            idx: int = 0,
            total: int = 0,
        ):
            logger.info(f"[{idx}/{total}] downloading...")
            return write_content(url, write_path, session, proxies, headers)

        Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(count_wrapper)(
                url.replace(host, ip),
                write_path,
                random.choice(sessions),
                proxies,
                {"Host": host},
                idx=idx,
                total=len(path_urls),
            )
            for write_path, url in path_urls
        )


@handle_exception
def get_task_info(
    task_id: str,
    token: str,
    domain: str,
    session: requests.Session | None = None,
    host: str | None = None,
):
    """请求task_info信息"""
    url = f"{domain}/api/v2/task/get/task-info"
    headers = __get_headers(token)
    if host:
        headers["Host"] = host
    params = {"taskId": task_id}
    response = (session or requests).post(url, headers=headers, json=params)
    response.raise_for_status()
    if response.status_code != 200:
        return None
    return response.json()


@handle_exception
def get_item_info(
    item_id: str,
    token: str,
    domain: str,
    session: requests.Session | None = None,
    host: str | None = None,
):
    """item 请求信息"""
    url = f"{domain}/api/v2/item/get-item-info"
    headers = __get_headers(token)
    if host:
        headers["Host"] = host
    params = {"itemId": item_id}
    response = (session or requests).post(url, headers=headers, json=params)
    response.raise_for_status()
    if response.status_code != 200:
        return None
    return response.json()


@handle_exception
def find_labels(
    task_id: str,
    item_id: str,
    token: str,
    domain: str,
    session: requests.Session | None = None,
    host: str | None = None,
):
    """请求标签信息"""
    url = f"{domain}/api/v2/label/find-labels"
    headers = __get_headers(token)
    if host:
        headers["Host"] = host
    params = {"taskId": task_id, "itemId": item_id}
    response = (session or requests).post(url, headers=headers, json=params)
    response.raise_for_status()
    if response.status_code != 200:
        return None
    return response.json()
