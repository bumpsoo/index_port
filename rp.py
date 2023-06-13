import pandas as pd
import numpy as np
import scipy.optimize as sco
import os

def getListOfIndex(fileName):
    new = []
    if os.path.exists(fileName):
        data_wb = pd.ExcelFile(fileName)
        for name in data_wb.sheet_names:
            if name == '내보내기 요약':
                continue
            new.append(name)
    return new

class rpo:
    def __init__(self, fileName, argv):
        self.fileName = fileName
        self.argv = argv
    def calc(self):
        DATA_FILE = self.fileName
        data_wb = pd.ExcelFile(DATA_FILE)
        new = pd.DataFrame()
        print(self.argv)
        for name in data_wb.sheet_names:
            if name == '내보내기 요약':
                continue
            if name not in self.argv:
                continue
            ttt = data_wb.parse(name, index_col=0)
            ttt = ttt.xs('종가', axis=1)
            ttt.index.name = None
            new[name] = ttt
        new = new.sort_index(axis='index', ascending=True)
        new_df = self.__make_df(new)
        self.covmat = np.array(new_df.cov() * 240)
        rp = self.__risk_parity_optimization(new_df)
        return rp['allocation']

    def __make_df(self, adj_price):
        df = adj_price.pct_change(1)
        df = df[1:]
        return df


    def __Risk_Contribution(self, weight):
        weight = np.array(weight)
        std = np.sqrt(np.dot(weight.T, np.dot(self.covmat, weight)))
        mrc = np.dot(self.covmat, weight) / std
        rc = weight * mrc

        return rc, std
    def __risk_parity_optimization(self,df):
        TOLERANCE = 1e-20
        num_assets = len(self.covmat)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1.0}, {'type': 'ineq', 'fun': lambda x: x})
        result = sco.minimize(self.__risk_parity_target, num_assets * [1. / num_assets, ], method='SLSQP',
                              constraints=constraints, tol=TOLERANCE)
        Risk_Parity_Allocation = pd.DataFrame(result.x, index=df.columns, columns=['allocation'])

        return round(Risk_Parity_Allocation * 100, 2)


    def __risk_parity_target(self,weight):
        rc, std = self.__Risk_Contribution(weight)
        RC_assets = rc
        RC_target = std / len(rc)
        objective_fun = np.sum(np.square(RC_assets - RC_target.T))

        return objective_fun


