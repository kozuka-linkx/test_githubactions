"""
getter，setter定義関数と，それを呼び出すデコレータで構成．

setter，getterで別の処理をしたい場合は定義関数内の関数を
適切な処理に変更し，対応するデコレータを作成してそれを
使用する．

<実装済みの定義関数>
    define_basic:
        フラグに応じて通常のgetter，setterもしくはwarning_**を定義する．

    define_numpy:
        初期値がlist，tupleの場合はndarray形式で初期化する．

    define_multiprocessing:
        排他制御が必要なマルチプロセス使用する．
        排他制御のためのmultiprocessing.Lock()を
        lockというキーワード引数で受け取って使用する．

    define_manager:
        変数を管理する管理クラスのプライベート変数を経由して値を読み取る
        場合に使用する．
        1つの管理クラスに対して複数のクラスが変数を読み取る場合に使用する．
        管理クラス自体はマルチプロセス/スレッドでも良いが，ここで並列に
        扱うクラスは多くともどれか1つのみが稼働している，という状態を
        想定する．

"""
import re


# =====================================================================
# ----------------------- ダミークラス，関数など -----------------------
class DummyLock:
    """
    マルチプロセス，マルチスレッドのLockのダミークラス．
    デフォルト値で使用するが，使用時はちゃんと宣言したものを使う．

    ダミー動作としてacquire及びreleaseは定義する．

    """
    def __init__(self):
        pass

    def acquire(self):
        """
        lock.acquire()のダミー

        """
        pass

    def release(self):
        """
        lock.release()のダミー

        """
        pass


class DummyManager:
    """
    変数管理のマネージャークラスのダミークラス．
    デフォルト値で使用するが，使用時はちゃんと宣言したものを使う．

    ダミー動作として__getattribute__をオーバーライドして
    対象によらずNoneを返す．

    """
    def __init__(self):
        pass

    def __getattribute__(self, name):
        """
        任意の変数名に対してNoneを返す

        Args
        --------------
        name: str
            なんでも

        """
        return None


def warning_getter_main(name):
    """
    読み込み不可で定義された場合のgetter動作を定義したデコレータ．
    固有の処理がなければこれで装飾するだけ．

    """
    def decorator_warning_getter(f):
        def wrapper_warning_getter(self):
            """
            is_readableがFalseの場合のgetterの定義．
            メッセージ出力のみ
            
            """
            print("="*20 + " WARNING " + "="*20)
            print("変数:<{}>は読み取れません".format(name))
            print("="*20 + "=========" + "="*20)
        return wrapper_warning_getter
    return decorator_warning_getter


def warning_setter_main(name):
    """
    書き込み不可で定義された場合のsetter動作を定義したデコレータ．
    固有の処理がなければこれで装飾するだけ．

    """
    def decorator_warning_setter(f):
        def wrapper_warning_setter(self, value):
            """
            is_writableがFalseの場合のgetterの定義
            メッセージ出力のみ
            
            """
            print("="*20 + " WARNING " + "="*20)
            print("変数:<{}>は書き込めません".format(name))
            print("="*20 + "=========" + "="*20)
        return wrapper_warning_setter
    return decorator_warning_setter


def compare_string_bytes(func_name):
    func = None
    # utf-8の文字コードに変換，文字ごとに配列要素にして
    # 10進数に変換した値の差分をとって，同じ文字列長の
    # もののうち違いが1文字のものを探す．
    f_byte = bytearray(func_name.encode("utf-8"))
    f_length = len(f_byte)
    for i, d in enumerate(DEFINES_BYTES):
        if f_length == len(d):
            count = 0
            for t1, t2 in zip(f_byte, d):
                if abs(t1 - t2) != 0:
                    count += 1
            if count < 2:
                maybe = DEFINES_STR[i]
                func = getattr(DefinePrivateValiable, maybe)
                print("maybe " + func_name + " is typo of " + maybe)
                print("try to use " + maybe)
                break
        else:
            continue
    return func


