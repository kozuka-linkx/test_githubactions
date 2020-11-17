from enum import Enum
# IDSカメラライブラリ
from pyueye import ueye
# IDSカメラの基本クラス
from ..base_camera_ids import BaseCameraIDS
# 使用するパラメータクラス
# ゲインとシャッタースピードを個別に自動，手動で切り替えられないため
# それ用のクラスを使用する．
from .parameters import GainShutter_Gain
from .parameters import GainShutter_Shutter
from .parameters import Focus
from .parameters import WhiteBalanceOffsetRed
from .parameters import WhiteBalanceOffsetBlue
"""
ハウジング済みのカメラ(UI-1007XS-C)用のカメラクラスを実装．
IDSカメラ基本クラスを継承して作成し，カメラ固有の処理のみ実装する．
ここではカメラパラメータの定義，画像サイズの定義を固有処理として行う．

"""

__author__ = "LiNKX"
__copyright__ = "Copyright 2020, LiNKX Inc,"
__credits__ = ["Toshiki Kozuka"]
__license__ = "*********UNDEFINED**********"
__version__ = "0.1.0"
__maintainer__ = "Toshiki Kozuka"
__email__ = "kozuka@linkx.dev"
__status__ = "Dev"
__data__ = "2020/10/23"


class ParameterDefinitions(Enum):
    """
    ボードカメラ用のカメラパラメータ列挙クラス．
    カメラに使用できるパラメータを調べてこのクラスで変数名と結びつける．
    カメラクラス内での変数定義時のためにEnum型で宣言する．
    ただし，画像サイズなどのカメラ定義後に変更不可な値は先頭に"_pt_"を
    つけて宣言する．

    """
    # フォーカス
    focus = Focus
    # ゲイン
    gain = GainShutter_Gain
    # シャッタースピード(露光時間)
    shutter = GainShutter_Shutter
    # ホワイトバランス
    # ただし赤，青のオフセットという形で調整する必要あり．
    white_balance_red = WhiteBalanceOffsetRed
    white_balance_blue = WhiteBalanceOffsetBlue
    # カメラ画像サイズの辞書
    # カメラ定義後は変更不可能なため，先頭に_pt_をつけて宣言する．
    #   キー: フォーマットID(公式ドキュメント参照)
    #   値: (高さ, 幅)
    _pt_image_size = {
        4: (1944, 2592),
        5: (1536, 2048),
        6: (1080, 1920),
        8: (960, 1280),
        9: (720, 1280),
        12: (480, 800),
        13: (480, 640),
        20: (1200, 1600),
        31: (480, 640),
        32: (480, 800),
    }


class CameraIDS_XS(BaseCameraIDS):
    """
    ハウジング済みカメラ用のカメラクラス．
    ハウジング済みカメラ固有の処理として以下を行う．
        1，カメラ画像サイズを定義する
        2，パラメータ列挙クラスをパラメータ定義メソッドへ渡す

    Methods
    -------------------------------------
    __init__(cam_id: int, **kwargs: dict) -> None
        カメラ，パラメータ定義

    start() -> None
        キャプチャ開始

    show_parameters() -> None
        定義済みカメラパラメータ出力

    """
    def __init__(self, cam_id=0, **kwargs):
        # カメラ名を出力
        print("IDS Camera: UI-1007XS-C")
        # デフォルトのformat_id
        default_format_id = 5

        # 引数にformat_idが未定義であればデフォルトの値を設定する．
        if "format_id" not in kwargs:
            kwargs["format_id"] = default_format_id
        # 辞書から画像サイズを読み取り
        height, width = \
            ParameterDefinitions._pt_image_size.value[kwargs["format_id"]]
        # c_typesのint型にする必要があるため変換
        kwargs["height"] = ueye.c_int(height)
        kwargs["width"] = ueye.c_int(width)

        # カメラ定義
        self.camera = self._def_camera(cam_id=cam_id, **kwargs)
        # # ホワイトバランス自動調整ON
        # # カメラ固有の処理のためここで実装
        # nRet = ueye.is_SetAutoParameter(
        #     self.camera, ueye.IS_SET_ENABLE_AUTO_SENSOR_WHITEBALANCE,
        #     ueye.c_double(1), ueye.c_double(0)
        # )
        # パラメータ定義
        self.define_parameters(ParameterDefinitions)
        return None

    def start(self):
        """
        キャプチャを開始するメソッド．
        固有の処理は特にないため，親クラスのstart_cameraを呼び出すのみ．

        """
        # キャプチャ開始
        self.start_camera()
        return None

    def show_parameters(self):
        """
        定義済みカメラパラメータを出力

        """
        print("="*30)
        print("all valid parameters")
        # Enum型から順に名前，値を出力
        for parameter in ParameterDefinitions:
            name = parameter.name
            value = parameter.value
            print("[" + name + "]{}".format(value))
        print("="*30)
        return None
