from django.db import models

# Create your models here.

from django.contrib.auth.models import User


# 放在最前面是让下面有需要用的model都可以使用这个choices
course_type_choices = (
    ('online', u'网络班'),
    ('offline_weekend', u'面授班(周末)'),
    ('offline_fulltime', u'面授班(脱产)'),
)


class School(models.Model):
    name = models.CharField(u'校区名称', max_length=64, unique=True)
    addr = models.CharField(u'地址', max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u'学校'
        verbose_name_plural = u'学校'  # 上面那个的复数形式
        # 这里的verbose_name 是控制django admin在显示表名时，显示verbose_name指定


class UserProfile(models.Model):
    user = models.OneToOneField(User)   # OneToOneField内部实现跟外键一样，只是是双向一对一
    name = models.CharField(u'姓名', max_length=32)
    # name = models.CharField(max_length=32, verbose_name=u'姓名')  # 这个与上面那个相同

    # school = models.ForeignKey('School') # 引号作用：被关联的model可能是定义在被关联之后
    school = models.ForeignKey(School)

    def __str__(self):   # 在把该表对象返回到页面上时，现实的是下面指明的数据，而不是对象
        return self.name

    class Meta:
        verbose_name = u'工作人员'
        verbose_name_plural = u'工作人员'

        # 把要对这个表的用户设置的权限注册到这里，就会显示在admin的权限管理中
        permissions = (
            ('view_customer_list', u'查看客户列表'),
            ('view_customer_info', u'查看客户详情'),
            ('edit_own_customer_info', u'编辑客户信息')
        )


class Customer(models.Model):
    qq = models.CharField(u'QQ', max_length=64, unique=True)
    name = models.CharField(u'姓名', max_length=32, blank=True, null=True)
    phone = models.BigIntegerField(u'电话', blank=True, null=True)
    course = models.ForeignKey('Course')  # 引号作用：被关联的model可能是定义在被关联之后
    course_type = models.CharField(u'课程类型', choices=course_type_choices, default='offline_weekend', max_length=64)
    consult_memo = models.TextField(u'咨询记录')
    class_list = models.ManyToManyField('ClassList', blank=True)
    # 对于M2M的字段，不需要null=True，有了也不起作用，默认可以为null

    source_type_choices = (
            ('qq', u'qq群'),
            ('referral', u'内部转介绍'),
            ('51cto', u'51cto'),
            ('agent', u'招生代理'),
            ('others', u'其他'),
    )
    source_type = models.CharField(u'客户来源', choices=source_type_choices, max_length=64)
    referral_from = models.ForeignKey('self',  # 某个表关联自己，一般写'self', 也可以写自己表名
                                      blank=True, null=True,
                                      related_name='referraled_who')
    status_choices = (
            ('signed', u'已报名'),
            ('unregistered', u'未报名'),
            ('graduated', u'已毕业'),
            ('drop-off', u'退学'),
    )
    status = models.CharField(u'状态', max_length=64, choices=status_choices)
    consultant = models.ForeignKey(UserProfile, verbose_name=u'课程顾问')
    # verbose_name作用： 让这个字段在django admin 里面显示指定的内容(一般中文)

    date = models.DateField(u'咨询日期', auto_now_add=True)
    # 这里第一个参数相当于verbose_name

    def __str__(self):
        return '%s (%s)' %(self.qq, self.name)

    class Meta:
        verbose_name = u'消费者(学生)'
        verbose_name_plural = u'消费者(学生)'


class CustomerTrackRecord(models.Model):
    customer = models.ForeignKey(Customer)
    track_record = models.TextField(u'跟踪记录')
    track_date = models.DateField(u'咨询日期', auto_now_add=True)
    follower = models.ForeignKey(UserProfile)
    status_choices = (
            (1, u'近期无报名计划'),
            (2, u'2个月内报名'),
            (3, u'1个月内报名'),
            (4, u'2周内报名'),
            (5, u'1周内报名'),
            (6, u'2天内报名'),
            (7, u'已报名'),
    )
    status = models.IntegerField(u'状态', choices=status_choices, help_text='选择客户此时的状态', default=2)
    # help_text 是在admin中增加该model对象时，下面显示的提示信息

    def __str__(self):
        return self.customer.name

    class Meta:
        verbose_name = u'咨询记录'
        verbose_name_plural = u'咨询记录'


class Course(models.Model):
    name = models.CharField(u'课程名称', max_length=128, unique=True)
    online_price = models.IntegerField(u'网络班价格')
    offline_price = models.IntegerField(u'面授班价格')
    introduction = models.TextField(u'课程简介')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = u'课程'
        verbose_name_plural = u'课程'


class ClassList(models.Model):
    course = models.ForeignKey(Course, verbose_name=u'课程')
    course_type = models.CharField(u'课程类型', max_length=32, choices=course_type_choices)
    semester = models.IntegerField(u'学期')
    teacher = models.ForeignKey(UserProfile, verbose_name=u'讲师')
    start_date = models.DateField(u'开班日期')
    graduate_date = models.DateField(u'结业日期')

    def __str__(self):
        return '%s (%s) (%s)' %(self.course.name, self.get_course_type_display(), self.semester)

    class Meta:
        verbose_name = u'班级列表'
        verbose_name_plural = u'班级列表'   # 上面那个的复数形式
        # 这里的verbose_name 是控制django admin在显示表名时，显示verbose_name指定的内容

        unique_together = ('course', 'course_type', 'semester')
        # 由unique_together指定的几个字段联合能唯一确定该表的一个对象


class CourseRecord(models.Model):
    class_obj = models.ForeignKey(ClassList, verbose_name=u'班级')
    day_num = models.IntegerField(u'第几节课')
    course_date = models.DateField(auto_now_add=True, verbose_name=u'上课时间')
    teacher = models.ForeignKey(UserProfile)

    def __str__(self):
        return '%s, %s' %(self.class_obj, self.day_num)

    class Meta:
        verbose_name = u'课程记录'
        verbose_name_plural = u'课程记录'
        unique_together = ('class_obj', 'day_num')


class StudyRecord(models.Model):
    student = models.ForeignKey(Customer, verbose_name=u'学生姓名')
    course_record = models.ForeignKey(CourseRecord, verbose_name=u'第几天课程')
    record_choices = (
        ('checked', u'已签到'),
        ('late', u'迟到'),
        ('noshow', u'缺勤'),
        ('leave_early', u'早退'),
    )
    record = models.CharField(u'上课记录', choices=record_choices, default='checked', max_length=64)
    score_choices = (
        (100, 'A+'),
        (90, 'A'),
        (85, 'B+'),
        (80, 'B'),
        (70, 'B-'),
        (60, 'C+'),
        (50, 'C'),
        (40, 'C-'),
        (0, 'D'),
        (-1, 'N/A'),
        (-100, 'COPY'),
        (-1000, 'FALL'),
    )
    score = models.IntegerField(u'本节成绩', choices=score_choices, default=-1)
    date = models.DateField(u'上课日期', auto_now_add=True)
    note = models.CharField(u'备注', max_length=255, blank=True, null=True)

    def __str__(self):
        return u"%s, 学员：%s, 记录：%s, 成绩：%s" % (self.course_record,
                                             self.student.name,
                                             self.get_record_display(),
                                             self.get_score_display()
                                             )
        # get_score_display()  不用默认显示的是分数，如;100, 用这个显示分数后面对应的'A+'/'B'...

    class Meta:
        verbose_name = u'学员学习记录'
        verbose_name_plural = u'学员学习记录'
        unique_together = ('course_record', 'student')
