from django.contrib import admin, messages
from django import forms
from django_object_actions import DjangoObjectActions, action
from import_export.admin import ImportExportModelAdmin

from .models import Map, Product, Tag, Anchor, Config
from .services import get_map, get_product, get_tag, get_anchor, service_manager


# Register your models here.
@admin.register(Map)
class MapAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ("id", "name", "floor", "matrix")
    changelist_actions = ('get_map_button',)
    search_fields = ["name", ]

    @action(label="获取地图")
    def get_map_button(self, request, queryset):
        try:
            get_map()
            self.message_user(request, "操作成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)
            return

    # 禁用添加
    def has_add_permission(self, request):
        return False

    # 禁用修改
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Product)
class ProductAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ("id", "product_type", "name", "desc")
    changelist_actions = ('get_product_button',)
    search_fields = ["name", "desc"]
    list_filter = ['product_type',]

    @action(label="获取产品")
    def get_product_button(self, request, queryset):
        try:
            get_product()
            self.message_user(request, "操作成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)
            return

    # 禁用添加
    def has_add_permission(self, request):
        return False

    # 禁用修改
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Tag)
class TagAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ("mac", "product", "percent", "is_online", "time", "online_time")
    changelist_actions = ('get_tag_button', "start_websocket", "stop_websocket")
    list_filter = ['is_online', ]
    search_fields = ["mac", "ip"]
    list_per_page = 20

    @action(label="获取标签")
    def get_tag_button(self, request, queryset):
        try:
            get_tag()
            self.message_user(request, "操作成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)
            return

    @action(label="启动服务")
    def start_websocket(self, request, queryset):
        if service_manager.start_websocket():
            self.message_user(request, "WebSocket服务已启动", messages.SUCCESS)
        else:
            self.message_user(request, "WebSocket服务已在运行中", messages.SUCCESS)

    @action(label="停止服务")
    def stop_websocket(self, request, queryset):
        if service_manager.stop_websocket():
            self.message_user(request, "WebSocket服务已停止", messages.SUCCESS)
        else:
            self.message_user(request, "WebSocket服务未在运行", messages.SUCCESS)

    # 禁用添加
    def has_add_permission(self, request):
        return False

    # 禁用修改
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Anchor)
class AnchorAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ("mac", "name", "product", "map", "is_online", "is_master", "online_time")
    changelist_actions = ('get_anchor_button',)
    search_fields = ["name", "desc"]
    list_filter = ['is_online', "is_master"]
    list_per_page = 20

    @action(label="获取基站")
    def get_anchor_button(self, request, queryset):
        try:
            get_anchor()
            self.message_user(request, "操作成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)
            return

    # 禁用添加
    def has_add_permission(self, request):
        return False

    # 禁用修改
    def has_change_permission(self, request, obj=None):
        return False


class ConfigForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 获取已经存在的 name 值（排除当前正在编辑的对象，如果是更新操作）
        existing_names = Config.objects.values_list('name', flat=True)
        if self.instance.pk:  # 如果是更新操作，排除当前实例的 name
            existing_names = existing_names.exclude(pk=self.instance.pk)

        # 动态过滤 NAME_CHOICES，只显示未使用的选项
        available_choices = [
            (name, display) for name, display in Config.NAME_CHOICES
            if name not in existing_names
        ]
        self.fields['name'].choices = available_choices


@admin.register(Config)
class ConfigAdmin(ImportExportModelAdmin):
    list_display = ("name", "value", "is_valid")
    form = ConfigForm

    # 记录创建和更新人信息
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        if change == False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
