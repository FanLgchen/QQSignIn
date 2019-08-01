
""""此接口展示了QQ登录在实际项目中的运用"""


import re

from django import http
from django.contrib.auth import login
from django.db import DatabaseError
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django_redis import get_redis_connection



#导入日志
import logging

from oauth.models import OAuthQQUser
from oauth.utils import generate_access_token, check_access_token
from users.models import User

logger =logging.getLogger('django')





class QQURLView(View):
    """
    提供QQ登录页面网址
    https://graph.qq.com/oauth2.0/authorize?
    response_type=code&
    client_id=xxx&
    redirect_uri=xxx&
    state=xxx
    """
    def get(self,request):

        #next 表示从哪个页面进入到登录页面，一旦登录成功，就自动回到那个页面
        next = request.GET.get('next')

        #创建OAuthQQ类的对象
        oauth = OAuthQQ(client_id= settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)

        #调用对象的获取qq地址方法
        login_url =oauth.get_qq_url()

        #返回登录地址
        return http.JsonResponse({'code': 200, 'errmsg': 'OK', 'login_url':login_url})



class QQUserView(View):
    """用户扫码登录的回调处理"""

    def get(self,request):

        """Oauth2.0认证"""
        #接收Authorization Code

        code = request.GET.get('code')
        if not code :
            return http.HttpResponseForbidden('缺少code')


        #创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            #携带code 向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)

            #携带access_token 向QQ服务器请求openid
            openid = oauth.get_open_id(access_token)

        except Exception as e :
            #如果上面获取的openid出错，验证失败
            logger.error(e)

            #返回结果
            return http.HttpResponseServerError('OAuth2.0认证失败')


        #判断openid是否绑定用户
        try :
            oauth_user = OAuthQQUser.objects.get(openid=openid)

        except OAuthQQUser.DoesNotExist:
            #如果openid没有绑定用户
            #调用封装好的方法
            access_token =generate_access_token(openid)

            # #拿到access_token 字符串，拼接字典
            context ={'access_token':access_token}

            # #返回响应，重新渲染
            return render(request,'oauth_callback.html',context)
            pass

        else :
            #如果已绑定用户
            qq_user = oauth_user.user

            #实现状态保持
            login(request,qq_user)

            #创建重定向到主页的对象
            response = redirect(reverse('contents:index'))

            #将用户信息写到cookie中，有效期15天
            response.set_cookie('username',qq_user.username,max_age=3600*24*15)

            #返回响应
            return response



    def post(self,request):

        """用户绑定到openid """

        #接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        access_token = request.POST.get('access_token')

        #校验参数
        if not all([mobile,password,sms_code_client]):
            return http.HttpResponseForbidden('缺少必传参数')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')

            # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        #判断短信验证码是否一致
        redis_conn =get_redis_connection('verify_code')

        #从redis取出sms_code值
        sms_code_server =redis_conn.get('sms_code_%s' %mobile)

        #判断是否存在
        if sms_code_server is None:
            return render(request,'oauth_callback.html',{'sms_code_errmsg':'无效的短信验证码'})

        if sms_code_client!=sms_code_server.decode():
            return render(request,'oauth_callback.html',{'sms_code_errmsg': '输入短信验证码有误'})

        #调用我们自己的函数，检验传入的access_token值是否正确
        #错误提示放在sms_code_errmsg位置
        openid =check_access_token(access_token)
        if not openid:
            return render(request,'oauth_callback.html',{'openid_errmsg': '无效的openid'})

        #保存用户数据
        try:
            user =User.objects.get(mobile=mobile)

        except User.DoesNotExist:
            #用户不存在，新建用户
            user =User.objects.create_user(username=mobile,password=password,mobile=mobile)

        else:
            #用户存在，检查用户密码
            if not user.check_password((password)):
                return render(request,'oauth_callback.html',{'account_errmsg': '用户名或密码错误'})

        #将用户绑定到openid
        try:
            OAuthQQUser.objects.create(openid=openid,user=user)

        except DatabaseError:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

        #实现状态保持
        login(request,user)

        #响应绑定结果
        next = request.GET.get('state')
        response =redirect(next)

        #登录时用户名写入到cookie
        response.set_cookie('username',user.username,max_age=3600 * 24 * 15)

        #响应
        return response


