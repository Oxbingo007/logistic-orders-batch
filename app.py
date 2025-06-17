# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# 设置页面配置
st.set_page_config(
    page_title="物流订单批量创建工具",
    page_icon="📦",
    layout="wide"
)

# 设置页面标题
st.title("📦 物流订单批量创建工具")

class OrderCreator:
    def __init__(self):
        self.api_url = os.getenv("API_URL", "https://gw.kiliexpress.com/manage/order/ship")
        self.platform_id = os.getenv("PLATFORM_ID", "LOGISTICSADMIN")
        self.auth_token = os.getenv("AUTH_TOKEN")
        print(f"当前使用的token: {self.auth_token}")

    def create_order(self, order_data):
        headers = {
            'Content-Type': 'application/json',
            'Platform-Id': self.platform_id,
            'Authorization': self.auth_token
        }
        
        try:
            # 递归将所有None替换为""
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
            print("即将提交的订单数据：", json.dumps(order_data, ensure_ascii=False, indent=2))
            response = requests.post(self.api_url, headers=headers, json=order_data)
            result = response.json()

            if result.get('code') == 0:
                 return result
            else:
                 error_message = result.get('message', '未知错误')
                 st.warning(f"订单创建API返回错误: {error_message} (Code: {result.get('code')})")
                 return result 

        except requests.exceptions.RequestException as e:
            st.error(f"创建订单请求失败: {str(e)}")
            return None
        except json.JSONDecodeError:
             st.error("创建订单响应解析失败")
             return None

    def process_excel(self, df):
        try:
            results = []
            progress_bar = st.progress(0)
            total_rows = len(df)
            
            for index, row in df.iterrows():
                order_data = {
                    "orderType": "NORMAL",
                    "valueAdded": [],
                    "customerOrderNo": row.get('customerOrderNo', ''),
                    "remark": None,
                    "countryCode": "KE",
                    "orderLogistics": {
                        "receiving": {
                            "serviceType": "CFS",
                            "stationCode": int(float(row.get('receivingStationCode', 1)))
                        },
                        "delivery": {
                            "serviceType": "CFS",
                            "stationCode": int(float(row.get('deliveryStationCode', 718864990)))
                        },
                        "shipper": {
                            "firstName": str(row.get('shipperFirstName', 'Sender')),
                            "lastName": str(row.get('shipperLastName', 'CFS')),
                            "phone": str(row.get('shipperPhone', '254115690969')),
                            "phone2": None,
                            "address": {
                                "country": "KE",
                                "area": None,
                                "address": None
                            }
                        },
                        "receiver": {
                            "firstName": str(row.get('receiverFirstName', 'Joy')),
                            "lastName": str(row.get('receiverLastName', 'Yang')),
                            "phone": str(row.get('receiverPhone', '115690969')),
                            "phone2": None,
                            "address": {
                                "country": "KE",
                                "province": str(row.get('province', 'Machakos')),
                                "town": str(row.get('town', 'Mavoko')),
                                "area": str(row.get('area', '361211000')),
                                "address": None
                            }
                        }
                    },
                    "orderStorage": {
                        "warehouseCode": None
                    },
                    "goodsList": [{
                        "sku": str(row.get('sku', '900361')),
                        "qty": int(row.get('qty', 3)),
                        "name": str(row.get('goodsName', 'goodsname')),
                        "transportType": None,
                        "length": int(row.get('length', 1)),
                        "width": int(row.get('width', 1)),
                        "height": int(row.get('height', 1)),
                        "weight": int(row.get('weight', 1)),
                        "internationalAnnex": {
                            "hsCode": None,
                            "hsName": None,
                            "hsAttributes": None,
                            "declaredValue": 0,
                            "declaredValueCurrency": None
                        }
                    }]
                }
                
                api_response = self.create_order(order_data)
                results.append({
                    'row': index + 1,
                    'status': 'success' if api_response and api_response.get('code') in [0, 200] else 'failed',
                    'response': api_response
                })
                
                progress = (index + 1) / total_rows
                progress_bar.progress(progress)
                
            return results
            
        except Exception as e:
            st.error(f"处理Excel文件时发生意外错误: {str(e)}")
            return []

def main():
    order_creator = OrderCreator()

    st.header("1. 上传Excel文件")
    uploaded_file = st.file_uploader("请选择包含订单信息的Excel文件 (.xlsx)", type=['xlsx'])
    
    if uploaded_file is not None:
        try:
            df_input = pd.read_excel(uploaded_file, engine='openpyxl', dtype={
                'sku': str,
                'customerOrderNo': str,
                'receivingStationCode': str,
                'deliveryStationCode': str,
                'area': str,
                'receiverLastName': str,
                'receiverPhone': str,
                'shipperPhone': str,
                'qty': str
            })
            # 清理数据：去除全空的行和列，去掉'Unnamed'开头的多余列
            df_input = df_input.dropna(how='all')
            df_input = df_input.dropna(axis=1, how='all')
            df_input = df_input.loc[:, ~df_input.columns.str.contains('^Unnamed')]

            st.header("2. 数据预览 (前10行)")
            st.dataframe(df_input.head(10))
            
            st.header("3. 列名检查")
            required_columns = [
                'shipperFirstName', 'shipperLastName', 'shipperPhone',
                'receiverFirstName', 'receiverLastName', 'receiverPhone',
                'province', 'town', 'area', 'sku', 'qty', 'goodsName',
                'receivingStationCode', 'deliveryStationCode', 'customerOrderNo'
            ]
            optional_goods_columns = ['length', 'width', 'height', 'weight']

            missing_columns = [col for col in required_columns if col not in df_input.columns]
            present_optional = [col for col in optional_goods_columns if col in df_input.columns]

            if missing_columns:
                st.error(f"❌ 缺少必要的列: {', '.join(missing_columns)}")
            else:
                st.success("✅ 所有必要的列都存在")
                st.info(f"ℹ️ 发现可选商品列: {', '.join(present_optional) if present_optional else '无'}")
                
                if st.button("🚀 开始创建订单"):
                    st.header("4. 处理结果")
                    with st.spinner('正在处理订单...'):
                        results = order_creator.process_excel(df_input)
                    
                    if results:
                        success_count = sum(1 for r in results if r['status'] == 'success')
                        failed_count = len(results) - success_count
                        
                        st.success(f"✔️ 处理完成 - 成功: {success_count}")
                        if failed_count > 0:
                            st.warning(f"⚠️ 处理完成 - 失败: {failed_count}")
                        
                        st.subheader("详细结果")
                        result_df = pd.DataFrame(results) 
                        st.dataframe(result_df)
                    else:
                        st.error("处理未完成或未返回结果，请检查上方错误信息。")
                        
        except Exception as e:
            st.error(f"读取或处理Excel文件时发生错误: {str(e)}")

if __name__ == "__main__":
    main() 