from django.db import connection


def get_chute_info():
    result = list()
    with connection.cursor() as cursor:
        raw_query = """
            SELECT
                tmp2.chute_id,
                tmp2.total_code,
                COUNT(cdt.id) AS total_pkg
            FROM
                (SELECT chute_id, GROUP_CONCAT(code_text) AS total_code
                FROM
                    (SELECT
                        spc.`chute_id`,
                        spc.`plan_id`,
                        spcd.`destination_code`,
                        spcd.`destination_type`,
                        p.`province_code` AS code_text
                    FROM
                        sorting_plan sp
                        INNER JOIN sorting_plan_chute spc ON spc.plan_id = sp.id
                        INNER JOIN sorting_plan_chute_detail spcd ON spc.id = spcd.sorting_plan_chute_id
                        INNER JOIN `province` p ON p.`province_id` = spcd.`destination_code`
                    WHERE
                        sp.`is_active` = 1 AND
                        spcd.`destination_type` = 0

                    UNION ALL
                        SELECT
                            spc.`chute_id`,
                            spc.`plan_id`,
                            spcd.`destination_code`,
                            spcd.`destination_type`,
                            s.`code` AS code_text
                        FROM
                            sorting_plan sp
                            INNER JOIN sorting_plan_chute spc ON spc.plan_id = sp.id
                            INNER JOIN sorting_plan_chute_detail spcd ON spc.id = spcd.sorting_plan_chute_id
                            INNER JOIN `station` s ON s.`id` = spcd.`destination_code`
                        WHERE
                            sp.`is_active` = 1 AND
                            spcd.`destination_type` = 1

                    UNION ALL
                        SELECT
                        spc.`chute_id`,
                        spc.`plan_id`,
                        spcd.`destination_code`,
                        spcd.`destination_type`,
                        m.`alias` AS code_text
                    FROM
                        sorting_plan sp
                        INNER JOIN sorting_plan_chute spc ON spc.plan_id = sp.id
                        INNER JOIN sorting_plan_chute_detail spcd ON spc.id = spcd.sorting_plan_chute_id
                        INNER JOIN `module` m ON m.`id` = spcd.`destination_code`
                    WHERE
                        sp.`is_active` = 1 AND
                        spcd.`destination_type` = 2
                    ) AS tmp
                GROUP BY
                    chute_id
                ) AS tmp2
            INNER JOIN `chute_detail` cdt ON tmp2.chute_id = cdt.`chute_id`
            WHERE
                cdt.`created` > NOW() - INTERVAL 3 HOUR
            GROUP BY
                tmp2.chute_id
        """
        cursor.execute(raw_query)
        for row in cursor.fetchall():
            chute_detail = {
                "chute_id": row[0],
                "total_code": row[1],
                "total_pkg": row[2]
            }
            result.append(chute_detail)
    return result


def group_destination_code(str_many_des_code):
    group_code = ""
    single = ""
    dct = {
        'single': list()
    }
    lst_code = str_many_des_code.split(',') if str_many_des_code else []
    if lst_code:
        lst_code_new = list()
        for item in lst_code:
            item = item.split('.')
            lst_code_new.append(item)
        for code in lst_code_new:
            if len(code) > 1:
                if code[0] not in dct.keys():
                    dct[code[0]] = list()
                    dct[code[0]].append(code[1])
                else:
                    dct[code[0]].append(code[1])
            else:
                dct['single'].append(code[0])
        station = list()
        for key, value in dct.items():
            if key == 'single':
                single = ",".join(value)
            else:
                station.append(key + "(" + ",".join(value) + ")")
        if single == "":
            group_code = ",".join(station)
        else:
            group_code = single + "," + ",".join(station)
    return group_code
