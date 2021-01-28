"""
外部から使用できるカメラクラスを列挙

from .cameras import カメラ固有クラス名

"""
from .ids_xs import CameraIDS_XS

__all__ = [
    "CameraIDS_XS"]


# 自動importの実験跡地
# from pathlib import Path
# import os
# import re
#
# now_dir = (Path(os.path.abspath(__file__))).parent
# for camera_dir in now_dir.glob("cameras"):
#     targets = camera_dir.glob("*.py")
#     for target in targets:
#         target_file_name = target.name
#         target_name = target.stem
#         if re.search(r"^__", target_file_name) is None:
#             with open(str(target), "r") as f:
#                 lines = f.readlines()
#             for single_line in lines:
#                 if re.search(r"^class Camera", single_line) is not None:
#                     from_target = ".cameras"
#                     import_name = \
#                         re.search(r"Camera[^\(]*", single_line).group()
#                     import_str = \
#                         "from " + from_target + " import " + import_name
#                     print("ids")
#                     print(import_str)
#                     exec(import_str)
