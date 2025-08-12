from rest_framework import serializers
from .models import Camera, Config


class CameraSerializer(serializers.ModelSerializer):
    number = serializers.CharField(source='index_code')
    type = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    extend = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = ['number', 'name', 'type', 'icon', 'extend']

    def get_type(self, obj):
        return self.context.get('config_type')

    def get_icon(self, obj):
        return self.context.get('config_icon')

    def get_extend(self, obj):
        request = self.context.get('request')

        # 确保请求对象存在
        if request is None:
            return {"channelId": ""}

        # 动态构建 URL
        preview_url = request.build_absolute_uri(
            f'/hikvision/preview/?index_code={obj.index_code}'
        )

        return {
            "channelId": preview_url,
        }
