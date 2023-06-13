import pandas as pd
import numpy as np
import scipy.optimize as sco
import matplotlib as plt

def get_mean(W, R):
    return sum(R * W)

#  포트폴리오 수익률 변동성(분산)
def get_var(W, C):
    return np.dot(np.dot(W, C), W)
    
# 포트폴리오 수익률 평균 및 분산

def get_mean_var(W, R, C):
    return sum(R * W), np.dot(np.dot(W, C), W)

class var:
    def __init__(self, fileName, argv):
        self.fileName = fileName
        self.argv = argv
        self.__init()

    def __init(self):
        DATA_FILE = self.fileName
        data_wb = pd.ExcelFile(DATA_FILE)
        new = pd.DataFrame()
        for name in data_wb.sheet_names:
            if name == '내보내기 요약':
                continue
            if name not in self.argv:
                continue
            ttt = data_wb.parse(name, index_col=0)
            ttt = ttt.xs('종가', axis=1)
            ttt.index.name = None
            new[name] = ttt
        self.new = new.sort_index(axis='index', ascending=True)
        self.universe = new[self.argv]
        self.universe.index = pd.to_datetime(self.universe.index)
        self.df = self.universe.resample('M').last().pct_change(1)
        self.covmat = np.array(self.df.cov()*12)
        self.exret = np.array(self.df.mean() * 12)
        self.rf = .02  # 무위험이자율
        self.n_assets = len(self.argv)
        self.pweight=self.n_assets*[1/self.n_assets]
        self.weight=np.array(self.pweight)

class meanV(var):
    def calc(self):
        sharp = self.__mean_variance_optimization(self.exret, self.covmat, self.rf)
        return sharp

    def __mean_variance_optimization(self,returns,covmat,rf):
    
        args=(returns,covmat,rf)
        constraints=({'type': 'eq','fun': lambda x: np.sum(x)-1})
        bounds=[(0.1,1) for i in range(self.n_assets)]

        result= sco.minimize(self.__sharpe_ratio,self.n_assets*[1./self.n_assets],args=args, method='SLSQP',
                             bounds=bounds,constraints=constraints)

        MVO_Allocation =pd.DataFrame(result.x,index=self.df.columns,columns=['allocation'])  # 종목명 인덱스만 가져다 쓴다.

        return round(MVO_Allocation*100,2)  


    def __sharpe_ratio(self, weights,returns,covmat,rf):
        ret=np.sum(returns*weights.T)
        std=np.sqrt(np.dot(weights,np.dot(covmat,weights.T)))
        sharpe =-(ret-rf)/std    # 최소화--> 최대화 되므로 마이너스 붙인다.

        return sharpe

class minV(var):
    def calc(self):
        return self.__minimum_variance_optimization(self.exret,self.covmat)['allocation']
    
    def __get_portf_vol(self, weights, returns, cov_mat):
        return np.sqrt(np.dot(weights.T, np.dot(cov_mat, weights)))
    
    def __minimum_variance_optimization(self,exret,covmat):
    
        num_assets=len(exret)
        args=(exret,covmat)
        constraints=({'type': 'eq','fun': lambda x: np.sum(x)-1})
        bounds=[(0,1) for i in range(num_assets)]

        result5= sco.minimize(self.__get_portf_vol,num_assets*[1./num_assets,],args=args, method='SLSQP',
                            bounds=bounds,constraints=constraints)

        MVO_Allocation =pd.DataFrame(result5.x,index=self.df.columns,columns=['allocation'])  # 종목명 인덱스만 가져다 쓴다.

        return round(MVO_Allocation*100,2)