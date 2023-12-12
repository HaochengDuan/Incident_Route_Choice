import os
import glob
import csv
import geopandas as gpd
import copy


Trajectory_Dict = {}
########################################################################################################################
#                                               Load geo information                                                   #
########################################################################################################################
link_file = gpd.read_file('Network_consolidated/mwcog_sub_links_step6_am_clustering_internal.geojson')
node_file = gpd.read_file('Network_consolidated/mwcog_sub_nodes_step6_am_clustering_internal.geojson')
link_file.iloc[:, :-1].to_csv("links.csv")
node_file.iloc[:, :-1].to_csv("nodes.csv")
link_data = list(csv.reader(open("links.csv")))
node_data = list(csv.reader(open("nodes.csv")))
########################################################################################################################
#                                            build up node/link info dict                                              #
########################################################################################################################
Link_Dict = {}
Node_Dict = {}
for i in range(1, len(node_data)):
    Node_Dict[node_data[i][1]] = [node_data[i][2], int(node_data[i][3]), node_data[i][4], node_data[i][5]]
    # list 0 FTYPE
    # list 1 isOD
    # list 2 X
    # list 3 Y
for j in range(1, len(link_data)):
    Link_Dict[link_data[j][1]] = [link_data[j][2], link_data[j][3], float(link_data[j][4]), link_data[j][5],
                                  link_data[j][6], link_data[j][7], int(link_data[j][8])]
    # list 0 A
    # list 1 B
    # list 2 DIST
    # list 3 POSTPD
    # list 4 FACTYPE
    # list 5 LANES
    # list 6 isOD
UpstreamLinkDict = {}
DownstreamLinkDict = {}

# build up empty dict
for i in range(1, len(node_data)):
    UpstreamLinkDict[node_data[i][1]] = []
    DownstreamLinkDict[node_data[i][1]] = []

for i in range(1, len(link_data)):
    UpstreamLinkDict[link_data[i][3]].append(link_data[i][1])
    DownstreamLinkDict[link_data[i][2]].append(link_data[i][1])
########################################################################################################################
#                                            Match OD                                                                  #
########################################################################################################################
Maximum_Search_step = 10
Maximum_Search_Length = 5 # in miles

def serach_O(link):
    Found_Indicator = 0
    UpstreamNode = Link_Dict[link][0] # need to change if last edge in point is not edge
    if Node_Dict[UpstreamNode][1] == 1: # need to change if last edge in point is not edge
        Original_Node = UpstreamNode
        Original_Link = link
    else:
        possible_searched_list = [[link]]
        founded_list = []
        for i in range(Maximum_Search_step):
            new_possible_searched_list = []
            for j in range(len(possible_searched_list)):
                this_link = possible_searched_list[j][0]
                this_link_upstream_node = Link_Dict[this_link][0]
                possible_upstream_link = UpstreamLinkDict[this_link_upstream_node]
                for upstream_link in possible_upstream_link:
                    Searched_List = possible_searched_list[j].copy()
                    Searched_List.insert(0, str(upstream_link))
                    if check_circle_for_O(Searched_List):
                        continue
                    if Node_Dict[Link_Dict[upstream_link][0]][1] == 1:
                        founded_list.append(Searched_List)
                    else:
                        new_possible_searched_list.append(Searched_List)
            possible_searched_list = new_possible_searched_list
        if len(founded_list) == 0:
            Original_Node = 'NoOriginalFounded'
        else:
            Length_list = []
            for j in range(len(founded_list)):
                length = 0
                for link_id in founded_list[j]:
                    length += Link_Dict[link_id][2]
                Length_list.append(length)
            index_min = min(range(len(Length_list)), key=Length_list.__getitem__)
            if Length_list[index_min] > Maximum_Search_Length:
                Original_Node = 'NoOriginalFounded'
            else:
                Original_Node = Link_Dict[founded_list[index_min][0]][0]
                Found_Indicator = 1
        if Found_Indicator == 1:
            Original_Link = founded_list[index_min][0]
        else:
            Original_Link = "NoLinkFound"
    return [Original_Node, Original_Link]


