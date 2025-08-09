from cfe.df_utils import df_to_orgtbl
import pandas as pd

d = {}
for t in ['2005-06','2009-10','2010-11','2011-12','2013-14','2015-16','2018-19','2019-20']:
    d[t] = pd.read_csv('../'+t+'/_/unitlabels.csv',index_col=0).squeeze()

d = pd.DataFrame(d)
print(df_to_orgtbl(d))
