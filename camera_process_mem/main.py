import multiprocessing
import multiprocessing.sharedctypes

import camera_main_process


if __name__ == '__main__':
    # 次の3つのプロセスABCを動作させる．
    # また以下の共有変数がある．
    # <共有変数>
    #   <a>．カメラ画像用共有メモリ3つ
    #   <b>．aのうち，最後に保存されたメモリを示すインデックス
    #   <c>．表示画像用共有メモリ1つ
    #   <d>．画像アップデート要求用共有変数1つ
    # (プロセス)
    #   (A)．カメラインスタンスを作成，カメラ画像を常に取得して<a>へ書き込み，
    #        <b>をアップデートする．
    #   (B)．<d>が要求側に変わった場合，<b>に対応する<a>へアクセスして取得した
    #        画像を<c>へ書き込む．
    #   (C)．<c>から画像を取得し，<d>を要求側に変更する．

    # マルチプロセスバージョン
    # 画像をメモリ空間で受け渡す必要がある．
    camera = camera_main_process.Camera()
    width = int(camera.get_param('camera_width'))
    height = int(camera.get_param('camera_height'))
    print('shape: ' + str((height, width)))
    # 保存，表示のために画像を復元する必要があるためサイズを渡す．
    pick = camera_main_process.PickPicture()
    show = camera_main_process.ShowPicture(height, width)

    # メモリ空間上に画像用のスペースを確保する．
    camera_memory0_0 = multiprocessing.sharedctypes.RawArray(
        'f', height*width*3)
    # メモリ空間上に画像用のスペースを確保する．
    camera_memory0_1 = multiprocessing.sharedctypes.RawArray(
        'f', height*width*3)
    # メモリ空間上に画像用のスペースを確保する．
    camera_memory0_2 = multiprocessing.sharedctypes.RawArray(
        'f', height*width*3)
    # メモリ空間上に画像用のスペースを確保する．
    pict_memory0 = multiprocessing.sharedctypes.RawArray(
        'f', height*width*3)
    # 画像インデックス
    image_index = multiprocessing.Value("i", 2)
    # showからthrowへ画像更新要求
    need_update = multiprocessing.Value("i", 0)
    # 排他制御用変数
    camera_pick_lock = multiprocessing.Lock()
    # 排他制御用変数
    pick_show_lock = multiprocessing.Lock()

    camera_kwargs = {
        "cam_mem1/3": camera_memory0_0,
        "cam_mem2/3": camera_memory0_1,
        "cam_mem3/3": camera_memory0_2,
        "cam_mem_index": image_index,
        "cam_pick_lock": camera_pick_lock,
    }
    pick_kwargs = {
        "cam_mem1/3": camera_memory0_0,
        "cam_mem2/3": camera_memory0_1,
        "cam_mem3/3": camera_memory0_2,
        "cam_mem_index": image_index,
        "cam_pick_lock": camera_pick_lock,
        "pick_mem1/1": pict_memory0,
        "need_update": need_update,
        "pick_show_lock": pick_show_lock,
    }
    show_kwargs = {
        "pick_mem1/1": pict_memory0,
        "need_update": need_update,
        "pick_show_lock": pick_show_lock,
    }
    # マルチプロセス定義
    camera_process = multiprocessing.Process(
        target=camera.main, args=(camera_kwargs,))
    pick_process = multiprocessing.Process(
        target=pick.main, args=(pick_kwargs,))
    show_process = multiprocessing.Process(
        target=show.main, args=(show_kwargs,), daemon=True)
    camera_process.start()
    pick_process.start()
    show_process.start()

    pick_process.join()
    camera_process.join()
