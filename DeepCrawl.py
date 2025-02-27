from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import re
import time
import sys
from selenium.webdriver.edge.options import Options
import datetime
import ollama

def judgeartical(soup : BeautifulSoup) -> bool:
    keywords = ['字体', '来源']
    pagination_found = any(keyword in soup.get_text() for keyword in keywords)
    if pagination_found:
        return True
    else:
        return False

def judgecolumn(soup: BeautifulSoup) -> bool:
    pagination_keywords = ['上一页', '下一页', '分页', '下页', '尾页', 'next']
    page_text = soup.get_text()
    title_text = soup.title.get_text() if soup.title else ''
    combined_text = page_text + title_text
    pagination_found = any(keyword in combined_text for keyword in pagination_keywords)
    pagination_found |= any(
        keyword in a.get('title', '') for a in soup.find_all('a') for keyword in pagination_keywords)
    if pagination_found:
        return True
    else:
        return False

def get_article(link, wd):
    if not link.startswith("http"):
        link = "http://" + link
    wd.get(link)
    article = None
    try:
        article_element = wd.find_element(By.CSS_SELECTOR, '.content_body_box, .bt_content, .trs_editor_view, .TRS_UEDITOR, .trs_paper_default, .bg_middle,'
                                                           ' .trs_web, .trs_word, .view, .trs_external, .b12c, .TRS_Editor, .article_con,'
                                                           '.article_con_title, #zoom, .detail-text-content, #Zoom, .pages_content, #detail')
        article = article_element.text + "\n"
    except:
        article = "无法获取正文内容\n" + str(datetime.date.today())
    title = None
    try:
        title = wd.find_element(By.CSS_SELECTOR, '.sp_title, .con-title, #ti, h1, h2, .title, .detail-title').text
    except:
        try:
            title = wd.find_element(By.CSS_SELECTOR, '.article_title').text
        except:
            title = str(datetime.date.today()) + article.splitlines()[0]
    return title, article

def get_date(url : str) -> str:
    match = re.search(r"20\d{2}(?:/\d{1,2}){1,2}|20\d{6}", url)
    if match:
        date = match.group(0)
    else:
        match = re.search(r"20\d{4}", url)
        if match:
            date = match.group(0)
        else:
            date = "(no_date)"
    return date

def get_summarise_with_ollama(title, article) -> str:
    prompt = f"""
        请根据以下的标题和正文,做100个字左右的总结:
        标题：{title}
        正文：{article}
        请仅返回总结即可，最多不超过一百二十个字，不要提供任何额外的解释或内容.
        """
    if len(article) >= 20:
        response = ollama.chat(model="qwen2.5:7b", messages=[{"role": "user", "content": prompt}])
        summarise = response['message']['content']
    else:
        summarise = "无正文内容。"
    return summarise

def getcolumn(link : str, wd):
    wd.get(link)
    titles = []
    links = []
    dates = []
    prev_page_content = ""
    pages = 0
    while True:
        page_source = wd.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        try:
            next_button = wd.find_element(By.XPATH,
                                          "//a[text()='下一页' or contains(@title, '下一页') or text()='下页' or contains(@title, '下页') or contains(@class, 'lucidity_pgBtn') and contains(@class, 'lucidity_pgNext') or contains(@class, 'default_pgBtn') and contains(@class, 'default_pgNext')]")
        except Exception:
            break
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            text1 = tag.get_text(strip=True)  # 提取 > < 之间的文本内容
            text2 = tag.get('title', '').strip()
            text = text2 if text2 else text1  # 优先选择 title 中的完整文本
            if text == "":
                text = "暂无"
            elif href == "" or len(text) < 6:
                continue
            links.append(href)
            titles.append(text)
            date = get_date(href)
            dates.append(date)

        pages += 1
        if pages >= 20:
            break
        if next_button.is_enabled():
            try:
                current_page_content = wd.page_source
                if current_page_content == prev_page_content:
                    break
                prev_page_content = current_page_content
                try:
                    next_button.click()
                except Exception:
                    try:
                        wd.execute_script("arguments[0].click();", next_button)
                    except Exception:
                        break
                time.sleep(0.4)  # 等待页面加载完成
            except Exception:
                break
        else:
            break
    return links, titles, dates

