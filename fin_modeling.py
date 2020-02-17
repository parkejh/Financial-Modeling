import numpy as np
import yaml

def cash_flows(costs, fuel_escalation, num_years, core_life=None, reserve_fuel_cost=None ):

    cash_flow = {}
    cash_flow['fuel'] = costs['annual_fuel_cost'] * fuel_escalation
    cash_flow['om'] = np.array([costs['annual_om_cost']] * num_years)
    cash_flow['capital'] = np.zeros(num_years)
    cash_flow['capital'][0] = costs['total_capital_cost'] + costs['one_time_cost']

    cash_flow['refurb'] = np.zeros(num_years)
    if core_life is not None and core_life > 0:
        cash_flow['refurb'] = np.array( ([costs['intermittent_costs']] + ([0] * (core_life - 1))) * (num_years // core_life) )

    cash_flow['reserve_fuel'] = np.zeros(num_years)
    if reserve_fuel_cost is not None:
        cash_flow['reserve_fuel'][0] = reserve_fuel_cost

    return cash_flow


def pmt(cash_flow, interest, num_years):

    total_annual = cash_flow['om'] + cash_flow['fuel'] + cash_flow['capital'] + cash_flow['refurb']
    
    return -npv.pmt(interest, num_years, np.npv(interest, total_annual))

def load_inputs():

    with open('inputs.yml', 'r') as yaml_file:
        inputs = yaml.load(yaml_file, Loader=yaml.FullLoader)

    return inputs

def process_fuel_costs(input_data):

    for gen_type, gen_data in input_data['cost_inputs']['generation'].items():
        gen_data['use_fuel_cost'] = {}
        for variation, fuel_cost in gen_data['fuel_cost_kWh'].items():
            if fuel_cost == 0:
                fuel_cost = gen_data['fuel_cost_BTU'][variation] * gen_data['heat_rate'][variation]
            gen_data['use_fuel_cost'][variation] = fuel_cost

    return input_data

        
def use_lng(primary_type, primary_data, backup_type, backup_data, lng_cost, scenario_name, variation='median'):

    if scenario_name == 'scenario_4':
        if primary_type == 'NaturalGas':
            primary_data['use_fuel_cost'][variation] = lng_cost[variation]
        if backup_type == 'NaturalGas':
            backup_data['use_fuel_cost'][variation] = lng_cost[variation]
    elif scenario_name == 'scenario_1' and backup_type == 'NaturalGas':
        backup_data['use_fuel_cost'][variation] = lng_cost[variation]

    return primary_data, backup_data
        

def evaluate_generation_costs(generation_data, power_gen, power_period, variation):

    costs = {}

    required_capacity =  power_gen / generation_data['capacity_factor'][variation]   # I am not sure about this assumption for backup power
    total_annual_generation = power_gen * power_period
    costs['total_capital_cost'] = required_capacity * generation_data['capital'][variation]
    
    costs['annual_fuel_cost'] =  generation_data['use_fuel_cost'][variation] * total_annual_generation
    
    annual_fixed_om_cost = generation_data['fixed_om'][variation] * reqiured_capacity
    annual_variable_om_cost = generation_data['variable_om'][variation] * total_annual_generation
    costs['annual_om_cost'] = annual_fixed_om_cost + annual_variable_om_cost

    costs['one_time_cost'] = generation_data['one_time_cost'][variation]
    costs['intermittent_costs'] = generation_data['refurb_cost'][variation]
    
    return costs

def solve_case(primary_type, primary_data, backup_type, backup_data, lng_cost, scenario_name, scenario_data, utility_pmt, backup_hours_per_year, discount_rate, variation='median'):

    primary_data, backup_data = use_lng(primary_type, primary_data, backup_type, backup_data, lng_cost, scenario_name, variation)

    primary_costs = evaluate_generation_costs(primary_data, scenario_data['primary_power_gen'] * kW_per_MW, hours_per_year)
    primary_cash_flow = cash_flows(primary_costs, fuel_escalation, primary_data['plant_life'][variation], primary_data['core_life'][variation])
    primary_pmt = pmt(primary_cash_flow, interest, primary_data['plant_life'][variation])

    backup_costs  = evaluate_generation_costs(backup_data, scenario_data['backup_power_gen'] * kW_per_MW, backup_hours_per_year)
    reserve_fuel_cost = backup_data['use_fuel_cost'][variation] * scenario_data['backup_power_gen'] * kW_per_MW * hours_per_day * assumption['days_of resilience'] 
    backup_cash_flow = cash_flows(backup_costs, fuel_escalation, backup_data['plant_life'][variation], backup_data['core_life'][variation], reserve_fuel_cost=reserve_fuel_cost)
    backup_pmt = pmt(backup_cash_flow, interest, backup_data['plant_life'][variation])
    
    return primary_pmt + backup_pmt + utility_pmt

def solve_scenario(scenario_name, scenario_data, cost_inputs, assumptions):

    scenario_result = {}
    
    utility_pmt = scenario_data['utility_power_gen'] * kW_per_MW * hours_per_year * assumptions['utility_rate'] 
    backup_hours_per_year = assumptions['days_backup_per_year'] * hours_per_daya

    for primary_type, primary_data in cost_inputs['generation'].items():
        for backup_type, backup_data in cost_inputs['generation'].items():
            scenario_results[(primary_type, backup_type)]  = solve_case(primary_type, primary_data,
                                                                        backup_type, backup_data,
                                                                        cost_inputs['lng_cost'],
                                                                        scenario_name, scenario_data,
                                                                        utility_pmt, backup_hours_per_year,
                                                                        assumptions['cost_of_capital'])

    return scenario_results

def main():
    
    input_data = load_inputs()

    input_data = process_fuel_costs(input_data)
    
    all_results = {}
    
    for scenario_name, scenario_data in input_data['scenarios'].items():
        all_results[scenario_name] = solve_scenario(scenario_name, scenario_data, input_data['cost_inputs'], input_data['assumptions'])

if __name__ == "__main__":
    main()
