from abc import ABCMeta, abstractmethod
from .define_properties import define_properties


"""
Compositeパターンでパラメータ関連の共通クラスを実装．

BaseParameter:
CommonParameter:
CommonParameterManager:

(依存ライブラリ)


"""

__author__ = "LiNKX"
__copyright__ = "Copyright 2020, LiNKX Inc,"
__credits__ = ["Toshiki Kozuka"]
__license__ = "***************UNDEFINED***************"
__version__ = "0.1.0"
__maintainer__ = "Toshiki Kozuka"
__email__ = "kozuka@linkx.dev"
__status__ = "Dev"
__data__ = "2020/10/26"


class EmptyValue:
    """
    デフォルト引数として与えるクラス．
    ""やNoneを引数として与えたい場合を考慮して作成．
    使い回せばいいのでシングルトンで作成．

    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(EmptyValue, cls).__new__(cls)
        return cls._instance



class BaseParameter(metaclass=ABCMeta):
    """


    """
    def add_parameter(self, param_name, init_value=EmptyValue()):
        """
        ParameterManagerクラスのみで具体的な実装を行う．

        """
        raise NotImplementedError

    @abstractmethod
    def get_parameter(self, param_name):
        """
        パタメータ取得メソッド．
        ParameterManagerではparam_nameで指定されたパラメータの
        get_parameter，Parameterではgetterを実行する．
        Parameterのgetterは次のtupleを返す．
            (最小，現在値，最大，自動機能オン(bool))

        """
        raise NotImplementedError

    @abstractmethod
    def set_parameter(self, param_name, set_value=EmptyValue()):
        """
        パラメータ変更メソッド．
        ParameterManagerではparam_nameで指定されたパラメータの
        set_parameter，Parameterではsetterを実行する．

        """
        raise NotImplementedError


class EmptyParameter(BaseParameter):
    """
    未定義パラメータに対応するクラス．
    処理を共通化するために作成．
    使い回せばいいのでシングルトンで作成．

    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(EmptyValue, cls).__new__(cls)
        return cls._instance


class CommonParameter(metaclass=ABCMeta):
    """


    """
    def _add_parameter(self, param_name, init_value=EmptyParameter()):
        """
        単体のパラメータ追加メソッド．
        カメラ固有のパラメータまとめクラスのインスタンス生成時に
        全てのパラメータに対して

        """

        @define_properties(param_name)
        def set_private_value(self, *args, **kwargs):
            return kwargs

        kwargs = {}
        if isinstance(init_value, EmptyValue) is False:
            kwargs[param_name] = init_value
        set_private_value(self, **kwargs)
        return None


class CommonParameterManager(metaclass=ABCMeta):
    """


    """

