import xgboost as xgb
import numpy as np
from sklearn.model_selection import cross_val_score, StratifiedKFold

class xgb_classifier:

    data = []
    data_dmatrix = None
    labels = []
    sub = -1
    reg = -1
    est = -1
    mcw = -1
    md = -1
    lr = -1
    gamma = -1
    col = -1

    def __init__(self, pre, sid, loadpath = "C:\\Users\\mash02-admin\\PycharmProjects\\johannes\\BA\\Ressources\\Results\\tuning\\hyperparameters\\" , parse=True, n_classes = None):
        self.path = loadpath
        if parse:
            self.parse(pre, sid)
            self.xg_class = xgb.XGBClassifier(objective='multi:softmax', subsample= self.sub, reg_alpha=self. reg, n_estimators=self.est, min_child_weight=self.mcw, max_depth=self.md, learning_rate=self.lr, gamma=self.gamma, colsample_bytree=self.col,verbosity=0, n_jobs=1)
        else:

                self.xg_class = xgb.XGBClassifier(objective='multi:softmax', num_class = n_classes)

                #self.xg_class = xgb.XGBClassifier(objective='multi:softmax')

    def from_dict(self, dic:dict):
        self.xg_class.set_params(**dic)

    def parse(self, pre, sid):
        loadpath = self.path + 'tuning' +'/' + 'Subject_'+str(sid)+'/'+ 'hyperparameters'+'/'+pre + '/' + 'XGB' + '/'
        if sid < 10:
            loadpath += 'hyperparameters' + pre + 'XGB' + '0' + str(sid)+'.txt'
        else:
            loadpath += 'hyperparameters' + pre + 'XGB' + str(sid)+'.txt'

        res = np.loadtxt(loadpath, dtype=str)
        strin = ""
        for x in res:
            strin = strin + x
        counter = 0
        active = False
        isstr = False
        helper = ""
        for char in strin:
            if char == '{':
                continue
            elif char == ':':
                active = True
            elif char == ','or char == '}':
                active = False
                if counter == 0:
                    self.sub = float(helper)
                elif counter == 1:
                    self.reg = float(helper)
                elif counter == 2:
                    self.est = int(helper)
                elif counter == 3:
                    self.mcw = int(helper)
                elif counter == 4:
                    self.md = int(helper)
                elif counter == 5:
                    self.lr = float(helper)
                elif counter == 6:
                    self.gamma=float(helper)
                elif counter == 7:
                    pass
                elif counter == 8:
                    self.col = float(helper)

                if isstr:
                    isstr = False
                counter += 1
                helper = ""

            elif not active:
                continue
            elif char == '\'':
                isstr = True
            else:
                helper += char


    def flatten(self, data):
        output = []
        for sample in data:
            helper = sample.flatten()
            output.append(helper)
        return np.array(output)

    def set_data(self, data, labels):
        self.data = self.flatten(data)
        # self.data_dmatrix = xgb.DMatrix(data=self.data, label=labels)

        self.labels = labels

    def fit(self, X_test, y_test):
        X_test = self.flatten(X_test)
        self.xg_class.fit(self.flatten(self.data), self.labels, verbose= True, eval_metric='merror', eval_set=[(X_test, y_test)], early_stopping_rounds=10)

    def classify(self, data):
        return self.xg_class.predict(self.flatten(data))

    def evaluate(self,x_test, y_test):
        #acc = self.cv(x_test, y_test)
        acc= self.xg_class.score(self.flatten(x_test), y_test)
        #del self.xg_class
        return acc

    def fit_one(self):
        self.xg_class.fit(self.flatten(self.data), self.labels, verbose=True, eval_metric='merror',)


    def cv(self, data, labels, cv=10):
        k_fold = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
        return np.mean(cross_val_score(self.xg_class, self.flatten(data), labels, cv=k_fold))

    def cross_val(self, data, labels, cv=10):
        return self.cv(data, labels, cv)

    def save(self, path):
        self.xg_class.save_model(path)

    def load(self,path):
        self.xg_class = xgb_classifier.load(path)