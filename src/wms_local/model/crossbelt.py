from enum import Enum
from django.db import models
from .wms_local import Station


class CrossbeltOperationConfig(models.Model):
    class Type(Enum):
        PROVINCE = "province"
        CHUTE = "chute"
        WEIGHT = "weight"

    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    modified = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_operation_config'


class CrossbeltInduction(models.Model):
    class Status(Enum):
        INACTIVE = 0
        ACTIVE = 1

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=70)
    status = models.IntegerField(
        choices=[(tag, tag.value) for tag in Status],
        default=Status.ACTIVE.value
    )
    description = models.CharField(max_length=300)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_induction'


class CrossbeltCarrier(models.Model):
    class Status(Enum):
        EMPTY = 0
        IS_LOAD = 1

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50)
    status = models.IntegerField(
        choices=[(tag, tag.value) for tag in Status],
        default=Status.IS_LOAD.value
    )
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_carrier'


class CarrierHistory(models.Model):
    id = models.AutoField(primary_key=True)
    carrier_empty = models.IntegerField(null=True)
    carrier_is_load = models.IntegerField(null=True)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_carrier_history'


class CrossbeltChute(models.Model):
    class Status(Enum):
        LOCK = 0
        RELEASE = 1

    class ZoneChoice(Enum):
        A = 1
        B = 2

    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50)
    status = models.IntegerField(
        choices=[(tag, tag.value) for tag in Status],
        default=Status.RELEASE.value
    )
    zone = models.IntegerField(choices=[(tag, tag.value) for tag in ZoneChoice])
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_chute'

    def __str__(self):
        return str(self.code)


class CrossbeltStatisticChute(models.Model):
    class ChuteState(Enum):
        ACTIVE = 1
        DEACTIVATE = 0

    id = models.AutoField(primary_key=True)
    chute_code = models.CharField(max_length=50)
    state = models.IntegerField(choices=[(tag, tag.value) for tag in ChuteState], null=True)
    spent_time = models.IntegerField(default=0)
    hour = models.IntegerField(null=True)
    stt_hour = models.IntegerField(null=True)
    stt_date = models.DateField(null=True)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_statistic_chute'


class CrossbeltPrinter(models.Model):
    class Model(Enum):
        HONEYWELL = "Honeywell"

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    code = models.CharField(max_length=50, blank=False, null=False)
    model = models.CharField(max_length=100, blank=False, null=False, choices=[(tag, tag.value) for tag in Model])
    mac_address = models.CharField(max_length=30, unique=True, blank=False, null=False)
    ip = models.CharField(max_length=30, blank=False, null=False)
    status = models.IntegerField()
    chute = models.ManyToManyField(
        CrossbeltChute,
        through='CrossbeltPrinterChute',
        related_name='printer',
        blank=True
    )
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_printer'

    def __str__(self):
        return str(self.code) if self.code else ""


