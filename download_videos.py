from functools import partial
from multiprocessing import Pool

import requests
import re
from bs4 import BeautifulSoup


# get the url of all videos
def download_video(url, pageNumClass, videoClass, titleClass):
    url_prefix = re.findall(r'http://.*?/', url)[0]

    txt = requests.get(url).text
    soup = BeautifulSoup(txt, 'lxml')
    txt_num = soup.find_all('div', class_=pageNumClass)
    # get the total page number of the videos
    page = re.findall(r"\d+", str(txt_num[0]))
    first = page[1]
    total = page[2]
    print("共有" + total + "页视频")
    pageUrlList = []
    nameList = []
    videoList = []
    # get the url of all videos
    for i in range(int(first), int(total) + 1):
        url1 = url + '&page=' + str(i)
        # print(url1)
        txt_index = requests.get(url1).text
        soup2 = BeautifulSoup(txt_index, 'lxml')
        t1 = soup2.find_all('a')
        for t2 in t1:
            t3 = str(t2.get('href'))
            # pattern1 = re.compile(r'product_view.aspx?id=')
            # if re.search(pattern1, t3):

            if re.match(videoClass, t3):
                pageUrlList.append(t3)
    print("共有" + str(len(pageUrlList)) + "个视频")
    # print(len(urlList))
    for i in pageUrlList:
        urlNow = url_prefix + "EWeb/" + i
        # print(urlNow)
        data = requests.get(urlNow).text
        soup3 = BeautifulSoup(data, 'lxml')
        video = soup3.find_all('video')
        names = soup3.find_all('h3', class_=titleClass)

        for src in video:
            video_src = url_prefix + str(src.get('src'))
            videoID = re.findall(r"\d+", video_src)[1]
            videoList.append(video_src)
            for name in names:
                t = videoID + '_' + name.get_text()
                nameList.append(t)
    # download the videos
    t = 0
    for i in range(len(videoList)):
        video = requests.get(videoList[i])
        try:
            with open(nameList[i] + '.mp4', 'wb') as f:
                f.write(video.content)
                print("\033[32m" + str(nameList[i]) + '下载成功\033[0m')
        except Exception as e:
            t = t + 1
            print(e)
            print("\033[31m" + str(nameList[i]) + '下载失败\033[0m')
        finally:
            f.close()
    a = len(nameList) - t
    print("下载完成" + str(a) + "个视频")


if __name__ == '__main__':
    # url必须传入数组，pageNumClass为视频页数的class，videoClass为视频栏的class
    url = ['http://www.jl1.cn/EWeb/product2.aspx?id=21&tid=30']
    pageNumClass = 'list_right3a'
    videoClass = 'product_view.aspx'
    titleClass = 'col-md-10 col-md-push-1 ej_title'
    func = partial(download_video, pageNumClass=pageNumClass, videoClass=videoClass, titleClass=titleClass)
    pool = Pool(16)
    pool.map(func, url)
    pool.close()
    pool.join()
