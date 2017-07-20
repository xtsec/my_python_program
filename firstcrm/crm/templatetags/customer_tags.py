#!/usr/bin/env python
# -*- coding:utf8 -*-

from django.utils.html import format_html
from django import template

register = template.Library()


@register.filter
def my_upper(val):
    print('----------val from template:', val)
    return val.upper()


@register.simple_tag
def guess_page(current_page, loop_page):
    offset = abs(current_page - loop_page)
    if offset < 3:
        if current_page == loop_page:
            page_ele = '''<li class="active"><a href="?page=%s" > %s</a></li>''' % (current_page, current_page)
        else:
            page_ele = '''<li class=""><a href="?page=%s" > %s</a></li>''' % (loop_page, loop_page)

        return format_html(page_ele)
    else:
        return ''


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
                    <ul class="pagination"> 
                        %s %s %s
                    </ul>
                </nav>
                ''' % (pre_html, page_ele, next_html)
    return format_html(html)
