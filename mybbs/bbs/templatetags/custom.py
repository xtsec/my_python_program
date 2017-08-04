#!/usr/bin/env python
# -*- coding:utf8 -*-

from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter
def get_img_url(url_obj):
    # ImageField 返回的是一个'ImageFieldFile' object，必须要用name或url属性才能获取字符串
    return '/'.join(url_obj.url.split('/')[1:])


@register.simple_tag
def get_comment_type(article_obj):
    # lowB简单方法 实现 分组聚合
    query_set = article_obj.comment_set.select_related()
    comments = {
        'comment_count': query_set.filter(comment_type=1).count(),
        'thumb_count': query_set.filter(comment_type=2).count(),
    }
    return comments


@register.filter
def get_format_time(t):
    return t.strftime('%Y-%m-%d %X')


@register.simple_tag
def format_comment(comment_list):
    def add_node(tree_dic, comment_obj):
        for key, sub_tree in tree_dic.items():
            if key == comment_obj.parent_comment:  # 找到了他爸
                tree_dic[comment_obj.parent_comment][comment_obj] = {}
            else:
                # 这里在创建树的时候，默认是现发布的评论先循环到(因为按时间排序了的)
                add_node(sub_tree,comment_obj)

    def build_tree(comment_set):
        tree_dic = {}
        for comment_obj in comment_set:
            if comment_obj.parent_comment is None:  # 若果父评论是None，则是第一级评论
                tree_dic[comment_obj] = {}
            else:
                add_node(tree_dic, comment_obj)

        return tree_dic

    def build_html_tree(tree_dic, margin_val=0):
        html = ''
        for key, sub_tree in tree_dic.items():
            ele = ("<div class='tree-node' style='margin-left:%spx;'>" %margin_val
                  + '<span id="comment-id" hidden>%s</span><img src=%s/><span>%s</span><span>%s</span><span>%s</span>'
                   % (key.id, '/static/%s' % get_img_url(key.user.head_img), key.user.name, key.comment,
                      get_format_time(key.date))+'<button type="button" class="btn btn-default btn-xs" '
                                                 '>我要评论</button>'+"</div>")
            html += ele
            html += build_html_tree(sub_tree, margin_val+40)

        return format_html(html)

    return build_html_tree(build_tree(comment_list))


@register.simple_tag
def get_hot_article(author_obj):
    article_list = author_obj.article_set.filter(status='published')
    article_dic = {}
    for article in article_list:
        article_dic[article.id] = article.comment_set.count()

    article_obj = None
    for k, v in article_dic.items():
        if v == max(article_dic.values()):
            for article in article_list:
                if article.id == k:
                    article_obj = article

    return article_obj


# 我的分页插件完整版
@register.simple_tag
def my_pagination(obj):
    current_page = obj.number
    def inner(obj):
        my_html = ''
        for loop_page in obj.paginator.page_range:
            offset = abs(current_page - loop_page)
            if offset < 3:
                if current_page == loop_page:
                    page_ele = '''<li class="active"><a href="?page=%s" > %s</a></li>''' % (current_page, current_page)
                else:
                    page_ele = '''<li class=""><a href="?page=%s" > %s</a></li>''' % (loop_page, loop_page)

                my_html = my_html + page_ele
            else:
                my_html = my_html + ''
        return my_html

    if obj.has_previous():
        pre_html = '''
        <li class="">
            <a href="?page=%s" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
            </a>
        </li>
        ''' % (obj.previous_page_number())
    else:
        pre_html = ''

    if obj.has_next():
        next_html = '''
                <li class="">
                    <a href="?page=%s" aria-label="Next">
                        <span aria-hidden="true">&raquo;</span>
                    </a>
                </li>
                ''' % (obj.next_page_number())
    else:
        next_html = ''

    page_ele = inner(obj)
    html = '''    
                <nav aria-label="...">
                    <ul class="pagination" style="margin-left:300px;"> 
                        %s %s %s
                    </ul>
                </nav>
                ''' % (pre_html, page_ele, next_html)
    return format_html(html)
