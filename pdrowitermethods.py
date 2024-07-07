import time
from typing import Callable, Any
import pandas as pd


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


class PdRowIterMethods:
    """DataFrame に関して、行ごとの値を参照して処理を行う方法の処理時間を比較

    1. DataFrame の iterrows メソッドを使う
    2. DataFrame の apply メソッドを使う
    3. DataFrame を dict に変換して処理を行い結果を辞書に追加、繰り返し終了後に辞書をDataFrameに変換
    4. DataFrame を dict に変換して処理を行い結果のリストを作成、繰り返し終了後にDataFrameにカラム追加
    5. DataFrame の values 属性を使う
    6. DataFrame の to_numpy メソッドを使う
    7. DataFrame の itertuples メソッドを使う
    8. DataFrame の 対象列を抜き出して zip で結合して処理を行う

    結論: 上記の昇順に処理時間が短くなる。itertuples メソッドを使うか、zip を使う方法がお勧め。iterrows は使わないほうがよい。


    ## 参考: プログラムが遅い原因を調べる方法

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
    """

    def make_data(self, iter_num: int = 100000) -> pd.DataFrame:
        """DataFrame を作成する"""
        columns = SampleData.EXAMPLE_2D_LIST[0]
        data = []
        for i in range(iter_num):
            data += SampleData.EXAMPLE_2D_LIST[1:]
        return pd.DataFrame(columns=columns, data=data)

    def make_dict_data(self, iter_num: int = 100000) -> list[dict[str, Any]]:
        """サンプルデータの dict のリストを作成する"""
        df = self.make_data(iter_num)
        return df.to_dict(orient="records")

    def iter_rows_with_zip_update(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - DataFrame から列を抜き出し zip で結合して処理する

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        # for文よりもリスト内包表記にしたほうが 10% 高速になる
        result = [
            PdRowIterMethods.classify(*x)
            for x in zip(df["colA"], df["colB"], df["colC"])
        ]
        df["colR"] = result
        return df

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

    def iter_rows_with_zip_for(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - DataFrame から列を抜き出し zip で結合して処理する

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        # for文よりもリスト内包表記にしたほうが 10% 高速になる
        result = []
        for x in zip(df["colA"], df["colB"], df["colC"]):
            result.append(PdRowIterMethods.classify(*x))
        df_ret = df.copy()
        df_ret["colR"] = result
        return df_ret

    def iter_rows_with_zip_new_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - DataFrame から列を抜き出し zip で結合して処理する

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        # for文よりもリスト内包表記にしたほうが 10% 高速になる
        result = [
            PdRowIterMethods.classify(*x)
            for x in zip(df["colA"], df["colB"], df["colC"])
        ]
        df_ret = pd.DataFrame(df[["colA", "colB", "colC"]])
        df_ret["colR"] = result
        return df_ret

    def iter_rows_with_itertuples(self, df: pd.DataFrame):
        """DataFrame を row ごとに処理する - DataFrame の itertuples メソッドを使う

                colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        s"""
        df_ret = df.copy()
        result = []
        for row in df_ret.itertuples():
            result.append(PdRowIterMethods.classify(row[1], row[2], row[3]))
        df_ret["colR"] = result
        return df_ret

    def iter_rows_with_itertuples_noname(self, df: pd.DataFrame):
        """DataFrame を row ごとに処理する - DataFrame の itertuples メソッドを使う

                colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        s"""
        df_ret = df.copy()
        # name=None にすると NamedTuples ではなく通常の tuple になり、30% 高速になる。
        result = [
            PdRowIterMethods.classify(a, b, c)
            for _id, a, b, c in df_ret.itertuples(name=None)
        ]
        df_ret["colR"] = result
        return df_ret

        return df_ret

    def iter_rows_with_to_numpy(self, df: pd.DataFrame):
        """DataFrame を row ごとに処理する - DataFrame の to_numpy メソッドを使う

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する

        """
        result = [
            PdRowIterMethods.classify(row[0], row[1], row[2]) for row in df.to_numpy()
        ]
        df_ret = df.copy()
        df_ret["colR"] = result
        return df_ret

    def iter_rows_with_values(self, df: pd.DataFrame):
        """DataFrame を row ごとに処理する - DataFrame の values 属性を使う

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        result = [
            PdRowIterMethods.classify(row[0], row[1], row[2]) for row in df.values
        ]
        df_ret = df.copy()
        df_ret["colR"] = result
        return df_ret

    def iter_rows_with_to_dict(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - 辞書に変換してから処理して、終わったらDataFrameにカラム追加

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        records = df.to_dict(orient="records")
        # 通常の for文よりもリスト内包表記の方が 8% 程度早い
        result = [
            PdRowIterMethods.classify(x["colA"], x["colB"], x["colC"]) for x in records
        ]
        df_ret = df.copy()
        df_ret["colR"] = result
        return df_ret

    def iter_rows_with_to_dict_for(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - 辞書に変換してから処理して、終わったらDataFrameにカラム追加

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        records = df.to_dict(orient="records")
        result = []
        for x in records:
            result.append(PdRowIterMethods.classify(x["colA"], x["colB"], x["colC"]))
        df_ret = df.copy()
        df_ret["colR"] = result
        return df_ret

    def iter_rows_with_to_dict_and_from_dict(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - 辞書に変換してから処理して、終わったら辞書をDataFrameに変換

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        records = df.to_dict(orient="records")
        for x in records:
            x["colR"] = PdRowIterMethods.classify(x["colA"], x["colB"], x["colC"])
        df_ret = pd.DataFrame.from_dict(records)
        return df_ret

    def iter_rows_with_to_dict_and_newdf(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - 辞書に変換してから処理して、終わったら辞書をDataFrameに変換

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        records = df.to_dict(orient="records")
        for x in records:
            x["colR"] = PdRowIterMethods.classify(x["colA"], x["colB"], x["colC"])
        df_ret = pd.DataFrame(records)
        return df_ret

    def iter_rows_with_to_dict_and_newdf_list(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame を row ごとに処理する - 辞書に変換してから処理して、終わったら辞書をDataFrameに変換

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        records = df.to_dict(orient="records")
        data = {"colA": [], "colB": [], "colC": [], "colR": []}
        for x in records:
            data["colA"].append(x["colA"])
            data["colB"].append(x["colB"])
            data["colC"].append(x["colC"])
            data["colR"].append(
                PdRowIterMethods.classify(x["colA"], x["colB"], x["colC"])
            )
        df_ret = pd.DataFrame(data)
        return df_ret

    def iter_rows_with_apply(self, df: pd.DataFrame):
        """DataFrame を row ごとに処理する - DataFrame の apply メソッドを使う

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        df_ret = df.copy()
        # apply メソッドに raw=True オプションを指定すると Numpy array として処理するので 46% 高速になる
        result = df_ret.apply(lambda x: PdRowIterMethods.classify(*x), axis=1, raw=True)
        df_ret["colR"] = result
        return df_ret

    def iter_rows_with_apply_default(self, df: pd.DataFrame):
        """DataFrame を row ごとに処理する - DataFrame の apply メソッドを使う

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する

        df.iterrows() を使わないほうがよい。
        https://stackoverflow.com/questions/16476924/how-can-i-iterate-over-rows-in-a-pandas-dataframe?rq=1
        """
        df_ret = df.copy()
        result = df_ret.apply(lambda x: PdRowIterMethods.classify(*x), axis=1)
        df_ret["colR"] = result
        return df_ret

    def iter_rows_with_iterrows(self, df: pd.DataFrame):
        """DataFrame を row ごとに処理する - DataFrame の iterrows メソッドを使う

        colA, colB, colC の値を使って判定を行い、判定結果を colR 列に保存して DataFrame に追加する
        """
        df_ret = df.copy()
        result = [
            PdRowIterMethods.classify(row["colA"], row["colB"], row["colC"])
            for id, row in df_ret.iterrows()
        ]
        df_ret["colR"] = result
        return df_ret

    def copy_only(self, df: pd.DataFrame):
        """copy only"""
        df_ret = df.copy()
        return df_ret

    def copy_update_only(self, df: pd.DataFrame):
        """copy update only"""
        df_ret = df.copy()
        df_ret["colR"] = "dummy"
        return df_ret

    def to_dict_only(self, df: pd.DataFrame):
        """copy only"""
        _ = df.to_dict()
        return df

    def to_dict_newdf_only(self, df: pd.DataFrame):
        """to_dict newdf only"""
        _dict = df.to_dict()
        df_ret = pd.DataFrame(_dict)
        return df_ret

    def to_dict_from_dict_only(self, df: pd.DataFrame):
        """to_dict from_dict only"""
        _dict = df.to_dict()
        df_ret = pd.DataFrame.from_dict(_dict)
        return df_ret

    def loop_only(self, data_list: list[dict[str, Any]]) -> list:
        """loop only"""
        ret_list = [self.classify(x["colA"], x["colB"], x["colC"]) for x in data_list]
        return ret_list

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

    @staticmethod
    def timeit(func, iter_num: int = 5):
        """関数の実行時間を測定するためのデコーレータ

        対象の関数の実行を指定回数行って、実行時間(sec)を計測し、実行時間の平均値を計算する
        """

        def my_func(*args, **kwargs) -> tuple[Callable, str]:
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
            return result, time_delta_average

        return my_func

    def one(self):
        """DataFrame の行ごとの判定結果を新しい列に書き込む処理を一つ実行する"""
        # サンプルデータの繰り返し生成回数
        iter_num = 100000
        # Pandas のバージョンを確認
        print("pandas version:", pd.__version__)
        # self = PdRowIterMethods()
        # 実行対象のメソッド
        d_func = self.iter_rows_with_to_dict_and_from_dict
        # d_func = self.iter_rows_with_zip  # 最も早い

        print("-- as_dict_with_from_dict")
        df = self.make_data(iter_num)
        print("df:", df.shape)
        df_result, timedelta_average = d_func(df)
        print("df_result:", df_result.shape)
        print(df_result.head(6))

    def compare(
        self, methods: dict[str, Callable], base_name: str = "#1_2_zip_comp_copy"
    ):
        """DataFrame の行ごとの判定結果を新しい列に書き込む処理について、複数の方法を比較する"""
        # サンプルデータの繰り返し生成回数
        iter_num = 100000
        # Pandas のバージョンを確認
        print("pandas version:", pd.__version__)

        if base_name not in list(methods):
            base_name = list(methods)[0]
        report = []
        for idx, key in enumerate(methods):
            print(f"-- {idx + 1}. {key}")
            df = self.make_data(iter_num)
            print("df.shape (before):", df.shape)
            d_func = PdRowIterMethods.timeit(methods[key])
            df_result, timedelta_average = d_func(df)
            print("df.shape (after):", df.shape)
            print("df_result.shape:", df_result.shape)
            print(df_result.head(6))

            report.append([key, timedelta_average])
            if key == base_name:
                base_ta = timedelta_average

        report_df = pd.DataFrame(data=report, columns=["name", "timedelta_average"])
        ratio = [ta / base_ta for _key, ta in report]
        report_df["ratio"] = ratio
        print("\nreport_df:\n", report_df)


def compare_methods(pdrowiter: PdRowIterMethods):
    # 比較対象のメソッド
    methods = {
        "#1_1_zip_comp_update": pdrowiter.iter_rows_with_zip_update,  # 最も早い
        "#1_2_zip_comp_copy": pdrowiter.iter_rows_with_zip,  # 最も早い
        "#1_3_zip_comp_newdf": pdrowiter.iter_rows_with_zip_new_df,  # 最も早い
        "#1_4_zip_for_copy": pdrowiter.iter_rows_with_zip_for,  # 最も早い
        "#2_1_itertuples_noname_comp_copy": pdrowiter.iter_rows_with_itertuples_noname,
        "#2_2_itertuples_named_comp_copy": pdrowiter.iter_rows_with_itertuples,
        "#3_1_to_numpy_comp_copy": pdrowiter.iter_rows_with_to_numpy,  # 早い
        "#4_1_values_comp_copy": pdrowiter.iter_rows_with_values,  # 早い
        "#5_1_to_dict_comp_copy": pdrowiter.iter_rows_with_to_dict,  # まあまあ
        "#5_2_to_dict_for_copy": pdrowiter.iter_rows_with_to_dict_for,  # まあまあ
        "#5_3_to_dict_for_list_newdf": pdrowiter.iter_rows_with_to_dict_and_newdf_list,
        "#5_4_to_dict_for_dict_newdf": pdrowiter.iter_rows_with_to_dict_and_newdf,
        "#5_5_to_dict_for_dict_from_dict": pdrowiter.iter_rows_with_to_dict_and_from_dict,  # 元
        "#7_1_apply_raw_copy": pdrowiter.iter_rows_with_apply,  # 遅い
        "#7_2_apply_default_copy": pdrowiter.iter_rows_with_apply_default,  # 遅い
        "#8_1_iterrows_comp_copy": pdrowiter.iter_rows_with_iterrows,  # 使わない
    }
    base_name = "#1_2_zip_comp_copy"
    pdrowiter.compare(methods, base_name)


def compare_elements(pdrowiter: PdRowIterMethods):
    # 比較対象のメソッド
    methods = {
        "#1_1_zip_comp_update": pdrowiter.iter_rows_with_zip_update,  # 最も早い
        "#1_2_zip_comp_copy": pdrowiter.iter_rows_with_zip,  # 最も早い
        # "#1_3_zip_comp_newdf": pdrowiter.iter_rows_with_zip_new_df,  # 最も早い
        # "#1_4_zip_for_copy": pdrowiter.iter_rows_with_zip_for,  # 最も早い
        # "#2_1_itertuples_noname_comp_copy": pdrowiter.iter_rows_with_itertuples_noname,
        # "#2_2_itertuples_named_comp_copy": pdrowiter.iter_rows_with_itertuples,
        # "#3_1_to_numpy_comp_copy": pdrowiter.iter_rows_with_to_numpy,  # 早い
        # "#4_1_values_comp_copy": pdrowiter.iter_rows_with_values,  # 早い
        "#5_1_to_dict_comp_copy": pdrowiter.iter_rows_with_to_dict,  # まあまあ
        # "#5_2_to_dict_for_copy": pdrowiter.iter_rows_with_to_dict_for,  # まあまあ
        # "#5_3_to_dict_for_list_newdf": pdrowiter.iter_rows_with_to_dict_and_newdf_list,
        "#5_4_to_dict_for_dict_newdf": pdrowiter.iter_rows_with_to_dict_and_newdf,
        # "#5_5_to_dict_for_dict_from_dict": pdrowiter.iter_rows_with_to_dict_and_from_dict,  # 元
        # "#7_1_apply_raw_copy": pdrowiter.iter_rows_with_apply,  # 遅い
        # "#7_2_apply_default_copy": pdrowiter.iter_rows_with_apply_default,  # 遅い
        # "#8_1_iterrows_comp_copy": pdrowiter.iter_rows_with_iterrows,  # 使わない
        "copy": pdrowiter.copy_only,
        "copy_update": pdrowiter.copy_update_only,
        "to_dict": pdrowiter.to_dict_only,
        "to_dict_newdf": pdrowiter.to_dict_newdf_only,
        "to_dict_from_dict": pdrowiter.to_dict_from_dict_only,
    }
    # base_name = "#5_4_to_dict_for_dict_newdf"
    base_name = "#1_2_zip_comp_copy"
    pdrowiter.compare(methods, base_name)


def main():
    pdrowiter = PdRowIterMethods()
    compare_methods(pdrowiter)
    compare_elements(pdrowiter)


if __name__ == "__main__":
    main()
