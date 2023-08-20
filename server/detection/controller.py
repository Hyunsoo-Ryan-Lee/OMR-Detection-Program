from detection.functions.userinfo_detector import personal_info
from detection.functions.userinfo_detector_additional import personal_info_additional
from detection.functions.coordinate_x import omr_whitespace_adjust, get_x_coordinate
from detection.functions.coordinate_y import get_y_coordinate
from detection.functions.make_answer_boxes import answer_boxes
from detection.functions.multi_line_detector import multi_line_detect
from detection.functions.answer_detector import get_answer
from detection.functions.point_number_detector import point_number_detect
from detection.functions.backside_detector import get_back_side
from detection.functions.threshold_value import get_threshold_value
import settings


def start_detection(omr_image, omr_list, double_sided_check: bool = False):

    (
        final_val_list,
        omr_error_list,
        special_back,
        mid_val_front,
        mid_val_back,
        mid_error_front,
        mid_error_back,
    ) = [[] for _ in range(7)]
    opencv_threshold = settings.thresh_value
    if "answer_list_x" in omr_list["meta"].keys():
        image, direction, recognition_coord, omr_margin = omr_whitespace_adjust(
            omr_image[0], omr_list["meta"]
        )
        # y 좌표 가져오기
        question_x_dict, question_y_dict = get_y_coordinate(
            recognition_coord, omr_list, omr_margin
        )
        # For test
        # print(question_x_dict)
        # print(question_y_dict)
        trial = 0
        while True:
            trial += 1
            boxes_dict, box_coords_dict, answer_max, answer_min = answer_boxes(
                image,
                recognition_coord,
                question_x_dict,
                question_y_dict,
                omr_list,
                opencv_threshold,
            )
            (
                detection_threshold,
                minor_value_ratio,
                tresh_max_list,
                thresh_min_ratio,
            ) = get_threshold_value(
                image,
                recognition_coord,
                omr_list,
                opencv_threshold,
                omr_margin,
                answer_max,
                answer_min,
            )
            # print(trial, thresh_min_ratio, opencv_threshold)
            if max(tresh_max_list) < 100 and trial == 3:
                sense_value = 120
                detection_threshold = max(tresh_max_list) * 2
                break
            else:
                sense_value = opencv_threshold
                break
                # if thresh_min_ratio >= 0.7:
                #     sense_value = opencv_threshold
                #     break
                # else:
                #     opencv_threshold -= 3
        #     if minor_value_ratio <= 0.2:
        #         if max(tresh_max_list) < 100:
        #             opencv_threshold += 3
        #         else:
        #             sense_value = opencv_threshold
        #             break
        #     else:
        #         opencv_threshold += 3
        # print(
        #     "trial : ",
        #     trial,
        #     " / ",
        #     "ratio : ",
        #     thresh_min_ratio,
        #     " / ",
        #     "sense_value : ",
        #     sense_value,
        #     " / ",
        #     "THRESHOLD : ",
        #     detection_threshold,
        # )
        # 인적 정보 영역 order 수 가져오기
        # print("THRESHOLD : ", detection_threshold)
        if omr_list["content_level"] in ["유아", "초등", "중등", "고등", "대학"]:
            (
                personal_final_list,
                personal_error_list,
                total_order,
                fatal_list,
            ) = personal_info_additional(
                image,
                recognition_coord,
                omr_list,
                sense_value,
                detection_threshold,
                omr_margin,
            )
        else:
            (
                personal_final_list,
                personal_error_list,
                total_order,
                fatal_list,
            ) = personal_info(
                image,
                recognition_coord,
                omr_list,
                sense_value,
                detection_threshold,
                omr_margin,
            )
        # For test
        # print([[t["type"], t["answer"]] for t in personal_final_list])
        # print(personal_error_list)

        # 앞면 multi line 유형 처리
        if "multi_line_front" in omr_list["meta"].keys():
            temp_val_list, temp_error_list, total_order = multi_line_detect(
                image,
                recognition_coord,
                omr_list["meta"],
                sense_value,
                total_order,
                detection_threshold,
                omr_margin,
            )
            mid_val_front = temp_val_list
            mid_error_front = temp_error_list
            # For test
            # print(temp_val_list)
            # print(temp_error_list)
            # print(total_order)

        # 답안 판독
        final_val_list, omr_error_list, total_order = get_answer(
            image,
            boxes_dict,
            box_coords_dict,
            omr_list["meta"],
            total_order,
            omr_list["meta"]["type"],
            detection_threshold,
        )

        final_val_list = mid_val_front + final_val_list
        omr_error_list = mid_error_front + omr_error_list

        # For test
        # print(final_val_list)
        # print(omr_error_list)
        # print(total_order)

        # 뒷면 multi line 유형 처리
        if "multi_line_back" in omr_list["meta"].keys():
            temp_val_list, temp_error_list, total_order = multi_line_detect(
                image,
                recognition_coord,
                omr_list,
                sense_value,
                total_order,
                detection_threshold,
                omr_margin,
            )
            mid_val_back = temp_val_list
            mid_error_back = temp_error_list

            final_val_list = final_val_list + mid_val_back
            omr_error_list = omr_error_list + mid_error_back

        # 소수점 포함 유형 처리
        if "point_number" in omr_list["meta"].keys():
            temp_val_list, temp_error_list, total_order = point_number_detect(
                image,
                recognition_coord,
                omr_list,
                sense_value,
                total_order,
                detection_threshold,
                omr_margin,
            )
            mid_val_back = temp_val_list
            mid_error_back = temp_error_list

            final_val_list = final_val_list + mid_val_back
            omr_error_list = omr_error_list + mid_error_back
    else:
        sense_value = 155
        image, direction, recognition_coord, omr_margin = omr_whitespace_adjust(
            omr_image[0], omr_list["meta"]
        )
        (
            detection_threshold,
            minor_value_ratio,
            tresh_max_list,
            thresh_min_ratio,
        ) = get_threshold_value(
            image, recognition_coord, omr_list, opencv_threshold, omr_margin, [], [],
        )

        if omr_list["content_level"] in ["유아", "초등", "중등", "고등"]:
            (
                personal_final_list,
                personal_error_list,
                total_order,
                fatal_list,
            ) = personal_info_additional(
                image,
                recognition_coord,
                omr_list,
                sense_value,
                detection_threshold,
                omr_margin,
            )
        else:
            (
                personal_final_list,
                personal_error_list,
                total_order,
                fatal_list,
            ) = personal_info(
                image, recognition_coord, omr_list, detection_threshold, omr_margin
            )
    # 양면 유형 처리
    if double_sided_check:
        sense_value = 155
        back_val_list, back_error_list, special_back = get_back_side(
            omr_image[1],
            omr_list,
            total_order,
            sense_value,
            detection_threshold,
            omr_margin,
        )
        final_val_list += back_val_list
        omr_error_list += back_error_list

    # 최종 판독, 에러 결과
    total_value = personal_final_list + final_val_list
    total_error = personal_error_list + omr_error_list
    return total_value, total_error, special_back, direction, fatal_list
