import sys
import data
from rp import rpo
from mv import minV
from mv import meanV
from rp import getListOfIndex

fileName = './data.xlsx'
chromeDriver = '/Users/bumpsoo/Desktop/chromedriver/chromedriver'
modelDict = {
    'riskParity': lambda fileName, argv: rpo(fileName=fileName, argv=argv[1:]).calc(),
    'meanVariance': lambda fileName, argv: meanV(fileName=fileName, argv=argv[1:]).calc(),
    'minVariance': lambda fileName, argv: minV(fileName=fileName, argv=argv[1:]).calc()
    }
modelList = list(modelDict.keys())
prompt = f"""
        가능한 모델 목록 {modelList}
        가능한 지수 목록 {getListOfIndex(fileName)}
        지수는 2개 이상이어야 합니다.
    """
defaultPrompt = f"""
가능한 명령어: pull calc
    pull 
        네이버 파이낸스 페이지에서 데이터를 가져와서 저장합니다.
    calc 모델 지수...
        가져온 데이터를 토대로 배분 비율을 결정합니다.
        {prompt}
"""


if len(sys.argv) <= 1:
    print(defaultPrompt)
    exit(0)

argv = sys.argv[1:]
if argv[0] == 'pull':
    argv = argv[1:]
    print("데이터를 가져오는 중입니다.")
    data.pull(fileName, chromeDriver=chromeDriver)
    print("데이터 저장 완료")

elif argv[0] == 'calc':
    argv = argv[1:]
    

    if len(argv) <= 1:
        print(prompt)
        exit(0)
    
    if argv[0] in modelList:
        print(argv[0])
        print(modelDict[argv[0]](fileName, argv))

    else:
        print(prompt)
        exit(0)

else:
    print(defaultPrompt)
    print(argv)