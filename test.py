import time

from DeepCrawl import *
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from main import *
#     "https://www.gov.cn/zhengce/wenjian/zhongyang/home_0.htm",  # 中国政府网中央有关文件  !!
#     "https://www.gov.cn/zhengce/zuixin/home.htm", # 中国政府网最新政策   !!
#     "https://www.ndrc.gov.cn/xxgk/zcfb/ghxwj/",  # 中国发改委规范性文件
#     "https://www.ndrc.gov.cn/xwdt/tzgg/index.html", # 中国发改委通知公告
#     "https://www.mee.gov.cn/zcwj/bwj/wj/index.shtml", # 中国生态环境部文件
#     "https://www.mee.gov.cn/zcwj/bwj/gg/index.shtml", # 中国生态环境部公告
#     "https://www.jiangxi.gov.cn/",  # 江西省政府
#     "https://www.jiangxi.gov.cn/col/col48473/index.html?uid=406462&pageNum=1", # 江西省政府文件
#     "https://www.jiangxi.gov.cn/col/col48474/index.html?uid=406478&pageNum=1", # 江西省办公厅文件
#     "https://www.jiangxi.gov.cn/col/col396/index.html?uid=45663&pageNum=1", # 江西省政府最新发布
#     "https://www.jiangxi.gov.cn/col/col4929/index.html?vc_xxgkarea=696076408",  # 江西省工信厅政策法规
#     "http://drc.jiangxi.gov.cn/col/col14590/index.html?vc_xxgkarea=014500858&uid=470259&pageNum=1",  # 江西省发改委通知公告
#     "http://drc.jiangxi.gov.cn/col/col14651/index.html?vc_xxgkarea=014500858%23div&uid=376208&pageNum=1", # 江西省发改委政策法规
#     "http://sthjt.jiangxi.gov.cn/col/col47550/index.html?uid=380055&pageNum=1", # 江西省生态环境厅头条
#     "http://sthjt.jiangxi.gov.cn/col/col42149/index.html?uid=380055&pageNum=1", # 江西省生态环境厅文件通知
url = "http://sthjt.jiangxi.gov.cn/col/col42149/index.html"
options = Options()
#options.add_argument('--headless')
options.add_argument("--disk-cache-size=4096")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
wd = webdriver.Edge(options=options)
wd.implicitly_wait(3)
# wd.get(url)
# time.sleep(15)
# # characteristic = re.search(r"(?<=//)([^/]+)",url).group(0)
# page_source = wd.page_source
# soup = BeautifulSoup(page_source, 'html.parser')
# print(judgecolumn(soup))
# title, article = get_article(url, wd)
# # # summarise = get_summarise_with_ollama(title, article)
savetitles, savelinks, savedates = deepcrawl(url, 0, wd)
wd.quit()
# # # # print(summarise)
# print(article)
for title, link in zip(savetitles, savelinks):
    print(title,link)

# characteristic = re.search(r"(?<=//)([^/]+)",url).group(0)
# print(characteristic)
# CLUSTER_ENDPOINT = "https://in03-029fdb297cf97d2.serverless.ali-cn-hangzhou.cloud.zilliz.com.cn"
# Token = "1169f81dcc8c7a6938167058e9b423e2d89540d53be97e90ea285ad31adde3c08eaaeec1d36007811945342344cb2831b8cd5862"
#
# Zilliz = zilliz(CLUSTER_ENDPOINT,Token)
# Zilliz.insert('./DCstorage/titleVectors.json', 'titles3b', oringinal_len = 0)
# with open("./DCstorage/titleVectors.json", 'r') as file:
#     data_from_json = json.load(file)
#     print(len(data_from_json))
# with open("./DCstorage/titles.json",'r', encoding='utf-8') as f:
#     titles = json.load(f)
# embedding = OllamaEmbedding()
# titlesvector = VectorStore(titles)      # 创建标题类
# titlesvector.get_vector(EmbeddingModel=embedding)     # 标题向量化
# titlesvector.persistVectors(path='DCstorage', name="titleVectors")        # 标题向量化保存