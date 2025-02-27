from DeepCrawl import *
from RAG.utils import ReadFiles
from RAG.Embeddings import OllamaEmbedding
from RAG.VectorBase import VectorStore
import requests
import json
from RAG.zilliz_data_base import zilliz
from docx import Document
from LLMprompt import *

#--------------------------------------------------------爬取并插入----------------------------------------------------

def crawlAndEmbed(link : str, depth : int):
    #-------------------------------------------Deep Crawl-----------------------------------------
    print("------------------------目标网站爬取中---------------------\n")
    crawl_main(link, depth)
    print("**************************爬取结束************************\n\n")

    #-----------------------------------------------------------------------------------------------
    #
    #---------------------------------------向量化创建数据库-------------------------------------------

    print("---------------------创建新向量本地库-----------------------\n")
    embedding = OllamaEmbedding() # 调用Ollama模型

    titles = ReadFiles('./DC标题UP').get_content(max_token_len=65, cover_content=0,is_split_point=False)    # 分块标题
    links = ReadFiles('./DC链接UP').get_content(max_token_len=95, cover_content=0,is_split_point=False)    # 分块链接
    dates = ReadFiles('./日期UP').get_content(max_token_len=10, cover_content=0,is_split_point=False)    # 分块日期
    summarises = ReadFiles('./总结UP').get_content(max_token_len=120, cover_content=0,is_split_point=False)    # 分块总结
    datevector = VectorStore(dates) # 创建date类
    datevector.persistTexts(path='DCstorage', name="datesUP")  # links分块保存
    linkvector = VectorStore(links)       # 创建links类
    linkvector.persistTexts(path='DCstorage', name="linksUP")        # links分块保存
    titlesvector = VectorStore(titles)      # 创建标题类
    titlesvector.get_vector(EmbeddingModel=embedding)     # 标题向量化
    titlesvector.persistTexts(path='DCstorage', name="titlesUP")         # 标题分块保存
    titlesvector.persistVectors(path='DCstorage', name="titleVectorsUP")        # 标题向量化保存
    summarisesvector = VectorStore(summarises)  # 创建标题类
    summarisesvector.get_vector(EmbeddingModel=embedding)  # 标题向量化
    summarisesvector.persistTexts(path='DCstorage', name="summarisesUP")  # 标题分块保存
    summarisesvector.persistVectors(path='DCstorage', name="summariseVectorsUP")  # 标题向量化保存
    print("*********************新向量本地库创建完成********************\n\n")

    # --------------------------------------------------------------------------------------------------

    #------------------------------------------更新数据库-------------------------------------------------

    print("--------------------更新线上及本地向量库---------------------\n")
    CLUSTER_ENDPOINT = "https://in03-029fdb297cf97d2.serverless.ali-cn-hangzhou.cloud.zilliz.com.cn"
    Token = "1169f81dcc8c7a6938167058e9b423e2d89540d53be97e90ea285ad31adde3c08eaaeec1d36007811945342344cb2831b8cd5862"

    Zilliz = zilliz(CLUSTER_ENDPOINT,Token)

    try:
        with open('./DCstorage/titleVectors.json', 'r', encoding='utf-8') as file:
            vectors = json.load(file)
    except json.JSONDecodeError:
        vectors = []

    try:
        with open('./DCstorage/summariseVectors.json', 'r', encoding='utf-8') as file:
            summarisevectors = json.load(file)
    except json.JSONDecodeError:
        summarisevectors = []

    Zilliz.insert('./DCstorage/titleVectorsUP.json', 'titles3b', oringinal_len = len(vectors))
    Zilliz.insert('./DCstorage/summariseVectorsUP.json', 'summarises3b', oringinal_len=len(summarisevectors))

    try:
        with open('./DCstorage/titleVectorsUP.json', 'r', encoding='utf-8') as file:
            vectorsUP = json.load(file)
    except json.JSONDecodeError:
        vectorsUP = []
        print("----未发现标题向量新增项----")
    for vectorUP in vectorsUP:
        vectors.append(vectorUP)
    with open('./DCstorage/titleVectors.json', 'w', encoding='utf-8') as f:
        json.dump(vectors, f, ensure_ascii=False)
    with open('./DCstorage/titleVectorsUP.json', 'w', encoding='utf-8') as file:
        pass

    try:
        with open('./DCstorage/titles.json', 'r', encoding='utf-8') as file:
            titles = json.load(file)
    except json.JSONDecodeError:
        titles = []
    try:
        with open('./DCstorage/titlesUP.json', 'r', encoding='utf-8') as file:
            titlesUP = json.load(file)
    except json.JSONDecodeError:
        titlesUP = []
        print("----未发现标题新增项----")
    for titleUP in titlesUP:
        titles.append(titleUP)
    with open('./DCstorage/titles.json', 'w', encoding='utf-8') as f:
        json.dump(titles, f, ensure_ascii=False)
    with open('./DCstorage/titlesUP.json', 'w', encoding='utf-8') as file:
        pass

    try:
        with open('./DCstorage/links.json', 'r', encoding='utf-8') as file:
            links = json.load(file)
    except json.JSONDecodeError:
        links = []
    try:
        with open('./DCstorage/linksUP.json', 'r', encoding='utf-8') as file:
            linksUP = json.load(file)
    except json.JSONDecodeError:
        linksUP = []
        print("----未发现链接新增项----")
    for linkUP in linksUP:
        links.append(linkUP)
    with open('./DCstorage/links.json', 'w', encoding='utf-8') as f:
        json.dump(links, f, ensure_ascii=False)
    with open('./DCstorage/linksUP.json', 'w', encoding='utf-8') as file:
        pass

    try:
        with open('./DCstorage/dates.json', 'r', encoding='utf-8') as file:
            dates = json.load(file)
    except json.JSONDecodeError:
        dates = []
    try:
        with open('./DCstorage/datesUP.json', 'r', encoding='utf-8') as file:
            datesUP = json.load(file)
    except json.JSONDecodeError:
        datesUP = []
        print("----未发现日期新增项----")
    for dateUP in datesUP:
        dates.append(dateUP)
    with open('./DCstorage/dates.json', 'w', encoding='utf-8') as f:
        json.dump(dates, f, ensure_ascii=False)
    with open('./DCstorage/datesUP.json', 'w', encoding='utf-8') as file:
        pass

    try:
        with open('./DCstorage/summariseVectorsUP.json', 'r', encoding='utf-8') as file:
            summarisevectorsUP = json.load(file)
    except json.JSONDecodeError:
        summarisevectorsUP = []
        print("----未发现总结向量新增项----")
    for summarisevectorUP in summarisevectorsUP:
        summarisevectors.append(summarisevectorUP)
    with open('./DCstorage/summariseVectors.json', 'w', encoding='utf-8') as f:
        json.dump(summarisevectors, f, ensure_ascii=False)
    with open('./DCstorage/summariseVectorsUP.json', 'w', encoding='utf-8') as file:
        pass

    try:
        with open('./DCstorage/summarises.json', 'r', encoding='utf-8') as file:
            summarises = json.load(file)
    except json.JSONDecodeError:
        summarises = []
    try:
        with open('./DCstorage/summarisesUP.json', 'r', encoding='utf-8') as file:
            summarisesUP = json.load(file)
    except json.JSONDecodeError:
        summarisesUP = []
        print("----未发现总结新增项----")
    for summariseUP in summarisesUP:
        summarises.append(summariseUP)
    with open('./DCstorage/summarises.json', 'w', encoding='utf-8') as f:
        json.dump(summarises, f, ensure_ascii=False)
    with open('./DCstorage/summarisesUP.json', 'w', encoding='utf-8') as file:
        pass
    print("********************所有数据库更新完成*********************\n\n")

    #----------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------

