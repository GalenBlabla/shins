def load_private_key_from_file(private_key_path):
    """
    从文件中加载私钥。
    
    :param private_key_path: 私钥文件的路径
    :return: 私钥字符串
    """
    try:
        with open(private_key_path, 'r') as file:
            private_key = file.read()
        print("private_key:",private_key)
        return private_key
    except Exception as e:
        print(f"Error loading private key from {private_key_path}: {e}")
        return None


def load_public_key_from_file(public_key_path):
    """
    从文件中加载公钥。
    
    :param public_key_path: 公钥文件的路径
    :return: 公钥字符串
    """
    try:
        with open(public_key_path, 'r') as file:
            public_key = file.read()
        print("public_key:",public_key)
        return public_key
    except Exception as e:
        print(f"Error loading public key from {public_key_path}: {e}")
        return None

PRIVATE_KEY_PATH = 'shensibackend/app/keys/private_key.txt'  # 更新为你的私钥文件路径
PUBLIC_KEY_PATH = 'shensibackend/app/keys/alipayPublicKey.txt'    # 更新为你的公钥文件路径

load_private_key_from_file(PRIVATE_KEY_PATH)
load_public_key_from_file(PUBLIC_KEY_PATH)