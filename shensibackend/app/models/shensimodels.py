# Database models using Tortoise ORM.

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class UserModel(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=100, unique=True)
    phone_number = fields.CharField(max_length=20, unique=True, null=True)
    hashed_password = fields.CharField(max_length=128)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)

    class Meta:
        table = "users"


class KeyModel(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        'shensidb_app.UserModel', related_name='keys')
    key = fields.CharField(max_length=100, unique=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "keys"


class PackageModel(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    description = fields.TextField()
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "packages"


class OrderModel(models.Model):
    id = fields.IntField(pk=True, description="主键，唯一标识订单")
    user_id = fields.IntField(description="用户ID，关联到用户表的ID，不使用外键关联")
    out_trade_no = fields.CharField(max_length=50, unique=True, description="订单号，唯一标识每一笔订单")
    total_amount = fields.DecimalField(max_digits=10, decimal_places=2, description="订单总金额")
    subject = fields.CharField(max_length=150, description="订单主题或标题")
    body = fields.TextField(description="订单内容描述")
    status = fields.CharField(max_length=20, default="PENDING",description="订单状态，如待支付（PENDING）、已支付（PAID）、已取消（CANCELED）等")
    created_at = fields.DatetimeField(auto_now_add=True, description="订单创建时间")

    class Meta:
        table = "orders"  # 定义数据库中的表名


# 更新 Pydantic 模型以反映新的字段
Order_Pydantic = pydantic_model_creator(OrderModel, name="Order")
OrderIn_Pydantic = pydantic_model_creator(
    OrderModel, name="OrderIn", exclude_readonly=True)
# Pydantic models for API
Package_Pydantic = pydantic_model_creator(PackageModel, name="Package")
PackageIn_Pydantic = pydantic_model_creator(
    PackageModel, name="PackageIn", exclude_readonly=True)
# Pydantic models for API
User_Pydantic = pydantic_model_creator(UserModel, name="User")
UserIn_Pydantic = pydantic_model_creator(
    UserModel, name="UserIn", exclude_readonly=True)
Key_Pydantic = pydantic_model_creator(KeyModel, name="Key")
