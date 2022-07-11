from bs4 import BeautifulSoup
import os, re, traceback
from httpx import AsyncClient
import asyncio
import os
import glob2
import numpy as np
import io
from tqdm import tqdm
import soundfile
import resampy
import pyworld
from pymysql.converters import escape_string
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
import torch
from multiprocessing import cpu_count
from concurrent.futures import ProcessPoolExecutor
from functools import partial
import pymysql
import os
from dotenv import load_dotenv
import torch
import numpy as np
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
import glob2

class DataSaveToMySQL(object):
    def __init__(self):
        # loading env config file
        dotenv_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
    def get_voice_data(self,char_name,min_loudness=0):
        conn = pymysql.connect(host=' ', port= ,
                               user=' ', password=' ',
                               db=' ')
        cur = conn.cursor()
        cur.execute("select * from charcter where char_name='{}';".format(char_name))
        result = cur.fetchone()
        print(result)
        num=result[3]
        print(num)
        cur.execute("select * from voice_data where char_name='{}' AND loudness<{};".format(char_name,min_loudness))
        #print(cur.fetchone())
        result = cur.fetchall()
        print(result)
        print(len(result))
        print(result[0][1])
        re=[]
        for i in range(len(result)):
            #print(i)
            re.append(result[i][1])
        conn.commit()
        cur.close()
        conn.close()
        return re



class Voicedataset(Dataset):
    def __init__(self,char_name='Kamisato Ayato',min_loudness=0):
        self.sql=DataSaveToMySQL()
        self.char_name=char_name
        self.min_loudness=min_loudness
        self.re = self.sql.get_voice_data(self.char_name, self.min_loudness)

    def __getitem__(self, index):
        return self.re[index]
    def __len__(self):
        return len(self.re)


if __name__=='__main__':
    dataset=Voicedataset('Yelan',-17)
    loader=DataLoader(dataset,batch_size=1)
    for a in loader:
        print(a)