#------------------------------------------------Zilliz查找向量-----------------------------------------------------

def onlineSearch(query : str, answerK : int):
    CLUSTER_ENDPOINT = "https://in03-029fdb297cf97d2.serverless.ali-cn-hangzhou.cloud.zilliz.com.cn"
    Token = "1169f81dcc8c7a6938167058e9b423e2d89540d53be97e90ea285ad31adde3c08eaaeec1d36007811945342344cb2831b8cd5862"
    Zilliz = zilliz(CLUSTER_ENDPOINT,Token)
    all = []
    print("----------------------线上查询中------------------------\n")
    embedding = OllamaEmbedding()
    with open(r'./DCstorage/titles.json', 'r', encoding='utf-8') as file:
        titles = json.load(file)
    with open(r'./DCstorage/links.json', 'r', encoding='utf-8') as file:
        links = json.load(file)
    with open(r'./DCstorage/dates.json', 'r', encoding='utf-8') as file:
        dates = json.load(file)
    with open(r'./DCstorage/summarises.json', 'r', encoding='utf-8') as file:
        summarises = json.load(file)
    query = query
    queryvector = embedding.get_embedding(query)
    titlesanswer = Zilliz.get_search('titles3b' , [queryvector], answerK)
    summarisesanswer = Zilliz.get_search('summarises3b', [queryvector], answerK)
    #print(answer)
    for i in range(0, len(titlesanswer[0])):
        id = titlesanswer[0][i]['id']
        all.append(dates[id].strip() + "发布的" + titles[id].strip() + "的链接:" + links[id].strip() + "\n总结: " + summarises[id].strip())

    for i in range(0, len(summarisesanswer[0])):
        id = summarisesanswer[0][i]['id']
        all.append(dates[id].strip() + "发布的" + titles[id].strip() + "的链接:" + links[id].strip() + "\n总结: " + summarises[id].strip())
    print("**********************线上查询完成************************\n\n")
    print(all)
    return all

