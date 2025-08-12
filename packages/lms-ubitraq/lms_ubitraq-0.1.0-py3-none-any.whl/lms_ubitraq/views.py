from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .services import service_manager
from .apps import UbitraqConfig


# Create your views here.

@login_required(login_url="/admin/")
def console_view(request):
    logs = service_manager.get_logs(count=200)
    return render(request, f'{UbitraqConfig.name}/console.html', {'logs': logs})


from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly
)
from .serializers import Anchor, AnchorSerializer
from .models import Config


class AnchorViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Anchor.objects.all()
    serializer_class = AnchorSerializer
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
        return context

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
