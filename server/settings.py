import os
from dotenv import load_dotenv

load_dotenv()

MONGO_HOST = os.environ.get("MONGO_HOST", "")
MONGO_PORT = os.environ.get("MONGO_PORT", "")
MONGO_USER = os.environ.get("MONGO_USER", "")
MONGO_PWD = os.environ.get("MONGO_PASSWORD", "")

# AWS settings
AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME", "")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME", "")

# Resize image width / height
resize_width = 1758
resize_height = 1240
allow_value = 0.2
thresh_value = 110
iii_coordinates = [
    (60, 270, 48, 47),
    (57, 366, 51, 49),
    (59, 415, 48, 46),
    (59, 511, 47, 46),
    (58, 608, 49, 46),
    (59, 753, 47, 46),
    (58, 898, 47, 46),
    (56, 1090, 48, 46),
    (107, 318, 49, 50),
    (107, 464, 47, 44),
    (107, 654, 47, 49),
    (106, 799, 47, 47),
    (105, 944, 47, 50),
    (104, 1136, 46, 50),
    (157, 415, 47, 49),
    (154, 560, 49, 46),
    (155, 755, 47, 47),
    (153, 846, 48, 49),
    (152, 994, 49, 47),
    (152, 1092, 49, 47),
    (225, 317, 47, 49),
    (224, 365, 48, 50),
    (225, 417, 47, 44),
    (223, 512, 49, 52),
    (224, 608, 45, 46),
    (222, 754, 48, 47),
    (222, 851, 48, 46),
    (223, 996, 47, 49),
    (223, 1138, 46, 49),
    (272, 270, 49, 49),
    (272, 563, 48, 44),
    (269, 654, 50, 49),
    (270, 801, 48, 49),
    (270, 897, 49, 49),
    (269, 1092, 48, 46),
    (322, 416, 47, 46),
    (319, 703, 48, 50),
    (318, 753, 49, 49),
    (319, 946, 47, 50),
    (317, 1045, 49, 47),
    (391, 271, 47, 49),
    (389, 467, 48, 46),
    (389, 564, 47, 44),
    (389, 706, 47, 47),
    (388, 804, 47, 44),
    (438, 273, 47, 47),
    (438, 319, 47, 49),
    (438, 511, 46, 49),
    (436, 608, 48, 49),
    (436, 754, 47, 47),
    (436, 898, 49, 50),
    (436, 996, 47, 46),
    (434, 1090, 50, 46),
    (487, 319, 47, 50),
    (485, 369, 48, 43),
    (486, 411, 51, 50),
    (484, 657, 47, 49),
    (485, 852, 48, 46),
    (483, 1041, 48, 49),
    (483, 1136, 46, 52),
    (557, 273, 46, 47),
    (556, 421, 46, 44),
    (555, 660, 47, 46),
    (552, 852, 48, 49),
    (552, 949, 48, 47),
    (554, 1095, 48, 47),
    (603, 272, 48, 47),
    (603, 322, 48, 46),
    (604, 465, 47, 49),
    (604, 566, 46, 46),
    (602, 706, 48, 52),
    (600, 901, 48, 46),
    (600, 1046, 47, 46),
    (602, 1143, 45, 46),
    (652, 275, 48, 44),
    (653, 371, 47, 49),
    (652, 514, 47, 47),
    (650, 612, 48, 44),
    (651, 757, 49, 47),
    (650, 999, 46, 44),
    (720, 371, 49, 47),
    (721, 564, 47, 46),
    (719, 660, 49, 46),
    (718, 758, 49, 43),
    (718, 801, 49, 49),
    (717, 996, 50, 47),
    (718, 1093, 50, 49),
    (769, 322, 48, 49),
    (767, 418, 49, 49),
    (768, 517, 47, 49),
    (767, 610, 48, 49),
    (768, 696, 47, 47),
    (766, 841, 49, 50),
    (767, 942, 49, 44),
    (766, 1036, 49, 46),
    (818, 266, 49, 46),
    (817, 457, 47, 46),
    (816, 603, 49, 46),
    (815, 891, 48, 49),
    (814, 1131, 48, 49),
    (886, 268, 49, 44),
    (886, 457, 47, 49),
    (886, 556, 48, 46),
    (884, 699, 49, 47),
    (885, 797, 49, 43),
    (935, 266, 47, 46),
    (933, 313, 50, 47),
    (933, 504, 48, 50),
    (934, 602, 48, 47),
    (933, 746, 46, 49),
    (933, 893, 48, 47),
    (932, 990, 47, 46),
    (933, 1083, 46, 49),
    (983, 315, 49, 46),
    (983, 361, 48, 49),
    (983, 409, 49, 46),
    (983, 649, 48, 50),
    (982, 844, 46, 49),
    (979, 1036, 47, 50),
    (979, 1133, 48, 49),
    (1053, 365, 46, 46),
    (1050, 457, 50, 50),
    (1049, 556, 49, 49),
    (1049, 699, 47, 49),
    (1048, 798, 48, 46),
    (1048, 992, 46, 46),
    (1048, 1136, 47, 46),
    (1101, 268, 48, 47),
    (1101, 318, 48, 41),
    (1099, 411, 46, 46),
    (1098, 507, 48, 46),
    (1099, 601, 47, 49),
    (1096, 748, 49, 47),
    (1096, 844, 48, 49),
    (1094, 1038, 50, 50),
    (1149, 315, 47, 44),
    (1147, 650, 47, 47),
    (1144, 893, 49, 50),
    (1147, 990, 46, 50),
    (1144, 1088, 48, 44),
    (1217, 362, 48, 50),
    (1217, 461, 47, 46),
    (1216, 556, 47, 46),
    (1216, 652, 47, 47),
    (1215, 751, 49, 46),
    (1214, 993, 47, 47),
    (1212, 1041, 49, 44),
    (1265, 269, 47, 46),
    (1265, 412, 47, 47),
    (1264, 507, 46, 49),
    (1263, 699, 49, 47),
    (1264, 797, 46, 50),
    (1263, 897, 47, 44),
    (1262, 1086, 48, 50),
    (1313, 315, 48, 49),
    (1312, 607, 48, 46),
    (1311, 847, 48, 47),
    (1312, 942, 48, 47),
    (1310, 1042, 47, 44),
    (1310, 1138, 46, 44),
    (1384, 315, 44, 50),
    (1384, 365, 46, 47),
    (1382, 413, 48, 44),
    (1380, 512, 48, 47),
    (1382, 609, 48, 43),
    (1380, 751, 48, 50),
    (1379, 850, 47, 49),
    (1378, 995, 48, 44),
    (1378, 1138, 48, 49),
    (1428, 272, 49, 43),
    (1428, 559, 48, 44),
    (1430, 652, 47, 47),
    (1428, 801, 47, 43),
    (1426, 899, 49, 46),
    (1426, 1091, 50, 47),
    (1479, 414, 46, 47),
    (1478, 699, 46, 53),
    (1478, 752, 46, 44),
    (1476, 945, 49, 50),
    (1475, 1044, 46, 47),
    (1545, 367, 51, 44),
    (1546, 556, 49, 49),
    (1546, 656, 48, 49),
    (1546, 755, 46, 43),
    (1544, 798, 48, 49),
    (1544, 995, 47, 46),
    (1543, 1091, 50, 47),
    (1597, 316, 46, 49),
    (1595, 412, 46, 49),
    (1596, 513, 48, 43),
    (1593, 607, 50, 46),
    (1594, 705, 46, 49),
    (1594, 850, 48, 49),
    (1591, 948, 51, 47),
    (1593, 1045, 47, 46),
    (1643, 269, 51, 50),
    (1642, 461, 50, 52),
    (1644, 609, 48, 44),
    (1641, 899, 49, 46),
    (1641, 1141, 48, 47),
]

