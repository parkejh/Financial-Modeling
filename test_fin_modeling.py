import fin_modeling
import numpy as np
import pytest

def test_cash_flows_nonnuke():

    costs = {
        'annual_fuel_cost': 9,
        'annual_om_cost' : 11,
        'total_capital_cost' : 100,
        'one_time_cost' : 30,
        'intermittent_costs' : 20
        }

    num_years = 30
    fuel_escalation = np.array([1] * num_years)

    obs = fin_modeling.cash_flows(costs, fuel_escalation, num_years)
    for key, val in obs.items():
        assert(len(val) == num_years)

    assert(np.sum(obs['fuel']) == num_years * costs['annual_fuel_cost'])
    assert(np.sum(obs['om']) == num_years * costs['annual_om_cost'])
    assert(np.sum(obs['capital']) == costs['total_capital_cost'] + costs['one_time_cost'])
    assert(np.sum(obs['refurb']) == 0)
    assert(np.sum(obs['reserve_fuel']) == 0)



def test_cash_flows_nuke():

    costs = {
        'annual_fuel_cost': 9,
        'annual_om_cost' : 11,
        'total_capital_cost' : 100,
        'one_time_cost' : 30,
        'intermittent_costs' : 20
        }

    num_years = 30
    fuel_escalation = np.array([1] * num_years)
    core_life = 10

    obs = fin_modeling.cash_flows(costs, fuel_escalation, num_years, core_life)
    for key, val in obs.items():
        assert(len(val) == num_years)

    assert(np.sum(obs['fuel']) == num_years * costs['annual_fuel_cost'])
    assert(np.sum(obs['om']) == num_years * costs['annual_om_cost'])
    assert(np.sum(obs['capital']) == costs['total_capital_cost'] + costs['one_time_cost'])
    assert(np.sum(obs['refurb']) == costs['intermittent_costs'] * (num_years // core_life))
    assert(np.sum(obs['reserve_fuel']) == 0)

def test_cash_flows_backup():

    costs = {
        'annual_fuel_cost': 9,
        'annual_om_cost' : 11,
        'total_capital_cost' : 100,
        'one_time_cost' : 30,
        'intermittent_costs' : 20
        }

    num_years = 30
    fuel_escalation = np.array([1] * num_years)
    reserve_fuel_cost = 130
    

    obs = fin_modeling.cash_flows(costs, fuel_escalation, num_years, reserve_fuel_cost=reserve_fuel_cost)
    for key, val in obs.items():
        assert(len(val) == num_years)

    assert(np.sum(obs['fuel']) == num_years * costs['annual_fuel_cost'])
    assert(np.sum(obs['om']) == num_years * costs['annual_om_cost'])
    assert(np.sum(obs['capital']) == costs['total_capital_cost'] + costs['one_time_cost'])
    assert(np.sum(obs['refurb']) == 0)
    assert(np.sum(obs['reserve_fuel']) == reserve_fuel_cost)
    
    
