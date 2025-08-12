from django.http import JsonResponse
from django.shortcuts import render

from .utils import get_camera_preview, get_camera_history_status, control_camera, get_camera_playback
from .apps import HikvisionConfig

from datetime import datetime
import json


# Create your views here.
def preview(request):
    ic = request.GET.get("index_code")
    preview_url = get_camera_preview(ic)
    context = {
        "preview_url": preview_url
    }
    return render(request, f'{HikvisionConfig.name}/preview.html', context)


def history(request):
    ic = request.GET.get("index_code")
    history = get_camera_history_status(ic)
    context = {}
    context["ic"] = ic
    context["timeline"] = {}
    # 可能返回空列表
    if history != []:
        # 对原始数据进行初步处理，防止它排序不统一
        sorted_data = sorted(history, key=lambda x: x['collectTime'], reverse=True)
        # 取最近数据的结束时间，最远数据的开始时间，计算总时长
        start_time = datetime.fromisoformat(sorted_data[-1].get('statusStartTime'))
        end_time = datetime.fromisoformat(sorted_data[0].get('statusEndTime'))
        total_time_second = (end_time - start_time).total_seconds()
        # 处理成时间线数据
        timeline = [
            {
                "statusStartTime": datetime.fromisoformat(each.get("statusStartTime")).strftime("%Y年%m月%d日 %H:%M:%S"),
                "statusDurationTime": "持续时间：" + each.get("statusDurationTime"),
                "devErrorMsg": each.get("devErrorMsg") if each.get("devErrorMsg") else "正常运行",
                "devErrorCode": "状态码：" + each.get("devErrorCode"),
                "type": "success" if each.get("online") == 1 else "danger",
            } for each in sorted_data
        ]

        online_time_second = sum([(datetime.fromisoformat(each.get('statusEndTime')) - datetime.fromisoformat(each.get('statusStartTime'))).total_seconds() for each in sorted_data if each.get("online") == 1])
        context["timeline"] = json.dumps(timeline)

        context["piesubtext"] = f"{start_time.strftime("%Y年%m月%d日 %H:%M:%S")} ~ {end_time.strftime("%Y年%m月%d日 %H:%M:%S")}"
        context["piedata"] = json.dumps([
            {
                "name": '在线时长',
                "value": round(online_time_second / 60 / 60, 2),
                "itemStyle": {
                    "color": '#67c23a'
                }
            },
            {
                "name": '离线时长',
                "value": round((total_time_second - online_time_second) / 60 / 60, 2),
                "itemStyle": {
                    "color": '#f56c6c'
                }
            },
        ])
    return render(request, f'{HikvisionConfig.name}/history.html', context)


def playback(request):
    ic = request.GET.get("index_code")
    st = request.GET.get("start_time", "").replace(' ', '+')
    et = request.GET.get("end_time", "").replace(' ', '+')
    # print(ic, st, et)
    if request.method == "GET":
        context = {}
        res = get_camera_playback(ic, st, et)
        # res = get_camera_playback(ic, "2025-07-23T14:50:00.000+08:00", "2025-07-23T15:50:00.000+08:00")
        context['res'] = res
        context['ic'] = ic
        context['st'] = st
        context['et'] = et
        # print(res)
        return render(request, f"{HikvisionConfig.name}/playback.html", context=context)


def control(request):
    try:
        data = json.loads(request.body)
        ic = data.get('index_code')
        ac = data.get('action')
        cmd = data.get('command')
        res = control_camera(ic, ac, cmd)
        return JsonResponse({'result': res})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly
)
from .serializers import Camera, CameraSerializer
from .models import Config


class CameraViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    pagination_class = None

    def get_serializer_context(self):
        """添加配置信息到序列化器上下文"""
        context = super().get_serializer_context()

        # 单次查询获取所有需要的配置
        configs = Config.objects.filter(name__in=["TYPE", "ICON"])
        config_dict = {cfg.name: cfg.value for cfg in configs}

        # 添加到上下文
        context['config_type'] = config_dict.get("TYPE", "default_camera_type")
        context['config_icon'] = config_dict.get("ICON", "default_camera_icon")
        # 确保请求对象已包含在上下文中
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
