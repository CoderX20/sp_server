# coding:utf-8

from gensim.models import Word2Vec
import jieba as jb
import numpy as np


class SentencesVecBuilder:

    def __init__(self,text_file: str, stop_words_file: str):
        self.sen_list=[]
        self.stop_list=[]
        with open(text_file, encoding="utf-8") as file_txt:
            self.sen_list = file_txt.read().split('\n')
        with open(stop_words_file, encoding="utf-8") as file_txt:
            self.stop_list = file_txt.read().split('\n')
        self.vec_mode=Word2Vec()

    def train(self, mode_path: str, size=100, min_count=1) -> Word2Vec:
        """训练词向量模型"""
        cut_list = []
        for sen in self.sen_list:
            cut_list.append([x for x in jb.lcut(sen) if x not in self.stop_list])

        self.vec_mode = Word2Vec(cut_list, vector_size=size, min_count=min_count)
        self.vec_mode.train(cut_list, total_examples=self.vec_mode.corpus_count,epochs=self.vec_mode.epochs)
        self.vec_mode.save(mode_path)

        return self.vec_mode

    def load(self,mode_path: str) -> Word2Vec:
        """加载已经训练好了的词向量模型"""
        self.vec_mode=Word2Vec.load(mode_path)
        return self.vec_mode

    def build_sentence_vec_one(self,sentence: str) -> np.ndarray:
        """"将一个句子转换为词向量"""
        words_list = jb.lcut(sentence)
        vec=np.zeros(self.vec_mode.vector_size)
        for word in words_list:
            if word not in self.stop_list:
                if word in self.vec_mode.wv:
                    vec+=self.vec_mode.wv[word]
        if len(vec)>self.vec_mode.vector_size:
            vec=vec[:self.vec_mode.vector_size]
        else:
            padding=np.zeros(self.vec_mode.vector_size-len(vec))
            vec=np.concatenate([vec,padding])
        return vec

    def build_sentence_vec_many(self,sentence_list:list)->list:
        """将多个语句转换为词向量"""
        out=[]
        for sen in sentence_list:
            out.append(self.build_sentence_vec_one(sen).tolist())
        return out


if __name__=="__main__":
    sentence="风景很好，我很喜欢"
    vec_mode=SentencesVecBuilder(text_file="./datasets/sentences.txt",stop_words_file="./datasets/百度停用词表.txt",)
    vec_mode.train(mode_path="./models/vec.model",size=100)
    print(vec_mode.vec_mode.vector_size)
    print(vec_mode.build_sentence_vec_one(sentence))
    print(vec_mode.build_sentence_vec_one(sentence).shape)



