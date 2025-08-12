from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django_object_actions import DjangoObjectActions, action
from django.contrib import messages

from .models import Camera, Config
from .utils import get_cameras_list, get_camera_online


# Register your models here.
@admin.register(Camera)
class CameraAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ("index_code", "name", "camera_type", "region_name", "is_online_html", "preview_html", "history_html")
    changelist_actions = ('get_camera', "get_battery")
    list_per_page = 20
    list_filter = ('region_name', "is_online")
    search_fields = ['name']

    @action(label="获取摄像头")
    def get_camera(self, request, queryset):
        try:
            result = get_cameras_list()
            for each in result:
                Camera.objects.update_or_create(
                    index_code=each["indexCode"],
                    defaults={
                        "resource_type": each.get("resourceType", ""),
                        "external_index_code": each.get("externalIndexCode", ""),
                        "name": each.get("name", ""),
                        "chan_num": each.get("chanNum", ""),
                        "cascade_code": each.get("cascadeCode", ""),
                        "parent_index_code": each.get("parentIndexCode", ""),

                        "longitude": each.get("longitude", ""),
                        "latitude": each.get("latitude", ""),
                        "altitude": each.get("elevation", ""),

                        "camera_type": each.get("cameraType", ""),
                        "capability": each.get("capability", ""),
                        "record_location": each.get("recordLocation", ""),
                        "channel_type": each.get("channelType", ""),
                        "region_index_code": each.get("regionIndexCode", ""),
                        "region_path": each.get("regionPath", ""),
                        "trans_type": each.get("transType", ""),
                        "treaty_type": each.get("treatyType", ""),
                        "install_location": each.get("installLocation", ""),
                        "dis_order": each.get("disOrder", ""),
                        "resource_index_code": each.get("resourceIndexCode", ""),
                        "decode_tag": each.get("decodeTag", ""),
                        "camera_relate_talk": each.get("cameraRelateTalk", ""),
                        "region_name": each.get("regionName", ""),
                        "region_path_name": each.get("regionPathName", ""),

                        "is_online": False,
                    }
                )
            self.message_user(request, "同步成功", messages.SUCCESS)
            return
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)
            return

    @action(label="获取电量")
    def get_battery(self, request, queryset):
        try:
            result = get_camera_online()
            for each in result:
                Camera.objects.filter(index_code=each.get("indexCode")).update(is_online=each.get("online"))
            self.message_user(request, "同步成功", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, str(e), messages.ERROR)
            return

    def is_online_html(self, obj):
        if obj.is_online:
            res = f'''<div style="color:green">在线</div>'''
        else:
            res = f'''<div style="color:red">离线</div>'''
        return format_html(res)

    is_online_html.short_description = "状态"

    def preview_html(self, obj):
        res = f'''<a href="/hikvision/preview?index_code={obj.index_code}">实时预览</a>'''
        return format_html(res)

    preview_html.short_description = "预览"

    def history_html(self, obj):
        res = f'''<a href="/hikvision/history?index_code={obj.index_code}">查看状态</a>'''
        return format_html(res)

    history_html.short_description = "状态"

    # 记录创建和更新人信息
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        if change == False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # 禁用添加
    def has_add_permission(self, request):
        return False

    # 禁用删除
    # def has_delete_permission(self, request, obj=None):
    #     return False

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
class ConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "is_valid")
    form = ConfigForm

    # 记录创建和更新人信息
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        if change == False:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
