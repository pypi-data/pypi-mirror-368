from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Map(models.Model):
    name = models.CharField(max_length=100, unique=False, verbose_name="地图名称")
    floor = models.IntegerField(default=1, unique=False, verbose_name="楼层")
    matrix = models.CharField(max_length=200, blank=True, null=True, verbose_name="转换矩阵")
    cfg = models.JSONField(default=dict, blank=True, null=True, verbose_name="其它配置")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created_by', editable=False, verbose_name="创建用户")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated_by', editable=False, verbose_name="更新用户")

    class Meta:
        verbose_name = "地图信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ("ANCHOR", "基站"),
        ("TAG", "标签"),
    ]
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPE_CHOICES, verbose_name="产品分类")
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name="型号名称")
    desc = models.CharField(max_length=200, null=True, blank=True, verbose_name="产品描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created_by', editable=False, verbose_name="创建用户")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated_by', editable=False, verbose_name="更新用户")

    class Meta:
        verbose_name = "产品信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Tag(models.Model):
    mac = models.CharField(max_length=20, unique=True, verbose_name="标签编号")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="产品型号", related_name="tag")
    is_online = models.BooleanField(default=False, verbose_name="是否在线")
    percent = models.IntegerField(default=0, blank=True, null=True, verbose_name="电量百分比")
    max_power = models.IntegerField(default=0, verbose_name="满电电量")
    power = models.IntegerField(default=0, blank=True, null=True, verbose_name="电量大小（mV）")

    ip = models.CharField(max_length=20, blank=True, null=True, verbose_name="IP地址")
    pos_anchor = models.CharField(max_length=20, blank=True, null=True, verbose_name="基站编号")
    imei = models.CharField(max_length=50, blank=True, null=True, verbose_name="移动设备识别码")
    iccid = models.CharField(max_length=50, blank=True, null=True, verbose_name="集成电路卡识别码")

    is_hold_ble = models.BooleanField(default=False, verbose_name="是否开启蓝牙")
    is_hold_uart = models.BooleanField(default=False, verbose_name="是否开启串口")
    is_hold_position = models.BooleanField(default=False, verbose_name="是否开启休眠")
    switch_distance = models.IntegerField(default=0, verbose_name="切站距离（m）")
    sleep_wait = models.IntegerField(default=0, verbose_name="进入休眠等待（s）")
    wake_period = models.IntegerField(default=0, verbose_name="唤醒周期（s）")
    ota_cfg = models.JSONField(default=dict, blank=True, null=True, verbose_name="OTA配置")

    time = models.DateTimeField(blank=True, null=True, verbose_name="最终定位时间")
    online_time = models.DateTimeField(blank=True, null=True, verbose_name="最终心跳时间")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created_by', editable=False, verbose_name="创建用户")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated_by', editable=False, verbose_name="更新用户")

    class Meta:
        verbose_name = "标签信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.mac


class Anchor(models.Model):
    mac = models.CharField(max_length=50, unique=True, verbose_name="基站编号")
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name="基站别名")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True, verbose_name="产品型号", related_name="anchor")
    map = models.ForeignKey(Map, on_delete=models.CASCADE, blank=True, null=True, verbose_name="地图", related_name="anchor")
    is_master = models.BooleanField(default=False, verbose_name="是否为主基站")
    master_list = models.CharField(max_length=200, blank=True, null=True, verbose_name="主基站列表")
    is_online = models.BooleanField(default=False, verbose_name="是否在线")

    x = models.FloatField(default=0, verbose_name="横坐标")
    y = models.FloatField(default=0, verbose_name="纵坐标")
    lon = models.FloatField(default=0, verbose_name="经度")
    lat = models.FloatField(default=0, verbose_name="纬度")

    cfg = models.JSONField(default=dict, blank=True, null=True, verbose_name="其它配置")
    thresholds = models.JSONField(default=dict, blank=True, null=True, verbose_name="阈值")
    ip = models.CharField(max_length=20, blank=True, null=True, verbose_name="IP地址")
    online_time = models.DateTimeField(blank=True, null=True, verbose_name="最终心跳时间")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created_by', editable=False, verbose_name="创建用户")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated_by', editable=False, verbose_name="更新用户")


class Config(models.Model):
    NAME_CHOICES = [
        ("HOST", "服务地址"),
        ("PROJECT_CODE", "项目编码"),
        ("ACCOUNT", "账号"),
        ("PASSWORD", "密码"),
        ("HEART_BEAT", "心跳间隔"),
        ("HTTP_URL", "驱动地址"),
        ("ICON", "图标字段"),
        ("TYPE", "类型字段")
    ]
    name = models.CharField(max_length=100, unique=True, choices=NAME_CHOICES, verbose_name="配置项")
    value = models.CharField(max_length=100, unique=False, verbose_name="数据值")
    is_valid = models.BooleanField(default=True, verbose_name="是否有效")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created_by', editable=False, verbose_name="创建用户")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_updated_by', editable=False, verbose_name="更新用户")

    class Meta:
        verbose_name = "应用配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
