#!/usr/bin/env python
# -*- coding:utf8 -*-

from django.forms import Form, ModelForm
from crm import models


class CustomerModelForm(ModelForm):
    class Meta:
        model = models.Customer
        fields = '__all__'
        # exclude = ()   两个效果一样的

    def __init__(self, *args, **kwargs):
        # 先继承，再重写
        super(CustomerModelForm, self).__init__(*args, **kwargs)
        # 下面是对某一个指定的字段添加指定的属性，class：form-control是bootstrap里面的
        # self.fields['qq'].widget.attrs['class'] = 'form-control'

        #下面通过循环对所有字段添加属性
        for field_name in self.base_fields:
            field = self.base_fields[field_name]
            field.widget.attrs.update({
                'class': 'form-control',
                'style': 'color: black',
            })