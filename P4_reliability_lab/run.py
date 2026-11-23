"""Localhost-only HTTP fault injection lab. Does not contact or load-test external hosts."""
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from urllib.request import build_opener,ProxyHandler
from urllib.error import HTTPError
import csv,json,time,math
ROOT=Path(__file__).resolve().parent

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        phase=self.server.phase
        if self.path=='/health':status,delay=200,0
        else:
            idx=int(self.path.split('/')[-1]);status=503 if phase=='injected' and idx%4==0 else 200
            delay=.065 if phase=='injected' and idx%5==0 else .004
        time.sleep(delay)
        payload=json.dumps({'status':status,'phase':phase}).encode()
        self.send_response(status);self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)

def summary(rows,target=.99,latency_ms=40):
    good=sum(r['status']==200 and r['latency_ms']<=latency_ms for r in rows)
    n=len(rows);lat=sorted(r['latency_ms'] for r in rows)
    return {'requests':n,'http_success_rate':round(sum(r['status']==200 for r in rows)/n,4),
      'good_request_rate':round(good/n,4),'p95_latency_ms':round(lat[math.ceil(.95*n)-1],3),
      'observed_bad_requests':n-good,'error_budget_burn_rate':round((1-good/n)/(1-target),2)}

def run():
    out=ROOT/'output';out.mkdir(exist_ok=True)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.daemon_threads=True
    worker=Thread(target=server.serve_forever,daemon=True);worker.start()
    rows=[]
    opener=build_opener(ProxyHandler({}))
    def request(idx):
        start=time.perf_counter()
        try:
            with opener.open(f'http://127.0.0.1:{server.server_port}/work/{idx}',timeout=3) as r:
                status=r.status;r.read()
        except HTTPError as e:status=e.code;e.read();e.close()
        except OSError:status=0
        return {'phase':server.phase,'request_id':idx,'status':status,'latency_ms':round((time.perf_counter()-start)*1000,3)}
    try:
        for phase in ['baseline','injected','recovery']:
            server.phase=phase
            with ThreadPoolExecutor(max_workers=3) as pool:rows.extend(pool.map(request,range(60)))
    finally:
        server.shutdown();server.server_close();worker.join(timeout=3)
    if any(sum(r['status']==200 for r in rows if r['phase']==p)==0 for p in ['baseline','injected','recovery']):
        raise RuntimeError('Local HTTP service could not be reached. Inspect local sandbox/firewall configuration; no benchmark claims can be made.')
    with (out/'requests.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result={'environment':'local host only, Python stdlib HTTP service','slo_definition':'200 status AND latency <= 40ms; educational target 99%',
      'phases':{p:summary([r for r in rows if r['phase']==p]) for p in ['baseline','injected','recovery']},
      'limitations':['Latency depends on this workstation; this is not a production benchmark.',
      '60 requests per phase and no multi-region/DR/real advertising system.',
      'Recovery is removal of injected behavior; it does not demonstrate production remediation.']}
    (out/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (out/'incident_review.txt').write_text(
      'LOCAL LAB INCIDENT REVIEW\n'
      'Trigger: deliberate 503 responses on every fourth request; 65ms handler delay on every fifth request.\n'
      'Detection: request-level status and elapsed-time SLI; evaluate burn against a 99% lab target.\n'
      'Isolation: compare phase CSVs and HTTP status vs latency. Root cause is known injected handler behavior.\n'
      'Recovery: disable injected phase and rerun requests; inspect host-dependent measured results.\n'
      'Follow-up: add dependency timeout tests, concurrent saturation sweeps and actual Linux process/network inspection.\n'
      'No production outage, on-call ownership, disaster recovery exercise or MTTR claim.\n',encoding='utf-8')
    return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
