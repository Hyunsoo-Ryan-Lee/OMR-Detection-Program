import cv2
import math
import numpy as np
import settings
from collections import Counter
from copy import deepcopy
from detection.functions.utils import empty_coord, groupby_dict, to_ratio

__all__ = ["multi_line_detect"]


def multi_line_detect(
    image,
    recognition_coord: list,
    omr_list: dict,
    sense_value: int,
    total_order: int,
    detection_threshold: int,
    omr_margin,
):
    (_, image_c) = cv2.threshold(image.copy(), sense_value, 255, cv2.THRESH_BINARY)

    sub_order = 0
    THRESH = detection_threshold
    start_point = omr_list["meta"]["start_point"]
    margin = omr_list["meta"]["margin"]
    width = omr_list["meta"]["width"]
    mod = int(margin // 12)

    _under = int(np.average([i[1] + i[3] for i in recognition_coord]))
    if omr_list["meta"]["image_idx"] == 34:
        pass
    elif omr_list["meta"]["image_idx"] == 59:
        _under -= 2
    elif omr_list["meta"]["image_idx"] in [86, 90]:
        _under -= margin * 2
    else:
        _under -= margin
    margin += omr_margin
    line_list = sorted([int(_under + i * margin) for i in range(47)])
    margin = int(margin)

    multi_line_meta = [
        omr_list["meta"][m] for m in omr_list["meta"].keys() if "multi_line" in m
    ][0]

    final_val_list, final_error_list, empty_, multi_ = [[] for _ in range(4)]
    o_empty_dict, o_multi_dict = [{} for _ in range(2)]
    for number, instance in enumerate(multi_line_meta.items()):
        sub_order += 1
        xx = recognition_coord[
            instance[1][0][0] : instance[1][0][1] + 1 : instance[1][2]
        ]
        yy = line_list[instance[1][1][0] : instance[1][1][1] + 1 : instance[1][3]]
        half_width = width // 2
        box, boxes, all_boxes = [[] for _ in range(3)]
        for y in yy:
            for x in xx:
                x_mid = x[0] + x[2] // 2
                section_img = image_c[
                    y + mod : y + margin - mod,
                    x_mid - half_width + 2 : x_mid + half_width - 2,
                ]
                box.append([x_mid - half_width, y, width, margin])
                all_boxes.append([number + 1, [x_mid - half_width, y, width, margin]])
                boxes.append(int(np.sum(section_img == 0)))

        box = box[: instance[1][5]]
        boxes = boxes[: instance[1][5]]
        if sum(i > THRESH for i in boxes) == 0:
            Val = [" "]
            empty_ += all_boxes
        elif sum(i > THRESH for i in boxes) > instance[1][-1]:
            if instance[1][-2] >= 10:
                Val = [
                    str(i + 1).zfill(2) for i in range(len(boxes)) if boxes[i] > THRESH
                ]
            else:
                Val = list(
                    map(str, [i + 1 for i in range(len(boxes)) if boxes[i] > THRESH])
                )
            [
                multi_.append([number + 1, box[i]])
                for i in range(len(boxes))
                if boxes[i] > THRESH
            ]
        else:
            if instance[1][-1] != 1:
                if instance[1][-2] >= 10:
                    Val = [
                        str(i + 1).zfill(2)
                        for i in range(len(boxes))
                        if boxes[i] > THRESH
                    ]
                else:
                    Val = list(
                        map(
                            str, [i + 1 for i in range(len(boxes)) if boxes[i] > THRESH]
                        )
                    )
            else:
                if instance[1][-2] >= 10:
                    Val = [str(int(np.argmax(boxes)) + instance[1][4]).zfill(2)]
                else:
                    Val = [str(int(np.argmax(boxes)) + instance[1][4])]

        final_val_list.append(
            {
                "section": "front",
                "totalOrder": total_order + sub_order,
                "type": "답안",
                "questionNumber": str(instance[0]),
                "answer": Val,
            }
        )

    if multi_:
        o_multi_dict = groupby_dict(
            list(map(lambda x: to_ratio(image, x), deepcopy(multi_)))
        )
        for m in o_multi_dict:
            final_error_list.append(
                {
                    "section": "front",
                    "content": "omr",
                    "errType": ["multi"],
                    "totalOrder": total_order + int(m),
                    "boxInfo": o_multi_dict[m],
                }
            )

    if empty_:
        o_empty_dict = groupby_dict(
            list(map(lambda x: to_ratio(image, x), deepcopy(empty_)))
        )
        for k, v in o_empty_dict.items():
            o_empty_dict[k] = [
                v[0][0],
                v[0][1],
                round(v[-1][0] - v[0][0] + v[0][2], 6),
                round(v[-1][1] - v[0][1] + v[0][3], 6),
            ]
        for e in o_empty_dict:
            final_error_list.append(
                {
                    "section": "front",
                    "content": "omr",
                    "errType": ["empty"],
                    "totalOrder": total_order + int(e),
                    "boxInfo": o_empty_dict[e],
                }
            )
    total_order_front = total_order + sub_order
    return final_val_list, final_error_list, total_order_front
