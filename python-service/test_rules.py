"""Run: python test_rules.py  (from python-service, needs the .pkl files)"""
import app

app.load_model()
BASE = dict(Age=35, MonthlyIncome=6000, Department='Research & Development', JobRole='Research Scientist',
            OverTime='No', DistanceFromHome=5, MaritalStatus='Married', Gender='Male',
            TotalWorkingYears=10, YearsAtCompany=5)

def run(**kw):
    resp = app.app.test_client().post('/predict', json={**BASE, **kw})
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()

CASES = [
    # name, overrides, expected prediction
    ("Teacher case: 20y, 1yr exp, ~$235/mo (INR 20k), single", dict(Age=20, MonthlyIncome=235, TotalWorkingYears=1, YearsAtCompany=1, MaritalStatus='Single', JobRole='Sales Representative', Department='Sales'), 'LEAVE'),
    ("Same, but ANY role (lab tech)", dict(Age=20, MonthlyIncome=235, TotalWorkingYears=1, YearsAtCompany=1, MaritalStatus='Single', JobRole='Laboratory Technician'), 'LEAVE'),
    ("Young, low pay, single, 2yr exp", dict(Age=23, MonthlyIncome=1800, TotalWorkingYears=2, YearsAtCompany=2, MaritalStatus='Single'), 'LEAVE'),
    ("Senior manager, married, 20yr, well paid", dict(Age=48, MonthlyIncome=15000, TotalWorkingYears=24, YearsAtCompany=15, JobRole='Manager', Department='Sales'), 'STAY'),
    ("Mid-career, married, average", dict(), 'STAY'),
    ("Young but well paid, married, experienced", dict(Age=26, MonthlyIncome=9000, TotalWorkingYears=4, YearsAtCompany=3), 'STAY'),
    ("Overtime + long commute + low pay", dict(OverTime='Yes', DistanceFromHome=28, MonthlyIncome=2500), 'LEAVE'),
]

bad = 0
for name, kw, want in CASES:
    r = run(**kw)
    ok = r['prediction'] == want
    bad += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {name}\n      model {r['modelPrediction']} {r['modelTurnoverProbability']:.2f}"
          f" -> final {r['prediction']} {r['turnoverProbability']:.2f} ({r['riskLevel']})")
raise SystemExit(bad)
