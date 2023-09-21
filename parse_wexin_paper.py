import requests
from lxml import etree
import os


def get_paper_content(url):
    html = requests.get(url).text
    # print(f'html:{html}')
    con = etree.HTML(html)

    # 获取标题
    h2 = con.xpath('//h1[@class="rich_media_title "]/text()')
    h2 = ",".join(map(str, h2))
    h2 = os.linesep.join([s for s in h2.splitlines(True) if s.strip()])
    h2 = h2.rstrip()  # 去除右空行
    print(f'h2:{h2}')
    # print(h2)

    # 获取正文
    p_text = ''
    span = con.xpath('//p | //section/span')  # 通过‘|’可以增加筛选的条件
    print(f'span:{span}')
    # print(span)
    for p_tex in span:
        p_tex = p_tex.xpath('string(.)')
        p_text = p_text + p_tex + '\n'
        # print(p_tex)
    # print(p_text)

    # 保存内容
    con_text = '%s%s%s%s' % (h2, '\n', p_text, '\n')
    return con_text


if __name__ == '__main__':
    # url = input("请输入要采集的微信公众号文章地址:")
    url = "https://mp.weixin.qq.com/s/xxx"
    get_paper_content(url)
