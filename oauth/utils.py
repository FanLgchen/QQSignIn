from itsdangerous import TimedJSONWebSignatureSerializer, BadData
from django.conf import settings


#对openid进行处理，生成access_token

def generate_access_token(openid):
    """
    签名 openid
    :param openid: 用户的 openid
    :return: access_token
    """

    # QQ登录保存用户数据的token有效期
    # settings.SECRET_KEY: 加密使用的秘钥
    # SAVE_QQ_USER_TOKEN_EXPIRES = 600: 过期时间
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                 expires_in=300)
    data = {'openid': openid}
    token = serializer.dumps(data)
    return token.decode()



#定义函数对传入的access_token 里面是否包含openid进行判断

def check_access_token(access_token):
    """
    检验用户传入的token
    :param access_token: token
    :return: openid or none
    """

    #调用itsdangerous中的类生成对象
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,
                                                 expires_in=300)

    try:
        # 尝试使用对象的 loads 函数
        # 对 access_token 进行反序列化( 类似于解密 )
        # 查看是否能够获取到数据:
        data = serializer.loads(access_token)

    except BadData:
        # 如果出错, 则说明 access_token 里面不是我们认可的.
        # 返回 None
        return None
    else:
        # 如果能够从中获取 data, 则把 data 中的 openid 返回
        return data.get('openid')

