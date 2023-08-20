import numpy as np

from copy import deepcopy
from detection.functions.utils import (
    groupby_dict,
    split_list,
    to_ratio,
)

__all__ = ["get_answer"]


def get_answer(
    image,
    boxes_dict,
    box_coords_dict,
    omr_list,
    total_order,
    omr_type,
    detection_threshold,
):

    if omr_type == 1:
        final_val_list, omr_error_list, total_order_front = _type1_answer(
            image,
            boxes_dict,
            box_coords_dict,
            omr_list,
            total_order,
            detection_threshold,
        )
    else:
        final_val_list, omr_error_list, total_order_front = _type2_answer(
            image,
            boxes_dict,
            box_coords_dict,
            omr_list,
            total_order,
            detection_threshold,
        )

    return final_val_list, omr_error_list, total_order_front


def _type1_answer(
    image,
    boxes_dict: dict,
    box_coords_dict: dict,
    omr_list: dict,
    total_order: int,
    detection_threshold: int,
):
    sub_order = 0
    THRESH = detection_threshold

    final_val_list, final_error_list, o_empty_dict, o_multi_dict = (
        list(),
        list(),
        dict(),
        dict(),
    )

    for n in range(len(omr_list["answer_list_x"])):
        answers, empty_list, multi_list = [list() for _ in range(3)]
        if (
            "v" in omr_list["answer_list_x"][f"x_{n+1}"]
            or "vv" in omr_list["answer_list_x"][f"x_{n+1}"]
        ):
            choice_list = [
                int((i[1] - i[0]) / (omr_list["answer_list_y"][f"y_{n+1}"][-1])) + 1
                for i in omr_list["answer_list_y"][f"y_{n+1}"][:-1]
            ]
        elif "r" in omr_list["answer_list_x"][f"x_{n+1}"]:
            choice_list = [
                int((i[1] - i[0]) / (omr_list["answer_list_x"][f"x_{n+1}"][-2])) + 1
                for i in omr_list["answer_list_x"][f"x_{n+1}"][:-2]
            ]
        elif "ww" in omr_list["answer_list_x"][f"x_{n+1}"]:
            choice_list = [
                int((i[1] - i[0]) / (omr_list["answer_list_x"][f"x_{n+1}"][-2])) + 1
                for i in omr_list["answer_list_x"][f"x_{n+1}"][:-2]
            ]
        else:
            choice_list = [
                int((i[1] - i[0]) / (omr_list["answer_list_x"][f"x_{n+1}"][-1])) + 1
                for i in omr_list["answer_list_x"][f"x_{n+1}"][:-1]
            ]
        answer_choice_idx = [
            i * j for i, j in zip(omr_list["answer_number"][f"a_{n+1}"], choice_list)
        ]
        final_idx = [0] + [
            sum(answer_choice_idx[:i]) for i in range(1, len(choice_list) + 1)
        ]
        for idx in range(len(final_idx) - 1):
            temp_ans = list()
            for box in boxes_dict[f"b_{n+1}"][final_idx[idx] : final_idx[idx + 1]]:
                temp_ans.append(np.sum(box == 0))
            answers.append(split_list(temp_ans, choice_list[idx]))

        box_number, ans_number = 0, 0
        for answer in answers:
            for ans in answer:
                if (
                    "vv" in omr_list["answer_list_x"][f"x_{n+1}"]
                    or "ww" in omr_list["answer_list_x"][f"x_{n+1}"]
                ):
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
                multi_, empty_, multi_number = [[] for _ in range(3)]
                ans_number += 1
                for i, a in enumerate(ans):
                    box_number += 1
                    if a > THRESH:
                        ans_cnt += 1
                        multi_.append(
                            [
                                total_order + ans_number + sub_order,
                                box_coords_dict[f"b_{n+1}"][box_number - 1],
                            ]
                        )
                        multi_number.append(str(i + 1))
                    else:
                        empty_.append(
                            [
                                total_order + ans_number + sub_order,
                                box_coords_dict[f"b_{n+1}"][box_number - 1],
                            ]
                        )

                if ans_cnt > 1:
                    multi_list += multi_
                    if (
                        "vv" in omr_list["answer_list_x"][f"x_{n+1}"]
                        or "ww" in omr_list["answer_list_x"][f"x_{n+1}"]
                    ):
                        Val = [str(m).zfill(2) for m in multi_number]
                    else:
                        Val = multi_number
                elif ans_cnt == 0:
                    empty_list += empty_
                    Val = [" "]

                final_val_list.append(
                    {
                        "section": "front",
                        "totalOrder": total_order + ans_number + sub_order,
                        "type": omr_list["question_title"][f"t_{n+1}"],
                        "questionNumber": str(ans_number),
                        "answer": Val,
                    }
                )
        sub_order += ans_number

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
                final_error_list.append(
                    {
                        "section": "front",
                        "content": "omr",
                        "errType": ["multi"],
                        "totalOrder": int(m),
                        "boxInfo": o_multi_dict[m],
                    }
                )

        if len(o_empty_dict) > 0:
            for e in o_empty_dict:
                final_error_list.append(
                    {
                        "section": "front",
                        "content": "omr",
                        "errType": ["empty"],
                        "totalOrder": int(e),
                        "boxInfo": o_empty_dict[e],
                    }
                )

    total_order_front = total_order + sub_order

    return final_val_list, final_error_list, total_order_front


