from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from cart.models import ShoppingCart
from goods.models import Goods

#加入购物车
def add_cart(request):
    if request.method == 'POST':
        #接收商品id值和商品数量num
        #组装存储的商品格式：[goods_id,num,is_select]
        #组装多个商品格式：[[goods_id,num,is_select],[goods_id,num,is_select],[goods_id,num,is_select]]
        goods_id = int(request.POST.get('goods_id'))
        goods_num = int(request.POST.get('goods_num'))
        # 组装数据
        goods_list = [goods_id,goods_num,1]

        session_goods = request.session.get('goods')
        if session_goods:
            # 1.添加重复的商品则修改数量
            # 2.添加的商品不存在于购物车中就新增
            flag = True
            for se_goods in session_goods:
                if se_goods[0] == goods_id:
                    se_goods[1]+= goods_num
                    flag = False
            if flag:
                # 2.添加的商品不存在于购物车中就新增
                session_goods.append(goods_list)
            #新增和修改都添加到session中
            request.session['goods'] = session_goods
            count = len(session_goods)


        else:
            #第一次添加购物车，
            # 需组装购物车商品格式为[[goods_id,num,is_select],[goods_id,num,is_select]]
            request.session['goods'] = [goods_list]
            count = 1
        return JsonResponse({'code': 200, 'masg': '请求成功', 'count': count})

#购物车内商品

# 数量
def cart_num(request):
    if request.method =='GET':
        session_goods = request.session.get('goods')
        if session_goods:
            count = len(session_goods)
        else:
            count = 0

        return JsonResponse({"code":200,'msg':'请求成功','count':count})


def cart(request):
    if request.method == 'GET':
        carts = ShoppingCart.objects.all()#获取数据库中的商品
        nums = len(carts)  #计算商品总数


        session_goods = request.session.get('goods')
        #组装返回格式 - [[obj1],[obj2],[obj3]]
        #obj ==> [Goods Objects,num ,is_select ,total_price]
        result = []
        if session_goods:
            for se_goods in session_goods:
                #se_goods 为[goods_id,num ,is_select]
                goods = Goods.objects.filter(pk=se_goods[0]).first()
                total_price = goods.shop_price * se_goods[1] #单价*数量=小计
                data = [goods,se_goods[1],se_goods[2],total_price]
                result.append(data)
        return render(request,'cart.html',{'result':result,'nums':nums})


def cart_price(request):
    if request.method == 'GET':
        session_goods = request.session.get('goods')
        #总的商品件数
        all_total = len(session_goods) if session_goods else 0

        all_price = 0

        is_select_num = 0
        for se_goods in session_goods:
            # se_goods 为[goods_id,num ,is_select]
            if se_goods[2]:
                goods = Goods.objects.filter(pk=se_goods[0]).first()
                #总价
                all_price += goods.shop_price * se_goods[1]
                #已选择数量
                is_select_num += 1
        return JsonResponse({'code':200,'msg':'请求成功','all_total':all_total,'all_price':all_price,'is_select_num':is_select_num})


#点击购物车页面增加减少 修改session值
def change_cart(request):
    if request.method == 'POST':
        #修改商品的数量和选择状态
        # 其实就是修改session中的商品信息，结构为[goods_id, num, is_select]

        # 1.获取商品id值和（数量或者选择状态）
        goods_id = int(request.POST.get('goods_id'))  # goods_id 是前端传的data值
        goods_num = request.POST.get('goods_num')
        goods_select = request.POST.get('goods_select')

        #修改
        session_goods = request.session.get('goods')


        for se_goods in session_goods:
            if se_goods[0] == goods_id:
                se_goods[1] =int(goods_num) if goods_num else se_goods[1]
                se_goods[2] =int(goods_select) if goods_select else se_goods[2]

        request.session['goods'] = session_goods
        return JsonResponse({'code':200,'msg':'请求成功'})


def check_box(request):
    if request.method =='POST':
        # 1.获取商品选择状态id
        goods_select = request.POST.get('is_select')
        goods_id = int(request.POST.get('id'))
        session_goods = request.session.get('goods')
        for se_goods in session_goods:
            if se_goods[0] == goods_id:
                se_goods[2] = goods_select

        session_goods = request.session.get('goods')
        return JsonResponse({'code': 200, 'msg': '请求成功'})



def del_cart(request,id):
    if request.method =='POST':
        #思路：通过传入的商品id值去session中查找到则删除
        session_goods = request.session.get('goods')
        for se_goods in session_goods:
            # se_goods结构为[goods_id, num, is_select]
            if se_goods[0] == id:
                session_goods.remove(se_goods)
                break

        request.session['goods'] = session_goods
        #删除数据库中购物车的商品信息
        user_id = request.session.get('                                               ')
        if user_id:
            ShoppingCart.objects.filter(goods_id=id,user_id=user_id).delete()

        return JsonResponse({'code':200,'msg':'请求成功'})