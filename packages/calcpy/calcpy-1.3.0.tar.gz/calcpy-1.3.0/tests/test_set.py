import numpy as np
import pandas as pd

from calcpy import unique, concat, union, intersection, difference, symmetric_difference, eq
from calcpy.matcher import PandasFrameMatcher


def test_all():
    in0_list = [8, 6, 4, 2, 0, 1, 3, 5, 6, 7]
    in1_list = [1, 3, 5, 7, 9, 8, 6, 4, 2]
    in2_list = [2, 6, 6, 3, 5, 5, 6, 7]
    lists = [in0_list, in1_list, in2_list]
    uni_list = [8, 6, 4, 2, 0, 1, 3, 5, 7]
    assert eq(unique(in0_list), uni_list)
    con_list = in0_list + in1_list + in2_list
    assert eq(concat(*lists), con_list)
    unn_list = [8, 6, 4, 2, 0, 1, 3, 5, 7, 9]
    assert eq(union(*lists), unn_list)
    int_list = [6, 2, 3, 5, 6, 7]
    assert eq(intersection(*lists), int_list)
    exc_list = [0]
    assert eq(difference(*lists), exc_list)
    xor_list = [0, 9, 2, 6, 6, 3, 5, 5, 6, 7]
    assert eq(symmetric_difference(*lists), xor_list)

    in0_tuple = tuple(in0_list)
    in1_tuple = tuple(in1_list)
    in2_tuple = tuple(in2_list)
    tuples = [in0_tuple, in1_tuple, in2_tuple]
    uni_tuple = tuple(uni_list)
    assert eq(unique(in0_tuple), uni_tuple)
    con_tuple = tuple(con_list)
    assert eq(concat(*tuples), con_tuple)
    unn_tuple = tuple(unn_list)
    assert eq(union(*tuples), unn_tuple)
    int_tuple = tuple(int_list)
    assert eq(intersection(*tuples), int_tuple)
    exc_tuple = tuple(exc_list)
    assert eq(difference(*tuples), exc_tuple)
    xor_tuple = tuple(xor_list)
    assert eq(symmetric_difference(*tuples), xor_tuple)

    in0_set = set(in0_list)
    in1_set = set(in1_list)
    in2_set = set(in2_list)
    sets = [in0_set, in1_set, in2_set]
    uni_set = set(uni_list)
    assert eq(unique(in0_set), uni_set)
    con_set = set(con_list)
    assert eq(concat(*sets), con_set)
    unn_set = set(unn_list)
    assert eq(union(*sets), unn_set)
    int_set = set(int_list)
    assert eq(intersection(*sets), int_set)
    exc_set = set(exc_list)
    assert eq(difference(*sets), exc_set)
    xor_set = set(xor_list)
    assert eq(symmetric_difference(*sets), xor_set)

    in0_arr = np.array(in0_list)
    in1_arr = np.array(in1_list)
    in2_arr = np.array(in2_list)
    arrs = [in0_arr, in1_arr, in2_arr]
    uni_arr = np.array(uni_list)
    assert eq(unique(in0_arr), uni_arr)
    con_arr = np.array(con_list)
    assert eq(concat(*arrs), con_arr)
    unn_arr = np.array(unn_list)
    assert eq(union(*arrs), unn_arr)
    int_arr = np.array(int_list)
    assert eq(intersection(*arrs), int_arr)
    exc_arr = np.array(exc_list)
    assert eq(difference(*arrs), exc_arr)
    xor_arr = np.array(xor_list)
    assert eq(symmetric_difference(*arrs), xor_arr)

    in0_s = pd.Series(in0_list, index=in0_list)
    in1_s = pd.Series(in1_list, index=in1_list)
    in2_s = pd.Series(in2_list, index=in2_list)
    ss = [in0_s, in1_s, in2_s]
    uni_s = pd.Series(uni_list, index=uni_list)
    assert eq(unique(in0_s), uni_s)
    con_s = pd.Series(con_list, index=con_list)
    assert eq(concat(*ss), con_s)
    unn_s = pd.Series(unn_list, index=unn_list)
    assert eq(union(*ss), unn_s)
    int_s = pd.Series(int_list, index=int_list)
    assert eq(intersection(*ss), int_s)
    exc_s = pd.Series(exc_list, index=exc_list)
    assert eq(difference(*ss), exc_s)
    xor_s = pd.Series(xor_list, index=xor_list)
    assert eq(symmetric_difference(*ss), xor_s)

    in0_df = in0_s.to_frame("V")
    in1_df = in1_s.to_frame("V")
    in2_df = in2_s.to_frame("V")
    dfs = [in0_df, in1_df, in2_df]
    uni_df = uni_s.to_frame("V")
    assert eq(unique(in0_df), uni_df)
    con_df = con_s.to_frame("V")
    assert eq(concat(*dfs), con_df)
    unn_df = unn_s.to_frame("V")
    assert eq(union(*dfs), unn_df)
    int_df = int_s.to_frame("V")
    assert eq(intersection(*dfs), int_df)
    exc_df = exc_s.to_frame("V")
    assert eq(difference(*dfs), exc_df)
    xor_df = xor_s.to_frame("V")
    assert eq(symmetric_difference(*dfs), xor_df)

    df1 = pd.DataFrame({"A": 1, "B": 2, "C": 3}, index=[0])
    df2 = pd.DataFrame({"A": 1, "B": 2, "C": 3}, index=[0])
    df3 = pd.DataFrame({"A": 1, "B": 2, "C": 3}, index=[0])
    assert len(unique([df1, df2, df3])) == 1

    df1 = pd.DataFrame({"A": [1, 2, 3], "B": [3, 2, 3]}, index=["X", "Y", "Z"])
    df2 = pd.DataFrame({"C": [4, 5, 6], "D": [8, 5, 2]}, index=["U", "V", "X"])
    intersection(df1, df2, key=PandasFrameMatcher(method="index"))
