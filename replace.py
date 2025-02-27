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