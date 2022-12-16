import scipy as sp
import numpy as np
from functools import partial

# 'hd_var' takes a list of PnL and returns a Harrells-Davis distributed Value-at-Rsik Value.
# if the PnL are dollar value, the returned VaR will be in dollar value
# if the PnL are percentage values, the returned VaR will be in percentage


def hd_var(pnl, ci=0.95):
    pnl = sorted(pnl, reverse=False)
    num_data = len(pnl)
    w = (num_data + 1) * ci
    z = (num_data + 1) * (1 - ci)
    beta_cdf = np.vectorize(partial(sp.stats.beta.cdf, a = z, b = w))
    temp = [1/num_data * i for i in range(num_data + 1)]
    x_lst = list(beta_cdf(temp))
    # x_lst = np.array(
    #     [
    #         sp.stats.beta.cdf(1/num_data * i, z, w) 
    #         for i in range(num_data + 1)
    #     ]
    # )
    hd_weights = [
        (x_lst[i + 1] - x_lst[i]) for i in range(num_data)
        ]
    var = sum(np.array(hd_weights) * pnl)
    return var

# 'hd_var_annual' converts VaR for a duration T to annual
# factor = sqrt(252 days/T), by default T = 10 days
def var_annualize(var_pct, factor=25.2**0.5):
    if abs(var_pct) > 1:
        ann_var = abs(var_pct) * factor
    else: ann_var = 1 - (1 - abs(var_pct))**factor
    return ann_var

# returns a annualized VaR from list of dollar value PnL
def hd_var_ann(pnl, pv, ci=0.95, factor=25.2**0.5):
    if pv == 0:
        return float('nan')
    else:
        var_pct = hd_var(pnl, ci) / pv
        return var_annualize(var_pct, factor)

# 'sort_lists' sorts two PnL time series lists based on values of list 1
# returns a list of [sorted_lst1, sorted_lst2]
def sort_lists(lst1, lst2):                    
    zipped = zip(lst1, lst2)
    tuples = sorted(zipped, key=lambda x:x[0]) # sorting is asc order based on first list from input
    return [i[0]for i in tuples], [i[1]for i in tuples]


# 'hd_var_nosort' is used in calculating VaR contribution of a position
# the pnl list in arg needs to be sorted beforehand
def hd_var_nosort(pnl, ci=0.95):
    num_data = len(pnl)
    w = (num_data + 1) * ci
    z = (num_data + 1) * (1 - ci)
    beta_cdf = np.vectorize(partial(sp.stats.beta.cdf, a = z, b = w))
    temp = [1/num_data * i for i in range(num_data + 1)]
    x_lst = list(beta_cdf(temp))
    # x_lst = np.array(
    #     [
    #         sp.stats.beta.cdf(1/num_data * i, z, w) 
    #         for i in range(num_data + 1)
    #     ]
    # )
    hd_weights = [
        (x_lst[i + 1] - x_lst[i]) for i in range(num_data)
        ]
    var = sum(np.array(hd_weights) * pnl)
    return var



# 'hd_contrib' calculates the VaR contribution relative to the whole portfolio
def hd_contrib(pnl_tot, pnl_pos, ci=0.95):
    if len(pnl_tot) != len(pnl_pos):
        raise Exception("Total and Position PnL have unequl data points.")
    sorted_lsts = sort_lists(pnl_tot, pnl_pos)
    contrib = hd_var_nosort(sorted_lsts[1])/hd_var_nosort(sorted_lsts[0])
    return contrib
    

# 'hd_incremental' calculates the marginal change in portfolio VaR due to adding/selling an asset
# adding new asset: w_pos = 1; selling all of one position: w_pos = -1
def hd_incremental(
    pnl_pfl, 
    pv_pfl, 
    pnl_pos, 
    pv_pos, 
    w_pos=1, 
    ci=0.95, 
    factor=25.2**0.5
):
    if len(pnl_pfl) != len(pnl_pos):
        raise Exception("Portfolio PnL and Position PnL have unequl data points.")
    if (pv_pfl == 0) | (pv_pos ==0):
        raise Exception("Portfolio PV and Position PV cannot be zero.")
    num_data = len(pnl_pfl)
    pv_sum = pv_pfl + w_pos * pv_pos
    pnl_sum = [0] * num_data
    for i in range(num_data):
        pnl_sum[i] = pnl_pfl[i] + w_pos * pnl_pos[i]
    var_before = hd_var(pnl_pfl, ci) / pv_pfl
    var_after = hd_var(pnl_sum, ci) / pv_sum
    increment = hd_var_ann(var_after, factor) - hd_var_ann(var_before, factor)
    return increment