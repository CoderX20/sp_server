# coding:utf-8

from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle
import pandas as pd
from WordVector import SentencesVecBuilder


# 高斯朴素贝叶斯
class EmotionClassifyModeGaussian:
    mode = GaussianNB()

    def __init__(self, vec_len: int, txt_path: str, stop_words_file: str, vec_mode_path: str):
        self.vec_maker = SentencesVecBuilder(text_file=txt_path, stop_words_file=stop_words_file)
        self.vec_maker.load(vec_mode_path)

    def train_mode(self, tsv_path: str):
        """训练贝叶斯模型"""
        train_datasets = pd.read_csv(tsv_path, header=0, sep='\t')
        label = [x[0] for x in train_datasets.values]
        data = [x[1] for x in train_datasets.values]
        x_train, x_test, y_train, y_test = train_test_split(self.vec_maker.build_sentence_vec_many(data), label, test_size=0.1, random_state=3)
        for value in set(label):
            print(f"{value} train len: {label.count(value)}")
        self.mode.fit(x_train, y_train)
        print(f"Test data score:{self.mode.score(x_test, y_test)}")

    def test_mode(self, tsv_path: str):
        """模型性能测试"""
        test_datasets = pd.read_csv(tsv_path, header=0, sep="\t")
        label = [x[1] for x in test_datasets.values]
        data = [x[2] for x in test_datasets.values]
        for value in set(label):
            print(f"{value} test len: {label.count(value)}")
        pre_data = self.mode.predict(self.vec_maker.build_sentence_vec_many(data))
        print(f"accuracy_score:{accuracy_score(label, pre_data)}")
        print(f"precision_score:{precision_score(label, pre_data, pos_label=1)}")
        print(f"recall_score:{recall_score(label, pre_data, pos_label=1)}")
        print(f"f1_score:{f1_score(label, pre_data)}")

    def save_mode(self, mode_path: str):
        """保存模型"""
        with open(mode_path, mode='wb') as file_mode:
            pickle.dump(self.mode, file_mode)

    def load_mode(self, mode_path: str):
        """读取模型"""
        with open(mode_path, mode='rb') as file_mode:
            self.mode = pickle.load(file_mode)

    def predict_single(self, sentence: str):
        """一条语句模型预测"""
        return self.mode.predict([self.vec_maker.build_sentence_vec_one(sentence)])

    def predict_many(self, sentences: list):
        """多个语句模型预测"""
        return self.mode.predict(self.vec_maker.build_sentence_vec_many(sentences))


# 支持向量机
class SVMEmotionClassifyMode(EmotionClassifyModeGaussian):

    def __init__(self, vec_len: int, txt_path: str, stop_words_file: str, vec_mode_path: str, kernel="", penalty=1.0):
        super().__init__(vec_len, txt_path, stop_words_file, vec_mode_path)
        self.vec_maker = SentencesVecBuilder(text_file=txt_path, stop_words_file=stop_words_file)
        self.vec_maker.load(vec_mode_path)
        self.mode = SVC(kernel=kernel, C=penalty)


if __name__ == "__main__":
    sentences_file = "./datasets/word_dict.json"
    stop_words = "./datasets/百度停用词表.txt"
    train_file = "./datasets/ChnSentiCorp/train.tsv"
    test_file = "./datasets/ChnSentiCorp/dev.tsv"
    vec_mode = "./models/vec.model"

    print("高斯朴素贝叶斯")
    classify_mode_gaussian=EmotionClassifyModeGaussian(vec_len=100, txt_path=sentences_file, stop_words_file=stop_words, vec_mode_path=vec_mode)
    classify_mode_gaussian.train_mode(train_file)
    classify_mode_gaussian.test_mode(test_file)

    print("支持向量机")
    classify_mode_SVM = SVMEmotionClassifyMode(vec_len=100, txt_path=sentences_file, stop_words_file=stop_words, vec_mode_path=vec_mode, kernel='rbf',
                                               penalty=1.5)
    classify_mode_SVM.train_mode(train_file)
    classify_mode_SVM.test_mode(test_file)
    classify_mode_SVM.save_mode('./models/SVC.pickle')
