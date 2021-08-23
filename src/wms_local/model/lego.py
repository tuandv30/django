from enum import Enum
from django.db import models
from .wms_local import DeviceSorting


class FlashScannerImages(models.Model):
    id = models.AutoField(primary_key=True)
    scan_history_id = models.IntegerField(null=False)
    image_id = models.IntegerField(null=False)
    created = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'fs_images'


class FlashScannerLog(models.Model):
    id = models.AutoField(primary_key=True)
    device_sorting_id = models.IntegerField(null=False)
    scanner_code = models.CharField(max_length=30)
    barcode = models.IntegerField()
    bag_code = models.IntegerField()
    is_bag = models.IntegerField(default=0)
    kafka_log = models.IntegerField(default=0)
    ghtk_log = models.IntegerField(default=0)
    wcs_created = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'fs_scan_log'


class LegoSortingPlanDetail(models.Model):
    class Type(Enum):
        STATION = 1
        MODULE = 2
        CART = 3

    class TrfType(Enum):
        ALL = 0
        ROAD = 1
        FLY = 2

    id = models.AutoField(primary_key=True)
    plan_id = models.IntegerField()
    destination_code = models.CharField(max_length=50, blank=True, null=True)
    type = models.IntegerField()
    trf_type = models.IntegerField()
    chute_id = models.IntegerField()
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'lego_sorting_plan_detail'


class LegoChute(models.Model):
    class Status(Enum):
        ACTIVE = 1
        INACTIVE = 0

    id = models.AutoField(primary_key=True)
    position = models.IntegerField()
    status = models.IntegerField()
    zone = models.IntegerField()
    device_sorting = models.ForeignKey(
        DeviceSorting,
        on_delete=models.SET_NULL,
        null=True
    )
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'lego_chute'


class LegoChuteConfig(models.Model):
    class ChuteType(Enum):
        NORMAL = 0
        REJECT = 1
        NOREAD = 2
        WRONG_ZONE = 3

    id = models.AutoField(primary_key=True)
    chute = models.ForeignKey(
        LegoChute,
        on_delete=models.SET_NULL,
        null=True
    )
    type = models.IntegerField(choices=[(tag, tag.value) for tag in ChuteType])
    device_sorting = models.ForeignKey(
        DeviceSorting,
        on_delete=models.SET_NULL,
        null=True
    )
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'lego_chute_config'


class SortingPlan(models.Model):
    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    type_ware = models.IntegerField()
    from_at = models.TimeField()
    to_at = models.TimeField()
    is_active = models.BooleanField()
    device_sorting = models.ForeignKey(
        DeviceSorting,
        on_delete=models.SET_NULL,
        null=True
    )
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'lego_sorting_plan'

    def __str__(self):
        return str(self.name)


class LegoSortingRequest(models.Model):
    id = models.AutoField(primary_key=True)
    barcode_input = models.CharField(max_length=400, blank=True, null=True)
    scanner_id = models.IntegerField()
    plan_id = models.IntegerField()
    device_sorting = models.ForeignKey(
        DeviceSorting,
        on_delete=models.SET_NULL,
        null=True
    )
    request_time = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'lego_sorting_request'


class SortingRequestDetail(models.Model):
    id = models.AutoField(primary_key=True)
    sorting_req = models.ForeignKey(
        LegoSortingRequest,
        on_delete=models.SET_NULL,
        null=True,
    )
    barcode = models.IntegerField()
    barcode_type = models.IntegerField()
    dst_chute = models.IntegerField()
    dst_code = models.CharField(max_length=50, blank=True, null=True)
    dst_type = models.IntegerField()
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'lego_sorting_req_detail'
