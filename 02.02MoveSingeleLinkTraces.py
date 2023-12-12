# import necessary libraries
import os
import glob
import csv

path = os.getcwd()+"/ODMatchedTrace"
output_path = os.getcwd()+"/2ODMatchedTrace"

print(path)
csv_files = glob.glob(os.path.join(path, "*.csv"))

def Read_Edge_String(string):
    li = list(string[1:-1].split(','))
    for edge_i in range(len(li)):
        li[edge_i] = eval(li[edge_i])
    return li

Rearrange_Trace_Dict_by_OD_list = {}

for OD_trace_file in csv_files:
    if OD_trace_file[-17:-11] == OD_trace_file[-10:-4]:
        continue
    else:
        output_csv = os.path.join(output_path, output_path+OD_trace_file[-18:])
        print(output_csv)
        with open(OD_trace_file, 'r') as inp, open(output_csv, 'w') as out:
            writer = csv.writer(out)
            i = 0
            for row in csv.reader(inp):
                if i == 0:
                    writer.writerow(row)
                    i += 1
                else:
                    Real_Link_Record = Read_Edge_String(row[-1])
                    if len(Real_Link_Record) != 1:
                        writer.writerow(row)
