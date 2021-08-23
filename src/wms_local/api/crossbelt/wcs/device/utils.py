from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from .....model.crossbelt import CrossbeltDeviceStateHistory, CrossbeltCarrier, CrossbeltChute, CrossbeltInduction


def update_carrier(code, state):
    try:
        carrier = CrossbeltCarrier.objects.get(code=code)
        if carrier:
            carrier.status = state
            carrier.save()
    except ObjectDoesNotExist:
        pass


def update_chute(code, state):
    try:
        chute = CrossbeltChute.objects.get(code=code)
        if chute:
            chute.status = 1 if state == "0" else 0 if state == "1" else chute.status
            chute.save()
    except ObjectDoesNotExist:
        pass


def update_induction(code, state):
    try:
        induction = CrossbeltInduction.objects.get(code=code)
        if induction:
            induction.status = state
            induction.save()
    except ObjectDoesNotExist:
        pass


def insert_device_state_history(device_code, device_type, state, create_time):
    device_state_history = CrossbeltDeviceStateHistory(
        device_code=device_code,
        device_type=device_type,
        state=state,
        created=datetime.strptime(
            create_time, "%Y-%m-%d %H:%M:%S") if create_time else None,
    )
    device_state_history.save()
