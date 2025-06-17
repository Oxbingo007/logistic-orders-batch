# -*- coding: utf-8 -*-
import requests
from dotenv import load_dotenv
import os

load_dotenv()

ACCOUNT = os.getenv("ACCOUNT")
PASSWORD = os.getenv("PASSWORD")

url = "https://gw.kiliexpress.com/open/api/auth/sign-in"
headers = {
    "Content-Type": "application/json",
    "Client-Id": "LOGISTICSADMIN"
}
data = {
    "authType": "ACCOUNT",
    "accountAuth": {
        "account": ACCOUNT,
        "password": PASSWORD
    }
}

try:
    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()
    print("完整响应：", result)
    if result.get("code") == 0:
        print("你的token是：", result.get("data", {}).get("token"))
    else:
        print("登录失败，原因：", result.get("message"))
except Exception as e:
    print("请求异常：", e) 