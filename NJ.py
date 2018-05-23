import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
pd.options.mode.chained_assignment = None

New_Capacity = input("Enter MW installed every month: ")
for j in range(3):
    Gats_Data= pd.read_excel("C:\\Users\\craghuram\\Desktop\\Python\\I-O files\\NJ_Model.xlsx")
    NJ_Installations = pd.read_excel("C:\\Users\\craghuram\\Desktop\\Python\\I-O files\\NJ_Solar_Installations.xlsx")
    Previous_installed = NJ_Installations.loc[0,'Total kW']
    NJ_Installations.drop(NJ_Installations.index[0],inplace=True)
    NJ_Installations["Reporting_Year"] = pd.to_datetime(NJ_Installations['Month']).apply (lambda x : x.year if x.month <= 6 else x.year + 1)
    Supply = pd.DataFrame(NJ_Installations.groupby(['Reporting_Year'], as_index=False)['Total kW'].sum())
    for i in range(len(Supply)):
        Supply.loc[i,'Total kW'] = Supply.loc[i,'Total kW']+ Previous_installed
        Previous_installed = Supply.loc[i,'Total kW']
    Supply['Total_Installed_MW'] = Supply['Total kW']/1000
    for i in range(20):
       if Supply["Reporting_Year"].iloc[-1] < 2025:
           Supply.loc[len(Supply)] = [Supply["Reporting_Year"].iloc[-1] + 1,0,Supply["Total_Installed_MW"].iloc[-1]*0.995+ float(New_Capacity) * 12]
       else:
           Supply.loc[len(Supply)] = Supply["Reporting_Year"].iloc[-1] + 1, 0,Supply["Total_Installed_MW"].iloc[-1]*0.995

#####################################
       if Supply.apply(lambda x:Supply["Reporting_Year"].iloc[i] - 15 in x.values,axis=1).any():
           Supply.loc[i, "Total_Installed_MW"] = Supply.loc[i, "Total_Installed_MW"] - Supply.loc[i-15, "Total_Installed_MW"]

#####################################
    Forecast = Supply.merge(Gats_Data,on='Reporting_Year',how='left')
    RPS= pd.read_excel("C:\\Users\\craghuram\\Desktop\\Python\\I-O files\\RPS_Demand.xlsx")
    if j==0:
        RPS = RPS.rename(columns={"Current Law":"RPS_Demand(MWh)"})
    elif j==1:
        RPS = RPS.rename(columns={"S877- As Revised By Senate 2/22/18": "RPS_Demand(MWh)"})
    else:
        RPS = RPS.rename(columns={"S877-Solar Industry Proposal": "RPS_Demand(MWh)"})
    Forecast = RPS.merge(Forecast,on='Reporting_Year',how='left')
    Forecast.sort_values(["Reporting_Year"], ascending=True, inplace=True)
    Forecast['SRECs_Minted'] = Forecast['Total_Installed_MW'] * 1500 * 0.78
    Forecast['SRECs_Retired'] = np.where(Forecast['Reporting_Year'] > 2017, Forecast['RPS_Demand(MWh)'],Forecast['SRECs_Retired'])
    Forecast.sort_values(["Reporting_Year"], ascending=True, inplace=True)
    Forecast['Banking'] = 0
    previous_Banking = 0
    Forecast.reset_index(drop=True, inplace=True)
    for i in range(len(Forecast)):
        if Forecast.loc[i, 'Reporting_Year'] > 2011:
            Forecast.loc[i, 'Banking'] = np.where(previous_Banking > 0, Forecast.loc[i, 'SRECs_Minted'] - Forecast.loc[i, 'SRECs_Retired'] + previous_Banking,Forecast.loc[i, 'SRECs_Minted'] - Forecast.loc[i, 'SRECs_Retired'])
            previous_Banking = Forecast.loc[i, 'Banking']
    Forecast['Total_Supply'] = np.where(Forecast['Banking'] > 0, Forecast['Banking'] + Forecast['SRECs_Minted'],Forecast['SRECs_Minted'])
    #Forecast['Total_Supply'] = np.where(Forecast['Reporting_Year'] < 2015, Forecast['SRECs_Retired'],Forecast['Total_Supply'])
    Plotting_Data = Forecast[['Reporting_Year', 'RPS_Demand(MWh)', 'SRECs_Minted', 'Banking', 'Total_Supply', 'SACP_1','SACP_2','PJM_Price']]
    Plotting_Data =Plotting_Data.rename(columns={'PJM_Price':'Price_SACP_1'})
    Plotting_Data['Price_SACP_1'] = np.where(Plotting_Data['Reporting_Year'] > 2017,240,Plotting_Data['Price_SACP_1'])

    Plotting_Data['Price_SACP_2'] = Plotting_Data['Price_SACP_1']
    Plotting_Data["% Over Supply"] = ((Plotting_Data['Total_Supply'] - Plotting_Data['RPS_Demand(MWh)'])*100) / Plotting_Data['Total_Supply']
