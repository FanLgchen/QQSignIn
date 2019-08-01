# QQSignIn
在django项目里如何使用QQ第三方登录的Demo及说明
## 使用说明
### qq登录开发者相关申请，操作
* 相关连接：http://wiki.connect.qq.com/%E5%87%86%E5%A4%87%E5%B7%A5%E4%BD%9C_oauth2-0
* 拿到QQ互联申请的客户端ID及秘钥 QQ_CLIENT_ID QQ_CLIENT_SECRET 
### 定义QQ登录模型类
### 安装QQLoginTool
* QQLoginTool是QQ登录的一个开源工具 pip install QQLoginTool
### QQLoginTool的使用
* 初始化对象
```python
oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, 
                client_secret=settings.QQ_CLIENT_SECRET, 
                redirect_uri=settings.QQ_REDIRECT_URI, 
                state=next)
```
* 获取QQ地址 login_url = oauth.get_qq_url()
* 获取 QQ 的 access_token access_token = oauth.get_access_token(code)
* 获取 QQ 的 access_token openid = oauth.get_open_id(access_token)

### 接口思路（请参考views）
* 获取QQ登录扫码接口
* 接收 Authorization Code
* OAuth2.0 认证获取 openid
  * 判断 openid 是否绑定过用户
    * 已绑定
    * 未绑定
   
## 补充
### itsdangerous 的使用
```python
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
                                                 expires_in=constants.ACCESS_TOKEN_EXPIRES)
    data = {'openid': openid}
    token = serializer.dumps(data)
    return token.decode()
```
```python
def check_access_token(access_token):
    """
    检验用户传入的 token
    :param token: token
    :return: openid or None
    """

    # 调用 itsdangerous 中的类, 生成对象
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 
                                                 expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)

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
```


  

                
                