def deepcrawl(link : str, depth : int, wd):
    if not link.startswith("http"):
        link = "http://" + link
    wd.get(link)
    characteristic = re.search(r"(?<=//)([^/]+)",link).group(0)
    page_source = wd.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    #print(soup)
    links = [link]
    titles = ["主页"]
    date = get_date(link)
    dates = [date]
    savelinks = []
    savetitles = []
    savedates = []
    crawled = [link]
    if judgecolumn(soup):  # 判断列表
        columnlinks, columntitles, columndates = getcolumn(link, wd)
        for columnlink, columntitle, columndate in zip(columnlinks, columntitles, columndates):
            # print(columnlink)
            if characteristic not in columnlink:
                if columnlink.startswith('/'):
                    columnlink = link + columnlink[1::]
                elif columnlink.startswith('./'):
                    if "htm" in link:
                        cut_link = re.sub(r'/[^/]+$', '/', link)
                        columnlink = cut_link + columnlink[2::]
                    else:
                        columnlink = link + columnlink[2::]
                elif columnlink.startswith('../'):
                    columnlink = "http://" + characteristic + columnlink[8::]
                else:
                    continue
            links.append(columnlink)
            titles.append(columntitle)
            dates.append(columndate)
    else:
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            #print(href)
            text1 = tag.get_text(strip=True)  # 提取 > < 之间的文本内容
            text2 = tag.get('title', '').strip()
            text = text2 if text2 else text1  # 优先选择 title 中的完整文本
            if href.startswith('/'):
                href = link + href[1::]
            elif href.startswith('./'):
                if "htm" in href:
                    cut_href = re.sub(r'/[^/]+$', '/', href)
                    href = cut_href + href[2::]
                else:
                    href = link + href[2::]
            elif href.startswith('../'):
                href = "http://" + characteristic + href[8::]
            else:
                continue
            if href in links:
                if len(text) > len(titles[links.index(href)]):
                    titles[links.index(href)] = text
                else:
                    continue
            if text in titles:
                if href in links:
                    continue
            if href.startswith("www"):
                href = "https://" + href
            if not href.startswith("http"):
                href = "http://" + href
            links.append(href)
            titles.append(text)
            date = get_date(href)
            dates.append(date)
    savelinks = savelinks + links
    savetitles = savetitles + titles
    savedates = savedates + dates
    for i in range(depth):
        newlinks = []
        newtitles = []
        newdates = []
        for index, link in enumerate(links):
            sys.stdout.write(f'\r--正在爬取深度{i + 1}，进度{round(index / len(links) * 100, 2):.2f}%...')  # \r 会将光标移到行首，覆盖上一行
            sys.stdout.flush()
            if link in crawled:
                continue
            else:
                crawled.append(link)
            try:
                wd.get(link)
            except Exception:
                continue
            try:
                page_source = wd.page_source
            except Exception:
                continue
            soup = BeautifulSoup(page_source, 'html.parser')
            if judgecolumn(soup):  # 判断列表
                columnlinks, columntitles, columndates = getcolumn(link, wd)
                for columnlink, columntitle, columndate in zip(columnlinks, columntitles, columndates):
                    if characteristic not in columnlink:
                        if columnlink.startswith('/'):
                            columnlink = link + columnlink[1::]
                        elif columnlink.startswith('./'):
                            if "htm" in link:
                                cut_link = re.sub(r'/[^/]+$', '/', link)
                                columnlink = cut_link + columnlink[2::]
                            else:
                                columnlink = link + columnlink[2::]
                        elif columnlink.startswith('../'):
                            columnlink = "http://" + characteristic + columnlink[8::]
                        else:
                            continue
                    newlinks.append(columnlink)
                    newtitles.append(columntitle)
                    newdates.append(columndate)
            elif judgeartical(soup):  # 判断文章
                pass
            else:
                for tag in soup.find_all('a', href=True):
                    href = tag['href']
                    text1 = tag.get_text(strip=True)  # 提取 > < 之间的文本内容
                    text2 = tag.get('title', '').strip()
                    text = text2 if text2 else text1  # 优先选择 title 中的完整文本
                    if href.startswith('/'):
                        href = link + href[1::]
                    elif href.startswith('./'):
                        if "htm" in href:
                            cut_href = re.sub(r'/[^/]+$', '/', href)
                            href = cut_href + href[2::]
                        else:
                            href = link + href[2::]
                    elif href.startswith('../'):
                        href = "http://" + characteristic + href[8::]
                    else:
                        continue
                    if href in newlinks:
                        continue
                    if text in newtitles:
                        if href in newlinks:
                            continue
                    if not href.startswith("http"):
                        href = "http://" + href
                    newlinks.append(href)
                    newtitles.append(text)
                    date = get_date(href)
                    newdates.append(date)
        sys.stdout.write(f'\r--深度{i + 1}爬取完成!--\n')  # \r 会将光标移到行首，覆盖上一行
        sys.stdout.flush()
        for link, title, date in zip(newlinks, newtitles, newdates):
            if link in savelinks:
                continue
            else:
                savetitles.append(title)
                savelinks.append(link)
                savedates.append(date)
        links = newlinks
    return savetitles, savelinks, savedates

