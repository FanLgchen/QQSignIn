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
'''python
oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, 
                client_secret=settings.QQ_CLIENT_SECRET, 
                redirect_uri=settings.QQ_REDIRECT_URI, 
                state=next)
'''


                
                