class CrossbeltPrinterChute(models.Model):
    id = models.AutoField(primary_key=True)
    chute = models.ForeignKey(CrossbeltChute, on_delete=models.SET_NULL, null=True)
    printer = models.ForeignKey(CrossbeltPrinter, on_delete=models.SET_NULL, null=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_printer_chute'
        unique_together = (('chute', 'printer'),)


class CrossbeltChuteDetail(models.Model):
    id = models.AutoField(primary_key=True)
    chute_id = models.IntegerField(null=False)
    pkg_order = models.IntegerField(null=False)
    sorting_history_id = models.IntegerField(null=True)
    status = models.IntegerField()
    in_chute_time = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_chute_detail'


class CrossbeltSortingHistory(models.Model):
    class ChuteType(Enum):
        SUCCESS = 0
        REJECT = 1
        PDA = 2  # chute for scanning manually when the scanner can not read

    id = models.AutoField(primary_key=True)
    barcode_input = models.CharField(max_length=300, blank=True, null=True)
    pkg_order = models.IntegerField()
    bag_order = models.IntegerField()
    scanner_id = models.IntegerField()
    induction_id = models.IntegerField()
    carrier_id = models.IntegerField()
    chute_id = models.IntegerField()
    chute_type = models.IntegerField(
        choices=[(tag, tag.value) for tag in ChuteType],
        default=ChuteType.SUCCESS.value)
    image_id = models.IntegerField()
    sorting_status = models.IntegerField()
    loop = models.IntegerField()
    destination_code = models.CharField(max_length=300, blank=True, null=True)
    sorting_plan_id = models.IntegerField()
    dst_request_time = models.DateTimeField(blank=True, null=True)
    sorting_report_time = models.DateTimeField(blank=True, null=True)
    in_chute_time = models.DateTimeField(blank=True, null=True)
    in_carrier_time = models.DateTimeField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_sorting_history'


class CrossbeltSortingPlan(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    from_at = models.TimeField()
    to_at = models.TimeField()
    is_active = models.BooleanField()
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_sorting_plan'

    def __str__(self):
        return str(self.name)


class CrossbeltDeviceStateHistory(models.Model):
    class DeviceType(Enum):
        CARRIER = 1
        CHUTE = 2
        ESTOP = 3
        INDUCTION = 4
        CONVEYOR = 5

    class DeviceState(Enum):
        ACTIVE = 1
        DEACTIVATE = 0

    id = models.AutoField(primary_key=True)
    device_code = models.CharField(max_length=50)
    device_type = models.IntegerField(choices=[(tag, tag.value) for tag in DeviceType], null=True)
    state = models.IntegerField(choices=[(tag, tag.value) for tag in DeviceState], null=True)
    spent_time = models.IntegerField(default=0)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    modified = models.DateTimeField(blank=True, null=True, auto_now=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_device_state_history'


class CrossbeltStatisticSorting(models.Model):
    id = models.AutoField(primary_key=True)
    induction_id = models.IntegerField()
    total = models.IntegerField()
    stt_date = models.DateField(null=True)
    total_success = models.IntegerField()
    total_reject = models.IntegerField()
    total_pda = models.IntegerField()
    stt_hour = models.IntegerField(null=True)
    hour = models.IntegerField(null=True)
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_statistic_sorting'


class CrossbeltSortingPlanChute(models.Model):
    id = models.AutoField(primary_key=True)
    chute_id = models.IntegerField()
    plan = models.ForeignKey(CrossbeltSortingPlan, on_delete=models.SET_NULL, null=True)
    transport_type = models.IntegerField()
    bag_type = models.IntegerField()
    main_station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        null=True
    )
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_sorting_plan_chute'


class CrossbeltSortPlanChuteExtra(models.Model):
    id = models.AutoField(primary_key=True)
    chute_id = models.IntegerField()
    plan = models.ForeignKey(CrossbeltSortingPlan, on_delete=models.SET_NULL, null=True)
    bag_type = models.IntegerField(default=0)
    main_station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,
        null=True
    )
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_sort_plan_chute_extra'


class CrossbeltSortingPlanChuteDetail(models.Model):
    id = models.AutoField(primary_key=True)
    sorting_plan_chute = models.ForeignKey(
        CrossbeltSortingPlanChute,
        on_delete=models.SET_NULL,
        null=True
    )
    destination_code = models.CharField(max_length=50)
    destination_type = models.IntegerField()
    created = models.DateTimeField(blank=True, null=True, auto_now_add=True)

    class Meta:
        managed = False
        db_table = "crossbelt_sorting_plan_chute_detail"


class CrossbeltChuteHistory(models.Model):
    class ChuteState(Enum):
        ACTIVE = 1
        DEACTIVATE = 0

    id = models.AutoField(primary_key=True)

    chute_code = models.CharField(max_length=50)
    state = models.IntegerField(choices=[(tag, tag.value) for tag in ChuteState], null=True)
    created = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'crossbelt_chute_history'
