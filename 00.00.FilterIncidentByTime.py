import datetime
import os
import pandas as pd

Analysis_Start_Time ='2020-01-01T00:00:00-05:00'
Analysis_End_Time ='2020-01-31T23:59:59-05:00'

# Add ISO timestamp column in the incident file
Event_path = os.getcwd()+"/Incidents/events_result_loop_keep_45_subset.csv"
Event_dataframe = pd.read_csv(Event_path)

Start_Timestep = datetime.datetime.fromisoformat(Analysis_Start_Time).timestamp()
End_Timestep = datetime.datetime.fromisoformat(Analysis_End_Time).timestamp()

Start_Time_list = [datetime.datetime.fromisoformat(Event_dataframe.loc[index]['Start_Time']).timestamp()
                   for index, _ in Event_dataframe.iterrows()]

End_Time_List = [datetime.datetime.fromisoformat(Event_dataframe.loc[index]['Closed_Time']).timestamp()
                 for index, _ in Event_dataframe.iterrows()]

Event_dataframe['Start Time Stamp'] = Start_Time_list
Event_dataframe['End Time Stamp'] = End_Time_List

# filter Inciednts by condition
Out_Put_File = Event_dataframe[(Event_dataframe['Start Time Stamp'] > Start_Timestep)
                               & (Event_dataframe['End Time Stamp'] < End_Timestep)]

Out_Put_File.to_csv(os.getcwd()+'/2020JanIncident.csv', index=False)
