from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
class Abilities(models.Model):
    group = fields.CharField(max_length=32, pk=True)  # 假设只将 group 设为主键
    model = fields.CharField(max_length=191)
    channel_id = fields.BigIntField()
    enabled = fields.BooleanField(null=True)
    priority = fields.BigIntField(default=0)

    class Meta:
        table = "abilities"

class Channels(models.Model):
    id = fields.BigIntField(pk=True)
    type = fields.BigIntField(default=0)
    key = fields.CharField(max_length=191)
    status = fields.BigIntField(default=1)
    name = fields.CharField(max_length=191, null=True)
    weight = fields.BigIntField(default=0)
    created_time = fields.BigIntField(null=True)
    test_time = fields.BigIntField(null=True)
    response_time = fields.BigIntField(null=True)
    base_url = fields.CharField(max_length=191, default='')
    other = fields.TextField()
    balance = fields.FloatField(null=True)
    balance_updated_time = fields.BigIntField(null=True)
    models = fields.TextField()
    group = fields.CharField(max_length=32, default='default')
    used_quota = fields.BigIntField(default=0)
    model_mapping = fields.CharField(max_length=1024, default='')
    priority = fields.BigIntField(default=0)

    class Meta:
        table = "channels"

class Logs(models.Model):
    id = fields.BigIntField(pk=True)
    user_id = fields.BigIntField(null=True)
    created_at = fields.BigIntField(null=True)
    type = fields.BigIntField(null=True)
    content = fields.TextField()
    username = fields.CharField(max_length=191, default='')
    token_name = fields.CharField(max_length=191, default='')
    model_name = fields.CharField(max_length=191, default='')
    quota = fields.BigIntField(default=0)
    prompt_tokens = fields.BigIntField(default=0)
    completion_tokens = fields.BigIntField(default=0)
    channel_id = fields.BigIntField(null=True)

    class Meta:
        table = "logs"

class Redemptions(models.Model):
    id = fields.BigIntField(pk=True)
    user_id = fields.BigIntField(null=True)
    key = fields.CharField(max_length=32, null=True)
    status = fields.BigIntField(default=1)
    name = fields.CharField(max_length=191, null=True)
    quota = fields.BigIntField(default=100)
    created_time = fields.BigIntField(null=True)
    redeemed_time = fields.BigIntField(null=True)

    class Meta:
        table = "redemptions"

class Tokens(models.Model):
    id = fields.BigIntField(pk=True)
    user_id = fields.BigIntField(null=True)
    key = fields.CharField(max_length=48, null=True)
    status = fields.BigIntField(default=1)
    name = fields.CharField(max_length=191, null=True)
    created_time = fields.BigIntField(null=True)
    accessed_time = fields.BigIntField(null=True)
    expired_time = fields.BigIntField(default=-1)
    remain_quota = fields.BigIntField(default=0)
    unlimited_quota = fields.BooleanField(default=False)
    used_quota = fields.BigIntField(default=0)

    class Meta:
        table = "tokens"

class Users(models.Model):
    id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=191, null=True)
    password = fields.TextField()
    display_name = fields.CharField(max_length=191, null=True)
    role = fields.BigIntField(default=1)
    status = fields.BigIntField(default=1)
    email = fields.CharField(max_length=191, null=True)
    github_id = fields.CharField(max_length=191, null=True)
    wechat_id = fields.CharField(max_length=191, null=True)
    access_token = fields.CharField(max_length=32, null=True)
    quota = fields.BigIntField(default=0)
    used_quota = fields.BigIntField(default=0)
    request_count = fields.BigIntField(default=0)
    group = fields.CharField(max_length=32, default='default')
    aff_code = fields.CharField(max_length=32, null=True)
    inviter_id = fields.BigIntField(null=True)

    class Meta:
        table = "users"


# 为每个模型创建 Pydantic 模型
Abilities_Pydantic = pydantic_model_creator(Abilities, name="Abilities")
Channels_Pydantic = pydantic_model_creator(Channels, name="Channels")
Logs_Pydantic = pydantic_model_creator(Logs, name="Logs")
Redemptions_Pydantic = pydantic_model_creator(Redemptions, name="Redemptions")
Tokens_Pydantic = pydantic_model_creator(Tokens, name="Tokens")
Users_Pydantic = pydantic_model_creator(Users, name="Users")

# 为输入创建 Pydantic 模型（可选，如果您需要接收来自 API 的数据）
AbilitiesIn_Pydantic = pydantic_model_creator(Abilities, name="AbilitiesIn", exclude_readonly=True)
ChannelsIn_Pydantic = pydantic_model_creator(Channels, name="ChannelsIn", exclude_readonly=True)
LogsIn_Pydantic = pydantic_model_creator(Logs, name="LogsIn", exclude_readonly=True)
RedemptionsIn_Pydantic = pydantic_model_creator(Redemptions, name="RedemptionsIn", exclude_readonly=True)
TokensIn_Pydantic = pydantic_model_creator(Tokens, name="TokensIn", exclude_readonly=True)
UsersIn_Pydantic = pydantic_model_creator(Users, name="UsersIn", exclude_readonly=True)
