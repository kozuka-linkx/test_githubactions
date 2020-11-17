import re
from abc import ABCMeta, abstractmethod
# setter，getterをパラメータ名から自動で定義するデコレータ
from .define_properties import define_properties

"""
全てのメーカーのカメラの基本クラスとして抽象クラスBaseCameraと
全てのパラメータの基本クラスとして抽象クラスBaseParameterを定義する．

またそれ以外に共通して使用するダミーの値クラスDummyValueと，
警告等のメッセージ出力用に使用するPrintMessage，MakeMessageクラスを
定義する．

(依存ライブラリ)


"""

# __author__ = "LiNKX"
# __copyright__ = "Copyright 2020, LiNKX Inc,"
# __credits__ = ["Toshiki Kozuka"]
# __license__ = "***************UNDEFINED***************"
# __version__ = "0.1.0"
# __maintainer__ = "Toshiki Kozuka"
# __email__ = "kozuka@linkx.dev"
# __status__ = "Dev"
# __data__ = "2020/10/"


class DummyValue:
    """
    BaseCameraクラスのset_parameterメソッドのデフォルト値として
    使用することで何かしらの値が引数に与えられたかどうかを判定
    するのに使用する．
    そのため中身は現状何も実装していない．

    """
    def __init__(self):
        pass


class NoParameterValue:
    """
    BaseParameterクラスの__call__メソッドのデフォルト値として
    使用してsetterとgetterを適切に呼ぶ．

    """
    def __init__(self):
        pass


