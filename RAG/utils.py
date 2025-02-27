import os
import PyPDF2
import markdown
import json
import tiktoken
from bs4 import BeautifulSoup
import re

enc = tiktoken.get_encoding("cl100k_base")

class ReadFiles:
    """
    class to read files
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self.file_list = self.get_files()

    def get_files(self):
        # args：dir_path，目标文件夹路径
        file_list = []
        for filepath, dirnames, filenames in os.walk(self._path):
            # os.walk 函数将递归遍历指定文件夹
            for filename in filenames:
                # 通过后缀名判断文件类型是否满足要求
                if filename.endswith(".md"):
                    # 如果满足要求，将其绝对路径加入到结果列表
                    file_list.append(os.path.join(filepath, filename))
                elif filename.endswith(".txt"):
                    file_list.append(os.path.join(filepath, filename))
                elif filename.endswith(".pdf"):
                    file_list.append(os.path.join(filepath, filename))
        return file_list

    def get_content(self, max_token_len: int = 600, cover_content: int = 150, is_split_point=False):
    # 从多个文件中读取内容并将这些内容处理成指定长度的块，内容块的最大长度600，分块时需要覆盖的内容长度150
        docs = []
        # 读取文件内容
        for file in self.file_list:
            content = self.read_file_content(file)
            chunk_content = self.get_chunk(
                content, max_token_len=max_token_len, cover_content=cover_content, is_split_point=is_split_point)  # 分块处理
            docs.extend(chunk_content)
        return docs

    @classmethod
    def get_chunk(cls, text: str, max_token_len: int = 600, cover_content: int = 150,is_split_point=False):
        chunk_text = []

        curr_len = 0  # 当前文本长度
        curr_chunk = ''  # 正在构建的块

        token_len = max_token_len - cover_content

        if is_split_point==False:
            result_list = [text[i:i+max_token_len] for i in range(0, len(text), max_token_len)]
  # 假设以换行符分割文本为行
        if is_split_point==True:
            result_list = re.split(r'。', text)

        for result in result_list:
            # line = line.replace(' ', '')  # 移除空格
            result_len = len(enc.encode(result))  # 计算行的长度
            if result_len > max_token_len:
                # 如果单行长度就超过限制，则将其分割成多个块
                num_chunks = (result_len + token_len - 1) // token_len  # 计算需要多少个块来容纳当前行，即使有剩余的部分也会额外计算为一个块
                for i in range(num_chunks):
                    start = i * token_len
                    end = start + token_len
                    # 计算当前块的开始和结束索引，避免跨单词分割
                    while not result[start:end].rstrip().isspace():
                    # 检查当前块的文本（line[start:end]）是否是一个完整的单词，rstrip()方法去掉末尾的空格，isspace()判断是否是空白字符串。
                        start += 1
                        end += 1
                        # 如果当前块不是完整的单词，那么就将start和end各自加1，继续向后查找，直到找到一个完整的单词为止
                        if start >= result_len:
                        # 检查如果start的值超出了行的长度，则终止循环，以防止数组越界
                            break
                    if cover_content == 0:
                        curr_chunk = result[start:end]
                    else:
                        curr_chunk = curr_chunk[-cover_content:] + result[start:end]
                    # curr_chunk的最后cover_content个字符与当前分割出的文本块拼接在一起
                    chunk_text.append(curr_chunk)
                # 处理最后一个块
                start = (num_chunks - 1) * token_len  # 重新计算最后一个块的起始位置，确保最后一个块的起始位置是正确的
                if cover_content == 0:
                    curr_chunk = result[start:end]
                else:
                    curr_chunk = curr_chunk[-cover_content:] + result[start:end]
                chunk_text.append(curr_chunk)
                
            # if curr_len + result_len <= token_len:
            # # 块可以容纳这行文本+curr_len
            #     curr_chunk += result  # 将当前行（line）添加到当前块（curr_chunk）中。
            #     curr_chunk += '\n'
            #     curr_len += result_len
            #     curr_len += 1
            # else:
            #     chunk_text.append(curr_chunk)  # 将当前块（curr_chunk）添加到结果列表（chunk_text）中。
            #     if cover_content == 0:
            #         curr_chunk = result
            #     else:
            #         curr_chunk = curr_chunk[-cover_content:]+result  # 将当前块更新为保留最后 cover_content 个字符，并添加当前行
            #     curr_len = result_len + cover_content
            if result == "":
                break
            else:
                chunk_text.append(result)

        # if curr_chunk:
        # # 如果当前块不为空，说明还有未处理的文本块
        #     chunk_text.append(curr_chunk)

        return [chunk for chunk in chunk_text if chunk]

    # def split_lines(self,text):
    #     lines = text.splitlines()
    #     return lines

    @classmethod
    def read_file_content(cls, file_path: str):
        # 根据文件扩展名选择读取方法
        if file_path.endswith('.pdf'):
            return cls.read_pdf(file_path)
        elif file_path.endswith('.md'):
            return cls.read_markdown(file_path)
        elif file_path.endswith('.txt'):
            return cls.read_text(file_path)
        else:
            raise ValueError("Unsupported file type")

    @classmethod
    def read_pdf(cls, file_path: str):
        # 读取PDF文件
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
            return text

    @classmethod
    def read_markdown(cls, file_path: str):
        # 读取Markdown文件
        with open(file_path, 'r', encoding='utf-8') as file:
            md_text = file.read()
            html_text = markdown.markdown(md_text)
            # 使用BeautifulSoup从HTML中提取纯文本
            soup = BeautifulSoup(html_text, 'html.parser')
            plain_text = soup.get_text()
            # 使用正则表达式移除网址链接
            text = re.sub(r'http\S+', '', plain_text) 
            return text

    @classmethod
    def read_text(cls, file_path: str):
        # 读取文本文件
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()


class Read_json:
    def __init__(self, path: str = '') -> None:
        self.path = path
    
    def get_content(self):
        with open(self.path, mode='r', encoding='utf-8') as f:
            content = json.load(f)
        return content
