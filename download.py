import os
import threading
import m3u8
import requests
from Crypto.Cipher import AES


m3u8_url = ''


def download(txt, segment, fileName):
    r = requests.get(segment.absolute_uri, headers=headers)
    data = r.content
    if segment.key is not None and segment.key.absolute_uri is not None:
        key = keys[segment.key.absolute_uri]
        iv = segment.key.iv
        if iv.startswith('0x'):
            iv = bytearray.fromhex(iv[2:])
        cryptos = AES.new(key, AES.MODE_CBC, iv)
        data = cryptos.decrypt(data)
    with open(fileName, "wb") as code:
        code.write(data)
    print(txt, fileName)
    semathore.release()

playlist = m3u8.load(m3u8_url)
folder = 'temp/'
os.makedirs(folder, exist_ok=True)
filelist = []
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}
keys = {}
for key in playlist.keys:
    if key is not None and key.absolute_uri is not None:
        key_content = requests.get(key.absolute_uri, headers=headers).content
        keys[key.absolute_uri] = key_content
semathore = threading.Semaphore(8)
total = len(playlist.segments)
for inx, segment in playlist.segments:
    fileName = folder + os.path.basename(segment.absolute_uri)
    filelist.append(fileName)
    if (os.path.exists(fileName)):
        continue
    semathore.acquire()
    threading.Thread(target=download,
                     args={'txt': '%s/%s' % (inx, total), 'segment': segment, 'fileName': fileName}).start()

for i in range(8):
    semathore.acquire()
final_file = open('final.ts', "wb")
for i in filelist:
    x = open(i, "rb")  # ���б��е��ļ�,��ȡ�ļ�����
    final_file.write(x.read())  # д���½���log�ļ���
    x.close()  # �ر��б��ļ�
final_file.close()
