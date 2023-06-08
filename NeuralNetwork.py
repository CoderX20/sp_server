# coding:utf-8

from sklearn.neural_network import MLPClassifier
from ML_train import EmotionClassifyModeGaussian
from WordVector import SentencesVecBuilder


# 神经网络
class NNEmotionClassifyMode(EmotionClassifyModeGaussian):

    def __init__(self, vec_len=200, txt_path="", stop_words_path="",vec_mode_path=""):
        super().__init__(vec_len, txt_path, stop_words_path,vec_mode_path=vec_mode_path)
        self.vec_maker=SentencesVecBuilder(text_file=txt_path,stop_words_file=stop_words_path)
        self.vec_maker.load(vec_mode_path)
        self.mode=MLPClassifier()

    def training(self,tsv_path:str,hidden_layer_sizes:tuple,active_fun:str,solver:str,alpha:float):
        """训练神经网络"""
        self.mode=MLPClassifier(hidden_layer_sizes=hidden_layer_sizes,activation=active_fun,solver=solver,alpha=alpha)
        self.train_mode(tsv_path)


if __name__=="__main__":
    word_dict="./datasets/word_dict.json"
    stop_words_file="./datasets/百度停用词表.txt"
    train_file = "./datasets/ChnSentiCorp/train.tsv"
    test_file = "./datasets/ChnSentiCorp/dev.tsv"
    vec_mode="./models/vec.model"
    print("神经网络")
    NN_classify_mode=NNEmotionClassifyMode(vec_len=100, txt_path=word_dict, stop_words_path=stop_words_file,vec_mode_path=vec_mode)
    NN_classify_mode.training(tsv_path=train_file,hidden_layer_sizes=(100,20,),active_fun="logistic",solver="adam",alpha=1e-5)
    NN_classify_mode.test_mode(test_file)
    NN_classify_mode.save_mode("./models/NN.pickle")