#------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------调用jina Rerank-----------------------------------------------------

def jinaRerank(query : str, all : list[str], answerK : 3):
    text = []
    print("-------------------After JINArerank------------------\n")
    url = 'https://api.jina.ai/v1/rerank'
    headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer jina_162558b5313a41ffa9f3ae7608d29058_3UXDoKR1zXcAF0DUYZPtCxJmDVV"
}
    data = {
        "model": "jina-reranker-v2-base-multilingual",
        "query": query,
        "top_n": answerK,
        "documents": all
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = json.loads(response.text)

    for result in response_data['results']:
        text.append(result['document']['text'])
        # print(text)
    all_text = "\n".join([f"{item}" for i, item in enumerate(text)])
    print("********************Rerank Completed*****************\n\n")
    return all_text

#------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------main-------------------------------------------------------------

if __name__ == "__main__":
    current_date = str(datetime.date.today())
    # # ------------------------日常更新-----------------------
    # urls = [
    #     # "https://www.gov.cn/zhengce/wenjian/zhongyang/home_0.htm",  # 中国政府网中央有关文件
    #     # "https://www.gov.cn/zhengce/zuixin/home.htm", # 中国政府网最新政策
    #     # "https://www.ndrc.gov.cn/xxgk/zcfb/ghxwj/",  # 中国发改委规范性文件
    #     # "https://www.ndrc.gov.cn/xwdt/tzgg/index.html", # 中国发改委通知公告
    #     # "https://www.mee.gov.cn/zcwj/bwj/wj/index.shtml", # 中国生态环境部文件
    #     # "https://www.mee.gov.cn/zcwj/bwj/gg/index.shtml", # 中国生态环境部公告
    #     # "https://www.jiangxi.gov.cn/",  # 江西省政府
    #     # "https://www.jiangxi.gov.cn/col/col48473/index.html?uid=406462&pageNum=1", # 江西省政府文件
    #     # "https://www.jiangxi.gov.cn/col/col48474/index.html?uid=406478&pageNum=1", # 江西省办公厅文件
    #     # "https://www.jiangxi.gov.cn/col/col396/index.html?uid=45663&pageNum=1", # 江西省政府最新发布
    #     # "https://www.jiangxi.gov.cn/col/col4929/index.html?vc_xxgkarea=696076408",  # 江西省工信厅政策法规
    #     # "http://drc.jiangxi.gov.cn/col/col14590/index.html?vc_xxgkarea=014500858&uid=470259&pageNum=1",  # 江西省发改委通知公告
    #     # "http://drc.jiangxi.gov.cn/col/col14651/index.html?vc_xxgkarea=014500858%23div&uid=376208&pageNum=1", # 江西省发改委政策法规
    #     "http://sthjt.jiangxi.gov.cn/col/col47550/index.html?uid=380055&pageNum=1", # 江西省生态环境厅头条
    #     "http://sthjt.jiangxi.gov.cn/col/col42149/index.html?uid=380055&pageNum=1", # 江西省生态环境厅文件通知
    # ]
    # titles = [
    #     # "中国政府网中央有关文件",
    #     # "中国政府网最新政策",
    #     # "中国发改委规范性文件",
    #     # "中国发改委通知公告",
    #     # "中国生态环境部文件",
    #     # "中国生态环境部公告",
    #     # "江西省政府网",
    #     # "江西省政府文件",
    #     # "江西省办公厅文件",
    #     # "江西省政府最新发布",
    #     # "江西省工信厅政策法规",
    #     # "江西省发改委通知公告",
    #     # "江西省发改委政策法规",
    #     "江西省生态环境厅头条",
    #     "江西省生态环境厅文件通知",
    # ]
    # with open("UpdatedDate.txt", "r") as f:
    #     updatedDate = str(f.readline())
    # if updatedDate != current_date:
    #     print("即将开始例行更新，请勿退出！预计耗时约2分钟。")
    #     for url, title in zip(urls, titles):
    #         print(f"正在更新: {title} ({url})")
    #         crawlAndEmbed(url, 0)
    #     with open("UpdatedDate.txt", 'w') as f:
    #         f.write(current_date)
    #     print("更新完成！")
    # else:
    #     print("今天已经更新过，无需更新。")
    # -------------------------日常更新--------------------

    mode = input("->1<- 深度爬取\n->2<- 政策搜索\n->3<- 原文转word\n选择:")     # 模式输入

    if mode == "1":     #   深 度 爬 取
        link = input("中国政府网中央有关文件: https://www.gov.cn/zhengce/wenjian/zhongyang/home_0.htm\n"
                    "中国政府网最新政策: https://www.gov.cn/zhengce/zuixin/home.htm\n"
                    "中国发改委规范性文件: https://www.ndrc.gov.cn/xxgk/zcfb/ghxwj/\n"
                    "中国发改委通知公告: https://www.ndrc.gov.cn/xwdt/tzgg/index.html\n"
                    "中国生态环境部文件: https://www.mee.gov.cn/zcwj/bwj/wj/index.shtml\n"
                    "中国生态环境部公告: https://www.mee.gov.cn/zcwj/bwj/gg/index.shtml\n "
                    "江西省政府https://www.jiangxi.gov.cn/\n"
                    "江西省政府文件https://www.jiangxi.gov.cn/col/col48473/index.html?uid=406462&pageNum=1\n"
                    "江西省办公厅文件https://www.jiangxi.gov.cn/col/col48474/index.html?uid=406478&pageNum=1\n"
                    "江西省政府最新发布https://www.jiangxi.gov.cn/col/col396/index.html?uid=45663&pageNum=1\n "
                    "江西省工信厅政策法规https://www.jiangxi.gov.cn/col/col4929/index.html?vc_xxgkarea=696076408\n"
                    "江西省发改委通知公告http://drc.jiangxi.gov.cn/col/col14590/index.html?vc_xxgkarea=014500858&uid=470259&pageNum=1\n"
                    "江西省发改委政策法规http://drc.jiangxi.gov.cn/col/col14651/index.html?vc_xxgkarea=014500858%23div&uid=376208&pageNum=1\n"
                    "江西省生态环境厅头条http://sthjt.jiangxi.gov.cn/col/col47550/index.html?uid=380055&pageNum=1\n"
                    "江西省生态环境厅文件通知http://sthjt.jiangxi.gov.cn/col/col42149/index.html?uid=380055&pageNum=1\n"
                     "link: ")  # 爬取目标链接
        crawlAndEmbed(link, 0)  #爬取并向量化保存     江西省上个月有哪些与能源相关的政策

    elif mode == "2":        # 查 找 原 文
        query = input("query: ")  # 问题输入
        processed_query = query_preprocessing(query)    # 问题预处理
        all = onlineSearch(processed_query, 100)   # 使用Zilliz向量库， answerK:返回多少条相似度高的
        all_text = jinaRerank(processed_query, all, 10)    #使用jinaRerank  输出1条(answerK)
        print(answer_postprocessing(processed_query, all_text))   # LLM润色回答

    elif mode == "3":   # 原文转word
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        wd = webdriver.Edge(options=options)
        wd.implicitly_wait(3)
        url = input("输入目标url: ")
        print("请稍后......")
        title, article = get_article(url, wd)
        wd.quit()
        doc = Document()
        doc.add_heading(title, level=1)
        doc.add_paragraph(article)
        file_name = f"{current_date + title}.docx"
        doc.save(file_name)   #保存在根路径
        print(f"文章 '{title}' 已保存为 Word 文件：{file_name}")

    else:               # 其他情况
        raise "输入有误"
#---------------------------------------------------------------------------------------------------------------