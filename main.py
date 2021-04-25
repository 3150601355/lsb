from flask import Flask, render_template, request, jsonify
from flask.json import jsonify
from werkzeug.utils import secure_filename
import os, sys, platform, time
from PIL import Image
import numpy as np

app = Flask(__name__)

mix_src = ""
out_src = ""

@app.route('/', methods=['GET'])
def index():
    global mix_src, out_src
    mix_src = ""
    out_src = ""    

    delOldFile()

    return render_template('index.html')


def reveal_file(imgMixed):
    bytesMixed = np.array(imgMixed).flatten()
    li_file_len = (bytesMixed[0] << 24) + (bytesMixed[1]<<16) + (bytesMixed[2]<<8) + bytesMixed[3]
    
    bytesLi = bytearray()
    for i in range(0, li_file_len):
        byteData = 0
        for index in range(0, 8):
            byteData += ((bytesMixed[4 + i*8+index] & 0x01)<<index)

        bytesLi.append(byteData)
    
    return bytesLi


def hide_file(bytesBiao, bytesLi):
    
    # 文件长度假设占用4个字节（可以代表4G的文件，够用了），放在bytesBiao前面，也就是占用了第一个像素
    li_file_len = len(bytesLi)
    for i in range(4):
        bytesBiao[i] = (li_file_len & 0xFF << (24-i*8)) >> (24-i*8)

    #计算合成图的每个像素的值及透明度
    for i in range(0, li_file_len):
        byteData = bytesLi[i]
        # 隐藏每个byteData需要bytesBiao中的8个字节
        for index in range(0, 8):
            # 依次把byteData的第0位赋值：先清零再加上index位的值
            bytesBiao[4 + i*8 + index] &= 0xFE # 4：文件长度占用了bytesBiao的前4个字节
            bytesBiao[4 + i*8 + index] += ( byteData & (0x01 << index) ) >> index

    return bytesBiao


# 接收表图
@app.route('/recv_img_biao', methods=['POST'])
def recv_img_biao():
    print('recv_img_biao')
    data = request.get_data()
    # print('表data：', data)
    with open( os.path.join('static', 'img', 'biao.png'), 'wb') as f:
        f.write(data)

    do_mix()
    return ("nothing")


# 接收里图
@app.route('/recv_img_li', methods=['POST'])
def recv_img_li():    
    data = request.get_data()
    with open( os.path.join('static', 'img',  'li.jpg'), 'wb') as f:
        f.write(data)

    do_mix()

    return ("nothing")


# 接收混合后的图（待提取的图）
@app.route('/recv_img_unmix', methods=['POST'])
def recv_img_unmix():
    data = request.get_data()
    with open( os.path.join('static', 'img', 'unmix.png'), 'wb') as f:
        f.write(data)

    do_unmix()

    return ("nothing")


# 混合两张图片
@app.route('/do_mix', methods=['POST'])
def do_mix():
    print ("do_mix()")
        
    biaoPath = os.path.join('static','img',  'biao.png')
    liPath = os.path.join('static', 'img', 'li.jpg')
    tankPath = os.path.join('static', 'img', 'tank-' + str(int(time.time())) + '.png')

    if (not os.path.exists(biaoPath) )  or (not os.path.exists(liPath) ):
        return

    

    #将表图片中的像素数据化为一维数组bytesBiao
    imgBiao = Image.open(biaoPath)
    height, width, channel = np.array(imgBiao).shape
    bytesBiao = np.array(imgBiao).flatten()

    # 里图也是类似
    with open(liPath, 'rb') as f:
        bytesLi = f.read()

    # 把里图数据嵌入表图
    bytesBiao = hide_file(bytesBiao, bytesLi)

    # 把表图数据变回原来的维度并保存
    reshapedBytesBiao = np.reshape(bytesBiao, (height, width, channel))
    imgMixed = Image.fromarray(reshapedBytesBiao)
    imgMixed.save( tankPath, 'PNG')

    # 在网页上显示混合后的图
    global out_src, mix_src
    mix_src = tankPath
    out_src = ""
    return ("nothing")


@app.route('/do_unmix', methods=['POST'])
def do_unmix():
    print ("do_unmix()")
    outPath = os.path.join('static', 'img', 'out-' + str(int(time.time())) + '.jpg')

    # 提取里图
    imgMixed = Image.open(os.path.join('static', 'img', 'unmix.png'))
    bytesLi = reveal_file(imgMixed)
    with open(outPath,'wb') as f:
        f.write(bytesLi)

    global out_src, mix_src
    out_src = outPath
    mix_src = ""    
    return ("nothing")


@app.route('/get_data', methods=['GET'])
def get_data():
    print('get_data()')
    print(mix_src, out_src)
    return jsonify(mix_src = mix_src, out_src = out_src)

def delOldFile():
    for root, dirs, files in os.walk(os.path.join('static', 'img'), topdown=False):
        for name in files:
            # print(name)
            if name != "bg.png":
                os.remove(os.path.join(root, name))

if __name__ == '__main__':
    app.run()