def check_circle_for_O(link_list=list):
    Indicate_number = 0
    UpStreamNode = Link_Dict[link_list[0]][0]
    for link in link_list[1:]:
        if UpStreamNode == Link_Dict[link][0] or UpStreamNode == Link_Dict[link][1]:
            Indicate_number = 1
    return Indicate_number
# 1 indicates it is a circle
# 0 indicates it is not a circle

def serach_D(link):
    Found_Indicator = 0
    DownstreamNode = Link_Dict[link][1] # need to change if last edge in point is not edge
    if Node_Dict[DownstreamNode][1] == 1: # need to change if last edge in point is not edge
        Destination_Node = DownstreamNode
        Destination_Link = link
    else:
        possible_searched_list = [[link]]
        founded_list = []
        for i in range(Maximum_Search_step):
            new_possible_searched_list = []
            for j in range(len(possible_searched_list)):
                this_link = possible_searched_list[j][-1]
                this_link_downstream_node = Link_Dict[this_link][1]
                possible_downstream_link = DownstreamLinkDict[this_link_downstream_node]
                for downstream_link in possible_downstream_link:
                    Searched_List = possible_searched_list[j].copy()
                    Searched_List.append(str(downstream_link))
                    if check_circle_for_D(Searched_List):
                        continue
                    if Node_Dict[Link_Dict[downstream_link][1]][1] == 1:
                        founded_list.append(Searched_List)
                    else:
                        new_possible_searched_list.append(Searched_List)
            possible_searched_list = new_possible_searched_list
        if len(founded_list) == 0:
            Destination_Node = 'NoDestinationFounded'
        else:
            Length_list = []
            for j in range(len(founded_list)):
                length = 0
                for link_id in founded_list[j]:
                    length += Link_Dict[link_id][2]
                Length_list.append(length)
            index_min = min(range(len(Length_list)), key=Length_list.__getitem__)
            if Length_list[index_min] > Maximum_Search_Length:
                Destination_Node = 'NoDestinationFounded'
            else:
                Destination_Node = Link_Dict[founded_list[index_min][-1]][1]
                Found_Indicator= 1
        if Found_Indicator == 1:
            Destination_Link = founded_list[index_min][-1]
        else:
            Destination_Link = "NoLinkFound"

    return [Destination_Node, Destination_Link]

def check_circle_for_D(link_list=list):
    Indicate_number = 0
    DownStreamNode = Link_Dict[link_list[-1]][1]
    for link in link_list[:-1]:
        if DownStreamNode  == Link_Dict[link][0] or DownStreamNode == Link_Dict[link][1]:
            Indicate_number = 1
    return Indicate_number
# 1 indicates it is a circle
# 0 indicates it is not a circle
########################################################################################################################
#                                                  Connect Links                                                       #
########################################################################################################################
Maximum_Searched_Connected_Link_Number = 10
Maximum_Searched_Connected_Link_Length = 5

def ConnectLinksByShortestLength(link, targeted_Link):
    TargetNode = Link_Dict[targeted_Link][0]
    possible_searched_list = [[link]]
    founded_list = []
    for i in range(Maximum_Searched_Connected_Link_Number):
        new_possible_searched_list = []
        for j in range(len(possible_searched_list)):
            this_link = possible_searched_list[j][-1]
            this_link_downstream_node = Link_Dict[this_link][1]
            possible_downstream_link = DownstreamLinkDict[this_link_downstream_node]
            for downstream_link in possible_downstream_link:
                Searched_List = possible_searched_list[j].copy()
                Searched_List.append(str(downstream_link))
                if check_circle_for_D(Searched_List):
                    continue
                if Node_Dict[Link_Dict[downstream_link][1]][1] == 1:
                    continue
                if Link_Dict[downstream_link][1] == TargetNode:
                    founded_list.append(Searched_List)
                else:
                    new_possible_searched_list.append(Searched_List)
        possible_searched_list = new_possible_searched_list
    if len(founded_list) == 0:
        ConnectedLinkList = ['NoConnectionFounded']
    else:
        Length_list = []
        for j in range(len(founded_list)):
            length = 0
            for link_id in founded_list[j]:
                length += Link_Dict[link_id][2]
            Length_list.append(length)
        index_min = min(range(len(Length_list)), key=Length_list.__getitem__)
        if Length_list[index_min] > Maximum_Searched_Connected_Link_Length:
            ConnectedLinkList = ['NoConnectionFounded']
        else:
            ConnectedLinkList = founded_list[index_min]
            del ConnectedLinkList[0]
    return ConnectedLinkList
