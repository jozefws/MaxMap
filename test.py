import pandas as pd 
dfcount = pd.read_csv('citycount.csv', index_col=0)

res = dfcount.query("city=='%s'" % ("Cardiff"))
dfcount.at[res.index[res['city'] == 'Cardiff'].tolist()[0], "count"] += 1
print(dfcount.head())