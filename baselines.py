#!/usr/bin/env python3
"""Training-only preprocessing; validation thresholds; held-out test reports."""
import argparse
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (roc_auc_score,average_precision_score,balanced_accuracy_score,
                             confusion_matrix,classification_report,f1_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from runtime import SEED,json_write

def run(args):
    samples=pd.concat([pd.read_parquet(args.data/f'historical-{s}.parquet') for s in ('train','validation','test')]).set_index('sample_id')
    tasks=pd.read_parquet(args.data/'task-index.parquet')
    allow=json.loads((args.data/'summary-v2.json').read_text())['feature_names']
    reports=[]; predictions=[]
    for task_name,index in tasks.groupby('task',sort=True):
        table=index.merge(samples.reset_index(),on='sample_id',validate='many_to_one',suffixes=('_index',''))
        assert (table.split==table.split_index).all()
        train=table[table.split=='train']; val=table[table.split=='validation']; test=table[table.split=='test']
        binary=task_name.startswith('binary_')
        if min(len(train),len(val),len(test))==0 or train.target.nunique()<2 or (binary and min(val.target.nunique(),test.target.nunique())<2):
            reports.append({'task':task_name,'status':'insufficient_class_support'}); continue
        for feature_set,columns in [('size_only',['feature_file_size_bytes']),('full',allow)]:
            for model_name in ('logistic_regression','random_forest'):
                estimator=(LogisticRegression(class_weight='balanced',max_iter=2000,random_state=SEED) if model_name=='logistic_regression'
                           else RandomForestClassifier(n_estimators=200,class_weight='balanced',random_state=SEED,n_jobs=4))
                pipeline=make_pipeline(SimpleImputer(strategy='median',add_indicator=True,keep_empty_features=True),StandardScaler(),estimator)
                pipeline.fit(train[columns],train.target)
                probabilities=pipeline.predict_proba(test[columns]); labels=pipeline.classes_.tolist()
                threshold=None
                if binary:
                    positive=labels.index('1'); vp=pipeline.predict_proba(val[columns])[:,positive]
                    thresholds=np.linspace(.01,.99,99)
                    scores=[balanced_accuracy_score(val.target.astype(int),(vp>=t).astype(int)) for t in thresholds]
                    threshold=float(thresholds[int(np.argmax(scores))]); pred=(probabilities[:,positive]>=threshold).astype(int).astype(str)
                else: pred=pipeline.predict(test[columns])
                actual=test.target.to_numpy(); report={'task':task_name,'feature_set':feature_set,'model':model_name,'status':'pass',
                   'train_rows':len(train),'validation_rows':len(val),'test_rows':len(test),'threshold':threshold,
                   'balanced_accuracy':float(balanced_accuracy_score(actual,pred)),
                   'macro_f1':float(f1_score(actual,pred,labels=labels,average='macro',zero_division=0)),
                   'labels':labels,'confusion_matrix':confusion_matrix(actual,pred,labels=labels).tolist(),
                   'per_class':classification_report(actual,pred,labels=labels,output_dict=True,zero_division=0),
                   'predictor_columns':columns,'seed':SEED}
                if binary:
                    report.update(auroc=float(roc_auc_score(actual.astype(int),probabilities[:,positive])),
                                  auprc=float(average_precision_score(actual.astype(int),probabilities[:,positive])))
                reports.append(report)
                predictions.extend({'sample_id':sid,'task':task_name,'feature_set':feature_set,'model':model_name,
                                    'target':y,'prediction':p} for sid,y,p in zip(test.sample_id,actual,pred))
                print(task_name,feature_set,model_name,round(report['balanced_accuracy'],4),flush=True)
    args.out.mkdir(parents=True,exist_ok=True)
    json_write(args.out/'baseline-results.json',{'seed':SEED,'results':reports})
    pd.DataFrame(predictions).to_parquet(args.out/'baseline-predictions.parquet',index=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--data',type=Path,required=True); p.add_argument('--out',type=Path,required=True)
    run(p.parse_args())