########################################################################################################################
#                                                Check Continuous                                                      #
########################################################################################################################
def check_continuity(list): # only works for matched links
    continuity_indicator = 1
    if len(list) == 1:
        continuity_indicator = 0
    else:
        for i in range(len(list)-1):
            if Link_Dict[list[i]][1] == Link_Dict[list[i+1]][0]:
                continue
            else:
                continuity_indicator = 0
                break
    return continuity_indicator
# 1 indicates it is continuous
# 0 indicates it is not continuous

Traj_path = os.getcwd()+"/HERE/Step1_sjoin"
csv_files = glob.glob(os.path.join(Traj_path, "*.csv"))

def insert_by_time_seq(traj_list=list, new_data_point=list):
    time = new_data_point[0]  # need to change if point 0 is not time
    for i in range(len(traj_list)):
        if traj_list[i][0] > time: # need to change if point 0 is not time
            traj_list.insert(i, new_data_point)
            break
    return traj_list

j = 0
for f in csv_files:
    df = csv.reader(open(f))
    Day = f[-16:-8]
    Time = f[-8:-4]
    if Day not in Trajectory_Dict.keys():
        Trajectory_Dict[Day] = {}
        Trajectory_Dict[Day][Time] = {}
    else:
        Trajectory_Dict[Day][Time] = {}
    i = 0
    for row in df:
        if i == 0:
            i += 1
            continue
        if row[0] not in Trajectory_Dict[Day][Time].keys():
            point = [int(row[1]), str(row[6]), row[8]]
            # print(type(str(row[6])))
            Trajectory_Dict[Day][Time][row[0]] = {}
            Trajectory_Dict[Day][Time][row[0]]['RealTraj'] = [point]
        else:
            point = [int(row[1]), str(row[6]), row[8]]
            insert_by_time_seq(Trajectory_Dict[Day][Time][row[0]]['RealTraj'], point)
    #if j == 1:
        #break
    j += 1


Output_Trace_Dict = copy.deepcopy(Trajectory_Dict)

bad_number = 0
total_number = 0
remove_number = 0

continuous_number = 0
for Day in Trajectory_Dict.keys():
    for Time in Trajectory_Dict[Day].keys():
        for ID in Trajectory_Dict[Day][Time].keys():
            Trace_List = Trajectory_Dict[Day][Time][ID]['RealTraj']
            not_matched_indicator = 0
            for point in Trace_List:
                if point[-1] not in Link_Dict.keys():
                    bad_number += 1
                    not_matched_indicator = 1
                    break
            if not_matched_indicator == 1:
                del Output_Trace_Dict[Day][Time][ID]
                # remove traces that not in
            else:
                First_Link_ID = Trace_List[0][-1]
                Last_Link_ID = Trace_List[-1][-1]
                Origin_Node = serach_O(First_Link_ID)[0]
                Origin_Link = serach_O(First_Link_ID)[1]
                Destination_Node = serach_D(Last_Link_ID)[0]
                Destination_Link = serach_D(Last_Link_ID)[1]
                if Origin_Node == 'NoOriginalFounded' or Destination_Node == 'NoDestinationFounded':
                    del Output_Trace_Dict[Day][Time][ID]
                    remove_number += 1
                else:
                    Output_Trace_Dict[Day][Time][ID]['O'] = Origin_Node
                    Output_Trace_Dict[Day][Time][ID]['Original_Link'] = Origin_Link
                    Output_Trace_Dict[Day][Time][ID]['D'] = Destination_Node
                    Output_Trace_Dict[Day][Time][ID]['Destination_Link'] = Destination_Link
                    # build real link record

                    Output_Trace_Dict[Day][Time][ID]['real_link_record'] = []
                    for point in Trace_List:
                        if point[-1] not in Output_Trace_Dict[Day][Time][ID]['real_link_record']:
                            Output_Trace_Dict[Day][Time][ID]['real_link_record'].append(point[-1])

                    # build estimated link record
                    OD_added_link_list = Output_Trace_Dict[Day][Time][ID]['real_link_record'].copy()
                    if Origin_Link not in Output_Trace_Dict[Day][Time][ID]['real_link_record']:
                        OD_added_link_list.insert(0, Origin_Link)
                    if Destination_Link not in Output_Trace_Dict[Day][Time][ID]['real_link_record']:
                        OD_added_link_list.append(Destination_Link)

                    Output_Trace_Dict[Day][Time][ID]['estimated_link_record'] = []
                    for i in range(len(OD_added_link_list)-1):
                        Output_Trace_Dict[Day][Time][ID]['estimated_link_record'].append(OD_added_link_list[i])
                        if check_continuity([OD_added_link_list[i], OD_added_link_list[i+1]]):
                            continue
                        else:
                            connected_link_list = ConnectLinksByShortestLength(OD_added_link_list[i], OD_added_link_list[i+1])
                            if connected_link_list[0] == 'NoConnectionFounded':
                                del Output_Trace_Dict[Day][Time][ID]
                                break
                            else:
                                for connected_link in connected_link_list:
                                    Output_Trace_Dict[Day][Time][ID]['estimated_link_record'].append(connected_link)
                    if ID in Output_Trace_Dict[Day][Time].keys():
                        Output_Trace_Dict[Day][Time][ID]['estimated_link_record'].append(Destination_Link)
                        Output_Trace_Dict[Day][Time][ID]["departure_timestamp"] = int(Trace_List[0][0])
            total_number += 1

