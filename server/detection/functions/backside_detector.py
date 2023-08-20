import cv2
import settings
import numpy as np
from detection.functions.coordinate_x import omr_whitespace_adjust, get_x_coordinate
from detection.functions.coordinate_y import get_y_coordinate
from detection.functions.make_answer_boxes import answer_boxes
from detection.functions.utils import (
    groupby_dict,
    split_list,
    to_ratio,
)
from detection.functions.omr_52_detector import omr_52_detector
from copy import deepcopy

__all__ = ["get_back_side"]


def get_back_side(
    image,
    omr_list: list,
    total_order: int,
    sense_value: int,
    detection_threshold: int,
    omr_margin,
):
    back_val_list, back_error_list, special_back = [[] for _ in range(3)]
    height_point = omr_list["meta"]["height_point"]
    recog_point_back = omr_list["meta"]["recog_point_back"]
    recog_diff_back = omr_list["meta"]["recog_diff_back"]
    recog_len_back = omr_list["meta"]["recog_len_back"]
    recog_startend = omr_list["meta"]["recog_startend_back"]

    double_sided = True
    if "omr_52_meta" in omr_list["meta"].keys():
        image_back, _, recognition_coord_back, coord_diff = get_x_coordinate(
            image, height_point, recog_point_back, recog_diff_back, recog_len_back
        )
        back_val_list, back_error_list = omr_52_detector(
            image_back,
            recognition_coord_back,
            omr_list,
            sense_value,
            total_order,
            detection_threshold,
            omr_margin,
        )

        return back_val_list, back_error_list, special_back

    if isinstance(omr_list["meta"]["double_sided"], list):
        image_back, _, recognition_coord_back, coord_diff = get_x_coordinate(
            image, height_point, recog_point_back, recog_diff_back, recog_len_back
        )
        special_back = _detect_iii_boxes(
            image_back, recognition_coord_back[0][0], sense_value
        )
        # print(special_back)
        return back_val_list, back_error_list, special_back

    image_back, _, recognition_coord_back, coord_diff = get_x_coordinate(
        image, height_point, recog_point_back, recog_diff_back, recog_len_back
    )
    question_x_dict_back, question_y_dict_back = get_y_coordinate(
        recognition_coord_back, omr_list, omr_margin, double_sided
    )
    boxes_dict_back, box_coords_dict_back = answer_boxes(
        image_back,
        recognition_coord_back,
        question_x_dict_back,
        question_y_dict_back,
        omr_list,
        sense_value,
        double_sided,
    )

    if omr_list["meta"]["type"] == 1:
        back_val_list, back_error_list = _type1_answer_back(
            image_back,
            boxes_dict_back,
            box_coords_dict_back,
            omr_list,
            total_order,
            detection_threshold,
        )

    return back_val_list, back_error_list, special_back


def _detect_iii_boxes(image, x_coord, sense_value):
    (_, image_c) = cv2.threshold(image, sense_value, 255, cv2.THRESH_BINARY)
    zero_values = list()
    diff = x_coord - 43
    outer_padding = -5
    inner_padding = 5
    new_iii = [(i[0] + diff, i[1], i[2], i[3]) for i in settings.iii_coordinates]
    for i in new_iii:
        x = i[0]
        y = i[1]
        w = i[2]
        h = i[3]

        normal_arr = image_c[y + outer_padding : y + h - (outer_padding * 2), x : x + w]
        pre_image = image_c[y + outer_padding : y + h - (outer_padding * 2), x : x + w]
        top_limit = [
            i
            for i in range(len(normal_arr))
            if np.sum(normal_arr[i] == 0) >= int(len(normal_arr[i]) * 0.8)
            and i <= int(len(normal_arr) / 3)
        ]
        bottom_limit = [
            i
            for i in range(len(normal_arr))
            if np.sum(normal_arr[i] == 0) >= int(len(normal_arr[i]) * 0.8)
            and i > int(len(normal_arr) * 2 / 3)
        ]
        if top_limit and bottom_limit:
            after_image = pre_image[max(top_limit) + 2 : min(bottom_limit) - 2, :]
        elif top_limit and not bottom_limit:
            after_image = pre_image[max(top_limit) + 2 :, :]
        elif bottom_limit and not top_limit:
            after_image = pre_image[: min(bottom_limit) - 2, :]
        else:
            after_image = pre_image.copy()

        transpose_arr = cv2.transpose(after_image)
        trans_top_limit = [
            i
            for i in range(len(transpose_arr))
            if np.sum(transpose_arr[i] == 0) >= int(len(transpose_arr[i]) * 0.8)
            and i <= int(len(transpose_arr) / 3)
        ]
        trans_bottom_limit = [
            i
            for i in range(len(transpose_arr))
            if np.sum(transpose_arr[i] == 0) >= int(len(transpose_arr[i]) * 0.8)
            and i > int(len(transpose_arr) * 2 / 3)
        ]
        if trans_top_limit and trans_bottom_limit:
            final_image = after_image[
                :, max(trans_top_limit) + 2 : min(trans_bottom_limit) - 2
            ]
        elif trans_top_limit and not trans_bottom_limit:
            final_image = after_image[:, max(trans_top_limit) + 2 :]
        elif trans_bottom_limit and not trans_top_limit:
            final_image = after_image[:, : min(trans_bottom_limit) - 2]
        else:
            final_image = after_image.copy()

        zeros = np.sum(
            final_image[
                inner_padding : len(after_image) - inner_padding,
                inner_padding : len(after_image[0]) - inner_padding,
            ]
            == 0
        )
        zero_values.append(zeros)
    try:
        thresh = int(min([i for i in zero_values if i > max(zero_values) * 0.1]))
        return ["1" if i >= thresh else "0" for i in zero_values]
    except:
        return "0" * len(zero_values)

    # 0에서 갑자기 숫자로 뛰는 값을 찾아서 0과 해당 값의 평균을 tresh로 잡으려고 했던 모양.
    # temp_ = sorted(zero_values)
    # diff_list = [temp_[i + 1] - temp_[i] for i in range(len(temp_) - 1)]
    # diff_index = diff_list.index(max(diff_list))
    # thresh = int(np.mean([temp_[diff_index], temp_[diff_index + 1]]))


