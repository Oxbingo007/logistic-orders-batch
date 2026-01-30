# -*- coding: utf-8 -*-
import requests
import os
import streamlit as st  # 关键：必须引入 streamlit 库
from dotenv import load_dotenv

# 加载本地 .env (防止你在本地运行时报错，虽然你删了但留着这行没事)
load_dotenv()

# --- 核心逻辑：获取账号密码 ---
def get_credentials():
    # 1. 优先去 Streamlit 云端保险箱 (Secrets) 里找
    if "ACCOUNT" in st.secrets and "PASSWORD" in st.secrets:
        return st.secrets["ACCOUNT"], st.secrets["PASSWORD"]
    
    # 2. 如果没找到，再去本地环境变量找 (兼容本地运行)
    return os.getenv("ACCOUNT"), os.getenv("PASSWORD")

ACCOUNT, PASSWORD = get_credentials()

def get_latest_token():
    if not ACCOUNT or not PASSWORD:
        st.error("❌ 缺少账号密码！请检查 Streamlit Secrets 配置。")
        return None

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
        # 发送请求给 Kilimall 接口
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        result = resp.json()
        
        if result.get("code") == 0:
            # 成功拿到 Token！直接返回给调用的程序
            return result.get("data", {}).get("token")
        else:
            st.error(f"登录失败: {result.get('message')}")
            return None
    except Exception as e:
        st.error(f"接口请求异常: {e}")
        return None

# 如果直接运行这个文件，打印 Token 方便调试
if __name__ == "__main__":
    print("获取到的 Token:", get_latest_token())