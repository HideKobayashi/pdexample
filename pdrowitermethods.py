import time
import pandas as pd


class PdRowIterMethods:
    """DataFrame に関して、行ごとの値を参照して処理を行う方法の処理時間を比較

    1. DataFrame の iterrows メソッドを使う
    2. DataFrame の apply メソッドを使う
    3. DataFrame を dict に変換して処理を行い結果を辞書に追加、繰り返し終了後に辞書をDataFrameに変換
    4. DataFrame を dict に変換して処理を行い結果のリストを作成、繰り返し終了後にDataFrameにカラム追加
    5. DataFrame の values 属性を使う
    6. DataFrame の itertuples メソッドを使う
    7. DataFrame の 対象列を抜き出して zip で結合して処理を行う

    結論: 上記の昇順に処理時間が短くなる。itertuples メソッドを使うか、zip を使う方法がお勧め。iterrows は使わないほうがよい。
    """

    def make_data(self, iter_num: int = 100000) -> pd.DataFrame:
        """DataFrame を作成する"""
        columns = SampleData.EXAMPLE_2D_LIST[0]
        data = []
        for i in range(iter_num):
            data += SampleData.EXAMPLE_2D_LIST[1:]
        return pd.DataFrame(columns=columns, data=data)

    def iterating_rows_df_as_dict_with_from_dict(
        self, df: pd.DataFrame
    ) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - 辞書に変換してから処理して、終わったら辞書をDataFrameに変換

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する

        DataFrame に対する loop を高速化
        https://qiita.com/siruku6/items/4bd337d80d7aaceae542#2-1-to_dictorientrecords---dataframe-%E3%81%AB%E5%AF%BE%E3%81%99%E3%82%8B-loop-%E3%82%92%E9%AB%98%E9%80%9F%E5%8C%96
        """
        records = df.to_dict(orient="records")
        for record in records:
            record["colR"] = self.classify(
                record["colA"], record["colB"], record["colC"]
            )
        df_ret = pd.DataFrame.from_dict(records)
        return df_ret

    def iterating_rows_df_as_dict_no_from_dict(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - 辞書に変換してから処理して、終わったらDataFrameにカラム追加

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する

        DataFrame に対する loop を高速化
        https://qiita.com/siruku6/items/4bd337d80d7aaceae542#2-1-to_dictorientrecords---dataframe-%E3%81%AB%E5%AF%BE%E3%81%99%E3%82%8B-loop-%E3%82%92%E9%AB%98%E9%80%9F%E5%8C%96
        """
        records = df.to_dict(orient="records")
        # result = []
        # for record in records:
        #     result.append(self.classify(record["colA"], record["colB"], record["colC"]))
        # リスト内包表記の方が 8% 程度早い
        result = [
            self.classify(record["colA"], record["colB"], record["colC"])
            for record in records
        ]
        df_ret = df.copy()
        df_ret["colR"] = result
        return df_ret

    def iterating_rows_df_as_df_with_zip(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - DataFrame から列を抜き出し zip で結合して処理する

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する

        df.iterrows() を使わないほうがよい。
        https://stackoverflow.com/questions/16476924/how-can-i-iterate-over-rows-in-a-pandas-dataframe?rq=1
        """
        # for文よりもリスト内包表記にしたほうが 10% くらい時間が短縮できる
        result = [self.classify(*x) for x in zip(df["colA"], df["colB"], df["colC"])]
        df_ret = df.copy()
        df_ret["colR"] = result
        return df_ret

    def iterating_rows_df_as_df_with_apply(self, df: pd.DataFrame):
        """DataFrame を row ごとに処理する - DataFrame の apply メソッドを使う

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する

        df.iterrows() を使わないほうがよい。
        https://stackoverflow.com/questions/16476924/how-can-i-iterate-over-rows-in-a-pandas-dataframe?rq=1
        """
        df_ret = df.copy()
        result = df_ret.apply(lambda x: self.classify(*x), axis=1)
        df_ret["colR"] = result
        return df_ret

    def iterating_rows_df_as_df_with_iterrows(self, df: pd.DataFrame):
        """DataFrame を row ごとに処理する - DataFrame の iterrows メソッドを使う

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する

        df.iterrows() を使わないほうがよい。
        https://stackoverflow.com/questions/16476924/how-can-i-iterate-over-rows-in-a-pandas-dataframe?rq=1
        """
        df_ret = df.copy()
        result = []
        for id, row in df_ret.iterrows():
            a, b, c = row["colA"], row["colB"], row["colC"]
            result.append(self.classify(a, b, c))
        df_ret["colR"] = result
        return df_ret

    def iterating_rows_df_as_df_with_itertuples(self, df: pd.DataFrame):
        """DataFrame を row ごとに処理する - DataFrame の itertuples メソッドを使う

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する

        df.iterrows() を使わないほうがよい。
        https://note.nkmk.me/python-pandas-dataframe-for-iteration/
        """
        df_ret = df.copy()
        result = []
        # name=None にすると NamedTuples ではなく通常の tuple になり、30% くらい高速になる。
        # for _id, a, b, c in df_ret.itertuples(name=None):
        #     # _id, a, b, c = row row[1], row[2], row[3]
        #     result.append(self.classify(a, b, c))
        # さらに、リスト内包表記にすると高速になる
        result = [
            self.classify(a, b, c) for _id, a, b, c in df_ret.itertuples(name=None)
        ]
        df_ret["colR"] = result
        return df_ret

    def iterating_rows_df_as_df_with_values(self, df: pd.DataFrame):
        """DataFrame を row ごとに処理する - DataFrame の values 属性を使う

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する

        df.iterrows() を使わないほうがよい。
        https://stackoverflow.com/questions/16476924/how-can-i-iterate-over-rows-in-a-pandas-dataframe?rq=1
        """
        df_ret = df.copy()
        map_column_and_index = {}
        for index, column in enumerate(df_ret.columns, 0):
            map_column_and_index[column] = index
        # result = []
        # for row in df_ret.values:
        #     a, b, c = (
        #         row[map_column_and_index["colA"]],
        #         row[map_column_and_index["colB"]],
        #         row[map_column_and_index["colC"]],
        #     )
        #     result.append(self.classify(a, b, c))
        # for文をリスト内包表記にすると 12% 高速になる
        result = [
            self.classify(
                row[map_column_and_index["colA"]],
                row[map_column_and_index["colB"]],
                row[map_column_and_index["colC"]],
            )
            for row in df_ret.values
        ]
        df_ret["colR"] = result
        return df_ret

    @staticmethod
    def classify(a: int, b: int, c: int) -> str:
        """三つの値を使って判定し、判定結果を返す"""
        class_result = ""
        if a % 5 == 0:
            class_result += "A"
        elif b % 5 == 0:
            class_result += "B"
        elif c % 5 == 0:
            class_result += "C"
        else:
            class_result += "N"
        return class_result


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


def timeit(func, iter_num: int = 5):
    """関数の実行時間を測定するためのデコーレータ

    対象の関数の実行を指定回数行って、実行時間(sec)を計測し、実行時間の平均値を計算する
    """

    def my_func(*args, **kwargs):
        time_delta_list = []
        for i in range(iter_num):
            time_start = time.time()
            result = func(*args, **kwargs)
            time_end = time.time()
            time_delta = time_end - time_start
            time_delta_list.append(time_delta)
            print(f"time_delta {i + 1}:", time_delta)
        time_delta_average = sum(time_delta_list) / len(time_delta_list)
        print("time_delta_average:", time_delta_average)
        return result

    return my_func


def main():
    """DataFrame の行ごとの判定結果を新しい列に書き込む処理について、複数の方法を比較する"""
    # サンプルデータの繰り返し生成回数
    iter_num = 100000
    # iter_num = 100
    # Pandas のバージョンを確認
    print("pandas version:", pd.__version__)
    pddict = PdRowIterMethods()

    # 比較対象のメソッド
    methods = {
        # "as_df_with_iterrows": pddict.iterating_rows_df_as_df_with_iterrows,  # 使わない
        "as_df_with_apply": pddict.iterating_rows_df_as_df_with_apply,  # 遅い
        "as_dict_with_from_dict": pddict.iterating_rows_df_as_dict_with_from_dict,  # まあまあ
        "as_dict_no_from_dict": pddict.iterating_rows_df_as_dict_no_from_dict,  # まあまあ
        "as_df_with_values": pddict.iterating_rows_df_as_df_with_values,  # 早い
        "as_df_with_itertuples": pddict.iterating_rows_df_as_df_with_itertuples,  # 早い
        "as_df_with_zip": pddict.iterating_rows_df_as_df_with_zip,  # 最も早い
    }

    for key in methods:
        print(f"-- {key}")
        df = pddict.make_data(iter_num)
        print("df:", df.shape)
        d_func = timeit(methods[key])
        df_result: pd.DataFrame = d_func(df)
        print("df_result:", df_result.shape)
        print(df_result.head(6))


if __name__ == "__main__":
    main()