class BaseCamera(metaclass=ABCMeta):
    """
    カメラ基本クラス．
    各ライブラリ用のカメラクラスはこれを継承して作成する．

    Methods
    ---------------------------------
    @abstractmethod
    get_image() -> NotImplementedError
        抽象クラス．
        カメラ画像取得用メソッドのため，必ずどこかで実装する．

    get_parameter(paramter_name: str) -> value: dict
        外部から呼び出すパラメータ取得用メソッド．
        基本的に以下のキーを持つ．
            "max": 最大値
            "min": 最小値
            "now": 現在値
            "is_auto": 自動調整がオンかどうか

    set_parameter(
        paramter_name: str, value: any, default DummyValue
    ) -> value: dict
        外部から呼び出すパラメータ設定メソッド．
        valueのデフォルト値をDummyValueとすることで，引数が
        与えられていない場合をパラメータ毎のsetterで判定
        できるようにしている．

    define_parameters(param_defs: Enum, *args: list, **kwargs: dict) -> None
        パラメータ定義用メソッド．
        カメラ固有クラスで定義するEnum型のパラメータクラスを受け取り，
        自動でパラメータ定義を行うメソッド．

    """
    @abstractmethod
    def get_image(self):
        """
        カメラ画像取得用のメソッド．
        ライブラリ毎，もしくはカメラ毎に実装する．

        """
        raise NotImplementedError

    def get_parameter(self, parameter_name):
        """
        外部からparameter_nameのカメラパラメータを取得するためのメソッド．

        Args
        ----------------------------
        parameter_name: str
            情報を取得したいカメラパラメータ名

        Returns
        ----------------------------
        values: dict
            基本的に以下のキーを持つ．
                "max": 最大値
                "min": 最小値
                "now": 現在値
                "is_auto": 自動調整がオンかどうか
        """
        try:
            # getattrでset_parameterと共通の関数を取得，
            # 引数なしで実行することでparameter_nameの
            # getterを実行する．
            value = getattr(self, parameter_name)()
        except AttributeError as e:
            # 存在しないパラメータ名を使用した場合は例外を返す
            value = e
        return value

    def set_parameter(self, parameter_name, value=DummyValue()):
        """
        外部からparameter_nameのカメラパラメータをvalueに設定するためのメソッド．
        パラメータ設定後，getattrにより変更後の値を取得する．

        Args
        ----------------------------
        parameter_name: str
            値を設定したいカメラパラメータ名
        value: any, default DummyValue()
            設定したい値．
            デフォルト値をDummyValue()とすることでNoneや空の
            文字列を設定値に与えたい場合にも対応．


        Returns
        ----------------------------
        values: dict
            基本的に以下のキーを持つ．
                "max": 最大値
                "min": 最小値
                "now": 現在値
                "is_auto": 自動調整がオンかどうか

        """
        try:
            # getattrでset_parameterと共通の関数を取得，
            # 引数ありで実行することでparameter_nameの
            # setterを実行する．
            func = getattr(self, parameter_name)
            func(value)
            # getattrにより実行結果を取得
            values = getattr(self, parameter_name)()
        except AttributeError:
            # 存在しないパラメータを指定した場合
            print("no paramenter: " + parameter_name)
            values = None
        except Exception as e:
            # パラメータクラスの実装や，使用しているカメラで
            # 使用できないパラメータを実装している場合
            print("="*20)
            print("error")
            print(e)
            print("="*20)
            values = e
        return values

    def define_parameters(self, param_defs, *args, **kwargs):
        """
        パラメータ定義用メソッド．
        カメラ固有クラスで定義するEnum型のパラメータクラスを受け取り，
        自動でパラメータ定義を行うメソッド．
        必ずカメラが定義された後に呼ばれなければならない．

        setter，getterの自動定義を行うために自作のデコレータを使用している．
        そのためpythonの引数をとるデコレータについての知識，プロパティの動的
        定義への理解が必要となるため完全に理解することは非推奨．
        デコレータの詳細はdefine_properties.pyのdef define_properties参照．

        Args
        --------------------------------------
        param_defs: Enum
            カメラ固有のパラメータを定義したEnum型のクラス．
        *args: list
            現状使用せず．
        **kwargs: dict
            現状使用せず．
            用途としては各パラメータの初期値を手動で定義したい場合に
            追加実装することで可能になる．

        """
        def is_not_pt(x):
            """
            数カ所使用する正規表現を用いた判定式．
            filterの条件式としても使用したいため関数化．
            列挙されたパラメータのうち，"_pt_"で始まるパラメータは
            定義から除外するための関数．

            """
            return re.search(r"^_pt_", x) is None

        # setter，getter定義用デコレータで使用するリスト作成
        # Enum型のparameter_defsのうち，名前が_pt_で始まっていないもののみ
        # 定義を行うためにfilterを使用
        self.__parameter_list = list(filter(
            lambda x: is_not_pt(x), [param.name for param in param_defs]
        ))

        # setter，getter定義用デコレータ
        @define_properties(self.__parameter_list)
        def def_params(self, *args, **kwargs):
            """
            この関数が呼ばれることでパラメータが定義される．

            Args
            ---------------------------------
            self: クラスオブジェクト
                パラメータをプライベートなインスタンス変数として定義する
                ために必要．
            *args: list
                現状使用せず．
            **kwargs: dict
                現状使用せず．
                用途としては各パラメータの初期値を手動で定義したい場合に
                追加実装することで可能になる．

            Returns
            ---------------------------------
            kwargs: dict
                kwargs[パラメータ名] = パラメータクラスのオブジェクト

            """
            i = -1
            # 列挙されている_pt_で始まらないパラメータについて，
            # パラメータクラスのインスタンスとして定義したい．
            # そのためにkwargs[パラメータ名]にパラメータクラスのインスタンスを
            # 与えて，return kwargsでデコレータにその情報を渡す．
            for i, parameter in enumerate(param_defs):
                if is_not_pt(parameter.name):
                    kwargs[parameter.name] = parameter.value(self.camera)
            # 与えられたEnum型が空の場合，エラーで終了．
            # パラメータがないカメラの場合，このメソッドを呼ばないことで対応．
            if i == -1:
                print("Please implement ParameteDefinitions(Enum)")
                import sys
                sys.exit()
            return kwargs

        # デコレータされたパラメータ定義関数を実行
        def_params(self, *args, **kwargs)
        return None

    @property
    def parameter_names(self):
        """
        定義済みのパラメータ名のリストを返すgetter．

        Returns
        ---------------------------------
        self.__parameter_list: list of str
            パラメータ名のリスト

        """
        return self.__parameter_list


