"""Fictional SGD manufacturing borrower. Educational credit case, not a lending recommendation."""
from pathlib import Path
import csv,json
ROOT=Path(__file__).resolve().parent

def evaluate(revenue,ebitda_margin,debt,cash,interest_rate,dso,dio,dpo):
    cogs=revenue*.65;ebitda=revenue*ebitda_margin;depreciation=revenue*.025
    ebit=ebitda-depreciation;interest=debt*interest_rate
    receivables=revenue*dso/365;inventory=cogs*dio/365;payables=cogs*dpo/365
    return {'revenue_sgd':round(revenue),'ebitda_sgd':round(ebitda),'ebit_sgd':round(ebit),
      'interest_sgd':round(interest),'net_debt_to_ebitda':round((debt-cash)/ebitda,3) if ebitda>0 else None,
      'ebit_interest_coverage':round(ebit/interest,3) if interest>0 else None,
      'cash_conversion_cycle_days':dso+dio-dpo,
      'operating_working_capital_sgd':round(receivables+inventory-payables),
      'debt_sgd':debt,'cash_sgd':cash,'dso':dso,'dio':dio,'dpo':dpo}

def run():
    out=ROOT/'output';out.mkdir(exist_ok=True)
    base=evaluate(25000000,.14,6000000,1200000,.06,60,55,40)
    stress=evaluate(22500000,.10,7000000,1000000,.08,75,65,35)
    assumptions={'currency':'SGD','borrower':'Fictional APAC Components Pte Ltd','all_inputs':'invented for portfolio education',
      'base':{'revenue':25000000,'ebitda_margin':.14,'debt':6000000,'cash':1200000,'interest_rate':.06,'dso':60,'dio':55,'dpo':40},
      'stress':{'revenue':22500000,'ebitda_margin':.10,'debt':7000000,'cash':1000000,'interest_rate':.08,'dso':75,'dio':65,'dpo':35}}
    (out/'assumptions.json').write_text(json.dumps(assumptions,indent=2),encoding='utf-8')
    rows=[]
    for growth in [-.2,-.1,0,.1]:
        for rate in [.06,.08,.10]:
            r=evaluate(25000000*(1+growth),.10,7000000,1000000,rate,75,65,35)
            rows.append({'revenue_growth':growth,'interest_rate':rate,**r})
    with (out/'sensitivity.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    result={'base':base,'stress':stress,'additional_working_capital_sgd':stress['operating_working_capital_sgd']-base['operating_working_capital_sgd'],
      'limitations':['No audited statements, collateral valuation, cash-flow model or actual bank credit policy.',
      'Coverage uses EBIT / interest, not EBITDA / interest or debt service coverage.',
      'Working-capital delta mixes sales and payment-term changes; no causal decomposition claimed.']}
    (out/'metrics.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (out/'credit_memo.txt').write_text(
      'FICTIONAL BORROWER - educational credit discussion\n'
      'Business: components supplier with a 75-day base cash conversion cycle.\n'
      f"Base EBIT/interest {base['ebit_interest_coverage']}x; stressed {stress['ebit_interest_coverage']}x.\n"
      f"Operating working-capital requirement rises by SGD {result['additional_working_capital_sgd']:,} in the joint stress scenario.\n"
      'Discussion: size a revolving facility to a verified borrowing base and seasonality; avoid relying solely on EBITDA.\n'
      'Before a credit decision: request audited statements, debt maturity schedule, customer concentration, aged receivables, inventory and FX exposures.\n'
      'Potential products to discuss: cash management, receivables finance and FX hedging if exposures are established. No actual product suitability assessment is performed.\n'
      'Monitoring proposal: quarterly leverage/coverage, overdue receivables and covenant headroom; thresholds require an actual lender policy.\n'
      'No claim of a real client engagement, approved facility or observed financial impact.\n',encoding='utf-8')
    return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