def define_properties(*names):
    """
    デコレータ自体の引数として定義するプライベート変数の名前のリストを受け取り，
    関数自体の引数としてデフォルト値とフラグ，使用する定義作成関数を受け取る．

    どんなgetter，setterでもこのデコレータを経由して定義する．
    変数funcで具体的なgetter，setterが定義された関数を指定する．

    Args
    -----------------
    *names: list of str
        定義するプライベート変数の名前のリスト．
        リストでなくても一応動作はする．

    """
    def decorator(f):
        """
        装飾された関数の動作．

        Args
        ------------------
        f: function
            装飾された関数．
            直接引数としては記述しない．

        """
        def wrapper(self, *args, **kwargs):
            """
            装飾された関数実行時にのラッパー関数．
            getter，setter定義用の関数と想定しているが，最後でf(self, **kwargs)と
            して元の関数を呼び出しているため，装飾元の関数で処理をしたければ
            そちらに実装する．

            Args
            ----------------
            self:

            **kwargs: dict of private valiables
                プライベート変数の初期値や，変数のフラグ情報．
                getter，setterの定義方法に応じた関数名も含む．

            """
            kwargs = f(self, **kwargs)
            # namesをlist，tupleでも羅列した形式でも実行可能にするため
            # ここで分析して形式を整える．
            if len(names) == 1 and isinstance(names[0], (tuple, list)):
                targets = names[0]
            else:
                targets = names
            # 読み込み可否
            #   : 定義されていればその値
            #     未定義であればTrue
            is_readable = kwargs.pop("is_readable", True)
            # 書き込み可否
            #   : 定義されていればその値
            #     未定義であればTrue
            is_writable = kwargs.pop("is_writable", True)
            # 初期化の可否
            #   : 定義されていればその値
            #     未定義であればTrue
            is_initialize = kwargs.pop("is_initialize", True)
            # getter，setterの定義方法
            #   : 適切な定義用関数を選ぶ．
            #     引数は文字列で受け取る．
            #     未定義であれば変数DEFAULT_DEFINITIONを呼ぶ．
            _func = kwargs.pop("func", DEFAULT_DEFINITION)
            # 関数名が存在しない場合でも1文字のタイポまでは許容するため，
            # try-exceptで対応する．
            #   -> 命名規則をきちんとしておかないとわけがわからなくなる，
            #      グローバル変数を定義しなければならないためないほうが
            #      いいかもしれない．
            try:
                func = getattr(DefinePrivateValiable, _func)
            except AttributeError as e:
                print(e)
                # 極めて似た関数名がないか確認する．
                func = compare_string_bytes(_func)
                if func is None:
                    raise ValueError

            # list(or tuple)形式で整えられた変数名に対して
            # for文で順にgetter，setterを定義
            for target in targets:
                # getter，setterを定義する．
                # 変数名，デフォルト値，各フラグは常に引数としてもっておき，
                # 各関数固有の引数は**kwargsで渡す．
                func(
                    self, target, value=kwargs.pop(target, None),
                    is_readable=is_readable, is_writable=is_writable,
                    is_initialize=is_initialize, **kwargs
                )
            # 呼び出し元の関数を実行する．
            f(self, **kwargs)
        return wrapper
    return decorator


