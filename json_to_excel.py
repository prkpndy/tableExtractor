import json
import pandas as pd

with open('/home/prkpndy/ankaha/pdf-text-extract-making-changes/pdf/data_COVID19Health_Fac08052020/ans.json') as json_file:
    data = json.load(json_file)

writer = pd.ExcelWriter('/home/prkpndy/ankaha/pdf-text-extract-making-changes/pdf/data_COVID19Health_Fac08052020/ans.xlsx', engine='xlsxwriter')

p = 0
for page in data.values():
    t = 0
    for table in page.values():
        content = table['content']
        df = pd.DataFrame(content)
        df.to_excel(writer, sheet_name='page'+str(p)+'table'+str(t), index=False)
        t += 1
    p += 1

writer.save()