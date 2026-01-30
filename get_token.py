# -*- coding: utf-8 -*-
import requests
from dotenv import load_dotenv
import os
import streamlit as st  # 必须导入 streamlit

load_dotenv()

# --- 修改开始：兼容云端 Secrets 和本地 .env ---
try:
    # 优先尝试从 Streamlit 云端 Secrets 读取
    ACCOUNT = st.secrets["ACCOUNT"]
    PASSWORD = st.secrets["PASSWORD"]
except FileNotFoundError:
    # 如果没找到 Secrets（比如在本地运行且没配置 secrets.toml），则回退读取环境变量
    ACCOUNT = os.getenv("ACCOUNT")
    PASSWORD = os.getenv("PASSWORD")
except KeyError:
     # 防止本地运行报错，兜底处理
    ACCOUNT = os.getenv("ACCOUNT")
    PASSWORD = os.getenv("PASSWORD")
# --- 修改结束 ---

url = "https://gw.kiliexpress.com/open/api/auth/sign-in"
headers = {
    "Content-Type": "application/json",
    "Client-Id": "LOGISTICSADMIN"
}

# (后面的代码不用动)
data = {
    "authType": "ACCOUNT",
    "accountAuth": {
        "account": ACCOUNT,
        "password": PASSWORD
    }
}

try:
    # 建议加上 timeout 防止卡死
    resp = requests.post(url, headers=headers, json=data, timeout=10)
    result = resp.json()
    # 打印部分日志方便调试（生产环境注意隐藏密码）
    print("API响应状态码:", result.get("code")) 
    
    if result.get("code") == 0:
        token = result.get("data", {}).get("token")
        # 将 token 返回给主程序，而不是只是打印
        # 注意：这里如果 app.py 是 import 这个文件，你需要把获取到的 token return 出去，或者存到 st.session_state
    else:
        print("登录失败，原因：", result.get("message"))
except Exception as e:
    print("请求异常：", e)