class DefinePrivateValiable:
    """
    実行元では文字列で指定して実行するためにクラスにstaticmethodで
    個別の実装関数を全て実装しておく．
    define_propertiesはgetattrを使って文字列からこのクラスのメソッドを呼ぶ．

    クラスメソッドの場合，デコレータだとインスタンスがどこまで残るか不明，
    特にクラスメソッドにする必要がないため全てstaticmethodで定義．

    """
    # =====================================================================
    # ------------------getter，setter定義関数-----------------------------
    # 通常の変数用．
    # デフォルト値では読み書き可．
    @staticmethod
    def define_basic(self, target, value=None, is_writable=True,
                     is_readable=True, is_initialize=True, **kwargs):
        """
        getter，setter定義関数．
        基本デコレータdefine_propertiesで複数の
        変数にgetter，setterを定義することを想定する．
        is_writable，is_readableでgetter，setterの定義仕方を決める．

        Args
        ------------------
        target: str
            プライベート変数名
        value: any
            nameの初期値．
            is_initializeがTrueの場合だけこの値で初期化する．

        is_writable: bool
            nameを書き換え可な値にするかどうか．
        is_readable: bool
            nameを読み込み可な値にするかどうか．
        is_initialize: bool
            nameをvalueで初期化するかどうか．
            Falseの場合，値書き込み前に読み込もうとするとエラー．

        **kwargs: dict
            固有の引数はないため，実装上の都合で．

        """
        # プライベート変数のプログラム上での名前を作成．
        # "_クラス名__変数名"
        field_name = "_{}__{}".format(self.__class__.__name__, target)

        # 初期化する場合にはsetattrでvalueに初期化
        if is_initialize is True:
            setattr(self, field_name, value)

        def getter(self):
            """
            getterの定義
            getattrで値取得

            """
            return getattr(self, field_name)

        def setter(self, value):
            """
            setterの定義
            setattrで値代入

            Args
            ----------------
            value: any
                代入する値

            """
            setattr(self, field_name, value)
            return None

        @warning_getter_main(target)
        def warning_getter(self):
            """
            is_readableがFalseの場合，
            共通の処理warning_getter_mainを実行

            """
            return None

        @warning_setter_main(target)
        def warning_setter(self, value):
            """
            is_writableがFalseの場合，
            共通の処理warning_setter_mainを実行

            """
            return None

        # is_writableとis_readableの組み合わせで4通りに分岐する．
        # またsetattrの注意としてproperty内はgetter->setterの順で記載すること．
        # propertyの引数が1つ目がgetter，2つ目がキーワード引数でsetterで
        # 定義されているため基本はgetter，setterの順で呼ぶ．
        # is_readable is_writable
        #     True        True    ->    getter         setter
        #     True        False   -> warning_getter    setter
        #     False       True    ->    getter      warning_setter
        #     False       False   -> エラーメッセージを出力
        #                            (raise ValueErrorとかでもいいかも)
        if (is_writable and is_readable) is True:
            setattr(self.__class__, target,
                    property(getter, setter))
        elif is_readable is True:
            setattr(self.__class__, target,
                    property(getter, warning_setter))
        elif is_writable is True:
            setattr(self.__class__, target,
                    property(warning_getter, setter))
        else:
            print("Please set make_setter or make_getter")
        return None

    @staticmethod
    def define_numpy(self, name, value=None, is_writable=True,
                     is_readable=True, is_initialize=True, **kwargs):
        """
        初期値やsetterの値がlist，tupleの場合ndarrayに変換して適用する．
        主に設定ファイルの読み込みのような外部ファイルの値取り込みなどに使用．

        Args
        ------------------
        name: str
            プライベート変数名
        value: any
            nameの初期値．
            これがlist，tupleの場合はndarrayで初期化

        is_writable: bool
            nameを書き換え可な値にするかどうか．
        is_readable: bool
            nameを読み込み可な値にするかどうか．
        is_initialize: bool
            nameをvalueで初期化するかどうか．
            Falseの場合，値書き込み前に読み込もうとするとエラー．

        **kwargs: dict
            固有の引数はないため，実装上の都合で．

        """
        # プライベート変数のプログラム上での名前を作成．
        # "_クラス名__変数名"
        field_name = "_{}__{}".format(self.__class__.__name__, name)

        # 初期化する場合にはsetattrでvalueに初期化
        # ただしlist，tupleの場合はnumpyで．
        if isinstance(value, (list, tuple)):
            # imoprt numpy as npどうする?
            import numpy as np
            setattr(self, field_name, np.array(value))
        else:
            setattr(self, field_name, value)

        def getter(self):
            """
            getterの定義
            getattrで値取得

            """
            return getattr(self, field_name)

        def setter(self, value):
            """
            setterの定義
            setattrで値代入

            Args
            ----------------
            value: any
                代入する値
                これがlist，tupleの場合はndarrayで初期化

            """
            if isinstance(value, (list, tuple)):
                value = np.array(value)
            setattr(self, field_name, value)
            return None

        @warning_getter_main(name)
        def warning_getter(self):
            """
            is_readableがFalseの場合，
            共通の処理warning_getter_mainを実行

            """
            return None

        @warning_setter_main(name)
        def warning_setter(self, value):
            """
            is_writableがFalseの場合，
            共通の処理warning_setter_mainを実行

            """
            return None

        # 各種フラグ不要だと思っていたときは次のsetattrのみでやってた
        # setattr(self.__class__, name, property(getter))

        # is_writableとis_readableの組み合わせで4通りに分岐する．
        # またsetattrの注意としてproperty内はgetter->setterの順で記載すること．
        # propertyの引数が1つ目がgetter，2つ目がキーワード引数でsetterで
        # 定義されているため基本はgetter，setterの順で呼ぶ．
        # is_readable is_writable
        #     True        True    ->    getter         setter
        #     True        False   -> warning_getter    setter
        #     False       True    ->    getter      warning_setter
        #     False       False   -> エラーメッセージを出力
        if (is_writable and is_readable) is True:
            setattr(self.__class__, name,
                    property(getter, setter))
        elif is_readable is True:
            setattr(self.__class__, name,
                    property(getter, warning_setter))
        elif is_writable is True:
            setattr(self.__class__, name,
                    property(warning_getter, setter))
        else:
            print("Please set make_setter or make_getter")
        return None

    @staticmethod
    def define_multiprocessing(self, name, lock=DummyLock(), value=None,
                               is_writable=True, is_readable=True,
                               is_initialize=True, **kwargs):
        """
        multiprocessing使用時に使用する．
        排他制御を行いつつgetter，setterを行う．

        Args
        ------------------
        name: str
            プライベート変数名
        lock: multiprocessing.Lock() or threading.Lock()
            排他制御用のオブジェクト
        value: multiprocessing.Value etc
            nameの初期値．
            is_initializeがTrueの場合だけこの値で初期化する．

        is_writable: bool
            nameを書き換え可な値にするかどうか．
        is_readable: bool
            nameを読み込み可な値にするかどうか．
        is_initialize: bool
            nameをvalueで初期化するかどうか．
            Falseの場合，値書き込み前に読み込もうとするとエラー．

        **kwargs: dict
            固有の引数はないため，実装上の都合で．

        """
        # プライベート変数のプログラム上での名前を作成．
        # "_クラス名__変数名"
        field_name = "_{}__{}".format(self.__class__.__name__, name)

        # 初期化する場合にはsetattrでvalueに初期化
        if is_initialize is True:
            setattr(self, field_name, value)

        def getter(self):
            """
            getterの定義
            排他制御しつつgetattrで値取得
            また共有変数なため，valueで値を取得

            """
            lock.acquire()
            val = (getattr(self, field_name)).value
            lock.release()
            return val

        def setter(self, value):
            """
            setterの定義
            排他制御しつつ，getattrで共有変数のオブジェクトそのものを取得して
            その値へvalueを代入する．

            通常のプライベート変数と同じように扱うためには共有変数を作成する
            multiprocessing.Value等のクラスで定義されているであろうsetter，
            getterをオーバーライドする必要があると推測される．
            それ自体は呼び出し元でやらなければいけない，そもそもそこまで
            対応できるか，ということもあるためここでは無視してここで
            valueで値を直接操作することとした．

            Args
            ----------------
            value: any
                代入する値

            """
            lock.acquire()
            target = getattr(self, field_name)
            target.value = value
            lock.release()
            return None

        @warning_getter_main(name)
        def warning_getter(self):
            """
            is_readableがFalseの場合，
            共通の処理warning_getter_mainを実行

            """
            return None

        @warning_setter_main(name)
        def warning_setter(self, value):
            """
            is_writableがFalseの場合，
            共通の処理warning_setter_mainを実行

            """
            return None

        # is_writableとis_readableの組み合わせで4通りに分岐する．
        # またsetattrの注意としてproperty内はgetter->setterの順で記載すること．
        # propertyの引数が1つ目がgetter，2つ目がキーワード引数でsetterで
        # 定義されているため基本はgetter，setterの順で呼ぶ．
        # is_readable is_writable
        #     True        True    ->    getter         setter
        #     True        False   -> warning_getter    setter
        #     False       True    ->    getter      warning_setter
        #     False       False   -> エラーメッセージを出力
        if (is_writable and is_readable) is True:
            setattr(self.__class__, name,
                    property(getter, setter))
        elif is_readable is True:
            setattr(self.__class__, name,
                    property(getter, warning_setter))
        elif is_writable is True:
            setattr(self.__class__, name,
                    property(warning_getter, setter))
        else:
            setattr(self.__class__, name,
                    property(warning_getter, warning_setter))
        return None

    @staticmethod
    def define_manager(self, name, manager=DummyManager(), value=None,
                       is_writable=True, is_readable=True, is_initialize=False,
                       **kwargs):
        """
        管理クラスの変数を複数のクラスから参照にする場合に，
        そのクラスに必要な変数だけ定義するために使用する．

        Args
        ------------------
        name: str
            プライベート変数名
        manager: Object
            管理クラスのインスタンス
        value: any
            nameの初期値．
            is_initializeがTrueの場合だけこの値で初期化する．

        is_writable: bool
            nameを書き換え可な値にするかどうか．
        is_readable: bool
            nameを読み込み可な値にするかどうか．
        is_initialize: bool
            nameをvalueで初期化するかどうか．
            Falseの場合，値書き込み前に読み込もうとするとエラー．

        **kwargs: dict
            固有の引数はないため，実装上の都合で．

        """
        # 初期化する場合にはsetattrでvalueに初期化
        if is_initialize is True:
            setattr(manager, name, value)

        def getter(self):
            """
            getterの定義
            getattrで値取得

            """
            return getattr(manager, name)

        def setter(self, value):
            """
            setterの定義
            setattrで値代入

            Args
            ----------------
            value: any
                代入する値

            """
            setattr(manager, name, value)
            return None

        @warning_getter_main(name)
        def warning_getter(self):
            """
            is_readableがFalseの場合，
            共通の処理warning_getter_mainを実行

            """
            return None

        @warning_setter_main(name)
        def warning_setter(self, value):
            """
            is_writableがFalseの場合，
            共通の処理warning_setter_mainを実行

            """
            return None

        # is_writableとis_readableの組み合わせで4通りに分岐する．
        # またsetattrの注意としてproperty内はgetter->setterの順で記載すること．
        # propertyの引数が1つ目がgetter，2つ目がキーワード引数でsetterで
        # 定義されているため基本はgetter，setterの順で呼ぶ．
        # is_readable is_writable
        #     True        True    ->    getter         setter
        #     True        False   -> warning_getter    setter
        #     False       True    ->    getter      warning_setter
        #     False       False   -> エラーメッセージを出力
        if (is_writable and is_readable) is True:
            setattr(self.__class__, name,
                    property(getter, setter))
        elif is_readable is True:
            setattr(self.__class__, name,
                    property(getter, warning_setter))
        elif is_writable is True:
            setattr(self.__class__, name,
                    property(warning_getter, setter))
        else:
            setattr(self.__class__, name,
                    property(warning_getter, warning_setter))
        return None


# 関数名比較のための準備．
# 比較してタイポ検出が不要ならばここの定義は必要なし．
DEFINES_STR = []
DEFINES_BYTES = []
for d in dir(DefinePrivateValiable):
    if re.search(r"^(?!__)", d):
        DEFINES_STR.append(d)
        DEFINES_BYTES.append(bytearray(d.encode("utf-8")))
DEFAULT_DEFINITION = "define_basic"


class Test:
    def __init__(self, **kwargs):
        self.AA = 100
        kwargs['func'] = "define_basic"
        self.print_num(**kwargs)
        return None

    @define_properties('test')
    def print_num(self, **kwargs):
        # print("print_num: " + str(kwargs.get("num", False)))
        print("print_num")
        return None

    def ppp(self):
        print("called getattr")
        return None


if __name__ == "__main__":
    # t = Test(test=200, is_writable=False)
    t = Test(test=200)
    print(t.test)
    t.test = -1
    temp = getattr(t, "ppp")
    temp()
    print("<"*30 + " [all defined functions] " + ">"*30)
    print(DEFINES_STR)

    a = DummyManager()
    print(a.a)
