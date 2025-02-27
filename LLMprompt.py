import ollama
import datetime
import re
# 江西有关双碳最新的一条政策是什么；江西上个月有什么电力相关政策；自从双碳目标提出后江西省有什么相关政策；请输出2021至2023年江西和全国GDP数据
#江西省最新的碳达峰、碳中和实施方案
#江西省上个月电力的实施方案

def query_preprocessing(query : str) -> str:
    prompt = f"""
    你是一个问题预处理高手，负责将宽泛的问题转换成更具体的政策领域问题。以下是2个规则和示例，帮助你理解如何进行问题转化。
    
    规则1:将问题中的总结、概括以及简化省略的词语，还原成完整的名词后加入到问题当中。
    示例:“自从提出四改后，浙江出台了什么相关政策”转化为“浙江省关于改作风、改制度、改作业、改评价的政策”。
    示例:“四川最新的三去政策有哪些”转化为“四川省关于去产能、去库存、去杠杆的政策”。
    
    规则2:去除问题中的量词（一个、两条）、疑问词（什么、哪些）、时间（上个月、上半年）、形容词（最新、最早）等。
    示例:“广东最新的道路交通法有什么”转化为“广东省道路交通法”。
    示例:“黑龙江省上个月对二胎政策有哪些改变”转化为“黑龙江省关于二胎政策”。
    
    这是需要转化的问题:{query}

    请严格按照所有规则进行问题转换，只输出转换后的问题,不需要额外的解释或补充。
    """
    response = ollama.chat(model="deepseek-r1:8b", messages=[{"role": "user", "content": prompt}])
    print(response['message']['content'])
    preprocessed_query = re.search(r'</think>\s*(.*)', response['message']['content'], re.DOTALL).group(1).strip()
    print(preprocessed_query)
    return preprocessed_query

def answer_postprocessing(query : str, answer : str) -> str:
    today = datetime.date.today()
    prompt = f"""
        根据问题和内容，选择合适的答案输出:

        当前日期:{today}

        问题:{query}

        内容:
        {answer}
        
        输出答案的格式为发布时间、名字、链接和总结，就像内容中的那样，不要随意编造信息，也不需要额外的解释或补充。
    """
    response = ollama.chat(model="deepseek-r1:8b", messages=[{"role": "user", "content": prompt}])
    post_processed_answer = re.search(r'</think>\s*(.*)', response['message']['content'], re.DOTALL).group(1).strip()
    #print(answer)
    return post_processed_answer