# -*-coding:utf-8 -*-
import random
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from urllib.request import urlretrieve
from selenium import webdriver
from bs4 import BeautifulSoup
import PIL.Image as image
import re


class Crack():
    def __init__(self, username, passwd):
        self.url = 'https://passport.bilibili.com/login'
        self.browser = webdriver.Chrome('chromedriver')
        self.wait = WebDriverWait(self.browser, 15)
        self.BORDER = 6
        self.passwd = passwd
        self.username = username

    def open(self):
        """
        打开浏览器,并输入查询内容
        """
        self.browser.get(self.url)
        keyword = self.wait.until(EC.presence_of_element_located((By.ID, 'login-username')))
        keyword.send_keys(self.username)
        keyword = self.wait.until(EC.presence_of_element_located((By.ID, 'login-passwd')))
        keyword.send_keys(self.passwd)
        # bowton.click()

    def get_images(self, bg_filename='bg.jpg', fullbg_filename='fullbg.jpg'):
        """
        获取验证码图片
        :return: 图片的location信息
        """
        bg = []
        fullgb = []
        while bg == [] and fullgb == []:
            bf = BeautifulSoup(self.browser.page_source, 'lxml')
            bg = bf.find_all('div', class_='gt_cut_bg_slice')
            fullgb = bf.find_all('div', class_='gt_cut_fullbg_slice')
        bg_url = re.findall('url\(\"(.*)\"\);', bg[0].get('style'))[0].replace('webp', 'jpg')
        fullgb_url = re.findall('url\(\"(.*)\"\);', fullgb[0].get('style'))[0].replace('webp', 'jpg')
        bg_location_list = []
        fullbg_location_list = []
        for each_bg in bg:
            location = {}
            location['x'] = int(re.findall('background-position: (.*)px (.*)px;', each_bg.get('style'))[0][0])
            location['y'] = int(re.findall('background-position: (.*)px (.*)px;', each_bg.get('style'))[0][1])
            bg_location_list.append(location)
        for each_fullgb in fullgb:
            location = {}
            location['x'] = int(re.findall('background-position: (.*)px (.*)px;', each_fullgb.get('style'))[0][0])
            location['y'] = int(re.findall('background-position: (.*)px (.*)px;', each_fullgb.get('style'))[0][1])
            fullbg_location_list.append(location)

        urlretrieve(url=bg_url, filename=bg_filename)
        print('缺口图片下载完成')
        urlretrieve(url=fullgb_url, filename=fullbg_filename)
        print('背景图片下载完成')
        return bg_location_list, fullbg_location_list

    def get_merge_image(self, filename, location_list):
        """
        根据位置对图片进行合并还原
        :filename:图片
        :location_list:图片位置
        """
        im = image.open(filename)
        new_im = image.new('RGB', (260, 116))
        im_list_upper = []
        im_list_down = []

        for location in location_list:
            if location['y'] == -58:
                im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 166)))
            if location['y'] == 0:
                im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))

        new_im = image.new('RGB', (260, 116))

        x_offset = 0
        for im in im_list_upper:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        x_offset = 0
        for im in im_list_down:
            new_im.paste(im, (x_offset, 58))
            x_offset += im.size[0]

        new_im.save(filename)

        return new_im

    def get_merge_image(self, filename, location_list):
        """
        根据位置对图片进行合并还原
        :filename:图片
        :location_list:图片位置
        """
        im = image.open(filename)
        new_im = image.new('RGB', (260, 116))
        im_list_upper = []
        im_list_down = []

        for location in location_list:
            if location['y'] == -58:
                im_list_upper.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 166)))
            if location['y'] == 0:
                im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x']) + 10, 58)))

        new_im = image.new('RGB', (260, 116))

        x_offset = 0
        for im in im_list_upper:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

        x_offset = 0
        for im in im_list_down:
            new_im.paste(im, (x_offset, 58))
            x_offset += im.size[0]

        new_im.save(filename)

        return new_im

    def is_pixel_equal(self, img1, img2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]
        threshold = 60
        if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(
                pix1[2] - pix2[2] < threshold)):
            return True
        else:
            return False

    def get_gap(self, img1, img2):
        """
        获取缺口偏移量
        :param img1: 不带缺口图片
        :param img2: 带缺口图片
        :return:
        """
        left = 43
        for i in range(left, img1.size[0]):
            for j in range(img1.size[1]):
                if not self.is_pixel_equal(img1, img2, i, j):
                    left = i
                    return left
        return left

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        ltrack = []
        rtrack = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 7 / 5
        mid1 = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0
        v1 = 0
        while current <= 230:
            a = 30
            v01 = v1
            # 当前速度v = v0 + at
            v1 = v01 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            rmove = v01 * t + 15 / 31 * a * t * t
            # 当前位移
            current += rmove
            # 加入轨迹
            rtrack.append(round(rmove))
        # 左轨迹
        while current > distance:
            if current > mid:
            # 加速度为正2
                a = 3
            else:
                # 加速度为负3
                a = -random.randint(2, 3)
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            lmove = -(v0 * t + 15 / 31 * a * t * t)
            # 当前位移
            current += lmove
            if lmove>0:
                break
            # 加入轨迹
            ltrack.append(round(lmove))
        print(current)
        return (ltrack, rtrack)


    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        while True:
            try:
                slider = self.browser.find_element_by_xpath("//div[@class='gt_slider_knob gt_show']")
                break
            except:
                time.sleep(0.5)
        return slider

    def move_to_gap(self, slider, ltrack, rtrack):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.browser).click_and_hold(slider).perform()
        time.sleep(0.4)
        while rtrack:
            x = random.choice(rtrack)
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
            rtrack.remove(x)
        time.sleep(0.4)

        while ltrack:
            x = random.choice(ltrack)
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
            ltrack.remove(x)
        ActionChains(self.browser).release().perform()

    def login(self):
        """
        登录验证，失败则继续
        :return:
        """
        for _ in range(10):
            if self.crack():
                print('验证通过，正在登录..')
                break
            else:
                print('验证失败，尝试重新登录..')

    def crack(self):
        # 打开浏览器
        self.open()

        # 保存的图片名字
        bg_filename = 'bg.jpg'
        fullbg_filename = 'fullbg.jpg'

        # 获取图片
        bg_location_list, fullbg_location_list = self.get_images(bg_filename, fullbg_filename)

        # 根据位置对图片进行合并还原
        bg_img = self.get_merge_image(bg_filename, bg_location_list)
        fullbg_img = self.get_merge_image(fullbg_filename, fullbg_location_list)

        # 获取缺口位置
        gap = self.get_gap(fullbg_img, bg_img)
        print('缺口位置', gap)

        ltrack, rtrack = self.get_track(gap - self.BORDER)
        print('滑动滑块')
        print(ltrack, rtrack)

        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.gt_holder.gt_float')))
        # 点按呼出缺口
        slider = self.get_slider()
        time.sleep(0.5)
        # 拖动滑块到缺口处
        self.move_to_gap(slider, ltrack, rtrack)

        try:
            success = self.wait.until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, 'gt_info_type'), '验证通过:'))
            return True
        except:
            return False


if __name__ == '__main__':
    crack = Crack('asd', 'gaibianzj6')
    # crack.crack()
    crack.login()
