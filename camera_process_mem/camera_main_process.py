import time

import numpy as np
import cv2

import camera_opencv_process as cv_cam
from camera_opencv_process import DummyLock


class ParameterDefinitions(cv_cam.Width, cv_cam.Height):
    """
    Thread版と一緒．

    ---------------------------------------------
    カメラパラメータ定義クラス．
    カメラパラメータ取得時，設定時に使用する．

    使用するパラメータクラスを全て継承させる．

    """

    def __init__(self, camera):
        """
        パラメータ名(self.param_names)から
        パラメータ辞書(self.param_dicts)を作成する．
        self.param_namesは使用するカメラとパラメータクラスに
        合わせて適切に定義する．

        (例)
        self.param_dicts = {
            パラメータA: {
                'min': 最小値,
                'max': 最大値,
                'set': 値設定関数,
                'get': 値取得関数
            },
            パラメータB: {
                ...
            },
            ...
        }

        Paramters
        -----------------
        camear: カメラオブジェクト
            使用しているカメラオブジェクト

        """
        print('ParameterDefinitions')
        self.param_names = [
            'camera_width', 'camera_height'
        ]
        self.param_dicts = {}
        self._make_dicts(camera)
        return None

    def _make_dicts(self, camera):
        """
        self.param_namesに基づいてself.param_dictsを作成する．

        """
        for name in self.param_names:
            self.param_dicts[name] = eval('self.' + name + '(camera)')
        return None

    def _set_param(self, param_name, value):
        """
        self.param_dictsの値設定関数'set'に基づいて
        指定したパラメータの値を設定する．

        Parameters
        -----------------------
        param_name: str
            設定するパラメータ名

        value: int, float, str,...etc
            パラメータ変更後の値
            型はパラメータ種類に依存

        """
        self.param_dicts[param_name]['set'](value)
        return None

    def _get_param(self, param_name):
        """
        self.param_dictsの値取得関数'get'に基づいて
        指定したパラメータの現在値を取得する．

        Parameters
        -----------------------
        param_name: str
            現在値を取得するパラメータ名

        Returns
        ----------------------
        self.param_dicts[param_name]['get'](camera): int, float, str, ...etc
            param_nameの現在値．
            型はパラメータ種類に依存．

        """
        return self.param_dicts[param_name]['get']()


class Camera:
    """
    Thread版とほぼ同一だが，マルチプロセスではこのクラスを
    実行するプロセスのみでカメラクラスを操作する．
    そのため撮影を実行するmainメソッドが新たに追加され，
    カメラ画像を返すPictureプロパティが削除されている．

    カメラクラス．
    外部からはこのインスタンスを通して全ての
    カメラ操作を行う．

    """
    def __init__(self):
        """
        外部からは直接アクセスできない形で使用する
        カメラのインスタンスとパラメータ定義のインスタンスを
        作成する．

        """
        print('__init__:Camera')
        self.__camera_base = cv_cam.CameraBase()
        self.__params = ParameterDefinitions(self.camera)
        return None

    def set_param(self, param_name, value):
        """
        パラメータ定義クラスのパラメータ設定メソッドを呼び出す．

        Parameters
        -----------------------
        param_name: str
            設定するパラメータ名

        value: int, float, str,...etc
            パラメータ変更後の値
            型はパラメータ種類に依存

        """
        self.__params._set_param(param_name, value)
        return None

    def get_param(self, param_name):
        """
        パラメータ定義クラスのパラメータ取得メソッドを呼び出す．

        Parameters
        -----------------------
        param_name: str
            現在値を取得するパラメータ名


        Returns
        ----------------------
        self.__params._get_param(...): int, float, str,...etc
            param_nameの現在値
            型はパラメータ種類に依存

        """
        return self.__params._get_param(param_name)

    def main(self, kwargs):
        error = False
        cam_mems = [
            kwargs["cam_mem1/3"], kwargs["cam_mem2/3"], kwargs["cam_mem3/3"]
        ]
        index = kwargs["cam_mem_index"]
        cam_pick_lock = kwargs["cam_pick_lock"]
        length = len(cam_mems) - 1
        st = time.perf_counter()
        ti = st - st
        print("start camera")
        while error is False and ti < 20:
            try:
                image = self.__camera_base._take_picture
                cam_pick_lock.acquire()
                index.value = (index.value + 1) % length
                np.asarray(cam_mems[index.value])[:] = image.flatten()
                cam_pick_lock.release()
            except Exception as e:
                error = e
                print("camera error : " + str(error))
            ti = time.perf_counter() - st
        try:
            cam_pick_lock.release()
        except (ValueError, RuntimeError):
            pass
        print('end camera')
        return None

    @property
    def camera(self):
        """
        カメラインスタンスのカメラオブジェクトを取得する．
        内部ではこれを操作することでカメラ操作を行っている．
        書き換えないためgetterのみ定義．

        Returns
        ------------------------
        self.__camera_base.camera: etc
            画像取得，パラメータ変更等で実際に使用されるカメラオブジェクト

        """
        return self.__camera_base.camera


