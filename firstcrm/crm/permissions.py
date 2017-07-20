#!/usr/bin/env python
# -*- coding:utf8 -*-
from django.core.urlresolvers import resolve
from django.shortcuts import render, redirect


# 把所有权限存放在一个字典里面
perm_dic = {
    'view_customer_list': ['customer_list','GET',[]],   # url别名， 请求方法， 请求参数
    'view_customer_info': ['customer_detail','GET',[]],
    'edit_own_customer_info': ['customer_detail','POST',['name','qq']],
}


# 这个函数实现权限验证
def check_perm(*args, **kwargs):
    request = args[0]
    url_resolve_obj = resolve(request.path_info)
    current_url_namespace = url_resolve_obj.url_name   # 获取前段传递过来的url的别名
    match_flag = False
    match_perm_key = None  # 匹配到的权限名称

    # 这里进行请求url与设定的权限系统进行匹配
    if current_url_namespace is not None:
        for perm_key in perm_dic:     # perm_key就是权限名称
            perm_val = perm_dic[perm_key]   # 根据权限名称，获取权限要求的几个内容(判断依据)
            if len(perm_val) == 3:    # 判断条件列表的长度，一般是相同的，不够长的以空列表代替
                url_namespace, request_method, request_args = perm_val  # 把条件分别赋值
                print('---->',url_namespace, request_method, request_args)
                if url_namespace == current_url_namespace:   # 匹配 url 别名
                    if request_method == request.method:   # 匹配请求方法
                        if not request_args:   # 判断当前权限是否需要参数
                            match_flag = True
                            match_perm_key = perm_key  # 从字典中匹配的权限名称
                            break
                        else:
                            for request_arg in request_args:  # 根据预先设定的要求参数进行循环取值
                                # print(request.POST)  # 这里注意，POST不是字符串
                                request_method_func = getattr(request,request_method)
                                # 如果get的字段不存在，返回为None
                                if request_method_func.get(request_arg) is not None:
                                    match_flag = True  # 在循环里面，表示任何一个参数都要存在
                                else:
                                    match_flag = False
                                    break

                            if match_flag == True:
                                match_perm_key = perm_key
                                break

    else:    # 当前接收的url没有进行权限设置，权限系统不工作
        return True

    # 这里把上面得出的结果与用户权限进行匹配
    if match_flag == True:
        perm_str = 'crm.%s' % match_perm_key    # 这里的'crm'是什么作用？

        if request.user.has_perm(perm_str):
            print('\033[42;1m -------passed permision check ------ \033[0m')
            return True
        else:
            print('\033[42;1m ------no permission ------ \033[0m')
            return False
    else:
        print('\033[42;1m ------no permission ------ \033[0m')


# 定义一个装饰器(要在不该动现有代码的情况下，给代码添加功能，使用装饰器是最好的选择)
def check_permission(func):
    def wrapper(*args, **kwargs):
        print('start check permssions'.center(50, '-'))
        print('---> current user:',args[0].user)
        if not check_perm(*args, **kwargs):
            return render(args[0], 'crm/403.html')
        return func(*args, **kwargs)
    return wrapper
