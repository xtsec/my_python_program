from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect

# Create your views here.
from bbs import models
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# 因为每个试图都要用到导航栏的版块Category_objs，所以这里直接弄成全局的
Category_objs = models.Category.objects.filter(set_as_top_menu=True).order_by('position_index')

# 首页
def index(request):
    category_obj = models.Category.objects.get(position_index=1)
    article_list = (models.Article.objects.filter(
        status='published').order_by('priority'))

    return render(request, 'bbs/index.html', {
        'Category_objs':Category_objs,
        'category_obj': category_obj,
        'article_list' : article_list,
    })


# 动态菜单
def categorys(request, cid):
    category_obj = models.Category.objects.get(id=cid)
    # 返回到页面的文章都按照priority(优先级)进行排序
    if category_obj.position_index == 1:
        article_list = (models.Article.objects.
                        filter(status='published').order_by('priority'))
    else:
        article_list = (models.Article.objects.filter(
            category_id=cid, status='published').order_by('priority'))  # 在filter里面查外键的字段

    return render(request, 'bbs/index.html', {
        'Category_objs': Category_objs,     # 显示哪些板块
        'category_obj': category_obj,      # 控制哪个版块选中
        'article_list': article_list,       # 文章列表
    })


# 登陆
def acc_login(request):
    if request.method == 'POST':
        print(request.POST)
        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user is not None:   # 如果不为空，则认证成功，并返回数据库对象
            login(request, user)   # 把验证成功的对象存到session，在访问其他页面时就是登陆状态了

            # 利用逻辑表达式的特性，直接判断跳转到那个页面
            return redirect(request.GET.get('next') or '/bbs')
            # return HttpResponseRedirect(request.GET.get('next') or '/bbs')
        else:
            login_err = 'Wrong username or password!'
            return render(request, 'login.html', {'login_err': login_err})

    return render(request, 'bbs/login.html')


# 注册
def acc_register(request):
    if request.method == 'POST':
        print(request.POST)
        new_user = models.UserProfile(
            user_username = request.POST.get('user'),
            user_email = request.POST.get('email'),
            user_password = request.POST.get('password'),
            name = request.POST.get('username')
        )
        new_user.save()


# 注销登陆
def acc_logout(request):
    logout(request)
    return redirect(request.GET.get('next') or '/bbs')


# 文章详情
def article_detail(request,article_id):
    article_obj = models.Article.objects.get(id=article_id)

    # 这里必须按发布时间获取所以评论列表，因为在建立树型时，默认父评论先发布
    comment_list = article_obj.comment_set.select_related().order_by('date')

    return render(request, 'bbs/article_detail.html',{
        'Category_objs': Category_objs,
        'article_obj': article_obj,
        'comment_list': comment_list,
    })


# ajax更新评论
def post_comments(request):
    if request.method == 'POST':
        if models.Article.objects.get(id=request.POST.get('article_id')):
            new_comment_obj = models.Comment(
                article_id=request.POST.get('article_id'),
                parent_comment_id=request.POST.get('parent_comment_id') or None,
                comment_type=request.POST.get('comment_type'),
                user_id=request.user.userprofile.id,
                comment=request.POST.get('comment')
            )
            new_comment_obj.save()
            comment_error = None
        else:
            comment_error = '你所评论的文章不存在！'

    return HttpResponse(comment_error or 'ok')


# ajax获取评论
def get_comments(request,aid):
    from bbs.templatetags.custom import format_comment
    # 这里必须要按时间排序啊
    comment_list = (
        models.Article.objects.get(id=aid).comment_set.
            select_related().order_by('date')
    )
    comment_tree_html = format_comment(comment_list)

    return HttpResponse(comment_tree_html)


# 用户信息
def author_info(request, auth_id):
    author_obj = models.UserProfile.objects.get(id=auth_id)
    author_article_list = models.Article.objects.filter(author_id=auth_id)
    author_comment_list = models.Comment.objects.filter(user_id=auth_id, comment_type=1)

    def get_Page(obj_list):
        paginator = Paginator(obj_list, 20)  # 生成一个分页实例，每页1条数据
        page = request.GET.get('page')  # 获取前端传递过来的请求第几页
        try:
            sub_obj_list = paginator.page(page)  # 生成第几页的数据
        except PageNotAnInteger:  # 默认访问时，page不存在，不是一个数字，返回第一页
            sub_obj_list = paginator.page(1)
        except EmptyPage:  # 当page超过页码长度，就返回最后一页
            sub_obj_list = paginator.page(paginator.num_pages)  # 返回最后一页
            # paginator.num_pages 返回有多少页

        return sub_obj_list

    return render(request, 'bbs/authors.html', {
        'Category_objs': Category_objs,
        'author_obj': author_obj,
        # 'author_article_list': author_article_list,
        # 'author_comment_list': author_comment_list,
        'author_article_list': get_Page(author_article_list),
        'author_comment_list': get_Page(author_comment_list),
    })

def update_info(request, auth_id):
    # update方法是对象集的，而不是某个对象的。所以更新单个对象的数据时必须用filter过滤，而不能用get
    author = models.UserProfile.objects.filter(id=auth_id)
    if request.POST.get('element_id') == '1':
        new_name = request.POST.get('new_value')
        print('new_value:', new_name)
        author.update(name=new_name)

    elif request.POST.get('element_id') == '2':
        new_signature = request.POST.get('new_value')
        print('new_signature:', new_signature)
        author.update(signature=new_signature)

    html = ('<div class="author_base_info-name">%s</div>'
            '<div class="author_base_info-signature">%s</div>'
            % (author[0].name, author[0].signature))

    return HttpResponse(html)