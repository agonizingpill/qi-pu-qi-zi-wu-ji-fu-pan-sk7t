from random import Random
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

def calculate(data):
    rng=Random(441)
    signals=[]; labels=[]
    for case in range(90):
        category=case%3
        signals.append([rng.uniform(2,12)+category*4, rng.randint(0,1)+category*2, int(category==2)])
        labels.append(['正常','核对提子','疑似重复落点'][category])
    train, hold, ytrain, yhold=train_test_split(signals,labels,test_size=.3,
                random_state=44,stratify=labels)
    pipeline=make_pipeline(StandardScaler(),SGDClassifier(loss='hinge',alpha=.01,random_state=44))
    pipeline.fit(train,ytrain)
    r=data['source']
    query=[[r['gap'],r['capture_claim'],int(r['repeat_move'])]]
    return {'label':str(pipeline.predict(query)[0]),'held_accuracy':round(float(pipeline.score(hold,yhold)),4),
            'margin':[round(float(x),4) for x in pipeline.decision_function(query)[0]],'n_holdout':len(hold)}