#Price forecasting
    for i in range(9, len(Plotting_Data)):
        for k in range(1,3):
            Over_Supply = Plotting_Data['% Over Supply'].head(i)
            Plotting_Data['Price_SACP_' + str(k)].loc[i] = np.where(Plotting_Data['% Over Supply'].loc[i]/100 <= 0,Plotting_Data['SACP_' + str(k)].loc[i] * 0.95,Plotting_Data['Price_SACP_' + str(k)].loc[i-1]*(1-Plotting_Data['% Over Supply'].loc[i]/100))
    Plotting_Data = Plotting_Data[Plotting_Data['Reporting_Year'] > 2017]
    Plotting_Data["Total_Supply"] = Plotting_Data["Total_Supply"].astype(int)
    Plotting_Data["SRECs_Minted"] = Plotting_Data["SRECs_Minted"].astype(int)
    Plotting_Data["Banking"] = Plotting_Data["Banking"].astype(int)
    Plotting_Data["RPS_Demand(MWh)"] = Plotting_Data["RPS_Demand(MWh)"].astype(int)
    Plotting_Data["% Over Supply"] = Plotting_Data["% Over Supply"].astype(int)
    Plotting_Data["% Over Supply"] = Plotting_Data["% Over Supply"].astype(str) + "%"
    Plotting_Data['Price_SACP_1'] = round(Plotting_Data['Price_SACP_1'],2)
    Plotting_Data['Price_SACP_2'] = round(Plotting_Data['Price_SACP_2'],2)
    Plotting_Data['Reporting_Year'] = Plotting_Data['Reporting_Year'].astype(int)
    Plotting_Data = Plotting_Data[Plotting_Data['Reporting_Year'] < 2025]
    ###############################################Plotting
    if j == 0:
        Current_Law = Plotting_Data
        ax1 = plt.subplot(311)
        plt.title('Current Law and Supply at ' + str(int(New_Capacity) *12) + 'MW forecasted installation every year',fontweight='bold')
        print("With Current RPS Demand:" % Current_Law)
    elif j == 1:
        S877_Senate = Plotting_Data
        ax1 = plt.subplot(312)
        plt.title(
            'S877- As Revised By Senate 2/22/18 and Supply at ' + str(int(New_Capacity) *12) + 'MW forecasted installation every year',fontweight='bold')
        print("With S877- As Revised By Senate 2/22/18:" % S877_Senate)
    else:
        S877_Solar_Industry = Plotting_Data
        ax1 = plt.subplot(313)
        plt.title('S877-Solar Industry Proposal and Supply at ' + str(int(New_Capacity) *12) + 'MW forecasted installation every year',fontweight='bold')
        print("With S877-Solar Industry Proposal:" % S877_Solar_Industry)
    N = len(Plotting_Data['RPS_Demand(MWh)'])
    plt.xticks(Plotting_Data['Reporting_Year'])
    plt.xlabel('Reporting Year', position=(1, 25))
    plt.ylabel('Demand/Supply(including banking)')
    ax1.bar(Plotting_Data['Reporting_Year'], Plotting_Data["Total_Supply"], width=0.2, color='b', label='Total Supply')
    ax1.bar(Plotting_Data['Reporting_Year'] - 0.2, Plotting_Data["RPS_Demand(MWh)"], width=0.2, color='g',
            label='Demand')
    ax1.legend(loc=2)
    ax1.set_ylim([2000000,Plotting_Data['Total_Supply'].max()+500000])
    ax = plt.twinx()
    ax.plot(Plotting_Data['Reporting_Year'], Plotting_Data['Price_SACP_1'],'--mD')
    ax.plot(Plotting_Data['Reporting_Year'], Plotting_Data['Price_SACP_2'], '--cD')
    ax.set_xlim([2017, 2025])
    ax.set_ylim([0, 350])
    ax.tick_params(axis='y', which='both', colors='m')
    ax.set_ylabel('Price ($)', color='m')
    ax.legend(loc=0)
    Plotting_Data['Price_SACP_1'] = "$" + round(Plotting_Data['Price_SACP_1'],2).astype(str)
    Plotting_Data['Price_SACP_2'] = "$" + round(Plotting_Data['Price_SACP_2'],2).astype(str)
    print(Plotting_Data.to_string(index=False))
plt.show()