Output_Trace_Dict_by_OD = {}

for Day in Output_Trace_Dict.keys():
    for Time in Output_Trace_Dict[Day].keys():
        for ID in Output_Trace_Dict[Day][Time].keys():
            OD_pair = str(Output_Trace_Dict[Day][Time][ID]['O']+"_"+Output_Trace_Dict[Day][Time][ID]['D'])
            if OD_pair in Output_Trace_Dict_by_OD.keys():
                new_row = {}
                new_row['ID'] = ID
                new_row['DepartureTimestamp'] = Output_Trace_Dict[Day][Time][ID]['departure_timestamp']
                new_row['EstimatedLinkRecord'] = Output_Trace_Dict[Day][Time][ID]['estimated_link_record']
                new_row['RealTraj'] = Output_Trace_Dict[Day][Time][ID]['RealTraj']
                new_row['RealLinkRecord'] = Output_Trace_Dict[Day][Time][ID]['real_link_record']
                Output_Trace_Dict_by_OD[OD_pair].append(new_row)
            else:
                Output_Trace_Dict_by_OD[OD_pair] = []
                new_row={}
                new_row['ID'] = ID
                new_row['DepartureTimestamp'] = Output_Trace_Dict[Day][Time][ID]['departure_timestamp']
                new_row['EstimatedLinkRecord'] = Output_Trace_Dict[Day][Time][ID]['estimated_link_record']
                new_row['RealTraj'] = Output_Trace_Dict[Day][Time][ID]['RealTraj']
                new_row['RealLinkRecord'] = Output_Trace_Dict[Day][Time][ID]['real_link_record']
                Output_Trace_Dict_by_OD[OD_pair].append(new_row)

csv_columns = ['ID', 'DepartureTimestamp', 'EstimatedLinkRecord', 'RealTraj', 'RealLinkRecord']
for OD_pair in Output_Trace_Dict_by_OD.keys():
    stored_CSV_file = "ODMatchedTrace/"+OD_pair+".csv"
    with open(stored_CSV_file, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in Output_Trace_Dict_by_OD[OD_pair]:
            writer.writerow(data)

file = open('OD_pair.txt', 'w')
for OD_pair in Output_Trace_Dict_by_OD.keys():
    file.write(OD_pair+"\n")

print(len(list(Output_Trace_Dict_by_OD.keys())))
breakpoint()

count_number = 0
for Day in Output_Trace_Dict.keys():
    for Time in Output_Trace_Dict[Day].keys():
        for ID in Output_Trace_Dict[Day][Time].keys():
            count_number += 1

print("remove_number", remove_number)
print("bad_number", bad_number)
print("count_number", count_number)
print("total", total_number)
print("continuous", continuous_number)




