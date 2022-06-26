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

voice_actor_list={'Jean':'Chiwa Saitō','Yelan':'Aya Endō','Kaedehara Kazuha':'Nobunaga Shimazaki','Venti':'Ayumu Murase',
                  'Xiao':'Yoshitsugu Matsuoka','Eula':'Rina Sato','Kamisato Ayaka':'Saori Hayami','Qiqi':'Yukari Tamura',
                  'Ganyu':'Reina Ueda','Aloy':'Ayahi Takagaki','Raiden Shogun':'Miyuki Sawashiro','Shenhe':'Ayako Kawasumi',
                  'Keqing':'Eri Kitamura','Albedo':'Kenji Nojima','Yae Miko':'Ayane Sakura','Zhongli':'Tomoaki Maeno',
                  'Traveler':'Shun Horie / Aoi Yūki','Tartaglia':'Ryohei Kimura','Sangonomiya Kokomi':'Suzuko Mimori',
                  'Arataki Itto':'Takanori Nishikawa','Mona':'Konomi Kohara','Yanfei':'Yumiri Hanamori','Hu Tao':'Rie Takahashi',
                  'Klee':'Misaki Kuno','Yoimiya':'Kana Ueda','Diluc':'Kensho Ono','Kamisato Ayato':'Akira Ishida'
                  }

def compute_loudness(
        wavfile_path
):
    wav, sr = soundfile.read(wavfile_path)
    meter = pyln.Meter(sr)  #
    loudness = meter.integrated_loudness(wav)
    loudness = np.array(loudness)
    return loudness

class DataSaveToMySQL(object):
    def __init__(self):
        # loading env config file
        dotenv_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
    def save_mysql_voicedata(self,char_name,voice_position,voice_content,voice_title,loudness):
        conn = pymysql.connect(host='127.0.0.1', port=3306,
                               user='root', password='Zwt170910',
                               db='genshin')
        cur = conn.cursor()

        cur.execute("insert into voice_data(char_name,voice_position,voice_content,voice_title,loudness) values('{}','{}','{}','{}',{});".format(
            escape_string(char_name),escape_string(voice_position),escape_string(voice_content),escape_string(voice_title),escape_string(str(loudness))))
        print(cur.fetchone())
        conn.commit()
        cur.close()
        conn.close()
    def save_mysql_char(self,char_name,voice_actor):
        conn = pymysql.connect(host='127.0.0.1', port=3306,
                               user='root', password='Zwt170910',
                               db='genshin')
        cur = conn.cursor()

        cur.execute("insert into charcter(genshin_version,char_name,voice_actor,voice_count) values('2.7','{}','{}',0);".format(
            escape_string(char_name),escape_string(voice_actor)))
        print(cur.fetchone())
        conn.commit()
        cur.close()
        conn.close()

FILE_PATH = os.path.dirname(__file__)
Audio_PATH = os.path.join(FILE_PATH, "Audio")
baseurl = "https://genshin-impact.fandom.com/wiki/Genshin_Impact_Wiki"


async def get_url(url):
    async with AsyncClient() as client:
        req = await client.get(
            url=url
        )
    return req.text


async def download(url, char_name, file_name,voice_content):
    print("Downloading {} 's {}".format(char_name, file_name))
    print(url)
    try:
        async with AsyncClient() as client:
            req = await client.get(
                url=url
            )

        while (1):
            if os.path.exists(os.path.join(Audio_PATH, char_name)):
                length=min(10,len(voice_content))
                with open(os.path.join(os.path.join(Audio_PATH, char_name), "{}.wav".format(voice_content[:length])), 'wb') as f:
                    print(os.path.join(os.path.join(Audio_PATH, char_name), "{}.wav".format(voice_content[:length])))
                    f.write(req.content)
                    f.close
                print("Done!")
                loudness=compute_loudness(os.path.join(os.path.join(Audio_PATH, char_name), "{}.wav".format(voice_content[:length])))
                print("loudness",loudness)
                sql=DataSaveToMySQL()
                sql.save_mysql_voicedata(char_name,os.path.join(os.path.join(Audio_PATH, char_name),
                                        "{}.wav".format(voice_content[:length])),
                                         voice_content,
                                         file_name,loudness)
                break
            else:
                os.makedirs(os.path.join(Audio_PATH, char_name), exist_ok=True)
    except:
        traceback.print_exc()
        print("Fail，doesn't exist")


async def main():
    base_data = await get_url(baseurl)
    content_bs = BeautifulSoup(base_data, 'lxml')
    raw_data_5star = content_bs.find_all("div", class_='card_container card_5 hidden')
    raw_data_4star = content_bs.find_all("div", class_='card_container card_4 hidden')
    raw_data = raw_data_5star# + raw_data_4star
    char_list = {}
    for i in raw_data[:10]:
        char_url = "https://genshin-impact.fandom.com" + i.find("a")["href"] + "/Voice-Overs/Japanese"
        print(i.find("a")["title"])
        sql = DataSaveToMySQL()
        sql.save_mysql_char(i.find("a")["title"],voice_actor_list[i.find("a")["title"]])
        if i.find("a")["title"] != "Traveler":
            char_list[i.find("a")["title"]] = char_url

    for i in char_list.keys():
        cahr_voice_data = await get_url(char_list[i])
        voice_bs = BeautifulSoup(cahr_voice_data, 'lxml')
        voice_data = voice_bs.find_all("table", class_='wikitable')

        # voice_data = voice_bs.find_all("span",class_='audio-button custom-theme hidden')
        tasks = []
        if len(voice_data) // 2 == 6:
            audio_index = [0, 4, 8]
        else:
            audio_index = [0, len(voice_data) // 2]

        temp_title = ""
        for g in audio_index:
            #print("audio index",g)
            for k in voice_data[g].tbody.find_all("tr")[1:]:
                #print("tr",k)
                if len(k.find_all("th")) == 0:
                    audio_title = temp_title
                else:
                    audio_title = k.find_all("th")[0].text
                    temp_title = audio_title

                audio_url = []
                for j in k.td.find_all("span", class_='audio-button custom-theme hidden'):
                    audio_url.append(j.find_all("a")[0]["href"])
                for j in k.td.find_all("span", lang='ja'):
                    #print(type(j))
                    #print("hello//////////")
                    print(j.string)
                    voice_content=j.string
                #print(voice_content)
                #print(audio_title)
                audio_chinese_title = ''.join(re.findall('[\u0800-\u9fa5]', audio_title))
                #print(audio_chinese_title)

                if len(audio_url) == 1:
                    tasks.append(
                        download(audio_url[0], i, "{}.wav".format(audio_title),voice_content))
                """
                elif len(audio_url) > 1:
                    for index, j in enumerate(audio_url):
                        tasks.append(
                            download(j, i, "{}{}.wav".format(audio_chinese_title, str(index + 1))))
                """
                # await download(audio_url,i,"{}.ogg".format(audio_chinese_title))

                # audio_url = k.find("a")["href"]
                # print(audio_url)

        await asyncio.wait(tasks)

    # os.makedirs(file, exist_ok=True)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())