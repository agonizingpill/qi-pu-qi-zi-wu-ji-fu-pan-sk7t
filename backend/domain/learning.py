from functools import lru_cache
from random import Random
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

NORMAL_LABEL = '正常'


@lru_cache(maxsize=1)
def _model():
    rng = Random(441)
    signals = []
    labels = []
    for case in range(90):
        category = case % 3
        signals.append([rng.uniform(2, 12) + category * 4, rng.randint(0, 1) + category * 2,
                        int(category == 2)])
        labels.append(['正常', '核对提子', '疑似重复落点'][category])
    train, hold, ytrain, yhold = train_test_split(signals, labels, test_size=.3,
                                                  random_state=44, stratify=labels)
    pipeline = make_pipeline(StandardScaler(), SGDClassifier(loss='hinge', alpha=.01, random_state=44))
    pipeline.fit(train, ytrain)
    return pipeline, labels, hold, yhold


def calculate(data):
    pipeline, labels, hold, yhold = _model()
    r = data['source']
    query = [[r['gap'], r['capture_claim'], int(r['repeat_move'])]]
    return {'label': str(pipeline.predict(query)[0]),
            'held_accuracy': round(float(pipeline.score(hold, yhold)), 4),
            'margin': [round(float(x), 4) for x in pipeline.decision_function(query)[0]],
            'n_holdout': len(hold)}


def normal_score(ply, value=None):
    """现有 SGD hinge 模型对该手次给出的“正常”类判别分（margin 放大取整，仅用于择优排序）。

    value 为该手候选提子数时，用候选值替换原件 capture_claim 再评分，使逐手分法的
    择优能反映“该手记几枚提子时更接近正常原件”。
    """
    pipeline, labels, _, _ = _model()
    claim = ply['capture_claim'] if value is None else value
    query = [[ply['gap'], claim, int(ply['repeat_move'])]]
    margins = pipeline.decision_function(query)[0]
    index = list(pipeline.classes_).index(NORMAL_LABEL)
    return round(float(margins[index]) * 1000)
