from enum import Enum
from django.db import models


class Station(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=40, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    trf_level = models.CharField(max_length=100, blank=True, null=True)
    working = models.IntegerField()
    province_id = models.IntegerField()
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'station'

    def __str__(self):
        return '{} - {}'.format(self.name, self.code)


class Province(models.Model):
    province_id = models.IntegerField(primary_key=True)
    province_name = models.CharField(max_length=30, blank=True, null=True)
    province_code = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'province'

    def __str__(self):
        return '{} - {}'.format(self.province_name, self.province_code)


class Module(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    alias = models.CharField(max_length=255)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    deleted = models.IntegerField(default=0)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)
    station_id = models.IntegerField()
    type = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'module'

    def __str__(self):
        return self.alias


class Cart(models.Model):
    id = models.CharField(primary_key=True, max_length=36)
    alias = models.CharField(max_length=255)
    is_visible = models.IntegerField()
    module_id = models.CharField(max_length=36)

    class Meta:
        managed = False
        db_table = 'cart'

    def __str__(self):
        return self.alias


class DeviceSorting(models.Model):
    class DeviceType(Enum):
        LEGO = "lego"
        ARM = "arm"
        WHEEL = "wheel"
        CROSSBELT = "crossbelt"
        AGV = "agv"

    id = models.AutoField(primary_key=True)
    device_code = models.CharField(max_length=255)
    device_name = models.CharField(max_length=255)
    device_type = models.CharField(choices=[(tag, tag.value) for tag in DeviceType], null=False, max_length=255)
    station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True)
    ghtk_id = models.IntegerField()
    ghtk_token = models.CharField(max_length=255)
    is_active = models.IntegerField()
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'device_sorting'

    def __str__(self):
        return str(self.device_name)


class Images(models.Model):
    id = models.AutoField(primary_key=True)
    scanner_code = models.CharField(max_length=30)
    file_name = models.CharField(max_length=255)
    ghtk_path = models.CharField(max_length=255)
    ghtk_id = models.CharField(max_length=50)
    barcode = models.CharField(max_length=255)
    num_barcode = models.IntegerField(null=True)
    wcs_created = models.DateTimeField(null=True)
    created = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'images'


class PackageWarehouse(models.Model):
    class WarehouseStatus(Enum):
        TRANSFERRING = 0  # transferring to current station
        IMPORT_WAREHOUSE = 10  # imported
        SORTING = 20  # sorting
        PUT_TO_BAG = 30
        EXPORT_TRUCK = 40  # exported

    class ImportExportType(Enum):
        SORTING = 0  # Hàng sorting
        TRANSIT = 1  # Hàng trung chuyển

    pkg_order = models.IntegerField(primary_key=True)
    bag_import = models.IntegerField(null=True)
    warehouse_status = models.IntegerField(null=True)
    import_type = models.IntegerField(null=True)
    export_type = models.IntegerField(null=True)
    import_time = models.DateTimeField(blank=True, null=True)
    export_time = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'package_warehouse'


class BagWMS(models.Model):
    bag_order = models.IntegerField(primary_key=True)
    dst_station_id = models.IntegerField(null=True)
    total_pkg = models.IntegerField(null=True)
    miss_pkg = models.IntegerField(null=True)
    exist_pkg = models.IntegerField(null=True)
    scan_pkg = models.IntegerField(null=True)
    num_verify = models.IntegerField(null=True)
    is_scan = models.IntegerField(null=True)
    device_sorting_id = models.IntegerField(null=True)
    verify_time = models.DateTimeField()
    scan_time = models.DateTimeField()
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'bag_wms'


class PackageWMS(models.Model):
    pkg_order = models.IntegerField(primary_key=True)
    bag_import = models.IntegerField(blank=True, null=True)
    pkg_status = models.IntegerField(blank=True, null=True)
    dst_station_id = models.IntegerField(blank=True, null=True)
    dst_cart_id = models.CharField(max_length=36, blank=True, null=True)
    dst_module_id = models.CharField(max_length=36, blank=True, null=True)
    pkg_id = models.CharField(max_length=36, blank=True, null=True)
    alias = models.CharField(max_length=100, blank=True, null=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    transport = models.CharField(max_length=20, blank=True, null=True)
    done_at = models.DateTimeField(blank=True, null=True)
    rt_delay = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'package_wms'


class MissingPackage(models.Model):
    id = models.AutoField(primary_key=True)
    bag_order = models.IntegerField()
    package_order = models.IntegerField()
    scan_bag = models.DateTimeField()
    verify_time = models.DateTimeField()
    created = models.DateTimeField(null=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'missing_package'


class Scanner(models.Model):
    class ZoneChoice(Enum):
        A = 1
        B = 2

    class Model(Enum):
        COGNEX = "Cognex"
        ZEBRA = "zebra"
        HIKVISION = "Hikvison"

    id = models.AutoField(primary_key=True)
    scanner_mac = models.CharField(max_length=30, unique=True, blank=True)
    scanner_code = models.CharField(max_length=30)
    device_sorting = models.ForeignKey(
        DeviceSorting,
        on_delete=models.SET_NULL,
        null=True
    )
    model = models.CharField(choices=[(tag, tag.value) for tag in ZoneChoice], max_length=30)
    zone = models.IntegerField(choices=[(tag, tag.value) for tag in ZoneChoice])
    description = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'scanner'


class SystemConfig(models.Model):
    key = models.CharField(primary_key=True, max_length=255)
    value = models.CharField(max_length=300, blank=True, null=True)
    data_type = models.CharField(max_length=50)
    status = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'system_config'


class ExportData(models.Model):
    class Status(Enum):
        SUCCESS = 1
        FAIL = 0

    id = models.AutoField(primary_key=True)
    ghtk_path = models.CharField(max_length=255)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    status = models.IntegerField(choices=[(tag, tag.value) for tag in Status])
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'export_data'


class KafkaError(models.Model):
    id = models.AutoField(primary_key=True)
    services = models.CharField(max_length=255)
    kafka_cluster = models.CharField(max_length=255)
    kafka_topic = models.CharField(max_length=255)
    msg = models.TextField()
    success = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'kafka_error'


class StatisticPackageWarehouse(models.Model):
    id = models.AutoField(primary_key=True)

    import_sorting = models.IntegerField()
    import_transit = models.IntegerField()
    export_sorting = models.IntegerField()
    export_transit = models.IntegerField()
    stt_date = models.DateField(null=True)
    hour = models.IntegerField(null=True)
    stt_hour = models.IntegerField(null=True)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'statistic_package_warehouse'
