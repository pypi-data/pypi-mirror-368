from rest_framework import serializers

from .models import Anchor


class AnchorSerializer(serializers.ModelSerializer):
    number = serializers.CharField(source='mac')
    type = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Anchor
        fields = ['number', 'name', 'type', 'icon']

    def get_type(self, obj):
        return self.context.get('config_type')

    def get_icon(self, obj):
        return self.context.get('config_icon')
