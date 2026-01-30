# -*- coding: utf-8 -*-
import requests
import os
import streamlit as st  # 引入 streamlit
from dotenv import load_dotenv

# 尝试加载本地环境（如果本地有.env就用，没有也不影响）
load_dotenv()

# 修改读取逻辑：优先从 Streamlit Secrets 读取，如果没有则读本地环境
ACCOUNT = st.secrets.get("ACCOUNT") or os.getenv("ACCOUNT")
PASSWORD = st.secrets.get("PASSWORD") or os.getenv("PASSWORD")

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
    if result.get("code") == 0:
        token = result.get("data", {}).get("token")
        # 如果你的 app.py 需要这个 token，请确保这里 return 或者赋值给 st.session_state
    else:
        st.error(f"登录失败：{result.get('message')}")
except Exception as e:
    st.error(f"请求异常：{e}")