def _type2_answer(
    image,
    boxes_dict: dict,
    box_coords_dict: dict,
    omr_list: dict,
    total_order: int,
    detection_threshold: int,
):
    sub_order = 0
    THRESH = detection_threshold
    final_val_list, final_error_list, o_empty_dict, o_multi_dict = (
        list(),
        list(),
        dict(),
        dict(),
    )
    box_index = 0
    for n in range(len(omr_list["answer_list_x"])):
        answers, locations, empty_list, multi_list = [[] for _ in range(4)]
        choice_list = list()

        # Check vertical
        if "v" in omr_list["answer_list_x"][f"x_{n+1}"]:
            choice_list = [
                omr_list["answer_list_y"][f"y_{n+1}"][0][1]
                - omr_list["answer_list_y"][f"y_{n+1}"][0][0]
                + 1
            ]
            final_idx = omr_list["answer_list_y"][f"y_{n+1}"][0]
        else:
            for nn in range(len(omr_list["answer_list_x"][f"x_{n+1}"])):
                x_meta = omr_list["answer_list_x"][f"x_{n+1}"][f"r_{nn+1}"]
                choice_list.append(*[int(x_meta[0][1] - x_meta[0][0]) + 1])
            answer_choice_idx = [
                i * j
                for i, j in zip(omr_list["answer_number"][f"a_{n+1}"], choice_list)
            ]
            final_idx = [0] + [
                sum(answer_choice_idx[:i]) for i in range(1, len(choice_list) + 1)
            ]

        for idx in range(len(final_idx) - 1):
            box_index += 1
            temp_ans, temp_coord = list(), list()
            for box in boxes_dict[f"b_{box_index}"]:
                temp_ans.append(np.sum(box == 0))
            answers += split_list(temp_ans, choice_list[idx])

            for box_coord in box_coords_dict[f"b_{box_index}"]:
                temp_coord.append(box_coord)
            locations += temp_coord
        box_number, ans_number = 0, 0

        for ans in answers:
            if "vv" in omr_list["answer_list_x"][f"x_{n+1}"]:
                try:
                    Val = [str(int(np.argmax(ans) + 1)).zfill(2)]
                except:
                    pass
            else:
                try:
                    Val = [str(int(np.argmax(ans) + 1))]
                except:
                    pass
            ans_cnt = 0
            multi_, empty_, multi_number = [[] for _ in range(3)]
            ans_number += 1
            for i, a in enumerate(ans):
                box_number += 1
                if a > THRESH:
                    ans_cnt += 1
                    multi_.append(
                        [
                            total_order + ans_number + sub_order,
                            locations[box_number - 1],
                        ]
                    )
                    multi_number.append(i + 1)
                else:
                    empty_.append(
                        [
                            total_order + ans_number + sub_order,
                            locations[box_number - 1],
                        ]
                    )

            if ans_cnt > 1:
                multi_list += multi_
                if "vv" in omr_list["answer_list_x"][f"x_{n+1}"]:
                    Val = [str(m).zfill(2) for m in multi_number]
                else:
                    Val = multi_number
            elif ans_cnt == 0:
                empty_list += empty_
                Val = [" "]
            final_val_list.append(
                {
                    "section": "front",
                    "totalOrder": total_order + ans_number + sub_order,
                    "type": omr_list["question_title"][f"t_{n+1}"],
                    "questionNumber": ans_number,
                    "answer": Val,
                }
            )
        sub_order += ans_number
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
                final_error_list.append(
                    {
                        "section": "front",
                        "content": "omr",
                        "errType": ["multi"],
                        "totalOrder": m,
                        "boxInfo": o_multi_dict[m],
                    }
                )

        if len(o_empty_dict) > 0:
            for e in o_empty_dict:
                final_error_list.append(
                    {
                        "section": "front",
                        "content": "omr",
                        "errType": ["empty"],
                        "totalOrder": e,
                        "boxInfo": o_empty_dict[e],
                    }
                )
    total_order_front = total_order + sub_order

    return final_val_list, final_error_list, total_order_front
