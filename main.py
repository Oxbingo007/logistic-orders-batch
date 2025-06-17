# -*- coding: utf-8 -*-
import pandas as pd
import requests
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class OrderCreator:
    def __init__(self):
        self.api_url = "https://gw.kiliexpress.com/manage/order/ship"
        self.platform_id = "LOGISTICSADMIN"
        self.auth_token = None
        
    def create_order(self, order_data):
        headers = {
            'Content-Type': 'application/json',
            'Platform-Id': self.platform_id,
            'Authorization': 'Bearer {}'.format(self.auth_token)
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=order_data)
            response.raise_for_status()
            print("下单请求头：", headers)
            print("下单请求体：", json.dumps(order_data, ensure_ascii=False))
            print("下单响应：", response.text)
            return response.json()
        except requests.exceptions.RequestException as e:
            print("创建订单失败: {}".format(str(e)))
            return None

    # 新增：安全转换函数
    def safe_int(self, val, default=0):
        try:
            if pd.isna(val):
                return default
            return int(float(val))
        except Exception:
            return default

    def safe_str(self, val, default=""):
        if pd.isna(val):
            return default
        return str(val)

    def process_excel(self, excel_path):
        try:
            # 读取Excel文件，指定使用openpyxl引擎
            df = pd.read_excel(excel_path, engine='openpyxl')
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # 去掉多余的NA列
            required_fields = [
                'customerOrderNo', 'sku', 'goodsName', 'qty',
                'shipperFirstName', 'shipperLastName', 'shipperPhone',
                'province', 'town', 'area',
                'receiverFirstName', 'receiverLastName', 'ds station',
                'receiverPhone', 'receivingStationCode', 'deliveryStationCode'
            ]
            df = df.dropna(subset=required_fields, how='any')
            
            print(df.head(10))
            
            # 处理每一行数据
            results = []
            for index, row in df.iterrows():
                order_number = index + 1  # 添加订单编号
                print("\n正在处理第 {} 个订单...".format(order_number))
                
                order_data = {
                    "orderType": "NORMAL",
                    "valueAdded": [],
                    "remark": "订单编号: {}".format(order_number),  # 在备注中添加订单编号
                    "countryCode": "KE",
                    "orderLogistics": {
                        "receiving": {
                            "serviceType": "CFS",
                            "stationCode": self.safe_int(row.get('receivingStationCode'), 1)
                        },
                        "delivery": {
                            "serviceType": "CFS",
                            "stationCode": self.safe_int(row.get('deliveryStationCode'), 718864990)
                        },
                        "shipper": {
                            "firstName": self.safe_str(row.get('shipperFirstName'), 'Sender'),
                            "lastName": self.safe_str(row.get('shipperLastName'), 'CFS'),
                            "phone": self.safe_str(row.get('shipperPhone'), '254115690969'),
                            "phone2": None,
                            "address": {
                                "country": "KE",
                                "area": self.safe_str(row.get('shipperArea'), None),
                                "address": self.safe_str(row.get('shipperAddress'), None)
                            }
                        },
                        "receiver": {
                            "firstName": self.safe_str(row.get('receiverFirstName'), 'Joy'),
                            "lastName": self.safe_str(row.get('receiverLastName'), 'Yang'),
                            "phone": self.safe_str(row.get('receiverPhone'), '115690969'),
                            "phone2": None,
                            "address": {
                                "country": "KE",
                                "province": self.safe_str(row.get('province'), 'Machakos'),
                                "town": self.safe_str(row.get('town'), 'Mavoko'),
                                "area": self.safe_str(row.get('area'), '361211000'),
                                "address": self.safe_str(row.get('receiverAddress'), None)
                            }
                        }
                    },
                    "orderStorage": {
                        "warehouseCode": self.safe_str(row.get('warehouseCode'), None)
                    },
                    "goodsList": [{
                        "sku": self.safe_str(row.get('sku'), '900361'),
                        "qty": self.safe_int(row.get('qty'), 3),
                        "name": self.safe_str(row.get('goodsName'), 'goodsname'),
                        "transportType": self.safe_str(row.get('transportType'), None),
                        "length": self.safe_int(row.get('length'), 1),
                        "width": self.safe_int(row.get('width'), 1),
                        "height": self.safe_int(row.get('height'), 1),
                        "weight": self.safe_int(row.get('weight'), 1),
                        "internationalAnnex": {
                            "hsCode": self.safe_str(row.get('hsCode'), None),
                            "hsName": self.safe_str(row.get('hsName'), None),
                            "hsAttributes": self.safe_str(row.get('hsAttributes'), None),
                            "declaredValue": self.safe_int(row.get('declaredValue'), 0),
                            "declaredValueCurrency": self.safe_str(row.get('declaredValueCurrency'), None)
                        }
                    }]
                }
                print("即将提交的订单数据：", json.dumps(order_data, ensure_ascii=False, indent=2))
                try:
                    result = self.create_order(order_data)
                    results.append({
                        'order_number': order_number,  # 添加订单编号到结果中
                        'status': 'success' if result else 'failed',
                        'response': result
                    })
                except Exception as e:
                    print("第 {} 个订单创建失败: {}".format(order_number, str(e)))
                    results.append({
                        'order_number': order_number,
                        'status': 'failed',
                        'response': str(e)
                    })
                
            return results
            
        except Exception as e:
            print("处理Excel文件时出错: {}".format(str(e)))
            return None

    def login(self, account, password):
        url = "https://gw.kiliexpress.com/open/api/auth/sign-in"
        headers = {
            "Content-Type": "application/json",
            "Client-Id": "LOGISTICSADMIN"
        }
        data = {
            "authType": "ACCOUNT",
            "accountAuth": {
                "account": account,
                "password": password
            }
        }
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") == 0:
            self.auth_token = result.get("data", {}).get("token")
            print("登录接口完整响应：", result)
            return True
        else:
            print("登录失败:", result.get("message"))
            return False

def main():
    # 创建订单创建器实例
    order_creator = OrderCreator()
    
    # 获取Excel文件路径
    excel_path = input("请输入Excel文件路径: ")
    
    # 登录
    if not order_creator.login("robin.xie@kilimall.com", "15658167069"):
        print("登录失败，终止")
        return
    
    # 处理Excel文件并创建订单
    results = order_creator.process_excel(excel_path)
    
    if results:
        print("\n处理结果:")
        for result in results:
            print("订单编号: {}, 状态: {}".format(result['order_number'], result['status']))
    else:
        print("处理失败")

if __name__ == "__main__":
    main() 