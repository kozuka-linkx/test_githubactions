import time
import numpy as np
import cv2


class DummyLock:
    """
    Lock用のダミークラス．
    Lockのデフォルト値として設定．
    要:適切なエラー処理

    """
    def acquire(self):
        """
        Lockによる排他制御開始のダミーメソッド．

        """
        pass

    def release(self):
        """
        Lockによる排他制御終了のダミーメソッド．

        """
        pass


class CameraBase:
    """
    実際にカメラを定義，操作するクラス．
    カメラの種類に応じて適切に実装する．

    """
    def __init__(self):
        """
        カメラ定義を行う．

        """
        print('Initialize Camera')
        self.camera = cv2.VideoCapture(0)
        return None

    @property
    def _take_picture(self):
        """
        一番原始的なカメラ画像取得メソッド

        Returns
        ---------------
        image: numpy.ndarray
            カメラ画像

        """
        ret = False
        while ret is not True:
            time.sleep(1/1000)
            ret, image = self.camera.read()
        return image

    def _taking(self, take_buffer, take_lock=DummyLock()):
        """
        無限ループでカメラ画像をメモリに書き込み続けるメソッド．

        Parameters
        ---------------------
        take_bufffer: multiprocessing.sharedctypes.RawArray
            カメラ画像格納用のメモリ領域．
        take_lock: DummyLock or multiprocessing.Lock
            排他制御用の変数．
            基本的に必要だが，複数プロセス間での画像共有方法次第では不要．

        """
        print('start take loop')
        error = False
        while error is False:
            try:
                time.sleep(1/1000)

                # >>排他制御開始
                take_lock.acquire()
                # カメラ画像取得
                image = self._take_picture
                # メモリへコピー
                np.asarray(take_buffer)[:] = image.flatten()
                # <<排他制御終了
                take_lock.release()
            except Exception as e:
                error = e
        try:
            take_lock.release()
        except (ValueError, RuntimeError):
            pass
        print('end take')
        return None


class Width:
    """
    OpenCVで取得できるカメラ画像の横幅を定義するパラメータクラス．
    Thread版と同一

    """
    def camera_width(self, camera):
        """
        パラメータ定義の辞書作成メソッド．
        メソッド名とParameterDefinitionsクラスで定義するパラメータ名を
        一致させること．

        Parameters
        -------------------
        camear: cv2.VideoCapture
            OpenCVのカメラオブジェクト

        Returns
        -------------------
        width_dict: dict
            カメラ画像の横幅定義辞書
            最低限パラメータ設定用の'set'とパラメータ取得用の'get'を
            キー，値が関数ポインタの要素が必要．
            他にパラメータ設定時の必要に応じて最大値，最小値などの
            データを記述する．

        """
        def set_value(value):
            """
            パラメータセット用関数

            Parameters
            ------------------
            value: int
                画像横幅の変更値

            """
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, value)
            return None

        def get_value():
            """
            パラメータ取得用関数

            Returns
            ------------------
            camera.get(cv2.CAP_PROP_FRAME_HEIGHT): int
                現在のカメラ画像横幅設定値

            """
            return camera.get(cv2.CAP_PROP_FRAME_WIDTH)

        # 設定，取得用関数ポインタを辞書に登録
        width_dict = {
            'set': set_value,
            'get': get_value
        }
        return width_dict


class Height:
    """
    OpenCVで取得できるカメラ画像の縦幅を定義するパラメータクラス．
    Thread版と同一

    """
    def camera_height(self, camera):
        """
        パラメータ定義の辞書作成メソッド．
        メソッド名とParameterDefinitionsクラスで定義するパラメータ名を
        一致させること．

        Returns
        -------------------
        camear: cv2.VideoCapture
            OpenCVのカメラオブジェクト

        height_dict: dict
            カメラ画像の縦幅定義辞書
            最低限パラメータ設定用の'set'とパラメータ取得用の'get'を
            キー，値が関数ポインタの要素が必要．
            他にパラメータ設定時の必要に応じて最大値，最小値などの
            データを記述する．

        """
        def set_value(value):
            """
            パラメータセット用関数

            Parameters
            ------------------
            value: int
                画像縦幅の変更値

            """
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, value)
            return None

        def get_value():
            """
            パラメータ取得用関数

            Parameters
            ------------------
            camera: cv2.VideoCapture
                OpenCVのカメラオブジェクト

            Returns
            ------------------
            camera.get(cv2.CAP_PROP_FRAME_HEIGHT): int
                現在のカメラ画像縦幅設定値

            """
            return camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

        # 設定，取得用関数ポインタを辞書に登録
        height_dict = {
            'set': set_value,
            'get': get_value
        }
        return height_dict