def _type1_answer_back(
    image,
    boxes_dict: dict,
    box_coords_dict: dict,
    omr_list: dict,
    total_order_front: int,
    detection_threshold: int,
):
    THRESH = detection_threshold
    if "numbering" in omr_list["meta"]["double_sided"].keys():
        number_list = omr_list["meta"]["double_sided"]["numbering"]
    else:
        number_list = [
            [f"{n+1}", 1]
            for n in range(
                sum(omr_list["meta"]["double_sided"]["answer_number"]["a_1"])
            )
        ]
    back_val_list, back_error_list, o_empty_dict, o_multi_dict = (
        list(),
        list(),
        dict(),
        dict(),
    )

    for n in range(len(omr_list["meta"]["double_sided"]["answer_list_x"])):
        answers, empty_list, multi_list = [[] for _ in range(3)]
        choice_list = [
            int(
                (i[1] - i[0])
                / (omr_list["meta"]["double_sided"]["answer_list_x"][f"x_{n+1}"][-1])
            )
            + 1
            for i in omr_list["meta"]["double_sided"]["answer_list_x"][f"x_{n+1}"][:-1]
        ]
        answer_choice_idx = [
            i * j
            for i, j in zip(
                omr_list["meta"]["double_sided"]["answer_number"][f"a_{n+1}"],
                choice_list,
            )
        ]
        final_idx = [0] + [
            sum(answer_choice_idx[:i]) for i in range(1, len(choice_list) + 1)
        ]
        # print(len(boxes_dict["b_1"]))
        for idx in range(len(final_idx) - 1):
            temp_ans = list()
            for box in boxes_dict[f"b_{n+1}"][final_idx[idx] : final_idx[idx + 1]]:
                temp_ans.append(np.sum(box == 0))
            answers.append(split_list(temp_ans, choice_list[idx]))
        box_number, ans_number = 0, 0
        for answer in answers:
            for ans in answer:
                if len(number_list[ans_number]) == 3:
                    try:
                        Val = [str(int(np.argmax(ans) + 1)).zfill(2)]
                    except Exception as e:
                        print(e)
                else:
                    try:
                        Val = [str(int(np.argmax(ans) + 1))]
                    except Exception as e:
                        print(e)
                ans_cnt = 0
                multi_, empty_, multi_number = list(), list(), list()
                ans_number += 1
                for i, a in enumerate(ans):
                    box_number += 1
                    if a > THRESH:
                        ans_cnt += 1
                        multi_.append(
                            [
                                total_order_front + ans_number,
                                box_coords_dict[f"b_{n+1}"][box_number - 1],
                            ]
                        )
                        multi_number.append(str(i + 1))
                        if number_list[ans_number - 1][-1] != 1:
                            Val = multi_number

                    else:
                        empty_.append(
                            [
                                total_order_front + ans_number,
                                box_coords_dict[f"b_{n+1}"][box_number - 1],
                            ]
                        )
                if ans_cnt > number_list[ans_number - 1][-1]:
                    multi_list += multi_
                    if len(number_list[ans_number - 1]) == 3:
                        Val = [str(m).zfill(2) for m in multi_number]
                    else:
                        Val = multi_number
                elif ans_cnt == 0:
                    empty_list += empty_
                    Val = [" "]
                else:
                    if len(number_list[ans_number - 1]) == 3:
                        Val = [str(m).zfill(2) for m in multi_number]
                    else:
                        Val = multi_number
                back_val_list.append(
                    {
                        "section": "back",
                        "totalOrder": total_order_front + ans_number,
                        "type": omr_list["meta"]["double_sided"]["question_title"][
                            f"t_{n+1}"
                        ],
                        "questionNumber": str(number_list[ans_number - 1][0]),
                        "answer": Val,
                    }
                )
        # for bb in back_val_list:
        #     print(bb["questionNumber"], bb["answer"])
        o_multi_dict = groupby_dict(
            list(map(lambda x: to_ratio(image, x), deepcopy(multi_list)))
        )
        o_empty_dict = groupby_dict(
            list(map(lambda x: to_ratio(image, x), deepcopy(empty_list)))
        )
        for k, v in o_empty_dict.items():
            o_empty_dict[k] = [
                v[0][0],
                v[0][1],
                round(v[-1][0] - v[0][0] + v[0][2], 6),
                round(v[-1][1] - v[0][1] + v[0][3], 6),
            ]

        if len(o_multi_dict) > 0:
            for m in o_multi_dict:
                back_error_list.append(
                    {
                        "section": "back",
                        "content": "omr",
                        "errType": ["multi"],
                        "totalOrder": int(m),
                        "boxInfo": o_multi_dict[m],
                    }
                )

        if len(o_empty_dict) > 0:
            for e in o_empty_dict:
                back_error_list.append(
                    {
                        "section": "back",
                        "content": "omr",
                        "errType": ["empty"],
                        "totalOrder": int(e),
                        "boxInfo": o_empty_dict[e],
                    }
                )
    return back_val_list, back_error_list
