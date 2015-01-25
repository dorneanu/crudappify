from marshmallow import Serializer, fields


class TagSerializer(Serializer):
    class Meta:
        fields = ('id', 'name', 'desc')

class ConnectionSerializer(Serializer):
    tags = fields.Nested(TagSerializer, many=True)
    class Meta:
        fields = ('id', 'conn_type', 'url', 'port', 'answer', 'ip', 'redirect', 'tags')


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


class TargetSerializer(Serializer):
    tags = fields.Nested(TagSerializer, many=True)
    connection = fields.Nested(ConnectionSerializer)
    class Meta :
        fields = ('id', 'scheme', 'user', 'password', 'netloc', 'port', 'path', 'params', 'query', 'fragment', 'comments', 'priority', 'tags', 'connection')


class AppBundleSerializer(Serializer):
    class Meta:
        fields = ('id', 'name', 'desc', 'contact')


class AppSerializer(Serializer):
    app_id = fields.Integer()
    app_name = fields.String()
    url = fields.String()
    desc = fields.String()
    date_added = fields.String()
    version = fields.String()
    environment = fields.String()
    platform = fields.String()
    contact = fields.String()
    comments = fields.String()
    severity = fields.String()

    # Scan details
    status = fields.String()
    last_scan = fields.String()
    reported_to_dpt = fields.String()
    open_issues = fields.String()

    # Relationships
    department = fields.Nested(DepartmentSerializer)
    app_type = fields.Nested(AppTypeSerializer)
    tags = fields.Nested(TagSerializer, many=True)
    bundle = fields.Nested('AppBundleSerializer', only=('id', 'name','desc', 'contact'), many=True)

class DNSSerializer(Serializer):
    class Meta:
        fields = ('id', 'domain', 'record', 'value')

