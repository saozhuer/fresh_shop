from django.shortcuts import render

# Create your views here.
from goods.models import Goods,GoodsCategory,RecentBrowsing
from user.models import User


def index(request):
    if  request.method == 'GET':
        # 思路 返回一个列表[object1,object2,object3,object4,object5,object6]
        # 列表结果对象包含分类，该分类的前4个商品信息
        #object ==> [分类,[前4个商品信息]]
        categorys = GoodsCategory.objects.all() #获取分类
        goods = Goods.objects.all()
        result = []
        for category in categorys: #循环分类

            goods = category.goods_set.all()[:4] #获取分类对应中商品的前4个商品信息
            data = [category,goods]
            result.append(data)


        print(result)
        user_id = request.session.get('user_id')
        user = User.objects.filter(pk=user_id).first()

        session_goods = request.session.get('goods')

        #如果访问首页，返回渲染的首页index.html页面
        return render(request,'index.html',{'result':result,'user':user,'categorys':categorys})



def detail(request,id):
    if request.method == 'GET':
        #返回详情页面解析的商品信息
        goods = Goods.objects.filter(pk=id).first()

        #最近浏览
        user_id = request.session.get('user_id')
        rb = RecentBrowsing.objects.filter(user_id=user_id,goods_id=id).first()
        if rb:
            count = rb.click_nums
            count += 1
            rb.click_nums=count
            rb.save()
        else:
            RecentBrowsing.objects.create(user_id=user_id,goods_id=id)


        return render(request,'detail.html',{'goods':goods})


def list(request):
    if request.method == 'GET':

        #获取分类id
        id = request.GET.get('id')
        # 获取分类对应的数据库商品
        goods = Goods.objects.filter(category_id=id)
        categorys = GoodsCategory.objects.filter(pk=id).first()  # 通过id获取分类对象

        return render(request,'list.html',{'goods':goods,'categorys':categorys})



def search(request):
    if request.method == 'GET':
        content = request.GET.get('word')
        #获取数据库中的商品名称
        search_goods = Goods.objects.filter(name__contains=content)
        print(search_goods)
        return render(request,'list.html',{'search_goods':search_goods})