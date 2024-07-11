# pdexample

## DataFrame の行ごとの値を参照する繰り返し処理

DataFrame の行ごとの値を参照する繰り返し処理を行う方法は複数あるが、適切な方法を選ばないと処理が非常に遅くなることがある。そこで、選択可能な方法それぞれについて実装例を作成し、処理速度を比較した。

1. DataFrame の 対象列を抜き出して zip で結合して処理を行う
2. DataFrame の itertuples メソッドを使う
3. DataFrame の to_numpy メソッドまたは values 属性を使う
4. DataFrame を dict に変換して処理を行い結果のリストを作成、繰り返し終了後にDataFrameにカラム追加
5. DataFrame を dict に変換して処理を行い結果を辞書に追加、繰り返し終了後に辞書をDataFrameに変換
6. DataFrame の apply メソッドを使う
7. DataFrame の iterrows メソッドを使う

上記の 1〜7 は、処理時間が短いに昇順に並んでいる。1 が最も処理時間が短く、7 が最も長い。

## まとめ

DataFrame の行ごとの値を参照して繰り返し処理を行うときに処理時間を短くするために気を付けること

1. DataFrame の対象列を抜き出して zip で結合して行ごとの処理を行う方法が最も高速。
2. itertuples を name=None オプションで使うと比較的高速。
3. for文よりもリスト内包表記をできるだけ使う。
4. DataFrame と 辞書のリスト形式の相互変換は時間がかかるので避ける。
5. apply を使うと遅い。
6. iterrows はものすごく遅いのでむしろ使わないほうがよい。


わかったこと

- DataFrame から 辞書のリストに変換して行ごとに繰り返す処理は zip で結合して処理するよりも 2倍の時間がかかる。
- pd.DataFrame() を使って辞書のリストを DataFrame に変換する処理は、DataFrame に列を追加する処理に比べて 30% 増の時間がかかる。
- pd.DataFrame.from_dict を使って辞書のリストを DataFrame に変換する処理にかかる時間は、pd.DataFrame() を使う場合と同等。
- itertuples メソッドは name=None オプションを用いると 30% 程度早くなる。zip で結合して処理するよりも 10% 増の時間がかかる程度で、比較的速い。
- itertuples メソッドは name=None オプションを用いないと zip で結合して処理するよりも 70% 増の時間がかかる。 
- to_numpy メソッドを使うと、zip で結合して処理するよりも 50% 増の時間がかかる。
- values 属性を使う方法は 処理にかかる時間が to_numpy を使う方法と同等。pandas 公式ドキュメントでは values よりも to_numpy() を使うことが推奨されている。 
- apply メソッドを axis=1 で用いる方法は、デフォルト設定で処理すると zip で結合して処理するよりも 9.2倍 の時間がかかる。
- apply メソッドで raw=True のオプションを使うとデフォルトよりも処理時間を半分程度まで高速化できるが zip で結合して処理するよりも 4.9 倍の時間がかかる。

処理時間の分解

- #5_4_to_dict_for_dict_newdf の場合、工程を三つに分けて処理時間の比を計測する。
    - ①, ②, ③ の処理にかかる時間の割合の比  ① : ② : ③ = 23 : 21 : 56
        - ①DataFrame から to_dict で辞書のリストに変換する、
        - ②行ごとに処理して処理結果で辞書を更新する、
        - ③更新された辞書を pd.DataFrame() で DataFrame に変換する 
    - DataFrame から to_dict で辞書のリストに変換する処理が 23% を占めている。
    - 辞書を pd.DataFrame() で DataFrame に変換する処理が 56% を占めている。 
- #1_2_zip_comp_copy の場合、工程を三つに分けて処理時間の比を計測する。
    - ①, ②, ③ の処理にかかる時間の割合の比  ① : ② : ③ = 0.6 : 96.1 : 3.3
        - ①DataFrame を copy する、
        - ②DataFrame から列ごとに値を取り出して zip で結合して行ごとに処理して処理結果をリストに保持する、
        - ③DataFrame に列を追加して値をリストの値で更新する
    - DataFrame を copy するために必要な時間は zip で結合して処理する時間の 0.6% でありごくわずかな時間である。
    - DataFrame に列を追加して値を更新するためにかかる時間は zip で結合して処理する時間の 3.3% でありわずかな時間である。

