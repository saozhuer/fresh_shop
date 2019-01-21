from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.shortcuts import render
from goods.models import RecentBrowsing,Goods

# Create your views here.
from fresh_shop.settings import ORDER_NUMBER
from order.models import OrderInfo
from user.forms import RegisterForm, LoginForm, AddressForm
from user.models import User, UserAddress
from django.http import HttpResponseRedirect
from django.urls import reverse

def register(request):
    if request.method == 'GET':
        return render(request,'register.html')
    if request.method == 'POST':
        # 使用表单form做校验
        form = RegisterForm(request.POST)
        if form.is_valid():
            #说名账号不存在数据库，密码和确认密码一致，邮箱格式正确
            username = form.cleaned_data['user_name']
            password = make_password(form.cleaned_data['pwd'])
            email = form.cleaned_data['email']
            User.objects.create(username=username,
                                password=password,
                                email =email,
                                )
            return HttpResponseRedirect(reverse('user:login'))
        else:
            errors = form.errors
            return render(request,'register.html',{'errors':errors})


def login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    if request.method =='POST':
       form = LoginForm(request.POST)
       if form.is_valid():
           #用户名存在，密码相同
           username = form.cleaned_data.get('username')
           user = User.objects.filter(username=username).first()
           request.session['user_id'] = user.id
           return HttpResponseRedirect(reverse('goods:index'))
       else:
           errors = form.errors
           return render(request,'login.html',{'errors':errors})



def logout(request):
    if request.method =='GET':
        #删除session中的键值对user_id
        del request.session['user_id']
        # 删除商品信息
        if request.session.get('goods'):
            del request.session['goods']


        return HttpResponseRedirect(reverse('goods:index'))


def user_site(request):
    if request.method =='GET':
        user_id = request.session.get('user_id')
        user_address = UserAddress.objects.filter(user_id=user_id)
        activate = 'site'
        return render(request,'user_center_site.html',{'user_address':user_address,'activate':activate})

    if request.method =='POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            address = form.cleaned_data['address']
            postcode = form.cleaned_data['postcode']
            mobile = form.cleaned_data['mobile']
            user_id = request.session.get('user_id')
            UserAddress.objects.create(user_id=user_id,
                                       address=address,
                                       signer_name=username,
                                       signer_postcode=postcode,
                                       signer_mobile=mobile)
            return HttpResponseRedirect(reverse('user:user_site'))
        else:
            errors = form.errors
            return render(request,'user_center_site.html',{'errors':errors})


def user_info(request):
    if request.method == 'GET':
        activate = 'info'

        #最近浏览
        # 判断登录用户
        user_id = request.GET.get('id')
        #h获取数据库的信息
        rb = RecentBrowsing.objects.filter(user_id=user_id,)
        goods = []
        for r in rb:
            goods_image = r.goods.goods_front_image

            goods_name = r.goods.name

            goods_price = r.goods.shop_price
            goods_id = r.goods_id
            goods.append([goods_image,goods_name,goods_price,goods_id])

        g_goods = goods[::-1][:5]


        return render(request,'user_center_info.html',{'activate':activate,'goods':g_goods})





def user_order(request):
    if request.method == 'GET':
        activate = 'order'
        page = int(request.GET.get('page',1))
        # 查询系统用户的id值
        user_id = request.session.get('user_id')
        # 查询当前用户产生的订单信息
        orders = OrderInfo.objects.filter(user_id=user_id)
        status = OrderInfo.ORDER_STATUS
        #分页
        pg = Paginator(orders,ORDER_NUMBER)
        orders = pg.page(page)
        return render(request,'user_center_order.html',{'orders':orders,'status':status,'activate':activate})
