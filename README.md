# 物流订单批量创建工具

这是一个用于批量创建物流订单的Python应用程序。它可以从Excel文件中读取订单信息，并通过API批量创建订单。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制`.env.example`文件为`.env`
2. 在`.env`文件中填入您的API认证信息：
   - PLATFORM_ID: 您的平台ID
   - AUTH_TOKEN: 您的认证令牌

## Excel文件格式

Excel文件应包含以下列（列名必须完全匹配）：

- shipper_first_name: 发货人名字
- shipper_last_name: 发货人姓氏
- shipper_phone: 发货人电话
- receiver_first_name: 收货人名字
- receiver_last_name: 收货人姓氏
- receiver_phone: 收货人电话
- province: 省份
- town: 城镇
- area: 区域代码
- sku: 商品SKU
- qty: 数量
- goods_name: 商品名称
- length: 长度
- width: 宽度
- height: 高度
- weight: 重量

## 使用方法

1. 运行程序：
```bash
python main.py
```

2. 当提示时，输入Excel文件的完整路径

3. 程序将处理Excel文件中的每一行，并为每一行创建一个订单

4. 处理完成后，程序会显示每行的处理结果 

## 环境变量配置（安全说明）

本项目涉及账号、密码、Token等敏感信息，**请勿将这些信息直接写在代码中或上传到GitHub**。

请在项目根目录下新建 `.env` 文件，内容如下：

```
ACCOUNT=your_account@example.com
PASSWORD=your_password
AUTH_TOKEN=your_token
PLATFORM_ID=LOGISTICSADMIN
API_URL=https://gw.kiliexpress.com/manage/order/ship
```

- `.env` 文件已加入 `.gitignore`，不会被上传到GitHub。
- 运行前请确保已正确配置 `.env` 文件。
- 代码中已通过 `python-dotenv` 自动加载环境变量。 