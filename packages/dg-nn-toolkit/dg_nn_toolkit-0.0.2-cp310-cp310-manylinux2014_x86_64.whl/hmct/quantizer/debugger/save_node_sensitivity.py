def save_node_sensitivity(node_info, save_dir, title=""):
    max_node_name_length = 50
    key_format = {}
    key_format["Node"] = 4
    for node, info in node_info.items():
        key_format["Node"] = max(len(node), key_format["Node"])
        for key, val in info.items():
            # Update the key format.
            if key == "Threshold":
                key_len = max(len(key), len(str(val[0])))
            else:
                key_len = max(len(key), len(str(val)))
            key_format[key] = (
                max(key_len, key_format[key]) if key in key_format else key_len
            )
    # Calculate the header length, and update the value in key_format.
    key_format["Node"] = min(max_node_name_length, key_format["Node"])
    head_length = 0
    for key in key_format:
        key_len = key_format[key] + 2
        head_length += key_len
        key_format[key] = "{:<" + str(key_len) + "}"

    # Generate result table.
    head = ""
    for key in key_format:
        head += key_format[key].format(key)

    equal_char = int((head_length - len(title)) / 2)
    title = "=" * equal_char + title + "=" * equal_char
    s = [title, head, "-" * head_length]
    with open(save_dir, "w") as f:
        for t in s:
            f.write(t + "\n")
        for node, info in node_info.items():
            if len(node) > max_node_name_length:
                each_log = key_format["Node"].format(
                    "..." + node[len(node) - max_node_name_length + 3 :],
                )
            else:
                each_log = key_format["Node"].format(node)

            for key, format in key_format.items():
                if key != "Node":
                    if key in info:
                        if key == "Threshold":
                            each_log += format.format(info[key][0])
                        else:
                            each_log += format.format(info[key])
                    else:
                        each_log += format.format("")
            f.write(each_log + "\n")
    f.close()
