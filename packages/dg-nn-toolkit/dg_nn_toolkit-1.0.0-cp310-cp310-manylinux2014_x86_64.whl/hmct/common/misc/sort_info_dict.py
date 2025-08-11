import math


def sort_info_dict(info_dict, key, reverse=False):
    info_with_key = []
    info_without_key = []
    for info in info_dict.items():
        for key_, value_ in info[1].items():
            if key == key_ and not math.isnan(float(value_)):
                info_with_key.append(info)
            else:
                info_without_key.append(info)

    info_sorted = sorted(
        info_with_key,
        key=lambda item: float(item[1][key]),
        reverse=reverse,
    )
    info_sorted.extend(info_without_key)
    return dict(info_sorted)