def crawl_main(link : str, depth : int):
    spinner = ['|', '/', '-', '\\']
    i = 1
    titles = ""
    dates = ""
    links = ""
    summarises =""
    Links = []
    articles = []
    Titles = []
    Dates = []
    with open('./DC标题UP/标题.txt', 'w', encoding='utf8') as f:
        pass
    with open('./DC链接UP/链接.txt', 'w', encoding='utf8') as f:
        pass
    with open('./日期UP/日期UP.txt', 'w', encoding='utf8') as f:
        pass
    with open('./总结UP/总结UP.txt', 'w', encoding='utf8') as f:
        pass
    with open("./DC链接总集/链接总集.txt", 'r', encoding='utf8') as f:
        content = f.readline()
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    wd = webdriver.Edge(options=options)
    wd.implicitly_wait(3)
    print("爬取中...")
    totaltitles, totallinks, totaldates = deepcrawl(link, depth, wd)
    print("写入中...")
    for title, link, date in zip(totaltitles, totallinks, totaldates):
        if len(title) > 65 or len(link) > 95:
            continue
        if link in content:
            continue
        Links.append(link)
        if len(title) < 1:
            title = "暂无"
        Titles.append(title)
        Dates.append(date)
        if len(title) < 65:
            title = title + " " * (65 - len(title))
        if len(link) < 95:
            link = link + " " * (95 - len(link))
        if len(date) < 10:
            date = date + " " * (10 - len(date))
        links = links + link
        titles = titles + title
        dates = dates + date
    sTitles = []
    for link in Links:
        sys.stdout.write(f'\r{spinner[i % 4]} 正在获取内容{round(i / len(Links) * 100, 2):.2f}%...')  # \r 会将光标移到行首，覆盖上一行
        sys.stdout.flush()
        if Dates[i-1] == "(no_date)":
            article = "无正文内容。"
            Title = "暂无"
        else:
            Title, article = get_article(link, wd)
        i += 1
        sTitles.append(Title)
        articles.append(article)
    i = 1
    for sTitle, article in zip(sTitles, articles):
        sys.stdout.write(f'\r{spinner[i % 4]} 正在总结{round(i / len(sTitles) * 100, 2):.2f}%...')  # \r 会将光标移到行首，覆盖上一行
        sys.stdout.flush()
        summarise = get_summarise_with_ollama(sTitle, article)
        if len(summarise) < 120:
            summarise = summarise + " " * (120 - len(summarise))
        else:
            summarise = summarise[0: 120]
        summarises = summarises + summarise
        i += 1
    wd.quit()
    with open('./DC标题总集/标题总集.txt', 'a', encoding='utf8') as f:
        f.write(titles)
    with open('./DC链接总集/链接总集.txt', 'a', encoding='utf8') as f:
        f.write(links)
    with open('./日期总集/日期总集.txt', 'a', encoding='utf8') as f:
        f.write(dates)
    with open('./总结/总结.txt', 'a', encoding='utf8') as f:
        f.write(summarises)
    with open('./DC标题UP/标题.txt', 'a', encoding='utf8') as f:
        f.write(titles)
    with open('./DC链接UP/链接.txt', 'a', encoding='utf8') as f:
        f.write(links)
    with open('./日期UP/日期UP.txt', 'a', encoding='utf8') as f:
        f.write(dates)
    with open('./总结UP/总结UP.txt', 'a', encoding='utf8') as f:
        f.write(summarises)