## 参考

- df.iterrows() を使わないほうがよい。
    - https://stackoverflow.com/questions/16476924/how-can-i-iterate-over-rows-in-a-pandas-dataframe?rq=1

- DataFrame に対する loop を高速化
    - https://qiita.com/siruku6/items/4bd337d80d7aaceae542#2-1-to_dictorientrecords---dataframe-%E3%81%AB%E5%AF%BE%E3%81%99%E3%82%8B-loop-%E3%82%92%E9%AB%98%E9%80%9F%E5%8C%96

## 参考: 


### プログラムが遅い原因を調べる方法

- https://note.com/navitime_tech/n/nce5d5f50af95#JjjM9

### cProfile を使う

```
python -m cProfile -s tottime pdrowitermethods.py > profile.txt
```

### SnakeViz で cProfile のデータを可視化する

```
pip install snakeviz
python -m cProfile -o snakeviz.prof pdrowitermethods.py
snakeviz snakeviz.prof
```

## 実装例と実行時間の計測方法

モデルケースとして ３つの列をもつ DataFrame の各行の３つの値を使って判定を行い、４種類のクラスに分類する処理を考える。

具体的には下記の入力データを用意する。

【入力データ】

|index|colA|colB|colC|
|-----|----|----|----|
| 0   |  1 |  2 |  3 |
| 1   |  4 |  5 |  6 |
| 2   |  7 |  8 |  9 |
| 3   | 10 | 11 | 12 |
| 4   | 13 | 14 | 15 |
| 5   | 16 | 17 | 18 |

各行の各フィールドの値について、判定を行い、colR 値を作成する。

1. colA の値が 5 で割り切れれば colR の文字を A とする
2. 上記を除き、colB の値が 5 で割り切れれば colR の文字を B とする
3. 上記を除き、colC の値が 5 で割り切れれば colR の文字を C とする
4. 上記を除き、いずれの列にも 5 で割り切れる値がなければ colR の文字を N とする

判定結果の列を入力のデータフレームに追加して出力する。

【出力データ】

|index|colA|colB|colC|colR|
|-----|----|----|----|----|
| 0   |  1 |  2 |  3 | N  |
| 1   |  4 |  5 |  6 | B  |
| 2   |  7 |  8 |  9 | N  |
| 3   | 10 | 11 | 12 | A  |
| 4   | 13 | 14 | 15 | C  |
| 5   | 16 | 17 | 18 | N  |

入力データは下記の様に作成する

```python
class SampleData:
    """サンプルデータ"""

    EXAMPLE_2D_LIST = [
        ["colA", "colB", "colC"],
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [10, 11, 12],
        [13, 14, 15],
        [16, 17, 18],
    ]
```

```python
class PdRowIterMethods:

    def make_data(self, iter_num: int = 100000) -> pd.DataFrame:
        """DataFrame を作成する"""
        columns = SampleData.EXAMPLE_2D_LIST[0]
        data = []
        for i in range(iter_num):
            data += SampleData.EXAMPLE_2D_LIST[1:]
        return pd.DataFrame(columns=columns, data=data)

```

### 1. DataFrame の 対象列を抜き出して zip で結合して処理を行う

結論だけ言うと、これが最も処理時間が短い。処理工程は、下記の３段階に分解できる。

1. 与えられたデータフレームをメモリ上でそのまま参照して処理を行い、処理結果はリストに格納する。
2. 与えられたデータフレームを DataFrame.copy メソッドでコピーして戻り値のデータフレームを作成し、
3. そこに新しい列を追加している。

あとで考察するが、2 の処理はごくわずかな時間、　3 の処理はわずかな時間しか消費していないため、処理時間の大部分は 1 の処理が占める。

```python
    def iter_rows_with_zip(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - DataFrame から列を抜き出し zip で結合して処理する

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        # for文よりもリスト内包表記にしたほうが 10% 高速になる
        result = [
            PdRowIterMethods.classify(*x)
            for x in zip(df["colA"], df["colB"], df["colC"])
        ]
        df_ret = df.copy()
        df_ret["colR"] = result
        return df_ret
```

