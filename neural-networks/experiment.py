import time
import typer
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split


url = "oos-intent.jsonl"
df = pd.read_json(url, lines=True)


def run_sklearn(X_train, X_test, y_train, y_test):
    from sklearn.neural_network import MLPClassifier

    t0 = time.time()
    model = MLPClassifier().fit(X_train, y_train)
    t1 = time.time()
    pred = model.predict(X_test)
    t2 = time.time()
    acc = np.mean(pred == y_test)
    return {"train_time": t1 - t0, "pred_time": t2 - t1, "acc": float(acc), "variant": "sklearn"}


def run_skearly(X_train, X_test, y_train, y_test):
    from sklearn.neural_network import MLPClassifier

    t0 = time.time()
    model = MLPClassifier(early_stopping=True).fit(X_train, y_train)
    t1 = time.time()
    pred = model.predict(X_test)
    t2 = time.time()
    acc = np.mean(pred == y_test)
    return {"train_time": t1 - t0, "pred_time": t2 - t1, "acc": float(acc), "variant": "skearly"}


def run_keras(X_train, X_test, y_train, y_test):
    from keras.models import Sequential
    from keras.layers import Dense
    from keras.optimizer_v2.adam import Adam

    label_enc = CountVectorizer().fit(y_train)
    y_lab_train = label_enc.transform(y_train)
    y_lab_test = label_enc.transform(y_test)

    clf = Sequential()
    clf.add(Dense(100, activation='relu', input_dim=X_train.shape[1]))
    clf.add(Dense(y_lab_train.shape[1], activation='sigmoid',))
    clf.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=["accuracy"])
    
    t0 = time.time()
    X_dense, y_dense = X_train.todense(), y_lab_train.todense()
    clf.fit(x=X_dense, y=y_dense, epochs=10)
    t1 = time.time()
    pred = np.argmax(clf.predict(X_test.todense()), axis=1)
    t2 = time.time()
    true_vals = np.asarray(np.argmax(y_lab_test.todense(), axis=1)).flatten()
    acc = np.mean(pred == true_vals)
    return {"train_time": t1 - t0, "pred_time": t2 - t1, "acc": float(acc), "variant": "keras"}


def main(model="sklearn"):
    X, y = CountVectorizer().fit_transform(df['text']), df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
    if model == "keras":
         print(run_keras(X_train, X_test, y_train, y_test))
    if model == "sklearn":
         print(run_sklearn(X_train, X_test, y_train, y_test))
    if model == "skearly":
        print(run_skearly(X_train, X_test, y_train, y_test))


if __name__ == "__main__":
    typer.run(main)
