from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Camera(models.Model):
    index_code = models.CharField(max_length=50, unique=True, verbose_name="唯一编码")

    RESOURCE_TYPE_CHOICE = (
        ("camera", "监控点"),
    )
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICE, unique=False, blank=True, null=True, verbose_name="资源类型")

    external_index_code = models.CharField(max_length=50, unique=True, verbose_name="监控点国标编号")
    name = models.CharField(max_length=50, unique=False, blank=True, null=True, verbose_name="资源名称")

    chan_num = models.IntegerField(unique=False, blank=True, null=True, verbose_name="通道号")
    cascade_code = models.CharField(max_length=50, unique=False, blank=True, null=True, verbose_name="级联编号")
    parent_index_code = models.CharField(max_length=50, unique=False, blank=True, null=True, verbose_name="父级资源编号")

    longitude = models.CharField(max_length=20, unique=False, blank=True, null=True, verbose_name="经度")
    latitude = models.CharField(max_length=20, unique=False, blank=True, null=True, verbose_name="纬度")
    altitude = models.CharField(max_length=20, unique=False, blank=True, null=True, verbose_name="高度")

    CAMERA_TYPE_CHOICE = [
        (0, "枪机"),
        (1, "半球"),
        (2, "快球"),
        (3, "带云台枪机")
    ]
    camera_type = models.IntegerField(choices=CAMERA_TYPE_CHOICE, unique=False, blank=True, null=True, verbose_name="监控点类型")
    capability = models.CharField(max_length=200, unique=False, blank=True, null=True, verbose_name="能力集")

    record_location = models.CharField(max_length=50, unique=False, blank=True, null=True, verbose_name="录像存储位置")

    CHANNEL_TYPE_CHOICE = [
        ("analog", "模拟通道"),
        ("digital", "数字通道"),
        ("mirror", "镜像通道"),
        ("record", "录播通道"),
        ("zero", "零通道")
    ]
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPE_CHOICE, unique=False, blank=True, null=True, verbose_name="通道子类型")
    region_index_code = models.CharField(max_length=50, unique=False, blank=True, null=True, verbose_name="所属区域")
    region_path = models.CharField(max_length=500, unique=False, blank=True, null=True, verbose_name="所属区域路径")
    TRANS_TYPE_CHOICE = [
        (0, "UDP"),
        (1, "TCP")
    ]
    trans_type = models.IntegerField(choices=TRANS_TYPE_CHOICE, unique=False, blank=True, null=True, verbose_name="传输协议")

    TREATY_TYPE_CHOICE = [
        ("hiksdk_net", "海康SDK"),
        ("gb_reg", "GB/T28181"),
        ("ehome_reg", "EHOME"),
        ("onvif_net", "ONVIF"),
        ("dhsdk_net", "大华SDK"),
        ("bi_reg", "B接口协议"),
        ("ezviz_net", "萤石协议")
    ]
    treaty_type = models.CharField(max_length=20, choices=TREATY_TYPE_CHOICE, unique=False, blank=True, null=True, verbose_name="接入协议")

    INSTALL_LOCATION_CHOICE = [
        ("communityPerimeter", "小区周界"),
        ("communityEntrance", "小区出入口"),
        ("fireChannel", "消防通道"),
        ("andscapePool", "景观池"),
        ("outsideBuilding", "住宅楼外"),
        ("parkEntrance", "停车场（库）出入口"),
        ("parkArea", "停车场区"),
        ("equipmentRoom", "设备房（机房、配电房、泵房）"),
        ("monitorCenter", "监控中心"),
        ("stopArea", "禁停区"),
        ("vault", "金库"),
    ]
    install_location = models.CharField(max_length=50, choices=INSTALL_LOCATION_CHOICE, unique=False, blank=True, null=True, verbose_name="安装位置")
    dis_order = models.IntegerField(unique=False, blank=True, null=True, verbose_name="数据在界面上的显示顺序")
    resource_index_code = models.CharField(max_length=50, unique=False, blank=True, null=True, verbose_name="资源唯一编码")
    decode_tag = models.CharField(max_length=50, unique=False, blank=True, null=True, verbose_name="解码模式")
    camera_relate_talk = models.CharField(max_length=50, unique=False, blank=True, null=True, verbose_name="监控点关联对讲唯一标志")
    region_name = models.CharField(max_length=50, unique=False, blank=True, null=True, verbose_name="所属区域路径")
    region_path_name = models.CharField(max_length=50, unique=False, blank=True, null=True, verbose_name="区域路径名称")

    is_online = models.BooleanField(default=False, verbose_name="在线状态")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hikcamera_created_by', editable=False, verbose_name="创建用户")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hikcamera_updated_by', editable=False, verbose_name="更新用户")

    class Meta:
        verbose_name = "海康摄像头"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Config(models.Model):
    NAME_CHOICES = [
        ("HOST", "服务地址"),
        ("APP_KEY", "应用标识"),
        ("APP_SECRET", "密钥凭证")
    ]
    name = models.CharField(max_length=100, unique=True, choices=NAME_CHOICES, verbose_name="配置项")
    value = models.CharField(max_length=100, unique=False, verbose_name="数据值")
    is_valid = models.BooleanField(default=True, verbose_name="是否有效")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='config_created_by', editable=False, verbose_name="创建用户")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='config_updated_by', editable=False, verbose_name="更新用户")

    class Meta:
        verbose_name = "应用配置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
