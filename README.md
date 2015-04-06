# Multi-thread chamber
マルチスレッドでパイプライン処理を行うためのフレームワーク

イントロ
=======================================================
このソフトウェアは、専用のスクリプト「ChamberLang」を利用することで、テキストやオブジェクト列に対してパイプライン処理を行うことをサポートします。
まず、簡単な例を見てみましょう::

    Read:file="./input" > inputdata
    Write:file="./output" < inputdata

このコードを``./example-code`` の名前で保存しておきます。
また、適当な行数を持ったテキストファイル ``./input`` も用意しておきましょう。
プログラムを実行するには::

    $ mt-chamber < ./example-code

これを実行すると、 ``./input`` と同一の内容の ``./output`` が生成されます。

このスクリプトは以下の解釈ができます

1. ``Read`` コマンドによって ``./input`` の内容を一行ずつ読み込み、変数 ``inputdata`` に出力する。
2. ``Write`` コマンドによって ``inputdata`` の内容を一行ずつ ``./output`` に書き出す。

ChamberLang
=======================================================

ChamberLang の基本
-------------------------------------------------------

ChamberLang の一行は、基本的にコマンド、コマンドのオプション、入力、出力からなっています。

    コマンド:オプション:オプション... < 入力 > 出力

入力や出力はコマンドに対して1個である必要はありません。コマンドによってはない場合もありますし、複数の入力を受ける場合もあります。
オプションは ``オプション名=値`` の形式で記述し、複数のオプションを指定する場合は ``:`` で区切ります。
オプション名のみ記述した場合は、自動的に ``オプション名=True`` として解釈されます。

``plugins`` に含まれる ``LengthCleaner`` コマンドを利用する場合は以下のようになります。

    Read:file="./en.tok" > en_tok
    Read:file="./ja.tok" > ja_tok
    LengthCleaner:maxlen1=80:maxlen2=80 < en_tok ja_tok > en_clean ja_clean
    Write:file="./en.clean" < en_clean
    Write:file="./ja.clean" < ja_clean

この例では、行ごとに対応した2つのファイル ``./en.tok`` と ``./ja.tok`` を読み込み、各行の単語数が80より多ければ除去します。

エイリアス
-------------------------------------------------------

オプションが長くなる場合、スクリプトの中に書いてしまうとスクリプトが読みにくくなります。
そのような場合のために、ChamberLang には ``Alias`` コマンドがあります。
Alias を利用することで、長いコマンドを別の名前で置き換えることができます。

    Alias MyCleaner LengthCleaner:maxlen1=80,maxlen2=80
    MyCleaner < en_tok ja_tok > en_clean ja_clean

Alias は C の ``#define`` によく似ています。すべての別名はスクリプトの解釈前に置換されます。

より複雑な書き方
-------------------------------------------------------

コマンドに対する入出力を指定する際、それぞれの入出力を複数の ``<`` や ``>`` を使って指定できます。

    LengthCleaner:maxlen1=80:maxlen2=80 < en_tok < ja_tok > en_clean ja_clean

更に、オプションの位置はコマンドの直後である必要はありません。

    LengthCleaner:maxlen1=80 < en_tok :maxlen2=80 < ja_tok > en_clean ja_clean

読むのが難しくなりました。では、Alias の #define とよく似た機能（プリプロセス）を活用してみましょう。

    Alias MyCleaner LengthCleaner:maxlen1=80 < en_tok 
    MyCleaner:maxlen2=80 < ja_tok > en_clean_with_ja ja_clean
    MyCleaner:maxlen2=70 < zh_tok > en_clean_with_zh zh_clean

何をしたか分かりましたか？
この例では、 ``Alias`` を使うことでスクリプトの一部 ``LengthCleaner:maxlen1=80 < en_tok`` を置き換えました。これにより、１つ目の入力とオプションだけは固定し、残りのオプションと入力を自由に変えられるコマンドのようなものを定義したことになります。

Pythonを使ったコマンドの定義
=======================================================


