#coding: utf-8
import numpy as np
import sys
from sklearn.metrics import accuracy_score
#from mlp import MultiLayerPerceptron
from sklearn.datasets import fetch_mldata
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import LabelBinarizer
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_recall_fscore_support

"""
mlp.py
多層パーセプトロン
forループの代わりに行列演算にした高速化版
入力層 - 隠れ層 - 出力層の3層構造で固定（PRMLではこれを2層と呼んでいる）
隠れ層の活性化関数にはtanh関数またはsigmoid logistic関数が使える
出力層の活性化関数にはtanh関数、sigmoid logistic関数、恒等関数、softmax関数が使える
"""

def tanh(x):
    return np.tanh(x)

# このスクリプトではxにtanhを通した値を与えることを仮定
def tanh_deriv(x):
    return 1.0 - x ** 2

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# このスクリプトではxにsigmoidを通した値を与えることを仮定
def sigmoid_deriv(x):
    return x * (1 - x)

def identity(x):
    return x

def identity_deriv(x):
    return 1

def softmax(x):
    temp = np.exp(x)
    return temp / np.sum(temp)

class MultiLayerPerceptron:
    def __init__(self, numInput, numHidden, numOutput, act1="tanh", act2="sigmoid", preMat=None, recMat=None, fscMat=None):
        """多層パーセプトロンを初期化
        numInput    入力層のユニット数（バイアスユニットは除く）

        numOutput   出力層のユニット数
        act1        隠れ層の活性化関数（tanh or sigmoid）
        act2        出力層の活性化関数（tanh or sigmoid or identity or softmax）
        """

        self.preMat = preMat
        self.recMat = recMat
        self.fscMat = fscMat

        #出力ファイルのクラスを記述しておく
        classes = [0,1,2,3,4,5,6,7,8,9]
        self.preMat.writerow(classes)
        self.recMat.writerow(classes)
        self.fscMat.writerow(classes)

        # 引数の指定に合わせて隠れ層の活性化関数とその微分関数を設定
        if act1 == "tanh":
            self.act1 = tanh
            self.act1_deriv = tanh_deriv
        elif act1 == "sigmoid":
            self.act1 = sigmoid
            self.act1_deriv = sigmoid_deriv
        else:
            print "ERROR: act1 is tanh or sigmoid"
            sys.exit()

        # 引数の指定に合わせて出力層の活性化関数とその微分関数を設定
        # 交差エントロピー誤差関数を使うので出力層の活性化関数の微分は不要
        if act2 == "tanh":
            self.act2 = tanh
        elif act2 == "sigmoid":
            self.act2 = sigmoid
        elif act2 == "softmax":
            self.act2 = softmax
        elif act2 == "identity":
            self.act2 = identity
        else:
            print "ERROR: act2 is tanh or sigmoid or softmax or identity"
            sys.exit()

        # バイアスユニットがあるので入力層と隠れ層は+1
        self.numInput = numInput + 1
        self.numHidden =numHidden + 1
        self.numOutput = numOutput

        # 重みを (-1.0, 1.0)の一様乱数で初期化
        self.weight1 = np.random.uniform(-1.0, 1.0, (self.numHidden, self.numInput))  # 入力層-隠れ層間
        self.weight2 = np.random.uniform(-1.0, 1.0, (self.numOutput, self.numHidden)) # 隠れ層-出力層間

    def fit(self, X, t, learning_rate=0.1, epochs=10000, xtest=None, ytest=None):
        self.xtest = xtest
        self.ytest = ytest

        """訓練データを用いてネットワークの重みを更新する"""
        # 入力データの最初の列にバイアスユニットの入力1を追加
        X = np.hstack([np.ones([X.shape[0], 1]), X])
        t = np.array(t)

        # 逐次学習
        # 訓練データからランダムサンプリングして重みを更新をepochs回繰り返す

        # 正解率を取得するタイミング
        getTimes=[5, 10, 50, 100, 500, 1000, 1500, 3000, 5000, 7500, 10000, 15000, 30000, 35000, 50000]
        # getTimesのindex
        gt = 0


        # epochsの回数, 学習を行う
        for k in range(epochs):
            # 途中経過を表示
            if k%100 == 0:
                print k

            # 訓練データからランダムに選択する
            i = np.random.randint(X.shape[0])
            x = X[i]

            #maskベクトルを生成
            m = np.random.random_integers(0, 1, self.numHidden)
            m[0] = 1
            # 入力を順伝播させて中間層の出力を計算
            z = self.act1(np.dot(self.weight1, x)) * m

            # 中間層の出力を順伝播させて出力層の出力を計算
            y = self.act2(np.dot(self.weight2, z))

            # 出力層の誤差を計算（交差エントロピー誤差関数を使用）
            delta2 = y - t[i]

            # 出力層の誤差を逆伝播させて隠れ層の誤差を計算
            delta1 = self.act1_deriv(z) * np.dot(self.weight2.T, delta2) * m

            # 隠れ層の誤差を用いて隠れ層の重みを更新
            # 行列演算になるので2次元ベクトルに変換する必要がある
            x = np.atleast_2d(x)
            delta1 = np.atleast_2d(delta1)

            #マスクベクトルを2次元ベクトルに変換(行列演算を行うため)
            m = np.atleast_2d(m)
            self.weight1 -= learning_rate * np.dot(delta1.T, x) * m.T

            # 出力層の誤差を用いて出力層の重みを更新
            z = np.atleast_2d(z)
            delta2 = np.atleast_2d(delta2)
            self.weight2 -= learning_rate * np.dot(delta2.T, z) * m


            # 指定されたepochsの時、汎化誤差を計算してファイルに出力
            if getTimes[gt] == k+1:
                predictions = []
                for i in range(xtest.shape[0]):
                    o = self.predict(xtest[i])
                    predictions.append(np.argmax(o))

                p, r, f, s = precision_recall_fscore_support(ytest, predictions, beta=0.5)

                self.preMat.writerow(p)
                self.recMat.writerow(r)
                self.fscMat.writerow(f)

                gt += 1

    def predict(self, x):
        """テストデータの出力を予測"""
        x = np.array(x)
        # バイアスの1を追加
        x = np.insert(x, 0, 1)
        # 順伝播によりネットワークの出力を計算
        z = self.act1(np.dot(self.weight1*0.5, x))
        y = self.act2(np.dot(self.weight2*0.5, z))
        return y

    def calcu_accuracy(self):
        countOf4 = 0
        # テストデータを用いて予測精度を計算
        predictions = []
        for i in range(self.xtest.shape[0]):
            o = self.predict(self.xtest[i])
            predictions.append(np.argmax(o))
        return accuracy_score(self.ytest, predictions)

if __name__ == "__main__":
    """XORの学習テスト"""
    mlp = MultiLayerPerceptron(2, 2, 1, "tanh", "sigmoid")
    X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    y = np.array([0, 1, 1, 0])
    mlp.fit(X, y)
    for i in [[0, 0], [0, 1], [1, 0], [1, 1]]:
        print i, mlp.predict(i)
