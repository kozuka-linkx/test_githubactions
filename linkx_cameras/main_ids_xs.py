import cv2
# import sys
# sys.path.append("../")
# from src import CameraIDS_XS
# # import src
# # from .src import CameraIDS_XS
# from ..src import CameraIDS_XS
# from ..src import CameraIDS_XS
from src import CameraIDS_XS


if __name__ == "__main__":
    def change_mode(cam, target_name):
        """
        パラメータの自動調整と手動調整を切り替えるための共通の関数．

        Args
        ---------------------------
        cam: camera
            カメラインスタンス

        target_name: str
            変更するパラメータ名

        Returns
        ----------------------------
        target_values: dict
            {"min": 最小値, "max": 最大値, "now": 現在値,
             "is_auto": 自動調整ON-OFF(True False)}

        """
        print("change " + target_name + " mode")
        # 空の文字列をset_parameterの引数に与え，
        # 変更後の値をtarget_valuesで受け取る．
        target_values = cam.set_parameter(target_name)
        # True Falseを文字列へ変換し，変更後の状態と
        # パラメータの現在値を出力する．
        mode = "auto" if target_values["is_auto"] is True else "manual"
        print("now " + target_name + " mode: " + mode)
        print("now " + target_name + " value: " + str(target_values["now"]))
        return target_values

    def change_value(cam, target_name, dvalue):
        """
        パラメータの値を変更するための共通の関数．

        Args
        ---------------------------
        cam: camera
            カメラインスタンス

        target_name: str
            変更するパラメータ名

        dvalue: int, float
            パラメータの値の変更幅

        Returns
        ----------------------------
        target_values: dict
            {"min": 最小値, "max": 最大値, "now": 現在値,
             "is_auto": 自動調整ON-OFF(True False)}
        """
        if dvalue > 0:
            print("increment " + target_name + " value")
        else:
            print("decrement " + target_name + " value")
        # 現在値取得のためパラメータ取得
        target_values = cam.get_parameter(target_name)
        # 変更後のパラメータの値を設定
        new_value = target_values["now"] + dvalue
        # 変更後のパラメータが設定可能な最大値より大きい場合
        if new_value > target_values["max"]:
            # 値を出力して何もしない．
            print(
                "new_" + target_name + ": " + str(new_value) + " > " +
                "max_" + target_name + ": " + str(target_values["max"])
            )
        # 変更後のパラメータが設定可能な最小値より小さい場合
        elif new_value < target_values["min"]:
            # 値を出力して何もしない．
            print(
                "new_" + target_name + ": " + str(new_value) + " < " +
                "min_" + target_name + ": " + str(target_values["min"])
            )
        # 変更後のパラメータが設定可能な値域に収まっている場合
        else:
            # set_parameterにより値を変更
            target_values = cam.set_parameter(target_name, new_value)
            # 変更後の実際の値を出力
            print("now " + target_name +
                  " value: " + str(target_values["now"]))
        return target_values

    # 以下の値は適切に変更して使用してください
    # =============================================================
    # -------------------------------------------------------------
    # パラメータの変更幅
    d_focus = 2
    # 単位は[ms]なことに注意
    d_shutter = 10
    d_gain = 5
    d_white_balance = 1

    # -------------------------------------------------------------
    # 描画用パラメータ
    # デフォルト解像度だと大きいため縮小して表示させる．
    # ボードカメラ用の出力画像の縮小率
    show_rate_board = 0.25
    # ハウジング済みカメラの出力画像の縮小率
    show_rate_xs = 0.75

    # -------------------------------------------------------------
    # カメラ選択パラメータ
    # ボードカメラ(UI-3881LE-C-HQ-AF)を使用する場合はTrue，
    # ハウジング済みカメラ(UI-1007XS-C)を使用する場合はFalseにする．
    use_board = True
    # =============================================================
    # cam = pt_cameras.CameraTis_AutoFocus()
    # cam = src.CameraIDS_XS()
    cam = CameraIDS_XS()
    cam.start_camera()
    show_rate = 0.5

    parameters = {}
    # get_parameterメソッドによりパラメータの設定可能最大値，設定可能最小値，
    # 現在値，自動調整機能のON-OFF(True False)を取得．
    parameters["focus"] = cam.get_parameter("focus")
    parameters["shutter"] = cam.get_parameter("shutter")
    parameters["gain"] = cam.get_parameter("gain")
    parameters["white_balance_red"] = cam.get_parameter("white_balance_red")
    # とりあえず現在の情報を出力する．
    print("FOCUS: {}".format(parameters["focus"]))
    print("SHUTTER: {}".format(parameters["shutter"]))
    print("GAIN: {}".format(parameters["gain"]))
    print("WHITE BALANCE: {}".format(parameters["white_balance_red"]))

    key = ""
    while key != ord("q"):
        # get_imageメソッドで画像取得
        image = cam.get_image()
        # 出力用にサイズ変更
        image = cv2.resize(image, (0, 0), fx=show_rate, fy=show_rate)
        cv2.imshow("window", image)
        key = cv2.waitKey(10) & 0xFF

        # フォーカスの自動，手動切り替え
        if key == ord("f"):
            target = "focus"
            if isinstance(parameters[target], dict):
                parameters[target] = change_mode(cam, target)
            else:
                print("フォーカスは変更できません")
        # フォーカス値の変更
        elif key in [ord("d"), ord("s")]:
            target = "focus"
            if isinstance(parameters[target], dict):
                if parameters[target]["is_auto"] is True:
                    print("WARNING: 自動フォーカスがONになっています")
                else:
                    if key == ord("d"):
                        dvalue = d_focus
                    else:
                        dvalue = (-1)*d_focus
                    parameters[target] = change_value(cam, target, int(dvalue))
            else:
                print("フォーカスは変更できません")
        # ゲインの自動，手動切り替え
        elif key == ord("r"):
            target = "gain"
            if isinstance(parameters[target], dict):
                parameters[target] = change_mode(cam, target)
            else:
                print("ゲインは変更できません")
        # ゲインの値の変更
        elif key in [ord("e"), ord("w")]:
            target = "gain"
            if isinstance(parameters[target], dict):
                if parameters[target]["is_auto"] is True:
                    print("WARNING: ゲインの自動調整がONになっています")
                else:
                    if key == ord("e"):
                        dvalue = d_gain
                    else:
                        dvalue = (-1)*d_gain
                    parameters[target] = change_value(cam, target, int(dvalue))
            else:
                print("ゲインは変更できません")
        # シャッタースピードの自動，手動切り替え
        elif key == ord("v"):
            target = "shutter"
            if isinstance(parameters[target], dict):
                parameters[target] = change_mode(cam, target)
            else:
                print("シャッタースピードは変更できません")
        # シャッタースピードの値の変更
        elif key in [ord("c"), ord("x")]:
            target = "shutter"
            if isinstance(parameters[target], dict):
                if parameters[target]["is_auto"] is True:
                    print("WARNING: 自動露光がONになっています")
                else:
                    if key == ord("c"):
                        dvalue = d_shutter
                    else:
                        dvalue = (-1)*d_shutter
                    parameters[target] = change_value(cam, target, dvalue)
            else:
                print("シャッタースピードは変更できません")
        # ホワイトバランスの自動，手動切り替え
        elif key == ord("u"):
            target = "white_balance_red"
            if isinstance(parameters[target], dict):
                parameters[target] = change_mode(cam, target)
            else:
                print("ホワイトバランスは変更できません")
        # ホワイトバランスの値の変更
        elif key in [ord("y"), ord("t")]:
            target = "white_balance_red"
            if isinstance(parameters[target], dict):
                if parameters[target]["is_auto"] is True:
                    print("WARNING: ホワイトバランスの自動調整がONになっています")
                else:
                    if key == ord("y"):
                        dvalue = d_white_balance
                    else:
                        dvalue = (-1)*d_white_balance
                    parameters[target] = \
                        change_value(cam, target, dvalue)
            else:
                print("ホワイトバランスは変更できません")
