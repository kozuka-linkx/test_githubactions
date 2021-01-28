from abc import ABCMeta
# 取得した画像のndarray化に使用
import numpy as np
# IDSカメラライブラリ
from pyueye import ueye
# カメラ基本クラス用
from ..common import base_camera_tools as bct

"""
IDSカメラ基本クラスBaseCameraIDSの定義．
カメラ基本クラスBaseCameraを継承している．
このクラス自体はIDSカメラ基本クラスなため，運用上はカメラ固有クラスの
CameraIDS_BoardやCameraIDS_XSを使用する．

==============================================================================
現時点で実装済みのカメラクラス
==============================================================================
CameraIDS_Board:
    ボードカメラ(UI-3881LE-C-HQ-AF)用のカメラクラス
CameraIDS_XS:
    ハウジング済みのカメラ(UI-1007XS-C)用のカメラクラス

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


class BaseCameraIDS(bct.BaseCamera, metaclass=ABCMeta):
    """
    IDSカメラ基本クラス．

    Methods
    -----------------------------------------------
    __init__(self, **kwargs: dict) -> None
        基本クラスで定義するインスタンス変数を列挙．
        基本的にカメラ固有クラスでオーバーライドするため実行されない．

    _def_camera(cam_id: int, **kwargs: dict) -> camera
        カメラ定義メソッド．
        カメラとの接続，メモリ確保等を行う．

    start_camera() -> None
        キャプチャ開始メソッド．

    get_image() -> numpy.ndarray
        画像取得メソッド．
        外部から呼び出す．

    __del__() -> None
        IDSカメラ共通のデコンストラクタ．

    """
    def __init__(self, **kwargs):
        """
        基本クラスで定義するインスタンス変数を列挙．
        基本的にカメラ固有クラスでオーバーライドするため実行されない．

        """
        self.camera = bct.DummyValue()
        self.get_data = bct.DummyValue()
        self.pcImageMemory = bct.DummyValue()
        self.MemID = bct.DummyValue()
        return None

    def _def_camera(self, cam_id, **kwargs):
        """
        カメラ初期化を行い，カメラインスタンスを作成して返すメソッド．
        ほぼサンプルそのままなため余計な部分が多いと思われる．

        Args
        -----------------------
        cam_id: int
            カメラ番号
        **kwargs: dict
            カメラ固有の引数．
            今はボード，XS共通で画像サイズを示すheight，widthのみ有効．


        Returns
        -----------------------
        hCam: camera
            定義されたカメラインスタンス

        """
        # ueyeライブラリで定義された型の変数を宣言
        hCam = ueye.HIDS(cam_id)
        sInfo = ueye.SENSORINFO()
        cInfo = ueye.CAMINFO()
        pcImageMemory = ueye.c_mem_p()
        MemID = ueye.int()
        pitch = ueye.INT()
        # nBitsPerPixel = ueye.INT(32)
        nBitsPerPixel = ueye.INT(24)
        m_nColorMode = ueye.INT()
        bytes_per_pixel = int(nBitsPerPixel / 8)
        # カメラ初期化本体
        nRet = ueye.is_InitCamera(hCam, None)
        if nRet != ueye.IS_SUCCESS:
            print("is_InitCamera ERROR")
        # カメラ情報の出力
        nRet = ueye.is_GetCameraInfo(hCam, cInfo)
        if nRet != ueye.IS_SUCCESS:
            print("is_GetCameraInfo ERROR")
        nRet = ueye.is_GetSensorInfo(hCam, sInfo)
        if nRet != ueye.IS_SUCCESS:
            print("is_GetSensorInfo ERROR")
        # 役割不明
        nRet = ueye.is_SetDisplayMode(hCam, ueye.IS_SET_DM_DIB)
        # カラーモード設定
        now_color_mode = int.from_bytes(
            sInfo.nColorMode.value, byteorder='big'
        )
        print("cmode_ : " + str(now_color_mode))
        if now_color_mode == ueye.IS_COLORMODE_BAYER:
            # setup the color depth to the current windows setting
            ueye.is_GetColorDepth(hCam, nBitsPerPixel, m_nColorMode)
            bytes_per_pixel = int(nBitsPerPixel / 8)
            print("IS_COLORMODE_BAYER: ", )
            print("\tm_nColorMode: \t\t", m_nColorMode)
            print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
            print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
            print()
        elif now_color_mode == ueye.IS_COLORMODE_CBYCRY:
            # for color camera models use RGB32 mode
            m_nColorMode = ueye.IS_CM_BGRA8_PACKED
            nBitsPerPixel = ueye.INT(32)
            bytes_per_pixel = int(nBitsPerPixel / 8)
            print("IS_COLORMODE_CBYCRY: ", )
            print("\tm_nColorMode: \t\t", m_nColorMode)
            print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
            print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
            print()
        elif now_color_mode == ueye.IS_COLORMODE_MONOCHROME:
            # for monochrome camera models use Y8 mode
            m_nColorMode = ueye.IS_CM_MONO8
            nBitsPerPixel = ueye.INT(8)
            bytes_per_pixel = int(nBitsPerPixel / 8)
            print("IS_COLORMODE_MONOCHROME: ", )
            print("\tm_nColorMode: \t\t", m_nColorMode)
            print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
            print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
            print()

        else:
            # for monochrome camera models use Y8 mode
            m_nColorMode = ueye.IS_CM_MONO8
            nBitsPerPixel = ueye.INT(8)
            bytes_per_pixel = int(nBitsPerPixel / 8)
            print("else")
        if nRet != ueye.IS_SUCCESS:
            print("cannot set color format")
        # rectAOI = ueye.IS_RECT()
        # nRet = ueye.is_AOI(
        #     hCam, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI)
        # )
        # if nRet != ueye.IS_SUCCESS:
        #     print("is_AOI ERROR")
        # # Prints out some information about the camera and the sensor
        print("Camera model:\t\t", sInfo.strSensorName.decode('utf-8'))
        print("Camera serial no.:\t", cInfo.SerNo.decode('utf-8'))

        # 追加実装
        # 画像サイズを設定する．
        # カメラで定義されたフォーマットIDで設定する必要があることに注意．
        if "format_id" in kwargs and "width" in kwargs and "height" in kwargs:
            format_id = kwargs["format_id"]
            # 表示，メモリ領域確保のために縦横の値を保持
            width = kwargs["width"]
            height = kwargs["height"]
            nRet = ueye.is_ImageFormat(
                hCam, ueye.IMGFRMT_CMD_SET_FORMAT,
                ueye.c_uint(format_id), 4
            )
            if nRet != ueye.IS_SUCCESS:
                print("format error")
        else:
            # format_idの指定がなければデフォルト値を使用する．
            width = rectAOI.s32Width
            height = rectAOI.s32Height
        print("image width:\t", width)
        print("image height:\t", height)

        # メモリ確保
        # Allocates an image memory for an image having its dimensions defined
        # by width and height and its color depth defined by nBitsPerPixel
        nRet = ueye.is_AllocImageMem(
            hCam, width, height, nBitsPerPixel, pcImageMemory, MemID
        )
        if nRet != ueye.IS_SUCCESS:
            print("is_AllocImageMem ERROR")
        else:
            # Makes the specified image memory the active memory
            nRet = ueye.is_SetImageMem(hCam, pcImageMemory, MemID)
            if nRet != ueye.IS_SUCCESS:
                print("is_SetImageMem ERROR")
            else:
                # Set the desired color mode
                nRet = ueye.is_SetColorMode(hCam, m_nColorMode)

        # 役割要調査
        # Enables the queue mode for existing image memory sequences
        nRet = ueye.is_InquireImageMem(
            hCam, pcImageMemory, MemID, width, height,
            nBitsPerPixel, pitch
        )
        if nRet != ueye.IS_SUCCESS:
            print("is_InquireImageMem ERROR")
        else:
            print("Press q to leave the programm")

        # 画像取得用関数定義
        def get_data():
            """
            メモリから画像を取得するための関数

            Returns
            ------------------------
            image: np.ndarray
                画像

            """
            array = ueye.get_data(
                pcImageMemory, width, height, nBitsPerPixel,
                pitch, copy=False
            )
            image = np.reshape(
                array, (height.value, width.value, bytes_per_pixel)
            )
            return image
        self.get_data = get_data

        # デコンストラクタで必要になるためインスタンス変数へ．
        self.pcImageMemory = pcImageMemory
        self.MemID = MemID
        return hCam

    def start_camera(self):
        """
        キャプチャ開始メソッド．

        """
        nRet = ueye.is_CaptureVideo(self.camera, ueye.IS_DONT_WAIT)
        if nRet != ueye.IS_SUCCESS:
            print("is_CaptureVideo ERROR")
        return None

    def get_image(self):
        """
        画像取得メソッド．
        IDSカメラではインスタンス変数が増えることを嫌って，
        _def_cameraメソッド中で定義した画像取得用関数を保持した
        インスタンス変数を呼び出す．

        """
        image = self.get_data()
        return image

    def __del__(self):
        """
        デコンストラクタ．
        IDSカメラの場合，手順を踏んで終了しないと正常終了せず，
        次回接続時にエラーが発生し得るため定義．
        ただ，エラーの有無に関わらずデコンストラクタ等の
        デバイス終了処理は適切に記述するよう心がける．

        サンプルプログラムから流用．

        """
        try:
            # キャプチャを停止する．
            nRet = ueye.is_StopLiveVideo(
                self.camera, ueye.IS_FORCE_VIDEO_STOP
            )
            print("stop: " + str(nRet))
        except Exception:
            print("")
        try:
            # 確保してあるメモリ領域の解放する．
            nRet = ueye.is_FreeImageMem(
                self.camera, self.pcImageMemory, self.MemID
            )
            print("release: " + str(nRet))
        except Exception:
            print("")
        # カメラとの接続を終了する．
        nRet = ueye.is_ExitCamera(self.camera)
        print("exit: " + str(nRet))
        return None
