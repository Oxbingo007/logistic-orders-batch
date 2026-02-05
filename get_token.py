# -*- coding: utf-8 -*-
import requests
import streamlit as st
import os

def get_token():
    # 优先从 Secrets 读取
    if "ACCOUNT" in st.secrets:
        ACCOUNT = st.secrets["ACCOUNT"]
        PASSWORD = st.secrets["PASSWORD"]
    else:
        ACCOUNT = os.getenv("ACCOUNT")
        PASSWORD = os.getenv("PASSWORD")

    if not ACCOUNT or not PASSWORD:
        return None

    url = "https://gw.kiliexpress.com/open/api/auth/sign-in"
    headers = {"Content-Type": "application/json", "Client-Id": "LOGISTICSADMIN"}
    data = {"authType": "ACCOUNT", "accountAuth": {"account": ACCOUNT, "password": PASSWORD}}

    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        result = resp.json()
        
        # ✅ 核心修复：同时允许 0 和 200，且通过 success 字段双重确认
        code = result.get("code")
        if code in [0, 200] or result.get("success") is True:
            return result.get("data", {}).get("token")
        return None
    except:
        return None