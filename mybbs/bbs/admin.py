from django.contrib import admin

# Register your models here.
from bbs import models


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'signature')


class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'brief', 'category', 'author', 'priority', 'status', 'pub_date', 'last_modify')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'set_as_top_menu', 'position_index', 'get_admins')


class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'parent_comment', 'comment_type', 'comment', 'user', 'date')


admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.Category, CategoryAdmin)
admin.site.register(models.Comment, CommentAdmin)