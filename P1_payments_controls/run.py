"""AI-assisted portfolio case. Synthetic payments; no Stripe/Citi data or affiliation."""
from pathlib import Path
import csv, json, random, sqlite3
from collections import Counter

ROOT = Path(__file__).resolve().parent

def reconcile(conn):
    # Aggregate first: duplicate partner records must not inflate ledger sums.
    return conn.execute('''
    WITH partner AS (
      SELECT payment_id, COUNT(*) n, MIN(currency) currency,
             SUM(gross_cents-fee_cents) net_cents
      FROM settlements GROUP BY payment_id
    )
    SELECT p.payment_id,p.currency,p.net_cents,COALESCE(s.net_cents,0),
      CASE WHEN s.payment_id IS NULL THEN 'missing'
           WHEN s.n>1 THEN 'duplicate'
           WHEN p.currency<>s.currency THEN 'currency'
           WHEN p.net_cents<>s.net_cents THEN 'amount'
           ELSE 'matched' END reason,
      p.age_days,p.partner
    FROM payments p LEFT JOIN partner s USING(payment_id)
    UNION ALL
    SELECT s.payment_id,s.currency,0,s.net_cents,'orphan',0,'unmapped'
    FROM partner s LEFT JOIN payments p USING(payment_id) WHERE p.payment_id IS NULL
    ORDER BY 1
    ''').fetchall()

def generate(conn, n=10000):
    rng=random.Random(27)
    conn.executescript('''CREATE TABLE payments(payment_id TEXT PRIMARY KEY,
    currency TEXT,net_cents INTEGER,age_days INTEGER,partner TEXT);
    CREATE TABLE settlements(payment_id TEXT,currency TEXT,gross_cents INTEGER,fee_cents INTEGER);''')
    for i in range(n):
        pid=f'pay_{i:06d}'; currency=['SGD','USD','EUR'][i%3]
        gross=rng.randrange(1000,500000); fee=gross*29//1000+30
        age=rng.randrange(0,46); partner=['A','B','C'][i%3]
        conn.execute('INSERT INTO payments VALUES(?,?,?,?,?)',(pid,currency,gross-fee,age,partner))
        rem=i%1000
        if rem<5: continue
        net_adjust=100 if 10<=rem<15 else 0
        cur='JPY' if 15<=rem<20 else currency
        conn.execute('INSERT INTO settlements VALUES(?,?,?,?)',(pid,cur,gross+net_adjust,fee))
        if 5<=rem<10:
            conn.execute('INSERT INTO settlements VALUES(?,?,?,?)',(pid,cur,gross,fee))
    for i in range(10):
        conn.execute('INSERT INTO settlements VALUES(?,?,?,?)',(f'orphan_{i}','SGD',10000,100))
    conn.commit()

def run():
    out=ROOT/'output'; out.mkdir(exist_ok=True)
    # Rebuild only this case's generated database; no raw source file is overwritten.
    conn=sqlite3.connect(':memory:'); generate(conn)
    rows=reconcile(conn); counts=Counter(r[4] for r in rows)
    exceptions=[r for r in rows if r[4]!='matched']
    with (out/'exceptions.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['payment_id','currency','ledger_net_cents','partner_net_cents','reason','age_days','partner']);w.writerows(exceptions)
    # Age by ledger currency. Amounts in different currencies are never added.
    aging={}
    for pid,cur,ledger,settled,reason,age,partner in rows:
        if reason=='matched' or reason=='orphan':continue
        bucket='0-7' if age<=7 else '8-30' if age<=30 else '31+'
        key=f'{cur}:{bucket}';aging[key]=aging.get(key,0)+ledger
    partner_costs=conn.execute('''SELECT currency, SUM(fee_cents),
      SUM(gross_cents),COUNT(*) FROM settlements
      WHERE payment_id NOT LIKE 'orphan_%' GROUP BY currency''').fetchall()
    result={'dataset':'synthetic seeded payments, 2027 scenario','seed':27,'ledger_payments':10000,
      'reconciliation_counts':dict(counts),'exceptions':len(exceptions),
      'unresolved_ledger_exposure_by_currency_age_cents':aging,
      'partner_raw_fee_basis_points':{c:round(f/g*10000,2) for c,f,g,n in partner_costs},
      'limitations':['Raw partner fee metric includes injected duplicates and corrupt rows; quarantine before commercial use.',
      'Unresolved exposure is a review queue, not proven cash loss or a sum across currencies.',
      'No refunds, FX, partial settlement, production API or real client records.']}
    (out/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    disk=sqlite3.connect(out/'payments.sqlite');conn.backup(disk);disk.close();conn.close()
    (out/'decision_note.txt').write_text(
      'SYNTHETIC CASE - payment controls and client cash visibility\n'
      f'{len(exceptions)} exception records require review; these are not measured financial losses.\n'
      'Prioritize duplicate/currency exceptions before exposing figures to treasury users.\n'
      'Use currency-specific aging queues; assign an owner and reconciliation SLA to every exception.\n'
      'Proposed pilot: review a sample with a finance stakeholder, agree on net/fee semantics, then measure false alerts and resolution time.\n'
      'For Citi Services: connect unresolved receivables to cash visibility and working-capital conversations.\n'
      'For Stripe: explain key uniqueness, idempotent runs, matching precedence and a safe backfill.\n',encoding='utf-8')
    return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
