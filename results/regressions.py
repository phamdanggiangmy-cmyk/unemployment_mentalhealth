import pandas as pd, numpy as np, statsmodels.formula.api as smf, json, sys
import os
base=""  # run from the project root folder
mh=pd.read_csv(base+'13100465.csv',usecols=['REF_DATE','GEO','Age group','Gender','Indicators','Characteristics','VALUE'])
u=pd.read_csv("results/unemp_sub.csv")
ages=['15 to 24 years','25 to 44 years','45 to 64 years','65 years and over']
provs=['Newfoundland and Labrador','Prince Edward Island','Nova Scotia','New Brunswick','Quebec','Ontario','Manitoba','Saskatchewan','Alberta','British Columbia']
IND=sys.argv[1] if len(sys.argv)>1 else 'Major depressive episode, 12 months'
def get(ch):
    s=mh[(mh.Indicators==IND)&(mh.Characteristics==ch)&mh.GEO.isin(provs)&mh['Age group'].isin(ages)&mh.Gender.isin(['Men+','Women+'])]
    return s.rename(columns={'REF_DATE':'year','GEO':'geo','Age group':'age','Gender':'gender'})[['year','geo','age','gender','VALUE']]
p=get('Percent').rename(columns={'VALUE':'mh'}); cv=get('Coefficient of variation for percent').rename(columns={'VALUE':'cv'})
m=p.merge(cv,on=['year','geo','age','gender'],how='left')
u['year']=u.REF_DATE.str[:4].astype(int)
ua=u[u.GEO.isin(provs)&u['Age group'].isin(ages)&u.Gender.isin(['Men+','Women+'])].groupby(['year','GEO','Age group','Gender'],as_index=False).VALUE.mean()
ua.columns=['year','geo','age','gender','unemp']
df=m.merge(ua,on=['year','geo','age','gender'])
print('rows mh',len(p),'nonnull',p.mh.notna().sum(),'merged',len(df)); df=df.dropna(subset=['mh','unemp'])
print('analysis rows',len(df)); print(df.groupby('year').size().to_dict(), df.groupby('age').size().to_dict())
df.to_csv('results/merged_depression_12m.csv',index=False)
print('r overall',round(df.mh.corr(df.unemp),3))
print('r within age', df.groupby('age').apply(lambda g: round(g.mh.corr(g.unemp),3)).to_dict())
print('means by age'); print(df.groupby('age')[['mh','unemp']].mean().round(2))
print('means by gender'); print(df.groupby('gender')[['mh','unemp']].mean().round(2))
prov="C(geo, Treatment('Ontario'))"; g="C(gender, Treatment('Men+'))"
m1=smf.ols('mh ~ unemp',df).fit(cov_type='HC3')
m2=smf.ols(f'mh ~ unemp + {g} + C(age) + {prov} + C(year)',df).fit(cov_type='HC3')
m3=smf.ols(f'mh ~ unemp*{g} + unemp*{prov} + C(age) + C(year)',df).fit(cov_type='HC3')
for n,mm in [('M1',m1),('M2',m2)]:
    print(n,'b=%.3f se=%.3f p=%.4f R2=%.3f adjR2=%.3f N=%d'%(mm.params['unemp'],mm.bse['unemp'],mm.pvalues['unemp'],mm.rsquared,mm.rsquared_adj,mm.nobs))
print('M2 other terms'); print(pd.DataFrame({'b':m2.params,'p':m2.pvalues}).round(3))
print('M3 R2=%.3f adj=%.3f N=%d'%(m3.rsquared,m3.rsquared_adj,m3.nobs))
print(pd.DataFrame({'b':m3.params,'se':m3.bse,'p':m3.pvalues}).filter(like='unemp',axis=0).round(3))
print(m3.wald_test_terms(scalar=True))
# slopes
gi=[k for k in m3.params.index if k.startswith('unemp:C(gender')][0]
w=np.zeros(len(m3.params)); w[list(m3.params.index).index('unemp')]=1; w[list(m3.params.index).index(gi)]=1
t=m3.t_test(w); print('women slope',float(t.effect),float(t.sd),float(t.pvalue))
rows=[]
for pv in provs:
    w=np.zeros(len(m3.params)); w[list(m3.params.index).index('unemp')]=1
    k=f"unemp:{prov}[T.{pv}]"
    if k in m3.params.index: w[list(m3.params.index).index(k)]=1
    t=m3.t_test(w); ci=t.conf_int()[0]
    rows.append((pv,round(float(t.effect),3),round(ci[0],3),round(ci[1],3),round(float(m3.pvalues.get(k,np.nan)),3)))
print(pd.DataFrame(rows,columns=['prov','slope','lo','hi','p_vs_ON']).sort_values('slope'))
# robustness: no 65+, low cv
for lab,d in [('no65',df[df.age!='65 years and over']),('cv<=33',df[df.cv.fillna(0)<=33.3])]:
    a=smf.ols(f'mh ~ unemp + {g} + C(age) + {prov} + C(year)',d).fit(cov_type='HC3')
    print(lab,'M2 b=%.3f p=%.4f N=%d'%(a.params['unemp'],a.pvalues['unemp'],a.nobs))
