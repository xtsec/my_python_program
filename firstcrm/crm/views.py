from django.shortcuts import render, redirect

# Create your views here.
from crm import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from crm import forms
from crm.permissions import check_permission


def dashboard(request):
    return render(request, 'crm/dashboard.html')


def customers(request):
    customer_list = models.Customer.objects.all()  # 只是返回可迭代的结果集，并不是所有数据
    paginator = Paginator(customer_list, 1)  # 生成一个分页实例，每页1条数据
    page = request.GET.get('page')   # 获取前端传递过来的请求第几页
    try:
        customer_objs = paginator.page(page)  # 生成第几页的数据
    except PageNotAnInteger:       # 默认访问时，page不存在，不是一个数字，返回第一页
        customer_objs = paginator.page(1)
    except EmptyPage:           # 当page超过页码长度，就返回最后一页
        customer_objs = paginator.page(paginator.num_pages)  # 返回最后一页
        # paginator.num_pages 返回有多少页

    return render(request, 'crm/customers.html', {
        'customer_list': customer_objs,
    })


@check_permission
def customer_detail(request, customer_id):
    customer_obj = models.Customer.objects.get(id=customer_id)
    if request.method == 'POST':
        # 下面这两行的作用：第一个是把前端数据新建一个对象，第二个是用前端数据更新后面指定的那个对象
        # form = forms.CustomerModelForm(request.POST)
        form = forms.CustomerModelForm(request.POST, instance=customer_obj)
        if form.is_valid():
            form.save()
        # request.path 就是请求过来的url，(不包含域名部分)
        base_url = '/'.join(request.path.split('/')[:-2])
        return redirect(base_url)
    else:
        # 下面这行代码的意思就是把查询出来的数据填充到生成的form表单里面去
        form = forms.CustomerModelForm(instance=customer_obj)

    return render(request, 'crm/customer_detail.html', {'customer_form': form})