import time
import os
import re
import requests
import js2py  # 导入 js2py
import ddddocr
import pymysql
from enum import Enum
from typing import Optional
from mcp.shared.exceptions import McpError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    ErrorData,
    Tool,
    TextContent,
    INVALID_PARAMS,
    INTERNAL_ERROR,
)
from pydantic import BaseModel, Field

class DpipblockTools(str, Enum):
    PORT_ADD = "port_add"
    PORT_DELETE = "port_delete"

def convert_time_to_seconds(time_str: str) -> str:
    time_str = time_str.strip().lower()
    
    if time_str in ["永久", "permanent", "forever", "-1"]:
        return "-1"
    
    if time_str.isdigit():
        return time_str
    
    match = re.match(r'(\d+)\s*([a-zA-Z\u4e00-\u9fff]+)', time_str)
    if not match:
        return "180"
    
    number = int(match.group(1))
    unit = match.group(2)
    
    time_units = {
        '分钟': 60, 'min': 60, 'm': 60, 'minute': 60, 'minutes': 60,
        '小时': 3600, 'hour': 3600, 'hours': 3600, 'h': 3600,
        '天': 86400, 'day': 86400, 'days': 86400, 'd': 86400,
        '周': 604800, 'week': 604800, 'weeks': 604800, 'w': 604800,
        '月': 2592000, 'month': 2592000, 'months': 2592000,
        '年': 31536000, 'year': 31536000, 'years': 31536000, 'y': 31536000,
        '秒': 1, 'second': 1, 'seconds': 1, 's': 1, 'sec': 1,
    }
    
    multiplier = time_units.get(unit, 1)
    return str(number * multiplier)


# 数据库操作
class DB():
    # 在setting.databases我已创建了数据库链接相关信息，在下方调用时直接写语句即可
    def __init__(self, host='host.docker.internal', port=3306, user='root', passwd='abc123456', db='wuhu_data'):
        # 建立连接
        self.conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd)
        # 创建游标
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def __enter__(self):
        # 返回游标
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交数据库并执行
        self.conn.commit()
        # 关闭游标
        self.cur.close()
        # 关闭数据库连接
        self.conn.close()

# 查询数据
def select_data(select_sql):
    with DB() as db:
        db.execute(select_sql)
        data_list = db.fetchall()
        return data_list

def get_account(sys_name):
    sql = "select * from ai_account where sys_name = '" + sys_name + "'"
    sys_account = select_data(sql)
    return sys_account[0]


