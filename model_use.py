# coding:utf-8

from ML_train import SVMEmotionClassifyMode
from NeuralNetwork import NNEmotionClassifyMode
from snownlp import SnowNLP as snow


if __name__=="__main__":
    dict_path="./datasets/word_dict.json"
    stop_words="./datasets/百度停用词表.txt"
    vec_mode="./models/vec.model"
    test_sentence=["果然是风景名胜，自然风光很不错，空气很清新",
                   "景区工作人员的服务态度很好，十分推荐",
                   "玩的没啥新意，感觉这些景点大同小异",
                   "景区里面连水都没卖的，真垃圾",
                   "他妈的，一个面包50块，宰客宰的真尼玛恶心"]

    SVM_mode=SVMEmotionClassifyMode(vec_len=100, txt_path=dict_path, stop_words_file=stop_words,vec_mode_path=vec_mode)
    SVM_mode.load_mode('./models/SVC.pickle')
    res=SVM_mode.predict_many(test_sentence)
    print(res)

    NN_mode=NNEmotionClassifyMode(vec_len=100, txt_path=dict_path, stop_words_path=stop_words,vec_mode_path=vec_mode)
    NN_mode.load_mode("./models/NN.pickle")
    res=NN_mode.predict_many(test_sentence)
    print(res)

    for sen in test_sentence:
        s=snow(sen)
        print(s.sentiments)