### 2. DataFrame の itertuples メソッドを使う



### 3. DataFrame の to_numpy メソッドを使う

### 4. DataFrame の values 属性を使う

### 5. DataFrame を dict に変換して処理を行い結果のリストを作成、繰り返し終了後にDataFrameにカラム追加

### 6. DataFrame を dict に変換して処理を行い結果を辞書に追加、繰り返し終了後に辞書をDataFrameに変換

### 7. DataFrame の apply メソッドを使う

### 8. DataFrame の iterrows メソッドを使う

```text
pandas version: 2.2.0
-- 1. #1_1_zip_comp_alter
df.shape (before): (600000, 3)
time_delta 1: 0.1349492073059082
time_delta 2: 0.13529610633850098
time_delta 3: 0.13814902305603027
time_delta 4: 0.1372060775756836
time_delta 5: 0.13701224327087402
time_delta_average: 0.13652253150939941
df.shape (after): (600000, 4)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 2. #1_2_zip_comp_copy
df.shape (before): (600000, 3)
time_delta 1: 0.1361992359161377
time_delta 2: 0.13821005821228027
time_delta 3: 0.13838624954223633
time_delta 4: 0.13945508003234863
time_delta 5: 0.13693904876708984
time_delta_average: 0.13783793449401854
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 3. #1_3_zip_comp_newdf
df.shape (before): (600000, 3)
time_delta 1: 0.13710403442382812
time_delta 2: 0.13925385475158691
time_delta 3: 0.13918685913085938
time_delta 4: 0.13738512992858887
time_delta 5: 0.13997316360473633
time_delta_average: 0.1385806083679199
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 4. #1_4_zip_for_copy
df.shape (before): (600000, 3)
time_delta 1: 0.14435100555419922
time_delta 2: 0.14540410041809082
time_delta 3: 0.14429593086242676
time_delta 4: 0.14346814155578613
time_delta 5: 0.14640212059020996
time_delta_average: 0.14478425979614257
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 5. #2_1_itertuples_noname_comp_copy
df.shape (before): (600000, 3)
time_delta 1: 0.1563870906829834
time_delta 2: 0.15492606163024902
time_delta 3: 0.1548750400543213
time_delta 4: 0.15903306007385254
time_delta 5: 0.1555471420288086
time_delta_average: 0.15615367889404297
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 6. #2_2_itertuples_named_comp_copy
df.shape (before): (600000, 3)
time_delta 1: 0.23888707160949707
time_delta 2: 0.23757505416870117
time_delta 3: 0.23758792877197266
time_delta 4: 0.2369070053100586
time_delta 5: 0.23753023147583008
time_delta_average: 0.23769745826721192
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 7. #3_1_to_numpy_comp_copy
df.shape (before): (600000, 3)
time_delta 1: 0.2126479148864746
time_delta 2: 0.21319890022277832
time_delta 3: 0.20970511436462402
time_delta 4: 0.20789599418640137
time_delta 5: 0.2107541561126709
time_delta_average: 0.21084041595458985
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 8. #4_1_values_comp_copy
df.shape (before): (600000, 3)
time_delta 1: 0.21399927139282227
time_delta 2: 0.21338820457458496
time_delta 3: 0.21325993537902832
time_delta 4: 0.20937299728393555
time_delta 5: 0.20795702934265137
time_delta_average: 0.2115954875946045
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 9. #5_1_to_dict_comp_copy
df.shape (before): (600000, 3)
time_delta 1: 0.28966403007507324
time_delta 2: 0.2925090789794922
time_delta 3: 0.29381823539733887
time_delta 4: 0.28738999366760254
time_delta 5: 0.28679895401000977
time_delta_average: 0.2900360584259033
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 10. #5_2_to_dict_for_copy
df.shape (before): (600000, 3)
time_delta 1: 0.2967829704284668
time_delta 2: 0.296159029006958
time_delta 3: 0.29615020751953125
time_delta 4: 0.3033299446105957
time_delta 5: 0.3001430034637451
time_delta_average: 0.29851303100585935
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 11. #5_3_to_dict_for_list_newdf
df.shape (before): (600000, 3)
time_delta 1: 0.5509228706359863
time_delta 2: 0.5431909561157227
time_delta 3: 0.5528731346130371
time_delta 4: 0.5514967441558838
time_delta 5: 0.540416955947876
time_delta_average: 0.5477801322937011
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 12. #5_4_to_dict_for_dict_newdf
df.shape (before): (600000, 3)
time_delta 1: 0.5589869022369385
time_delta 2: 0.5549652576446533
time_delta 3: 0.554602861404419
time_delta 4: 0.5549266338348389
time_delta 5: 0.5542211532592773
time_delta_average: 0.5555405616760254
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 13. #5_5_to_dict_for_dict_from_dict
df.shape (before): (600000, 3)
time_delta 1: 0.5561578273773193
time_delta 2: 0.5554251670837402
time_delta 3: 0.5554289817810059
time_delta 4: 0.5614120960235596
time_delta 5: 0.5590720176696777
time_delta_average: 0.5574992179870606
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 14. #7_1_apply_raw_copy
df.shape (before): (600000, 3)
time_delta 1: 0.6702141761779785
time_delta 2: 0.6761472225189209
time_delta 3: 0.6881179809570312
time_delta 4: 0.6922340393066406
time_delta 5: 0.6782209873199463
time_delta_average: 0.6809868812561035
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 15. #7_2_apply_default_copy
df.shape (before): (600000, 3)
time_delta 1: 1.2827341556549072
time_delta 2: 1.2827839851379395
time_delta 3: 1.272749900817871
time_delta 4: 1.2757580280303955
time_delta 5: 1.2725379467010498
time_delta_average: 1.2773128032684327
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N
-- 16. #8_1_iterrows_comp_copy
df.shape (before): (600000, 3)
time_delta 1: 7.431341171264648
time_delta 2: 7.413279056549072
time_delta 3: 7.422508955001831
time_delta 4: 7.446452856063843
time_delta 5: 7.447351694107056
time_delta_average: 7.43218674659729
df.shape (after): (600000, 3)
df_result.shape: (600000, 4)
   colA  colB  colC colR
0     1     2     3    N
1     4     5     6    B
2     7     8     9    N
3    10    11    12    A
4    13    14    15    C
5    16    17    18    N

```

