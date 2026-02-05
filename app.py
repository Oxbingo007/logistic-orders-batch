# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests
import json
import os
from dotenv import load_dotenv
from get_token import get_token  # 导入修复后的函数

load_dotenv()

st.set_page_config(page_title="物流订单批量创建工具", page_icon="📦", layout="wide")
st.title("📦 物流订单批量创建工具")

class OrderCreator:
    def __init__(self):
        self.api_url = os.getenv("API_URL", "https://gw.kiliexpress.com/manage/order/ship")
        self.platform_id = os.getenv("PLATFORM_ID", "LOGISTICSADMIN")
        
        # 获取 Token
        self.auth_token = get_token()
        
        # 状态显示
        if self.auth_token:
            st.sidebar.success("🔑 Token 获取成功")
        else:
            st.sidebar.error("❌ Token 获取失败 (请检查 secrets.toml)")

    def create_order(self, order_data):
        if not self.auth_token:
            return {"code": -1, "message": "无有效Token"}

        headers = {
            'Content-Type': 'application/json',
            'Platform-Id': self.platform_id,
            'Authorization': self.auth_token
        }
        
        try:
            def replace_none(obj):
                if isinstance(obj, dict):
                    return {k: replace_none(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [replace_none(i) for i in obj]
                elif obj is None:
                    return ""
                else:
                    return obj
            order_data = replace_none(order_data)
            
            response = requests.post(self.api_url, headers=headers, json=order_data, timeout=15)
            result = response.json()

            # ✅ 核心修复：这里也改成了 code in [0, 200]
            if result.get('code') in [0, 200] or result.get("success") is True:
                 # 强制修正 code 为 0 以便后续逻辑识别成功
                 result['code'] = 0 
                 return result
            else:
                 return result 

        except Exception as e:
            return {"code": -1, "message": str(e)}

    def process_excel(self, df):
        try:
            results = []
            progress_bar = st.progress(0)
            total_rows = len(df)
            
            for index, row in df.iterrows():
                # (这里保持你的订单组装逻辑不变，省略以节省篇幅，直接复制你原来的即可)
                # ...
                # 临时写一个简化版逻辑占位，请保留你原来 app.py 里的这部分 logic
                order_data = {
                    "orderType": "NORMAL",
                    "customerOrderNo": str(row.get('customerOrderNo', '')),
                    "countryCode": "KE",
                    "orderLogistics": {
                        "receiving": {"serviceType": "CFS", "stationCode": int(float(row.get('receivingStationCode', 1)))},
                        "delivery": {"serviceType": "CFS", "stationCode": int(float(row.get('deliveryStationCode', 718864990)))},
                        "shipper": {
                            "firstName": str(row.get('shipperFirstName', 'Sender')),
                            "lastName": str(row.get('shipperLastName', 'CFS')),
                            "phone": str(row.get('shipperPhone', '')),
                            "address": {"country": "KE"}
                        },
                        "receiver": {
                            "firstName": str(row.get('receiverFirstName', '')),
                            "lastName": str(row.get('receiverLastName', '')),
                            "phone": str(row.get('receiverPhone', '')),
                            "address": {
                                "country": "KE",
                                "province": str(row.get('province', '')),
                                "town": str(row.get('town', '')),
                                "area": str(row.get('area', '')),
                                "address": str(row.get('address', ''))
                            }
                        }
                    },
                    "goodsList": [{
                        "sku": str(row.get('sku', '')),
                        "qty": int(row.get('qty', 1)),
                        "name": str(row.get('goodsName', '')),
                        "length": 1, "width": 1, "height": 1, "weight": 1
                    }]
                }

                api_response = self.create_order(order_data)
                
                # 判断成功状态
                status = '✅ 成功' if api_response.get('code') == 0 else '❌ 失败'
                results.append({
                    '订单号': row.get('customerOrderNo'),
                    '状态': status,
                    '反馈': api_response.get('message')
                })
                progress_bar.progress((index + 1) / total_rows)
                
            return results
        except Exception as e:
            st.error(f"处理错误: {str(e)}")
            return []

def main():
    order_creator = OrderCreator()
    uploaded_file = st.file_uploader("上传Excel", type=['xlsx'])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.dataframe(df.head())
        if st.button("🚀 开始创建"):
            st.table(order_creator.process_excel(df))

if __name__ == "__main__":
    main()