class BaseParameter(metaclass=ABCMeta):
    """
    パラメータ基本クラス．
    各ライブラリ用のパラメータクラスはこれを継承して作成する．

    Methods
    -----------------------------------
    __call__(value: any, default NoParameterValue) -> dict or None
        パラメータクラスのgetter，setterをカメラクラスから適切に
        操作するために実装．
        カメラクラスと併せてもっと適切な実装はあるかも．

    get_max_value() -> NotImplementedError
        抽象メソッド．
        パラメータの設定可能な最大値を取得するためのメソッド．

    get_min_value() -> NotImplementedError
        抽象メソッド．
        パラメータの設定可能な最小値を取得するためのメソッド．

    get_now_value() -> NotImplementedError
        抽象メソッド．
        パラメータの設定可能な現在値を取得するためのメソッド．

    get_now_status() -> NotImplementedError
        現状ではパラメータの自動調整が可能かどうかを取得するメソッド．
        ただし自動調整が存在しないパラメータもあるため，抽象メソッドにはせず
        NotImplementedErrorを返す．

    @property
    @abstractmethod
    value() -> NotImplementedError
        抽象メソッド．
        パラメータ値のgetter．

    @value.setter
    @abstractmethod
    value(value: any) -> NotImplementedError
        抽象メソッド．
        パラメータ値のsetter．

    """
    def __call__(self, value=NoParameterValue()):
        """
        パラメータクラスのgetter，setterをカメラクラスから適切に
        操作するために実装．
        カメラクラスと併せてもっと適切な実装はあるかも．

        Args
        --------------------------
        value: any, default NoParameteValue
            パラメータに設定したい値．
            デフォルト値のNoParameterValueの場合はgetter，そうでない場合は
            setterを呼び出す．

        Returns
        ---------------------------
        self.value or None: dict or None
            getterの場合はself.value: dict，
            setterの場合はNone

        """
        # valueがデフォルト値の場合はgetterを呼ぶ
        if isinstance(value, NoParameterValue):
            return self.value
        # valueに値が与えられている場合はsetterを呼ぶ．
        else:
            self.value = value
            return None

    @abstractmethod
    def get_max_value(self):
        """
        抽象メソッド．
        パラメータの設定可能な最大値を取得するためのメソッド．

        """
        raise NotImplementedError

    @abstractmethod
    def get_min_value(self):
        """
        抽象メソッド．
        パラメータの設定可能な最小値を取得するためのメソッド．

        """
        raise NotImplementedError

    @abstractmethod
    def get_now_value(self):
        """
        抽象メソッド．
        パラメータの現在値を取得するためのメソッド．

        """
        raise NotImplementedError

    def get_now_status(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def value(self):
        """
        抽象メソッド．
        パラメータ値のgetter．

        """
        raise NotImplementedError

    @value.setter
    @abstractmethod
    def value(self, value):
        """
        抽象メソッド．
        パラメータ値のsetter．

        Args
        ------------------
        value: any
            パラメータの設定値

        """
        raise NotImplementedError


class MakeMessage:
    """
    警告等のメッセージ作成クラス．


    Methods
    ------------------------
    @staticmethod
    cannot_change_value(target: str) -> str
        自動調整が有効で値を変更できない場合のメッセージ作成を行う
        staticmethod．

    """
    @staticmethod
    def cannot_change_value(target):
        """
        自動調整が有効で値を変更できない場合のメッセージ作成を行う
        staticmethod．

        Args
        -------------------
        target: str
            対象としたいパラメータ名．
            (例)
            "オートフォーカス"

        Returns
        -------------------
        msg: str
            作成した警告メッセージ
            (例)
            "WARNNG: オートフォーカスが有効のため値を変更できません"

        """
        msg = "WARNING: " + target + "が有効のため値を変更できません"
        return msg


class PrintMessage:
    """
    警告等のメッセージ出力クラス．
    MakeMessageクラスと組み合わせて標準出力にメッセージを出力する．


    Methods
    ------------------------
    @staticmethod
    cannot_change_value(target: str) -> None
        自動調整が有効で値を変更できない場合のメッセージをMakeMessageクラスの
        cannot_change_valueメソッドで行い，作成されたメッセージをprint文で
        出力するstaticmethod．

    """
    @staticmethod
    def cannot_change_value(target):
        """
        自動調整が有効で値を変更できない場合のメッセージを標準出力に出力する
        staticmethod．
        (出力例)
        <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
        "WARNNG: オートフォーカスが有効のため値を変更できません"
        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        Args
        -------------------
        target: str
            対象としたいパラメータ名．
            (例)
            "オートフォーカス"


        """
        # メッセージ作成
        msg = MakeMessage.cannot_change_value(target)
        # メッセージ出力
        print("<"*30)
        print(msg)
        print(">"*30)
        return None
