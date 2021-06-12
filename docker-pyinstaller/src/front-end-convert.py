import os
import re
from bs4 import BeautifulSoup

DIRECTORY = 'public'

#調整inlineScript
def inlineScript(script, title):
    #替換Api網址
    script.string = script.string.replace('http://localhost/', 'api/v1')
    #移除script前三行
    script.string = script.string.split('\n', 3)[3]
    #移除script後一行
    script.string = script.string.rsplit('\n', 2)[0]
    script.string = ("""export default {
    """+script.string+"""
}""") 
    return script

#靜態html
for root, dirnames, fileNames in os.walk(DIRECTORY):
    for fileName in fileNames:
        if fileName.endswith('.html'):
            fname = os.path.join(root, fileName)
            print('Filename Html: {}'.format(fname)+' To:'+DIRECTORY+'_replace/'+fileName)
            with open(DIRECTORY+'/'+fileName, 'r', encoding='utf-8') as file:
                content = file.read()
                soup = BeautifulSoup(content, 'html.parser')

                #找尋<link>tag, href是./開頭的
                cssLinks = soup.findAll('link', {'href': re.compile('^./')})
                for cssLink in cssLinks:
                    cssLink['href'] = cssLink['href'].replace('./', 'assets/')
                #找尋<script>tag, src./開頭的
                scriptLinks = soup.findAll('script', {'src': re.compile('^./')})
                for scriptLink in scriptLinks:
                    scriptLink['src'] = scriptLink['src'].replace('./', 'assets/')
                #找尋<img>tag, src./開頭的
                imgLinks = soup.findAll('img', {'src': re.compile('^./')})
                for imgLink in imgLinks:
                    imgLink['src'] = imgLink['src'].replace('./', 'assets/')
                #找尋<a>tag, 替換href的.html為空字串
                # aLinks = soup.findAll('a')
                # for aLink in aLinks:
                    # aLink['href'] = aLink['href'].replace('.html', '')
                #替換Api連結
                scripts = soup.findAll('script', {'src': None})
                for script in scripts:
                    #替換api網址
                    script.string = script.string.replace('http://localhost/', 'api/v1')
            with open(DIRECTORY+'_replace/'+fileName, 'w', encoding='utf-8') as file:
                file.write(str(soup.prettify()))
#vue component
VUE_COMPONENT_DIRECTORY = 'resources/js/Pages'
for root, dirnames, fileNames in os.walk(DIRECTORY):
    for fileName in fileNames:
        if fileName.endswith('.html'):
            fname = os.path.join(root, fileName)
            baseFileName = os.path.splitext(fileName)[0]
            print('Filename Vue Component: {}'.format(fname)+' To:'+VUE_COMPONENT_DIRECTORY+'/'+baseFileName+'.vue')
            with open(DIRECTORY+'/'+fileName, 'r', encoding='utf-8') as file:
                content = file.read()
                soup = BeautifulSoup(content, 'html.parser')

                #找尋<title>tag
                title = soup.find('title')
                #找尋<img>tag, src./開頭的
                imgLinks = soup.findAll('img', {'src': re.compile('^./')})
                for imgLink in imgLinks:
                    imgLink['src'] = imgLink['src'].replace('./', 'assets/')
                #替換<a>tag為<inertia-link>tag
                aLinks = soup.findAll('a')
                inertiaLinks = []
                for aLink in aLinks:
                    aLink['href'] = aLink['href'].replace('./', '')
                    # aLink['href'] = aLink['href'].replace('.html', '')
                    inertiaLink = soup.new_tag('inertia-link', attrs=aLink.attrs)
                    inertiaLink.string = aLink.text
                    inertiaLinks.append(inertiaLink)
                for inertiaLink in inertiaLinks:
                    soup.a.replace_with(inertiaLink)
                #取得div#app
                appDiv = soup.find('div', {'id': 'app'})
                #建立<template>tag
                template = soup.new_tag('template')
                appDiv = appDiv.wrap(template)
            with open(VUE_COMPONENT_DIRECTORY+'/'+baseFileName+'.vue', 'w', encoding='utf-8') as file:
                #inline-css
                styleString = ''
                csss = soup.findAll('link', {'href': re.compile('^./css/A')})
                for css in csss:
                    style = soup.new_tag('style')
                    style.string = '@import \'../../../public/'+css['href'].replace('./', 'assets/')+'\';'
                    styleString += style.prettify()+'\n'
                #inline-script
                scripts = soup.findAll('script', {'src': None})
                scriptString = ''
                for script in scripts:
                    script = inlineScript(script, title)
                    scriptString += script.prettify()
                file.write(styleString+str(template.prettify())+scriptString)