def dpfhq_login(username: str, password: str) -> Optional[dict]:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    js_file_path = os.path.join(current_dir, "7_dpfhq.js")
    
    with open(js_file_path, "r", encoding="UTF-8") as file:
        js_code = file.read()
    
    context = js2py.EvalJs()
    context.execute(js_code)

    check = context.valid_refresh()
    uname = context.conplat_str_encrypt(username)
    pwd = context.conplat_str_encrypt(password)

    for i in range(1, 11):
        url = f'https://10.138.36.249:8889/func/web_main/validate?check={check}'
        main_url_html = requests.get(url=url, verify=False)
        ocr = ddddocr.DdddOcr(show_ad=False)
        image = main_url_html.content
        code = ocr.classification(image)

        pData = [
            "_csrf_token=4356274536756456326",
            f"uname={uname}",
            f"ppwd={pwd}",
            "language=1",
            "ppwd1=",
            "otp_value=",
            f"code={code}",
            f"check={check}"
        ]
        
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'slotType=0; SID=jCEonCX7hYrKNz055v0uUlSlxTnmNnLV',
            'Host': '10.138.36.249:8889',
            'Referer': 'https://10.138.36.249:8889/html/login.html',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }

        url = 'https://10.138.36.249:8889/func/web_main/login_tamper/user/user_login_check_code'
        main_url_html = requests.get(url=url, headers=headers, verify=False)
        response = main_url_html.text
        match = re.search(r'<checkcode>(.*?)</checkcode>', response)
        ycode = match.group(1)
        encryptCode = context.getEncryptCode(pData, ycode)

        params = {
            '_csrf_token': '4356274536756456326',
            'uname': uname,
            'ppwd': pwd,
            'language': '1',
            'ppwd1': '',
            'otp_value': '',
            'code': code,
            'check': check,
            'encryptCode': encryptCode
        }

        url = 'https://10.138.36.249:8889/func/web_main/login'
        main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
        response = main_url_html.text

        if "校验码验证失败！" in response:
            print("校验码验证失败！")
            time.sleep(1)
            continue

        cookies = main_url_html.cookies
        cookie_list = cookies.get_dict()
        SID = cookie_list.get('SID')

        headers2 = {
            'Accept': 'text/css,*/*;q=0.1',
            'Cookie': f'slotType=0; SID={SID}',
            'Host': '10.138.36.249:8889',
            'Referer': 'https://10.138.36.249:8889/func/web_main/display/frame/main',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
        return headers2

    return None

def dpfhq_logout(headers):
    url = 'https://10.138.36.249:8889/func/web_main/logout?lang=cn'
    requests.get(url=url, headers=headers, verify=False)

def dpfhq_port_management_getValueId(ip: str, headers: dict) -> Optional[str]:
    params = {
        'searchsips': ip,
        'searchsipe': ip,
        'searchages': 0,
        'searchagee': 31535999,
        'searchact': 0,
        'searchgroups': 128,
        'searchsta': 2,
        'searchgroupname': None
    }
    url = 'https://10.138.36.249:8889/func/web_main/display/maf/maf_addrfilter/maf_cidr_v4_wblist'
    main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
    response = main_url_html.text
    match = re.search(r'<TR VALUE="(.*?)">', response)
    return match.group(1) if match else None

class DpipblockServer:
    def dpfhq_port_management_add(self, ip: str, time_str: str) -> str:
        account = get_account('迪普防火墙')
        headers = dpfhq_login(account['sys_account'], account['sys_password'])
        if headers is not None:
            time_seconds = convert_time_to_seconds(time_str)
            params = {
                'to_add': f'端口封禁?Default?1?{ip}?{ip}?32?{time_seconds}?2?1',
                'del_all': None
            }
            url = 'https://10.138.36.249:8889/func/web_main/submit/maf/maf_addrfilter/maf_cidr_v4_wblist'
            main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
            response = main_url_html.text
            dpfhq_logout(headers)
            return f"({ip})端口封禁成功！封禁时长：{time_str}（{time_seconds}秒）" if "HiddenSubWin" in response else f"({ip})端口封禁失败！"
        return f"({ip})登录失败，无法执行封禁操作！"
    
    def dpfhq_port_management_delete(self, ip: str) -> str:
        account = get_account('迪普防火墙')
        headers = dpfhq_login(account['sys_account'], account['sys_password'])
        if headers is not None:
            valueId = dpfhq_port_management_getValueId(ip, headers)
            if valueId is not None:
                params = {
                    'to_delete': f'{valueId}?Default?1?{ip}?{ip}?32?180?2?1',
                    'del_all': None
                }
                url = 'https://10.138.36.249:8889/func/web_main/submit/maf/maf_addrfilter/maf_cidr_v4_wblist'
                main_url_html = requests.post(url=url, data=params, headers=headers, verify=False)
                response = main_url_html.text
                dpfhq_logout(headers)
                return f"({ip})端口解禁成功！" if "HiddenSubWin" in response else f"({ip})端口解禁失败！"
            dpfhq_logout(headers)
            return f"({ip})未找到对应的封禁记录！"
        return f"({ip})登录失败，无法执行解禁操作！"

async def serve() -> None:
    server = Server("mcp-dpipblock")
    tdpipblock_server = DpipblockServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=DpipblockTools.PORT_ADD.value,
                description="在防火墙层面封禁IP地址",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip": {
                            "type": "string",
                            "format": "ipv4",
                            "description": "IPv4 address to be blocked at the port level, e.g., '192.168.1.1'",
                        },
                        "time": {
                            "type": "string",
                            "description": "Time of sequestration. Supports formats: '永久'(permanent), '1分钟'/'1min'/'1m', '1小时'/'1hour'/'1h', '1天'/'1day'/'1d', '1周'/'1week'/'1w', '1月'/'1month', '1年'/'1year'/'1y', or pure number (seconds)",
                        }
                    },
                    "required": ["ip", "time"]
                },
            ),
            Tool(
                name=DpipblockTools.PORT_DELETE.value,
                description="在防火墙层面解封IP地址",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "ip": {
                            "type": "string",
                            "format": "ipv4",
                            "description": "IPv4 address to be unblocked at the port level, e.g., '192.168.1.1'",
                        }
                    },
                    "required": ["ip"]
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            match name:
                case DpipblockTools.PORT_ADD.value:
                    if not all(k in arguments for k in ["ip", "time"]):
                        raise ValueError("Missing required arguments")
                    result = tdpipblock_server.dpfhq_port_management_add(arguments["ip"], arguments["time"])

                case DpipblockTools.PORT_DELETE.value:
                    ip = arguments.get("ip")
                    if not ip:
                        raise ValueError("Missing required argument: ip")
                    result = tdpipblock_server.dpfhq_port_management_delete(ip)

                case _:
                    raise ValueError(f"Unknown tool: {name}")
            return [TextContent(type="text", text=result)]

        except Exception as e:
            raise ValueError(f"Error processing mcp-server-dpipblock query: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)