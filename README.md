# Multi-thread chamber
マルチスレッドでパイプライン処理を行うためのフレームワーク

イントロ
=======================================================
このソフトウェアは、専用のスクリプト「ChamberLang」を利用することで、テキストやオブジェクト列に対してパイプライン処理を行うことをサポートします。
まず、簡単な例を見てみましょう。

    Read:file="./input" > inputdata
    Write:file="./output" < inputdata

このコードを``./example-code`` の名前で保存しておきます。
また、適当な行数を持ったテキストファイル ``./input`` も用意しておきましょう。
プログラムを実行するには

    $ mt-chamber < ./example-code

これを実行すると、 ``./input`` と同一の内容の ``./output`` が生成されます。

このスクリプトは以下の解釈ができます。

1. ``Read`` コマンドによって ``./input`` の内容を一行ずつ読み込み、変数 ``inputdata`` に出力する。
2. ``Write`` コマンドによって ``inputdata`` の内容を一行ずつ ``./output`` に書き出す。

ChamberLang
=======================================================

ChamberLang の基本
-------------------------------------------------------

ChamberLang の一行は、基本的にコマンド、コマンドのオプション、入力、出力から成っています。

    コマンド:オプション:オプション... < 入力 > 出力

入力や出力はコマンドに対して1個である必要はありません。コマンドによっては入力または出力がない場合もありますし、複数の入出力を受ける場合もあります。
オプションは ``オプション名=値`` の形式で記述し、複数のオプションを指定する場合は ``:`` で区切ります。
オプション名のみを記述した場合は、自動的に ``オプション名=True`` として解釈されます。

``plugins`` に含まれる ``LengthCleaner`` コマンドを利用する例を以下に示します。

    Read:file="./en.tok" > en_tok
    Read:file="./ja.tok" > ja_tok
    LengthCleaner:maxlen1=80:maxlen2=80 < en_tok ja_tok > en_clean ja_clean
    Write:file="./en.clean" < en_clean
    Write:file="./ja.clean" < ja_clean

この例では、行ごとに対応した2つのファイル ``./en.tok`` と ``./ja.tok`` を読み込み、各行の単語数が80より多ければ、両方のファイルから該当する行を除去します。

エイリアス
-------------------------------------------------------

オプションが長くなる場合、それをスクリプトの中に書いてしまうと可読性が低くなります。
その問題を回避するために、ChamberLang には ``Alias`` と呼ばれるコマンドがあります。
Alias を利用することで、長いコマンドを別の名前で置き換えることができます。

    Alias MyCleaner LengthCleaner:maxlen1=80,maxlen2=80
    MyCleaner < en_tok ja_tok > en_clean ja_clean

Alias は C の ``#define`` によく似ています。定義されたすべての別名は、スクリプトの解釈前に置換されます（プリプロセス）。

より複雑な書き方
-------------------------------------------------------

コマンドに対する入出力を指定する際、それぞれの入出力を複数の ``<`` や ``>`` によって分割して指定できます。
例えば

    LengthCleaner:maxlen1=80:maxlen2=80 < en_tok ja_tok > en_clean ja_clean

を書き換えると

    LengthCleaner:maxlen1=80:maxlen2=80 < en_tok < ja_tok > en_clean ja_clean

更に、オプションの位置はコマンドの直後である必要は無いため

    LengthCleaner:maxlen1=80 < en_tok :maxlen2=80 < ja_tok > en_clean ja_clean

読むのが難しくなりました。では、Alias の #define とよく似た機能を活用してみましょう。

    Alias MyCleaner LengthCleaner:maxlen1=80 < en_tok 
    MyCleaner:maxlen2=80 < ja_tok > en_clean_with_ja ja_clean
    MyCleaner:maxlen2=70 < zh_tok > en_clean_with_zh zh_clean

何をしたか分かりましたか？
この例では、 ``Alias`` を使うことでスクリプトの一部 ``LengthCleaner:maxlen1=80 < en_tok`` を置き換えました。これにより、1つ目の入力とオプションだけは固定し、残りのオプションと入力を自由に変えられる「コマンドのようなもの」を定義したことになります。

Pythonを使ったコマンドの定義
=======================================================

では、Pythonを使ったより柔軟なコマンドの定義方法を見て行きましょう。

新しいコマンドを定義するには、 ``plugins`` 下にPythonのファイルを設置します。
まず、コマンドを定義するためのファイルを ``plugins/コマンド.py`` に設置します。
このファイルでは、以下のような ``Command`` クラスを定義します。

    class Command:

        # 設定変数
        InputSize = 1
        OutputSize = 1
        MultiThreadable = True
        ShareResources = False

        def __init__(self, options...):
            ::::

        def routine(self, instream):
            ::::

設定変数の意味は次のとおりです。

* **InputSize:** 入力タプルのサイズ。
* **OutputSize:** 出力タプルのサイズ。
* **MultiThreadable:** コマンドを並列処理できる場合は ``True``。ファイルの読み書きのように、マルチスレッド化が困難な場合は ``False`` に設定します。
* **ShareResources:** スコープをスレッド間で共有する場合は ``True``。スコープを共有すると、スレッド間で変数の使い回しが可能になります。それぞれのスレッドを独立に実行したい場合は ``False`` に設定します。

``Command`` クラスでは、最低限 ``__init__`` 関数と ``routine`` 関数が定義されます。

* **__init__:** 初期化の段階で呼び出されます。この関数では ``options...`` の内容に従ってクラスの初期化を行います。 ``ShareResources`` が ``True`` の場合は全体で1回のみ実行され、 ``False`` の場合はスレッドごとに1回呼び出されます。 ``options...`` では、コマンドのオプションを関数の引数として定義します。
* **routine:** コマンドがデータを受け取った際に呼び出されます。 ``instream`` 引数には入力データがタプルとして格納されます。処理が終わったら出力データをタプルとして返します。タプルの代わりに ``None`` を返した場合、処理が終了します。また、これによって以降のコマンドも連鎖的に終了します。
