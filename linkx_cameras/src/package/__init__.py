"""
外部から使用できるカメラクラスを列挙

from .ライブラリ.cameras.カメラ固有ファイル名 import カメラ固有クラス名

"""
from .ids.ids_xs import CameraIDS_XS

__all__ = [
    "CameraIDS_XS"]


# 自動importの実験跡地
# from pathlib import Path
# import os
# import re
#
# now_dir = (Path(os.path.abspath(__file__))).parent
# for single_dir in now_dir.glob("*"):
#     print(single_dir)
#     if single_dir.is_dir() is True:
#         camera_dir = single_dir/"cameras"
#         targets = camera_dir.glob("*.py")
#         for target in targets:
#             target_dir_name1 = target.parents[1].name
#             target_dir_name2 = target.parents[0].name
#             target_dir_name = target_dir_name1 + "." + target_dir_name2
#             target_file_name = target.name
#             target_name = target.stem
#             if re.search(r"^__", target_file_name) is None:
#                 with open(str(target), "r") as f:
#                     lines = f.readlines()
#                 for single_line in lines:
#                     if re.search(r"^class Camera", single_line) is not None:
#                         from_target = \
#                             "." + target_dir_name + "." + target_name
#                         import_name = \
#                             re.search(r"Camera[^\(]*", single_line).group()
#                         import_str = \
#                             "from " + from_target + " import " + import_name
#                         print(import_str)
#                         exec(import_str)
