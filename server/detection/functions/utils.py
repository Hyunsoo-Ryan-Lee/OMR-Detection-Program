import cv2
import numpy as np
import imutils
from PIL import Image, ImageOps
import settings
import boto3

create_name_base = {
    "service_name": "personal",
    "kor_begin": 44032,
    "kor_end": 55203,
    "chosung_base": 588,
    "jungsung_base": 28,
    "jaum_begin": 12593,
    "jaum_end": 12622,
    "moum_begin": 12623,
    "moum_end": 12643,
    "chosung_list": [
        "ㄱ",
        "ㄲ",
        "ㄴ",
        "ㄷ",
        "ㄸ",
        "ㄹ",
        "ㅁ",
        "ㅂ",
        "ㅃ",
        "ㅅ",
        "ㅆ",
        "ㅇ",
        "ㅈ",
        "ㅉ",
        "ㅊ",
        "ㅋ",
        "ㅌ",
        "ㅍ",
        "ㅎ",
    ],
    "jungsung_list": [
        "ㅏ",
        "ㅐ",
        "ㅑ",
        "ㅒ",
        "ㅓ",
        "ㅔ",
        "ㅕ",
        "ㅖ",
        "ㅗ",
        "ㅘ",
        "ㅙ",
        "ㅚ",
        "ㅛ",
        "ㅜ",
        "ㅝ",
        "ㅞ",
        "ㅟ",
        "ㅠ",
        "ㅡ",
        "ㅢ",
        "ㅣ",
    ],
    "jongsung_list": [
        " ",
        "ㄱ",
        "ㄲ",
        "ㄳ",
        "ㄴ",
        "ㄵ",
        "ㄶ",
        "ㄷ",
        "ㄹ",
        "ㄺ",
        "ㄻ",
        "ㄼ",
        "ㄽ",
        "ㄾ",
        "ㄿ",
        "ㅀ",
        "ㅁ",
        "ㅂ",
        "ㅄ",
        "ㅅ",
        "ㅆ",
        "ㅇ",
        "ㅈ",
        "ㅊ",
        "ㅋ",
        "ㅌ",
        "ㅍ",
        "ㅎ",
    ],
    "jaum_list": [
        "ㄱ",
        "ㄲ",
        "ㄳ",
        "ㄴ",
        "ㄵ",
        "ㄶ",
        "ㄷ",
        "ㄸ",
        "ㄹ",
        "ㄺ",
        "ㄻ",
        "ㄼ",
        "ㄽ",
        "ㄾ",
        "ㄿ",
        "ㅀ",
        "ㅁ",
        "ㅂ",
        "ㅃ",
        "ㅄ",
        "ㅅ",
        "ㅆ",
        "ㅇ",
        "ㅈ",
        "ㅉ",
        "ㅊ",
        "ㅋ",
        "ㅌ",
        "ㅍ",
        "ㅎ",
    ],
    "moum_list": [
        "ㅏ",
        "ㅐ",
        "ㅑ",
        "ㅒ",
        "ㅓ",
        "ㅔ",
        "ㅕ",
        "ㅖ",
        "ㅗ",
        "ㅘ",
        "ㅙ",
        "ㅚ",
        "ㅛ",
        "ㅜ",
        "ㅝ",
        "ㅞ",
        "ㅟ",
        "ㅠ",
        "ㅡ",
        "ㅢ",
        "ㅣ",
    ],
    "detected_chosung_list": [
        "ㄱ",
        "ㄲ",
        "ㄴ",
        "ㄷ",
        "ㄸ",
        "ㄹ",
        "ㅁ",
        "ㅂ",
        "ㅃ",
        "ㅅ",
        "ㅆ",
        "ㅇ",
        "ㅈ",
        "ㅉ",
        "ㅊ",
        "ㅋ",
        "ㅌ",
        "ㅍ",
        "ㅎ",
    ],
    "detected_jungsung_list": [
        "ㅏ",
        "ㅐ",
        "ㅑ",
        "ㅒ",
        "ㅓ",
        "ㅔ",
        "ㅕ",
        "ㅖ",
        "ㅗ",
        "ㅘ",
        "ㅙ",
        "ㅚ",
        "ㅛ",
        "ㅜ",
        "ㅝ",
        "ㅞ",
        "ㅟ",
        "ㅠ",
        "ㅡ",
        "ㅢ",
        "ㅣ",
    ],
    "detected_jongsung_list": [
        "ㄱ",
        "ㄲ",
        "ㄴ",
        "ㄶ",
        "ㄷ",
        "ㄹ",
        "ㄺ",
        "ㄻ",
        "ㄼ",
        "ㅀ",
        "ㅁ",
        "ㅂ",
        "ㅅ",
        "ㅆ",
        "ㅇ",
        "ㅈ",
        "ㅊ",
        "ㅋ",
        "ㅌ",
        "ㅍ",
        "ㅎ",
    ],
}


