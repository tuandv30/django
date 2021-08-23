from django.db import connection

from .....model.crossbelt import CrossbeltPrinter, CrossbeltPrinterChute


def get_all_printer():
    printer_object = dict()
    with connection.cursor() as cursor:
        raw_query = """
            SELECT
                printer.`id`,
                printer.`name`,
                printer.`code`,
                printer.`ip`,
                printer.`mac_address`,
                printer.`status`,
                printer_chute.`chute_id`,
                chute.`code`
            FROM
                printer
            LEFT JOIN printer_chute ON printer.`id` = printer_chute.`printer_id`
            LEFT JOIN chute on printer_chute.`chute_id` = chute.`id`
            ORDER BY printer.`id`
        """
        cursor.execute(raw_query)
        for row in cursor.fetchall():
            printer_id = row[0]
            printer_name = row[1]
            printer_code = row[2]
            printer_ip = row[3]
            printer_mac_address = row[4]
            printer_status = row[5]
            chute_id = row[6]
            chute_code = row[7]
            if chute_id:
                chute = {
                    "chute_id": chute_id,
                    "chute_code": chute_code
                }
            else:
                chute = None
            if printer_id not in printer_object.keys():
                printer_object[printer_id] = {
                    "printer_id": printer_id,
                    "printer_name": printer_name,
                    "printer_code": printer_code,
                    "printer_ip": printer_ip,
                    "printer_mac": printer_mac_address,
                    "printer_status": "active" if printer_status == 1 else "deactive",
                    "chute": [chute] if chute else []
                }
            else:
                printer_object[printer_id]["chute"] = printer_object[printer_id]["chute"] + [chute]

    return printer_object


def collect_printer(printer_id, chute_id):
    """This function select printer to forward api print bill

    Args:
        printer_id (interger): ID of printer
        chute_id (interger): ID of chute

    Returns:
        [string]: IP of printer
    """
    printer_ip = None
    if printer_id:
        printer = CrossbeltPrinter.objects.filter(pk=printer_id).first()
        if printer:
            printer_ip = printer.ip
    else:
        printer_chute = CrossbeltPrinterChute.objects.filter(chute_id=chute_id).first()
        if printer_chute:
            printer_id = printer_chute.printer_id
            printer = CrossbeltPrinter.objects.filter(pk=printer_id).first()
            if printer:
                printer_ip = printer.ip

    return printer_ip
