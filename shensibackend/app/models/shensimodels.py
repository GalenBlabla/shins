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
    user = fields.ForeignKeyField('shensidb_app.UserModel', related_name='keys')
    key = fields.CharField(max_length=100, unique=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "keys"

# Pydantic models for API
User_Pydantic = pydantic_model_creator(UserModel, name="User")
UserIn_Pydantic = pydantic_model_creator(UserModel, name="UserIn", exclude_readonly=True)
Key_Pydantic = pydantic_model_creator(KeyModel, name="Key")