from sklearn.ensemble import IsolationForest
import pickle


def get_model():
    print('train your model first')
    return IsolationForest(random_state=0)


def fit(model, X):
    model.fit(X)


def save(model):
    pickle.dump(model, open('model', 'wb'))


def load():
    return pickle.load(open('model', 'rb'))