class PickPicture:
    """
    サンプルの作業プロセス
    画像表示を行っている．
    画像をメモリから読み込む以外はThread版と同様．

    """
    def __init__(self):
        """
        メモリから画像を復元するために縦横の長さを
        インスタンス作成時に引数として受け取る．

        """
        print('__init__:ShowPicture')
        self.interval = 3
        self.loop_time = 20
        return None

    def main(self, kwargs):
        cam_mems = [
            kwargs["cam_mem1/3"], kwargs["cam_mem2/3"], kwargs["cam_mem3/3"]
        ]
        pick_mem = kwargs["pick_mem1/1"]
        index = kwargs["cam_mem_index"]
        need_update = kwargs["need_update"]
        cam_pick_lock = kwargs["cam_pick_lock"]
        pick_show_lock = kwargs["pick_show_lock"]

        error = False
        count = 0
        print("start pick")
        while error is False and count < self.loop_time:
            try:
                pick_show_lock.acquire()
                if need_update.value == 1:
                    cam_pick_lock.acquire()
                    serial_array = np.array(
                        cam_mems[index.value], dtype=np.float32, copy=True)
                    cam_pick_lock.release()
                    np.asarray(pick_mem)[:] = serial_array
                    need_update.value = 0
                    pick_show_lock.release()
                    count += 1
                    time.sleep(self.interval)
                else:
                    time.sleep(0.01)
                    pick_show_lock.release()
            except Exception as e:
                error = e
                print(error)
        try:
            cam_pick_lock.release()
        except (ValueError, RuntimeError):
            pass
        try:
            pick_show_lock.release()
        except (ValueError, RuntimeError):
            pass
        print('end pick')
        return None


class ShowPicture:
    """
    サンプルの作業プロセス．
    ファイルへの画像出力を行う．
    画像をメモリから読み込む以外はThread版と同様．

    """
    def __init__(self, height, width):
        """
        メモリから画像を復元するために縦横の長さを
        インスタンス作成時に引数として受け取る．

        Parameters
        --------------------------
        height: int
            縦の長さ
        width: int
            縦の長さ

        """
        print('__init__:SavePicture')
        self.height = height
        self.width = width
        # ファイル名の関数ポインタ
        self.name = '/ramdisk/save_{0:04d}.png'.format
        return None

    def main(self, kwargs):
        pick_mem = kwargs["pick_mem1/1"]
        pick_show_lock = kwargs["pick_show_lock"]
        need_update = kwargs["need_update"]
        error = False
        count = 0
        key = ""
        is_save = False
        print('start show')
        while error is False and key != ord("q"):
            pick_show_lock.acquire()
            try:
                serial_array = np.array(
                    pick_mem, dtype=np.float32, copy=True
                )
                if need_update.value == 0:
                    need_update.value = 1
                    pick_show_lock.release()
                    is_save = True
                else:
                    pick_show_lock.release()
                    is_save = False
                    time.sleep(0.05)
                image = np.reshape(
                    serial_array, (self.height, self.width, 3)
                )
                image = image.astype(np.uint8)
                cv2.imshow("image", image)
                if is_save is True:
                    cv2.imwrite(self.name(count), image)
                count += 1
                key = cv2.waitKey(10)
            except Exception as e:
                error = e
        try:
            pick_show_lock.release()
        except (ValueError, RuntimeError):
            pass
        print("end show")
        return None
