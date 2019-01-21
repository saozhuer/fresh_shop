import re

from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect,HttpResponse

from cart.models import ShoppingCart
from user.models import User



#对所有请求进行登录状态的校验
class TestMiddleware1(MiddlewareMixin):

    def process_request(self,request):
        # 1.
        user_id = request.session.get('user_id')
        if user_id:
            user = User.objects.filter(pk=user_id).first()
            request.user = user
        # 2.登陆校验 ，需要区分那些地址需要登录校验和那些不需要校验
        path = request.path
        if path == '/':
            return None
        #不需要做登录校验的地址
        not_need_check = ['/media/.*/','/cart/.*/','/goods/index/','/user/login/','/user/register/','/goods/detail/.*/','/goods/list/','/goods/search/']
        for check_path in not_need_check:
            if re.match(check_path,path):
                #当前path路径为不需要登录校验的路由
                return None
        # path为需要做登录校验的路由时，判断用户是否登录，没有登陆跳转登陆
        if not user_id:
            return HttpResponseRedirect(reverse('user:login'))



class SessionToDbMiddleware(MiddlewareMixin):

    def process_response(self,request,response):
        #同步session中的商品信息和数据库中购物车表的商品信息
        # 1. 判断用户否登陆，登陆才做数据同步
        user_id = request.session.get('user_id')
        if user_id:
            # 2 . 同步
            # 2.1判断session中的商品是否存在于数据库中，如果存再，则更新
            # 2.2如果不存在则 创建
            # 2.3数据库中有数据而session中没有则将数据库商品同步到session中
            session_goods = request.session.get('goods')
            if session_goods: #如果session有数据
                for se_goods in session_goods:
                    # se_goods 为[goods_id,num ,is_select]
                    #查询数据库数据
                    cart = ShoppingCart.objects.filter(user_id=user_id,goods_id=se_goods[0]).first()
                    if cart:
                        #更新商品信息
                        if cart.nums != se_goods[1] or cart.is_select != se_goods[2]:
                            cart.nums = se_goods[1]
                            cart.is_select = se_goods[2]
                            cart.save()
                    else:
                        #创建
                        carts = ShoppingCart.objects.create(user_id=user_id,goods_id=se_goods[0],nums=se_goods[1],is_select=se_goods[2])

            #否则 同步数据库中的数据到session中
            db_carts = ShoppingCart.objects.filter(user_id=user_id)
            #组装多个商品格式：[[goods_id,nums,is_select],[goods_id,nums,is_select],[goods_id,nums,is_select]]
            if db_carts:
                new_session_goods = [[cart.goods_id,cart.nums,cart.is_select] for cart in db_carts]
                request.session['goods'] = new_session_goods
                # result = []
                # for cart in db_carts:
                #     data = [cart.goods_id,cart.nums,cart.is_select]
                #     result.append(data)
        return response