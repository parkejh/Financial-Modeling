# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 13:40:49 2020

@author: James
"""
import numpy as np
import yaml
import pandas as pd

MW2KW = 1000
HrPerYr = 8760
HrPerDay = 24
DaysOfPowerPerYear = 365





def pmt_total(Scenario, generation_type_one, generation_type_two, generation_variation, interest):
    
    if Scenario == 'Scenario4' and generation_type_one == 'NaturalGas':
        input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost'] =666 # input_data()['generation_data']['NaturalGas'][generation_variation]['LNG']
        print("HYUKNJOO")
        print(input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost'])
        print(input_data()['generation_data']['NaturalGas'][generation_variation]['LNG'])
    else:
        input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost'] = input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost']

    if Scenario == 'Scenario4' and generation_type_two == 'NaturalGas':
        input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost'] = input_data()['generation_data']['NaturalGas'][generation_variation]['LNG']
    else:
        input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost'] = input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost']

    if Scenario == 'Scenario3' and generation_type_two == 'NaturalGas':
        input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost'] = input_data()['generation_data']['NaturalGas'][generation_variation]['LNG']
    else:
        input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost'] = input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost']

    print(Scenario, generation_type_one, generation_type_two, input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost'])
    def evaluate_generation_costs_utility(Scenario):
        
        UtilityRate = input_data()['model_assumptions']['UtilityRate']
        UtilityPower = input_data()['scenario_assumptions'][Scenario]['UtilityPower']
        if Scenario == 'Scenario2':
            return (UtilityRate*UtilityPower*MW2KW*HrPerYr)+(UtilityRate*UtilityPower*MW2KW*HrPerDay*input_data()['model_assumptions']['DaysOfBackupPower'])
        else:
            return UtilityRate*UtilityPower*MW2KW*HrPerYr
    
    def evaluate_generation_costs_one(Scenario, generation_type_one, generation_variation, interest):

        costs_one = {}

        required_capacity =  input_data()['scenario_assumptions'][Scenario]['PrimaryPower'] / input_data()['generation_data'][generation_type_one][generation_variation]['CapacityFactor']
        total_annual_generation = input_data()['scenario_assumptions'][Scenario]['PrimaryPower']*DaysOfPowerPerYear*HrPerDay*MW2KW
        costs_one['total_capital_cost'] = required_capacity * input_data()['generation_data'][generation_type_one][generation_variation]['CapitalCost']*MW2KW
    
        costs_one['annual_fuel_cost'] =  input_data()['generation_data'][generation_type_one][generation_variation]['FuelCost'] *total_annual_generation
    
        annual_fixed_om_cost = input_data()['generation_data'][generation_type_one][generation_variation]['FixedOMCost'] * input_data()['scenario_assumptions'][Scenario]['PrimaryPower']*MW2KW
        annual_variable_om_cost = 0#generation_data['variable_om'][variation] * total_annual_generation
        costs_one['annual_om_cost'] = annual_fixed_om_cost + annual_variable_om_cost

        costs_one['refurb_cost'] = input_data()['generation_data'][generation_type_one][generation_variation]['RefurbishmentCost']
        costs_one['decommission_cost'] = input_data()['generation_data'][generation_type_one][generation_variation]['DecommissionCost']*required_capacity*MW2KW*HrPerYr
    
        cash_flow_one = {}
        cash_flow_one['om_primary'] = np.array([costs_one['annual_om_cost']] * (input_data()['generation_data'][generation_type_one][generation_variation]['AssetLife']+1))
        cash_flow_one['om_primary'][0] = 0
        cash_flow_one['fuel_primary'] = np.array([costs_one['annual_fuel_cost']] * (input_data()['generation_data'][generation_type_one][generation_variation]['AssetLife']+1))
        cash_flow_one['fuel_primary'][0] = 0
        cash_flow_one['capital_primary'] = np.zeros(input_data()['generation_data'][generation_type_one][generation_variation]['AssetLife']+1)
        cash_flow_one['capital_primary'][0] = costs_one['total_capital_cost']

        cash_flow_one['refurb_primary'] = 0# np.zeros(input_data()['generation_data'][generation_type_one][generation_variation]['AssetLife'])
        #cash_flow_one['refurb_primary'] = np.array( ([costs_one['refurb_cost']] + ([0] * (input_data()['generation_data'][generation_type_one][generation_variation]['CoreLife'] - 1))) * (input_data()['generation_data'][generation_type_one][generation_variation]['AssetLife'] // input_data()['generation_data'][generation_type_one][generation_variation]['CoreLife']) )

    
        cash_flow_one['decommission_primary'] = np.array([costs_one['decommission_cost']] * (input_data()['generation_data'][generation_type_one][generation_variation]['AssetLife']+1))
        cash_flow_one['decommission_primary'][0] = 0
        total_annual_one = cash_flow_one['om_primary'] + cash_flow_one['fuel_primary'] + cash_flow_one['capital_primary'] + cash_flow_one['refurb_primary']+cash_flow_one['decommission_primary']
        return -np.pmt(interest, input_data()['generation_data'][generation_type_one][generation_variation]['AssetLife'], np.npv(interest, total_annual_one))





    def evaluate_generation_costs_two(Scenario, generation_type_two, generation_variation, interest):

        costs_two = {}

        total_annual_generation = input_data()['scenario_assumptions'][Scenario]['BackupPower']*HrPerDay*MW2KW*input_data()['model_assumptions']['DaysOfBackupPower']
        costs_two['total_capital_cost'] = input_data()['scenario_assumptions'][Scenario]['BackupPower'] * input_data()['generation_data'][generation_type_two][generation_variation]['CapitalCost']*MW2KW
    
        costs_two['annual_fuel_cost'] =  input_data()['generation_data'][generation_type_two][generation_variation]['FuelCost'] * total_annual_generation
    
        annual_fixed_om_cost = input_data()['generation_data'][generation_type_two][generation_variation]['FixedOMCost'] * input_data()['scenario_assumptions'][Scenario]['BackupPower']*MW2KW
        annual_variable_om_cost = 0#generation_data['variable_om'][variation] * total_annual_generation
        costs_two['annual_om_cost'] = annual_fixed_om_cost + annual_variable_om_cost

        costs_two['ReserveFuel'] = input_data()['model_assumptions']['DaysOfResilience']*input_data()['generation_data'][generation_type_two][generation_variation]['FuelCost']*input_data()['scenario_assumptions'][Scenario]['BackupPower']*MW2KW*HrPerYr/DaysOfPowerPerYear
        cash_flow_two = {}
        
        cash_flow_two['reserve_fuel'] = np.zeros(input_data()['generation_data'][generation_type_two][generation_variation]['AssetLife']+1)
        cash_flow_two['reserve_fuel'][0] = costs_two['ReserveFuel']
    
        cash_flow_two['capital_backup'] = np.zeros(input_data()['generation_data'][generation_type_two][generation_variation]['AssetLife']+1)
        cash_flow_two['capital_backup'][0] = costs_two['total_capital_cost']
        cash_flow_two['om_backup'] = np.array([costs_two['annual_om_cost']] * (input_data()['generation_data'][generation_type_two][generation_variation]['AssetLife']+1))
        cash_flow_two['fuel_backup'] = np.array([costs_two['annual_fuel_cost']] * (input_data()['generation_data'][generation_type_two][generation_variation]['AssetLife']+1))
        cash_flow_two['om_backup'][0] = 0
        cash_flow_two['fuel_backup'][0] = 0
        total_annual_two = cash_flow_two['reserve_fuel']+cash_flow_two['capital_backup']+cash_flow_two['om_backup']+cash_flow_two['fuel_backup']
    
        return -np.pmt(interest, input_data()['generation_data'][generation_type_two][generation_variation]['AssetLife'], np.npv(interest, total_annual_two))
 
    return evaluate_generation_costs_utility(Scenario)+evaluate_generation_costs_one(Scenario, generation_type_one, generation_variation, interest)+evaluate_generation_costs_two(Scenario, generation_type_two, generation_variation, interest)
    

def load_inputs():

    with open('inputs.yml', 'r') as yaml_file:
        inputs = yaml.load(yaml_file, Loader=yaml.FullLoader)

    return inputs


def input_data():
    
    input_data = load_inputs()
    return input_data



if __name__ == "__main__":
    Results = []
    input_data()
    interest = .02
    generation_variation = 'Median'
    for Scenario in ['Scenario1']:
        for generation_type_one, generation_type_two in zip(['None','None','None'], ['Nuclear','Diesel','NaturalGas']):
            Results.append([Scenario, generation_type_one, generation_type_two, interest, pmt_total(Scenario, generation_type_one, generation_type_two, generation_variation, interest)])
    for Scenario in ['Scenario2']:
        for generation_type_one, generation_type_two in zip(['Nuclear','Diesel','NaturalGas'],['None','None','None']):#'Diesel','NaturalGas'], ['None','None','None']):
            Results.append([Scenario, generation_type_one, generation_type_two, interest, pmt_total(Scenario, generation_type_one, generation_type_two, generation_variation, interest)])
    for Scenario in ['Scenario3']:
        for generation_type_one, generation_type_two in zip(['Nuclear','Diesel','NaturalGas'], ['Diesel','NaturalGas','Diesel']):
            Results.append([Scenario, generation_type_one, generation_type_two, interest, pmt_total(Scenario, generation_type_one, generation_type_two, generation_variation, interest)])
    for Scenario in ['Scenario4']:
        for generation_type_one, generation_type_two in zip(['Nuclear','Diesel','NaturalGas'], ['Diesel','NaturalGas','Diesel']):
            Results.append([Scenario, generation_type_one, generation_type_two, interest, pmt_total(Scenario, generation_type_one, generation_type_two, generation_variation, interest)])
            #print(Scenario, generation_type_one, generation_type_two, input_data()['generation_data']['NaturalGas'][generation_variation]['FuelCost'])
    dfResults = pd.DataFrame(Results, columns = ['Scenario', 'Power Type','Backup', 'interest','Annual Payment'])
    dfResults['Annual Payment'] = dfResults.apply(lambda x: "{0:,.2f}".format(x['Annual Payment']), axis=1)
    print(dfResults)










































