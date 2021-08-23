from datetime import datetime, timedelta
from .sync_data_kafka import SyncDataKafka
from ...system_config import SystemConfigKey
from ...constant import KAFKA_PRODUCER_CROSSBELT_SORTING_HISTORY_TOPIC
from ...model.crossbelt import CrossbeltSortingHistory


class CrossbeltSyncSortingHistory(SyncDataKafka):
    def __init__(self):
        super().__init__(
            system_config_key=SystemConfigKey.SYNC_WMS_CENTRAL_LAST_SORTING_HISTORY_ID.value,
            kafka_topic=KAFKA_PRODUCER_CROSSBELT_SORTING_HISTORY_TOPIC
        )

    def get_data_sync(self):
        max_id = self.previous_id_sync
        data_prepared = list()

        list_data = CrossbeltSortingHistory.objects.filter(
            id__gt=self.previous_id_sync,
            modified__lte=datetime.now() - timedelta(minutes=30)  # delay 30 minutes sync to get latest sorting_status
        )[:3000]
        for csh in list_data:
            if csh.id > max_id:
                max_id = csh.id
            data_prepared.append(dict(
                id=csh.id,
                barcode_input=csh.barcode_input,
                pkg_order=csh.pkg_order,
                bag_order=csh.bag_order,
                scanner_id=csh.scanner_id,
                induction_id=csh.induction_id,
                carrier_id=csh.carrier_id,
                chute_id=csh.chute_id,
                chute_type=csh.chute_type,
                image_id=csh.image_id,
                sorting_status=csh.sorting_status,
                destination_code=csh.destination_code,
                sorting_plan_id=csh.sorting_plan_id,
                dst_request_time=csh.dst_request_time.strftime('%Y-%m-%d %H:%M:%S') if csh.dst_request_time else None,
                sorting_report_time=csh.sorting_report_time.strftime(
                    '%Y-%m-%d %H:%M:%S') if csh.sorting_report_time else None,
                in_chute_time=csh.in_chute_time.strftime('%Y-%m-%d %H:%M:%S') if csh.in_chute_time else None,
                in_carrier_time=csh.in_carrier_time.strftime('%Y-%m-%d %H:%M:%S') if csh.in_carrier_time else None,
                created=csh.created.strftime('%Y-%m-%d %H:%M:%S') if csh.created else None,
                modified=csh.modified.strftime('%Y-%m-%d %H:%M:%S') if csh.modified else None,
            ))
        return data_prepared, max_id
