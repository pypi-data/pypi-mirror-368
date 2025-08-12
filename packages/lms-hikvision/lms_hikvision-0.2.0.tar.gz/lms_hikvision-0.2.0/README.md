# 一、安装

```shell
pip install lms_hikvision
pip install django_object_actions
```

# 二、配置

```python
# settings.py
INSTALLED_APPS = [
    # 其他
    "django_object_actions",
    "lms_hikvision",
]
```

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path("hikvision/", include("lms_hikvision.urls")),
]
```

# 三、页面

- hikvision/camera/
- hikvision/config/