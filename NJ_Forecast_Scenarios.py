import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model


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
    Forecast = Supply.merge(Gats_Data,on='Reporting_Year',how='left')
    Forecast['Total_Installed_MW'] = Forecast['Total kW']/1000
    for i in range(10):
        Forecast.loc[len(Forecast)] = [Forecast["Reporting_Year"].iloc[-1] + 1, 0,0,0,0,0,Forecast["Total_Installed_MW"].iloc[-1]+ float(New_Capacity) * 12]
    RPS= pd.read_excel("C:\\Users\\craghuram\\Desktop\\Python\\I-O files\\RPS_Demand.xlsx")
    if j==0:
        RPS = RPS.rename(columns={"SEIA_NJ_RPS_Demand(MWh)":"RPS_Demand(MWh)"})
    elif j==1:
        RPS = RPS.rename(columns={"Current_NJ_RPS_Demand(MWh)": "RPS_Demand(MWh)"})
    else:
        RPS = RPS.rename(columns={"Best_fit_NJ_RPS_Demand(MWh)": "RPS_Demand(MWh)"})
    Forecast = RPS.merge(Forecast,on='Reporting_Year',how='left')
    Forecast.sort_values(["Reporting_Year"],ascending=True,inplace=True)
    Forecast['SRECs_Minted'] = np.where(Forecast['Reporting_Year']>2014,Forecast['Total_Installed_MW']*1500*0.78*0.995,Forecast['SRECs_Minted'])
    Forecast['SRECs_Retired'] = np.where(Forecast['Reporting_Year']>2014,Forecast['RPS_Demand(MWh)'],Forecast['SRECs_Retired'])
    Forecast.sort_values(["Reporting_Year"],ascending=True,inplace=True)
    Forecast['Banking'] = 0
    previous_Banking = 0
    Forecast.reset_index(drop=True,inplace=True)
    for i in range(len(Forecast)):
        if Forecast.loc[i,'Reporting_Year'] > 2011:
            Forecast.loc[i,'Banking'] = Forecast.loc[i,'SRECs_Minted']-Forecast.loc[i,'SRECs_Retired']+previous_Banking
            previous_Banking = Forecast.loc[i,'Banking']
    Forecast['Total_Supply'] = np.where(Forecast['Banking']>0,Forecast['Banking']+Forecast['SRECs_Minted'],Forecast['SRECs_Minted'])
################################################Linear Regression on history 2010-2014########################################################################
    Pricing_Data = Forecast[Forecast['Reporting_Year'].between(2010, 2014, inclusive=True)]
    Demand = Pricing_Data['RPS_Demand(MWh)']
    Supply = Pricing_Data['Total_Supply']
    Price = Pricing_Data['PJM_Price']
    Demand_Supply = np.column_stack([Demand,Supply])
    clf = linear_model.LinearRegression()
    clf.fit(Demand_Supply,Price)
##############################################################################################################################################################
    Plotting_Data = Forecast[Forecast['Reporting_Year'].between(2013, 2022, inclusive=True)]
    Plotting_Data = Forecast[['Reporting_Year','RPS_Demand(MWh)','Total_Supply']]
    Plotting_Data = Plotting_Data[(Plotting_Data.Reporting_Year.between(2013, 2022, inclusive=True))]
    Plotting_Data["% Over Supply"] = ((Plotting_Data['Total_Supply'] - Plotting_Data['RPS_Demand(MWh)'])*100)/Plotting_Data['Total_Supply']
    Demand = Plotting_Data['RPS_Demand(MWh)']
    Supply = Plotting_Data['Total_Supply']
    Demand_Supply = np.column_stack([Demand,Supply])
    Plotting_Data["Price"] = clf.predict(Demand_Supply)
    Plotting_Data["Total_Supply"] = Plotting_Data["Total_Supply"].astype(int)
    Plotting_Data["RPS_Demand(MWh)"] = Plotting_Data["RPS_Demand(MWh)"].astype(int)
    Plotting_Data["% Over Supply"] = Plotting_Data["% Over Supply"].astype(int)
    Plotting_Data["% Over Supply"] = Plotting_Data["% Over Supply"].astype(str) + "%"
    Plotting_Data["Price"] = Plotting_Data["Price"].astype(int)
    if j == 0:
        SEIA_RPS = Plotting_Data
        ax1 = plt.subplot(311)
        plt.title('NJ SREC Annual Demand(SEIA) and Supply with ' + New_Capacity + 'MW forecasted installation per month')
        print("With SEIA's RPS Demand:" % SEIA_RPS)
    elif j == 1:
        Current_RPS = Plotting_Data
        ax1 = plt.subplot(312)
        plt.title('NJ SREC Annual Demand(Current) and Supply with ' + New_Capacity + 'MW forecasted installation per month')
        print("With Current RPS Demand:" % Current_RPS)
    else:
        Best_Fit_RPS = Plotting_Data
        ax1 = plt.subplot(313)
        plt.title('NJ SREC Annual Demand(Best Fit) and Supply with ' + New_Capacity + 'MW forecasted installation per month')
        print("With Best fit RPS Demand:" % Best_Fit_RPS)
    N = len(Plotting_Data['RPS_Demand(MWh)'])
    plt.xticks(Plotting_Data['Reporting_Year'])
    plt.xlabel('Reporting Year')
    plt.ylabel('Demand/Supply(including banking)')
    plt.grid(True)
    ax1.bar(Plotting_Data['Reporting_Year'], Plotting_Data["Total_Supply"], width=0.2, color='b', label='Total Supply')
    ax1.bar(Plotting_Data['Reporting_Year'] - 0.2, Plotting_Data["RPS_Demand(MWh)"], width=0.2, color='g', label='Demand')
    ax1.legend(loc=2)
    ax = plt.twinx()
    ax.plot(Plotting_Data['Reporting_Year'], Plotting_Data['Price'], '--rD')
    ax.set_xlim([2012, 2023])
    ax.set_ylim([0, 250])
    ax.tick_params(axis='y', which='both', colors='r')
    ax.set_ylabel('Price ($)', color='r')
    ax.legend(loc=0)
    Plotting_Data["Price"] = "$" + Plotting_Data["Price"].astype(str)
    print (Plotting_Data.to_string(index=False))
plt.show()





