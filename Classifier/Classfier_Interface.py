from Classifier.XGB_Classifier import xgb_classifier


class ClassifierInterface:

    def __init__(self, mode='xgb', pre=None, sid=42):
        if mode == 'xgb':
            self.classifier = xgb_classifier(None, 42, parse=False, n_classes=3)
        else:
            raise NotImplementedError

    def fit(self, x_train, y_train, x_test, y_test):
        self.classifier.set_data(x_train, y_train)
        self.classifier.fit(x_test, y_test)

    def predict(self, data):
        return self.classifier.classify(data)

    def fit_one(self, x_train, y_train):
        self.classifier.set_data(x_train, y_train)
        self.classifier.fit_one()
