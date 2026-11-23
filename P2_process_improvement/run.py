"""Synthetic operations event log; before/after results are scenarios, not causal estimates."""
from pathlib import Path
import csv,json,random,statistics
ROOT=Path(__file__).resolve().parent

def summarize(rows):
    hours=[r['total_hours'] for r in rows];ordered=sorted(hours)
    return {'cases':len(rows),'median_hours':round(statistics.median(hours),2),
      'p90_hours':round(ordered[int(.9*(len(ordered)-1))],2),
      'sla_breach_rate':round(sum(x>48 for x in hours)/len(hours),4),
      'rework_rate':round(sum(r['rework'] for r in rows)/len(rows),4),
      'total_queue_hours':round(sum(r['queue_hours'] for r in rows),2)}

def run():
    out=ROOT/'output';out.mkdir(exist_ok=True);rng=random.Random(2027)
    baseline=[];proposed=[]
    for i in range(1500):
        tier='complex' if rng.random()<.3 else 'standard'
        queue=rng.uniform(12,72) if tier=='complex' else rng.uniform(2,40)
        service=rng.uniform(1,8);rework=int(rng.random()<(.25 if tier=='complex' else .1))
        extra=12*rework
        b={'case_id':i,'tier':tier,'queue_hours':round(queue,3),'service_hours':round(service,3),'rework':rework,'total_hours':round(queue+service+extra,3)}
        # Counterfactual: deterministic routing assumption with paired case mix.
        new_queue=queue*(.8 if tier=='complex' else .55)
        p={**b,'queue_hours':round(new_queue,3),'total_hours':round(new_queue+service+extra,3)}
        baseline.append(b);proposed.append(p)
    for name,rows in [('baseline',baseline),('routing_scenario',proposed)]:
        with (out/f'{name}.csv').open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result={'dataset':'synthetic paired cases; fixed seed 2027','baseline':summarize(baseline),'routing_scenario':summarize(proposed),
      'assumptions':['Queue time reduced 20% for complex and 45% for standard cases by construction.',
      'No observed rollout, realized savings, staffing reduction or causal evidence.'],
      'segments':{t:{'baseline':summarize([r for r in baseline if r['tier']==t]),'scenario':summarize([r for r in proposed if r['tier']==t])} for t in ['standard','complex']}}
    (out/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (out/'management_memo.txt').write_text(
      'SYNTHETIC CASE - routing proposal\n'
      'Recommendation: test a standard-case triage rule with the process owner; preserve manual escalation for complex cases.\n'
      'Current flow: intake -> queue -> review -> possible rework -> closure.\n'
      'Proposed flow: intake -> validation -> tier routing -> review -> closure.\n'
      'Pilot design: randomized comparable cases if feasible; report P90 and breach rates by tier, not only averages.\n'
      'Guardrails: review accuracy, escalation rate and staff workload. Revert if error rates increase.\n'
      'RACI proposal: Operations owns process; analyst measures; compliance approves control changes; engineering implements. These are hypothetical roles, not actual collaborators.\n'
      'Risks: omitted arrival patterns/capacity constraints; queue reductions are assumptions. Do not claim saved business hours.\n',encoding='utf-8')
    return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
