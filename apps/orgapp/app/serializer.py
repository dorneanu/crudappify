from marshmallow import Serializer, fields


class TagSerializer(Serializer):
	class Meta:
		fields = ('id', 'name', 'desc')

class ConnectionSerializer(Serializer):
	tags = fields.Nested(TagSerializer, many=True)
	class Meta:
		fields = ('id', 'conn_type', 'url', 'port', 'answer', 'redirect', 'tags')


class HeaderSerializer(Serializer):
	conn = fields.Nested(ConnectionSerializer)
	class Meta:
		fields = ('id', 'conn', 'header', 'value')


class OrganizationSerializer(Serializer):
	class Meta:
		fields = ('id', 'desc')


class DepartmentSerializer(Serializer):
	org = fields.Nested(OrganizationSerializer)
	class Meta:
		fields = ('id', 'org', 'desc', 'contact')


class AppTypeSerializer(Serializer):
	class Meta:
		fields = ('id', 'desc')


class AppSerializer(Serializer):
	app_id = fields.Integer()
	url = fields.String()
	desc = fields.String()
	date_added = fields.String()
	version = fields.String()
	environment = fields.String()
	platform = fields.String()
	department = fields.Nested(DepartmentSerializer)
	app_type = fields.Nested(AppTypeSerializer)
	tags = fields.Nested(TagSerializer, many=True)
