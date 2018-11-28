# encoding:utf-8
from tensorflow.contrib import learn
import numpy as np
import random
import string
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import wordnet
import os

root_path = os.path.dirname(os.path.abspath(os.path.join(os.getcwd(), ".")))
# stop_words = []
# with open('textcnn/stop_words.txt', 'r') as stop_file:
#     for line in stop_file.readlines():
#         line = line.replace("\n", "").replace("\\", "")
#         stop_words.append(line)


class Processing(object):
    '''
        语料的预处理工作
    '''
    def loadPracticeFile(self, filename):
        '''
        :param filename: 文件名
        训练文件格式
        1/t/t全民保/t/t实体
        :return:
        '''
        with open(filename, 'r', encoding='utf-8') as fr:
            articles = []
            tags = []
            for line in fr.readlines():
                data = line.replace("\t\t", "\t").replace("\n", "").split("\t")
                if len(data) == 3:
                    articles.append(self.preprocess(data[1]))
                    tags.append(data[2])
                else:
                    print(line+"------格式错误")
        return articles, tags

    def preprocess(self, doc):
        wnl = WordNetLemmatizer()  # 词形还原
        ps = PorterStemmer()  # 词干提取
        for c in string.punctuation:
            # 去标点
            doc = doc.replace(c, ' ')
        for c in string.digits:
            # 去数字
            doc = doc.replace(c, '')
        doc = nltk.word_tokenize(doc)
        # 分割成单词 只保留特定词性单词, 如名词
        # filter = nltk.pos_tag(doc)
        # doc = [w for w, pos in filter if pos.startswith("NN")]
        # 只保留长度不小于3的单词,去除停用词,验证是否为英文单词(利用wordnet)
        newdoc = []
        for word in doc:
            # if len(word) >= 3 and word not in stop_words and wordnet.synsets(word):
            if len(word) >= 3 and wordnet.synsets(word):
                word = wnl.lemmatize(word)
                # word = ps.stem(word)
                newdoc.append(word)
        return ' '.join(newdoc)

    def embedding(self, articles, tags):
        length = []
        articlesWords = []
        for article in articles:
            article = self.preprocess(article)
            # words = [x for x in jieba.cut(article) if x != ' ']
            # articlesWords.append(' '.join(words))
            articlesWords.append(article)
            length.append(len(article.split(" ")))
        max_length = max(length)
        vocab_processor = learn.preprocessing.VocabularyProcessor(max_length)
        vocab_processor.fit(articlesWords)
        data_embedding = np.array(list(vocab_processor.fit_transform(articlesWords)))
        vocab_processor.save('model/vocab.pickle')
        index = [x for x in range(len(articles))]
        random.shuffle(index)
        data_embedding_new = [data_embedding[x] for x in index]
        tags_new = [tags[x] for x in index]

        # 将类型用数字替换
        label_file = open('model/labels.txt', 'w')
        type = list(set(tags_new))
        for temp in range(len(type)):
            print(str(temp) + ":" + type[temp])
            label_file.writelines(str(temp) + ":" + type[temp] + "\n")
        tags_new = [type.index(x) for x in tags_new]
        tags_vec = []
        for x in tags_new:
            temp = [0] * len(type)
            temp[x] = 1
            tags_vec.append(temp)

        return data_embedding_new, tags_vec


if __name__ == '__main__':
    processing = Processing()
    processing.loadPracticeFile(root_path+"/data/train.txt")
