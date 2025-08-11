import sys
import os
import pandas as pd

sys.path.append('/home/kimyh/library/textbasic')
from textbasic.compare.similarityanalysis import *


def main():
    print('데이터 불러오기...')
    df = pd.read_csv('./faultcode_whole.csv', encoding='utf-8-sig')
    # df = df[:10]
    data = df.copy()
    explain_list = data['설명'].tolist()
    # print(data)
    # sys.exit()
    # data = df['설명'].tolist()
    # print(data)

    string = '운전석 정면 4단계 전개 컨트롤(하위 결함)'
    sim_p_list = []
    for explain in explain_list:
        sim_p = compare_sim(string, explain)
        sim_p_list.append(sim_p)
    print(sim_p_list)
    sys.exit()
    

    # df, sim_df = extract_sim(
    #     data=data,
    #     # column='설명',
    #     unique=True,
    #     p=99,
    #     # preserve=True
    # )
    # print(df)
    # print(sim_df)


if __name__ == '__main__':
    main()