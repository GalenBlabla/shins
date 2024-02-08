import os
from dotenv import load_dotenv

from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models

load_dotenv()

def create_client() -> Dysmsapi20170525Client:
    access_key_id = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
    access_key_secret = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    
    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret
    )
    config.endpoint = 'dysmsapi.aliyuncs.com'
    return Dysmsapi20170525Client(config)


async def send_verification_code(mobile:str,code:str):
    client = create_client()
    send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
        phone_numbers=mobile,
        sign_name=os.getenv("SMS_SIGN_NAME"),  # Use your sign name here
        template_code=os.getenv("SMS_TEMPLATE_CODE"),  # Use your template code here
        template_param=f'{{"code":"{code}"}}'
    )
    runtime = util_models.RuntimeOptions()
    try:
        # Send SMS
        await client.send_sms_with_options_async(send_sms_request, runtime)
    except Exception as error:
        raise error # Consider proper error handling

