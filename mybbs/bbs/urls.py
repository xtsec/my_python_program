
from django.conf.urls import url
from bbs import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^categorys/(\d+)/$', views.categorys, name='categorys'),
    url(r'^article/(\d+)/$', views.article_detail, name='article_detail'),
    url(r'^comments/$', views.post_comments, name='post_comments'),
    url(r'^comments/(\d+)/$', views.get_comments, name='get_comments'),
    url(r'^author_info/(\d+)/$', views.author_info, name='author_info'),
    url(r'^update_info/(\d+)/$', views.update_info, name='update_info'),

]
