# import necessary libraries
import os
import glob
import csv
import datetime as dt

path = os.getcwd()+"/2ODMatchedTrace"
output_path = os.getcwd()+"/3ODMatchedTrace"
link_set = set()

print(path)
csv_files = glob.glob(os.path.join(path, "*.csv"))

def Read_Edge_String(string):
    li = list(string[1:-1].split(','))
    for edge_i in range(len(li)):
        li[edge_i] = eval(li[edge_i])
    return li
# format int
def format_int(s):
    if (len(s) == 2) & (s[0] == '0'):
        return int(s[1])
    else:
        return int(s)

# day of week
def dow(s):
    x1, x2, x3 = [format_int(x) for x in s.split('-')]
    return dt.datetime(x1, x2, x3).weekday()
link_set = set()
for OD_trace_file in csv_files:
    output_csv = os.path.join(output_path, output_path + OD_trace_file[-18:])
    with open(OD_trace_file, 'r') as inp, open(output_csv, 'w') as out:
        writer = csv.writer(out)
        i = 0
        for row in csv.reader(inp):
            if i == 0:
                writer.writerow(row)
                i += 1
            else:
                date = row[3][15:25]
                if dow(date) < 5:
                    writer.writerow(row)
                    Estimated_Link_Record = Read_Edge_String(row[2])
                    print(Estimated_Link_Record)
                    link_set.update(Estimated_Link_Record)

link_ls = list(link_set)

file = open('Estimated_link_used.txt', 'w')
for link in link_ls:
    file.write(link+"\n")