def set_approx(x, y, w, h):
    """
    Image에 대한 numpy array 좌표 생성하는 함수
    """
    approx = np.zeros((4, 1, 2), dtype=np.int32)
    approx[0][0][0], approx[0][0][1] = x + w, y
    approx[1][0][0], approx[1][0][1] = x + w, y + h
    approx[2][0][0], approx[2][0][1] = x, y + h
    approx[3][0][0], approx[3][0][1] = x, y
    return approx


def drop_dupli_lines(lines: list, diff: int):
    """
    특정 간격 이하의 좌표들을 list에서 제거하는 함수
    """
    lines.append(0)
    lines.sort()
    line_diff = []
    for i, j in enumerate([lines[i + 1] - lines[i] for i in range(len(lines) - 1)]):
        if j > diff:
            line_diff.append(lines[i + 1])
    return line_diff


def split_list(arr, size):
    """
    List를 원하는 size 크기로 분해하는 함수
    """
    arrs = []
    while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
    arrs.append(arr)
    return arrs


def draw_bbox(image, len_approx_range, area_range, ratio_range, d, sigma):
    """
    이미지와 영역 범위, 비율 등을 받아와 해당 영역, 비율 안에 들어오는 도형 탐지하는 함수
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16, 16))
    gray = clahe.apply(image)
    bfilter = cv2.bilateralFilter(gray, d, sigma, sigma)
    edged = cv2.Canny(bfilter, 30, 200)
    _, thresh = cv2.threshold(edged.copy(), 127, 255, cv2.THRESH_BINARY)
    mask = thresh.copy()

    dilate_cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ret_img = image.copy()
    candidates = list()
    cont_area = list()
    for c in imutils.grab_contours(dilate_cnts):
        peri = cv2.arcLength(c, True)  # 외곽선 길이를 반환
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)  # 외곽선을 근사화(단순화) 합니다.
        approx = cv2.convexHull(approx)  # 주어진 점으로부터 컨벡스 헐을 반환
        area = cv2.contourArea(approx)  #  외곽선이 감싸는 영역의 면적을 반환

        x, y, w, h = cv2.boundingRect(approx)  # 주어진 점을 감싸는 최소 크기 사각형(바운딩 박스)를 반환
        if not (len_approx_range[0] <= len(approx) <= len_approx_range[1]):
            continue
        if not (area_range[0] < w * h < area_range[1]):
            continue
        if not (ratio_range[0] < h / w < ratio_range[1]):
            continue
        approx = np.zeros((4, 1, 2), dtype=np.int32)
        approx[0][0][0], approx[0][0][1] = x + w, y
        approx[1][0][0], approx[1][0][1] = x + w, y + h
        approx[2][0][0], approx[2][0][1] = x, y + h
        approx[3][0][0], approx[3][0][1] = x, y

        candidates.append([approx, w, h])
        cont_area.append([area, cv2.boundingRect(approx)])
        cv2.drawContours(ret_img, [approx], -1, (0, 255, 0), 2)
    return mask, candidates, cont_area


def detect_recog_points(img, criteria_list):
    """
    상단부 문제 위치 기준 사각형 좌표값을 밝기 차이를 통해 잡아내는 함수
    """
    y_ = criteria_list[0][1]
    w_ = criteria_list[0][2]
    h_ = criteria_list[0][3]
    image_b = img[y_ : y_ + h_, :]
    # image_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)
    (_, image_b) = cv2.threshold(image_b, 155, 255, cv2.THRESH_BINARY)
    image_b = cv2.transpose(image_b)
    y_list = [
        i for i in range(image_b.shape[0]) if np.sum(image_b[i]) < int(255 * h_ * 0.35)
    ]
    y_list = drop_dupli_lines(y_list, 10)
    return y_list


def get_coord(image, ans_list: list, color: tuple):
    """
    좌표를 받아와 컨투어 그려주는 함수
    """
    color = color
    for i in ans_list:
        x, y, w, h = i[0], i[1], i[2], i[3]
        approx = np.zeros((4, 1, 2), dtype=np.int32)
        approx[0][0][0], approx[0][0][1] = x + w, y
        approx[1][0][0], approx[1][0][1] = x + w, y + h
        approx[2][0][0], approx[2][0][1] = x, y + h
        approx[3][0][0], approx[3][0][1] = x, y
        cv2.drawContours(image, [approx], -1, color, 2)


def read_image_from_s3(bucket_name, filename):
    s3 = boto3.resource(
        "s3",
        region_name=settings.AWS_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )
    bucket = s3.Bucket(bucket_name)
    object = bucket.Object(filename)
    response = object.get()
    img = Image.open(response["Body"])
    img = ImageOps.exif_transpose(img)
    return img


def to_ratio(image, m):
    try:
        m[1][0] = round(m[1][0] / image.shape[1], 6)
        m[1][1] = round(m[1][1] / image.shape[0], 6)
        m[1][2] = round(m[1][2] / image.shape[1], 6)
        m[1][3] = round(m[1][3] / image.shape[0], 6)
    except:
        m[0] = round(m[0] / image.shape[1], 6)
        m[1] = round(m[1] / image.shape[0], 6)
        m[2] = round(m[2] / image.shape[1], 6)
        m[3] = round(m[3] / image.shape[0], 6)
    return m


def groupby_dict(res: list):
    res_dict = dict()
    for i in res:
        if i[0] in res_dict.keys():
            res_dict[i[0]].append(i[1])
        else:
            res_dict[i[0]] = [i[1]]
    return res_dict


def error_number_dict(instance: str, t_dict: dict, order: int):
    if instance in t_dict.keys():
        t_dict[instance].append(order)
    else:
        t_dict[instance] = [order]
    return t_dict


def empty_coord(emp):
    for k in emp:
        val = emp[k]
        emp[k] = [
            val[0][0],
            val[0][1],
            round(val[-1][0] - val[0][0], 6),
            round(val[-1][1] - val[0][1], 6),
        ]
    return emp


def compose(chosung, jungsung, jongsung):
    if chosung is None or jungsung is None:
        char = ""
    if jongsung is None:
        jongsung = " "
    char = chr(
        create_name_base["kor_begin"]
        + create_name_base["chosung_base"]
        * create_name_base["chosung_list"].index(chosung)
        + create_name_base["jungsung_base"]
        * create_name_base["jungsung_list"].index(jungsung)
        + create_name_base["jongsung_list"].index(jongsung)
    )
    return char


def convert_name(name):
    convert_name = []
    for i, j in enumerate(name):
        if j != None:
            if i == 0:
                convert_name.append(create_name_base["detected_chosung_list"][j])
            elif i == 1:
                convert_name.append(create_name_base["detected_jungsung_list"][j])
            elif i == 2:
                convert_name.append(create_name_base["detected_jongsung_list"][j])
        else:
            convert_name.append(None)
    return convert_name


def make_korean_name(name_index: list):
    """
    한글 초성, 중성, 종성의 ASCII 값을 조합하여 한글 이름을 만들어내는 함수
    """
    full_name = ""
    error = ""
    if None in [
        name_index[0],
        name_index[1],
        name_index[3],
        name_index[4],
        name_index[6],
        name_index[7],
    ]:
        error = "error"

    for i in range(0, 9, 3):
        try:
            full_name += compose(*convert_name(name_index[i : i + 3]))
        except:
            full_name += " "
    return full_name, error
