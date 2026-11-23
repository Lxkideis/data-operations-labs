"""Synthetic operations risk model. NumPy logistic regression with ID-ordered holdouts."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent
FEATURES=['queue_hours','amount_log','prior_exceptions']
FORBIDDEN=['resolution_code','case_id','segment','target']

def auc(y,p):
    # Pairwise AUC with half credit for ties; small test data keep memory bounded.
    pos=p[y==1];neg=p[y==0]
    return float(((pos[:,None]>neg).sum()+.5*(pos[:,None]==neg).sum())/(len(pos)*len(neg)))

def metrics(y,p,threshold):
    pred=p>=threshold;tp=int(((y==1)&pred).sum());fp=int(((y==0)&pred).sum());fn=int(((y==1)&~pred).sum())
    return {'rows':len(y),'roc_auc':round(auc(y,p),4),'brier_score':round(float(np.mean((p-y)**2)),4),
      'precision':round(tp/(tp+fp),4) if tp+fp else 0,'recall':round(tp/(tp+fn),4) if tp+fn else 0,
      'flagged_cases':int(pred.sum()),'tp':tp,'fp':fp,'fn':fn}

def prepare(train,val,test):
    median=np.nanmedian(train,axis=0)
    clean=[np.where(np.isnan(x),median,x) for x in [train,val,test]]
    mean=clean[0].mean(axis=0);sd=clean[0].std(axis=0);sd[sd==0]=1
    return [np.column_stack([np.ones(len(x)),(x-mean)/sd]) for x in clean],median,mean,sd

def run():
    out=ROOT/'output';out.mkdir(exist_ok=True);rng=np.random.default_rng(27);n=3000
    queue=rng.exponential(18,n);amount=rng.normal(8,1.2,n);prior=rng.poisson(.8,n)
    segment=np.where(np.arange(n)%2==0,'A','B')
    logits=-2+.055*queue+.3*(amount-8)+.65*prior
    y=(rng.random(n)<1/(1+np.exp(-logits))).astype(int)
    x=np.column_stack([queue,amount,prior]);x[rng.random(x.shape)<.02]=np.nan
    # resolution_code intentionally leaks the label, but is never admitted to FEATURES.
    with (out/'synthetic_cases.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['case_id','segment',*FEATURES,'resolution_code','target'])
        for i in range(n):w.writerow([i,segment[i],*[('' if np.isnan(v) else round(v,5)) for v in x[i]],'confirmed' if y[i] else 'clear',int(y[i])])
    train_end,val_end=1800,2400
    (train,val,test),median,mean,sd=prepare(x[:train_end],x[train_end:val_end],x[val_end:])
    weights=np.zeros(train.shape[1])
    for _ in range(1200):
        p=1/(1+np.exp(-np.clip(train@weights,-30,30)))
        reg=.01*weights;reg[0]=0
        weights-=.08*(train.T@(p-y[:train_end])/len(train)+reg)
    predict=lambda a:1/(1+np.exp(-np.clip(a@weights,-30,30)))
    vp=predict(val);yp=y[train_end:val_end]
    choices=[]
    for t in np.arange(.05,.96,.01):
        m=metrics(yp,vp,float(t))
        if m['recall']>=.75:choices.append((m['precision'],float(t)))
    threshold=max(choices)[1] if choices else .5
    p=predict(test);yt=y[val_end:];test_metric=metrics(yt,p,threshold)
    result={'dataset':'3000 independent synthetic operations cases ordered by case id',
      'features':FEATURES,'blocked_columns':FORBIDDEN,'split':{'train':1800,'validation':600,'test':600},
      'threshold_selected_on_validation':round(threshold,3),'validation_recall_target':.75,
      'test':test_metric,'constant_baseline':metrics(yt,np.repeat(y[:train_end].mean(),len(yt)),threshold),
      'test_by_synthetic_segment':{s:metrics(yt[segment[val_end:]==s],p[segment[val_end:]==s],threshold) for s in ['A','B']},
      'train_only_preprocessing':{'median':median.tolist(),'mean':mean.tolist(),'std':sd.tolist()},
      'model_weights':weights.tolist(),
      'data_sha256':hashlib.sha256((out/'synthetic_cases.csv').read_bytes()).hexdigest(),
      'limitations':['Synthetic independent data do not reproduce real temporal drift.',
      'Segment A/B is arbitrary, not a protected attribute or a fairness certification.',
      'No LLM, cloud deployment, real customer data or measured ROI.']}
    (out/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (out/'model_card.txt').write_text(
      'SYNTHETIC MODEL CARD\n'
      'Purpose: prioritize operations cases for human review, never automatically decline clients.\n'
      'Lineage: seed 27 -> synthetic CSV -> ordered 60/20/20 split -> train-only median/scale -> logistic model -> validation threshold -> test report.\n'
      'Schema: case_id ordered identifier; segment arbitrary A/B; queue_hours intake queue age; amount_log transaction amount scale; prior_exceptions historical count; target simulated review need.\n'
      'Leakage control: resolution_code is post-outcome information and excluded, along with identifiers/segment/target.\n'
      'Evaluation: compare ROC-AUC and Brier against constant baseline; report precision/recall and false alerts at the chosen threshold.\n'
      'Governance proposal: version dataset hashes and model weights; access by role; human review; monitor drift and escalation rates. These controls are proposed, not deployed.\n'
      'Privacy: no personal records; production retention and legal review would need organization-specific policies.\n',encoding='utf-8')
    return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