```
report_df:
                                 name  timedelta_average      ratio
0                #1_1_zip_comp_alter           0.136523   0.990457
1                 #1_2_zip_comp_copy           0.137838   1.000000
2                #1_3_zip_comp_newdf           0.138581   1.005388
3                  #1_4_zip_for_copy           0.144784   1.050395
4   #2_1_itertuples_noname_comp_copy           0.156154   1.132879
5    #2_2_itertuples_named_comp_copy           0.237697   1.724471
6            #3_1_to_numpy_comp_copy           0.210840   1.529625
7              #4_1_values_comp_copy           0.211595   1.535103
8             #5_1_to_dict_comp_copy           0.290036   2.104182
9              #5_2_to_dict_for_copy           0.298513   2.165681
10       #5_3_to_dict_for_list_newdf           0.547780   3.974088
11       #5_4_to_dict_for_dict_newdf           0.555541   4.030389
12   #5_5_to_dict_for_dict_from_dict           0.557499   4.044599
13               #7_1_apply_raw_copy           0.680987   4.940490
14           #7_2_apply_default_copy           1.277313   9.266773
15           #8_1_iterrows_comp_copy           7.432187  53.919748
```

```text
report_df:
                           name  timedelta_average     ratio
0         #1_1_zip_comp_update           0.139311  0.991528
1           #1_2_zip_comp_copy           0.140501  1.000000
2       #5_1_to_dict_comp_copy           0.279852  1.991818
3  #5_4_to_dict_for_dict_newdf           0.545384  3.881707
4                         copy           0.001000  0.007119
5                  copy_update           0.005364  0.038175
6                      to_dict           0.128729  0.916212
7                to_dict_newdf           0.433660  3.086526
8            to_dict_from_dict           0.434399  3.091789
```