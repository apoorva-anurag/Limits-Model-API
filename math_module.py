import pandas as pd
import numpy as np
import math

def annualized_revenue(revenue, revenue_period):
    num = revenue*12
    try:
        try:
            denom = int(revenue_period[:2])
        except:
            denom = int(revenue_period[:1])
        answer = num/denom
    except:
        answer = ''
    
    return answer

# a = annualised_revenue(1240.3, 'n.a.')
# print(a)

def annualized_ebitda(ebitda, ebitda_period):
    num = ebitda*12
    try:
        try:
            denom = int(ebitda_period[:2])
        except:
            denom = int(ebitda_period[:1])
        answer = num/denom
    except:
        answer = ''
    
    return answer

def annualized_pat(pat, pat_period):
    num = pat*12
    try:
        try:
            denom = int(pat_period[:2])
        except:
            denom = int(pat_period[:1])
        answer = num/denom
    except:
        answer = ''
    
    return answer

def managed_debt( fi_ef=None, on_bs_borrowings=None, off_bs_aum=None, contingent_liability=None):
    try:
        if fi_ef == 'FS':
            answer = off_bs_aum+on_bs_borrowings
        else:
            answer = on_bs_borrowings + contingent_liability
    except:
        answer = ''
    
    return answer

# md w/o contingent liability
# on_bs_borrowings/networth

def managed_debt_wo_contingent_liability(on_bs_borrowings):
    try:
        answer = on_bs_borrowings
    except:
        answer = ''
    return answer


def on_bs_borrowings(on_bs_borrowings):
    answer = on_bs_borrowings

    return answer

def networth(netw):
    try:
        answer = netw
    except:
        answer = ''

    return answer

def managed_leverage(off_bs_aum=None, on_bs_borrowings=None,contingent_liability=None, networth=None, fi_ef=None):
    try:
        if fi_ef == 'FS':
            answer = managed_debt(fi_ef, on_bs_borrowings, off_bs_aum)/networth
        else:
            answer = (on_bs_borrowings+contingent_liability)/networth

    except:
        answer = ''

    return answer

def on_bs_leverage(on_bs_borrowings, networth): # or DEBT or MD w/o Contingent Liability
    answer = on_bs_borrowings/networth

    return answer

def managed_aum(off_bs_aum, on_bs_aum):
    # only for FS - Financial Services will have AUM
    try:
        answer = off_bs_aum+on_bs_aum
    except:
        answer = ''
    
    return answer

def debt_ebitda(managed_debt, ebitda, ebitda_period): # EF only
    md = managed_debt
    ae = annualized_ebitda(ebitda, ebitda_period)

    try:
        answer = md/ae
    except:
        answer = ''

    return answer

def networth_runway(annualized_pat, fi_ef, networth=None, on_bs_aum=None, off_bs_aum=None):
    ap = annualized_pat

    try:
        if ap >= 0:
            result = 0
        else:
            if fi_ef == "EF":
                result = networth / abs(ap)
            else:
                result = (networth - (0.15 * on_bs_aum + 0.075 * off_bs_aum)) / abs(ap)
    except:
        result = ''

    return result

def profit_making(pat,networth_runway):
    print("INSIDE PROFIT MAKING")
    try:
        if pat>=0 or networth_runway>2.5:
            answer = 'Yes'
        else:
            answer = 'No'
    except:
        answer = ''

    return answer

def asset_class_score(secure_status,sub_asset_class, fi_ef):
    # secure_status marked as Type in UI
    if secure_status == "Secured":
        if sub_asset_class in ["Commercial Vehicle Finance", "Diversified", "SFB", "Education Loans", "Two Wheeler Finance", "Secured BL", "Agri"] or fi_ef == "EF":
            result = 5
        else:
            result = 0
    else:
        result = 10

    return result

def pe_investor_score(pe_investor, governance_score):

    if pe_investor in ["Yes", "Institutional"]:
        result = 0
    else:
        if pe_investor == "Medium" and (governance_score == 0 or governance_score == 1):
            result = 0
        elif pe_investor == "No" and governance_score == 0:
            result = 0
        elif pe_investor == "Medium" and governance_score == 2:
            result = 5
        elif pe_investor == "No" and governance_score == 1:
            result = 5
        else:
            result = 10
        
    return result

def pat_score(profit_making):
    if profit_making == "No":
        result = 10
    else:
        result = 0
    
    return result

def managed_leverage_score(managed_leverage, fi_ef, asset_class, sub_asset_class):
    ml = managed_leverage
    mls_df = pd.read_pickle('./data/MLS_Table.pickle')
    answer = 0
    mask = (mls_df['FI/EF']==fi_ef) & (mls_df['Asset Class']==asset_class) & (mls_df['Sub Asset Class']==sub_asset_class) 
    value = mls_df.loc[mask, 'Value']
    try:
        if fi_ef == "EF":
            if ml > 3:
                answer = 10
            else:
                answer = 0
        elif ml>value.to_list()[0]:
            answer = 10
        else:
            answer = 0
    except:
        answer = 'NaN'
    return answer

# print(managed_leverage_score(1.2,"FS","Housing Finance","Housing Finance"))

def debt_ebitda_score(debt_ebitda, fi_ef):

    de = debt_ebitda

    try:
        if fi_ef == "EF":
            if de < 0:
                result = 10
            elif 0 <= abs(de) < 4:
                result = 0
            elif 4 <= abs(de) < 5:
                result = 5
            else:
                result = 10
        else:
            result = 0
    except:
        result = 0

    return result


# IF(BC6="EF",SUMPRODUCT(BI6:BM6,List!$AH$3:$AL$3),SUMPRODUCT(BI6:BM6,List!$AH$4:$AL$4))

def lgd_score(asset_class_score, pe_investor_score, pat_score, manage_leverage_score, debt_ebitda_score, fi_ef):
    # asset class score BI
    # debt/ebitda score BM
    # List Sheet - Asset Class (AH) and Debt/EBITDA (AL)

    list1 = [asset_class_score, pe_investor_score, pat_score, manage_leverage_score, debt_ebitda_score]
    list_ef = [0,0.4505,0.084,0.105,0.36] # Asset Class (AH) and Debt/EBITDA (AL)
    list_fs = [0.105,0.4505,0.084, 0.36,0]

    try:
        if fi_ef == 'EF':
            answer = sum([x*y for x,y in zip(list1,list_ef)])
        else:
            answer = sum([x*y for x,y in zip(list1,list_fs)])
    except:
        answer = ''

    

    return answer

def lgd_normalized_score(entity_name,lgd_score):

    en = entity_name
    lgd = lgd_score
    df = pd.read_pickle('./data/testing_LGD_score_storage.pickle')

    if en in df['Entity'].to_list():
        index_of_value = df[df['Entity'] == en].index.tolist()
        df['LGD Score'].iloc[index_of_value] = lgd
    else:
        df.loc[len(df)] = [en,lgd]

        
    lgd_score = df['LGD Score'].to_list()
    df.to_pickle('./data/testing_LGD_writeback.pickle')

    avg_lgd = np.nanmean(lgd_score)
    stdev_lgd = np.nanstd(lgd_score)

    answer = (lgd - avg_lgd)/stdev_lgd

    return answer

# LGD Worked Score Components

def derived_rating(external_rating, external_rating_agency, internal_rating):

    rating_list = ['AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'BB-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D']
    answer = ''
    
    if external_rating == 'D':
        answer = 'D'
    elif internal_rating == 'Unrated':
        try:
            get_index = rating_list.index(external_rating)
        except:
            pass
        if external_rating_agency.strip() == 'CARE':
            answer = rating_list[get_index+1]
        elif external_rating_agency.strip() == 'Brickwork':
            answer = rating_list[get_index+2]
        elif external_rating_agency.strip() == 'Acuite (SMERA)':
            answer = rating_list[get_index+3]
        elif external_rating_agency.strip() == 'Infomerics':
            answer = rating_list[get_index+4]
        elif external_rating_agency.strip() == 'CRISIL' or external_rating_agency == 'ICRA' or external_rating_agency == 'India Ratings':
            answer = external_rating
        elif external_rating.strip() == 'Unrated':
            answer = 'BB-'
    else:
        answer = internal_rating

    return answer

# print("DERIVED RATING")
# print(derived_rating('BB+', 'CARE', 'Unrated'))

def derived_pd(derived_rating, avg_tenure):

    pd_df = pd.read_pickle('./data/PD.pickle')
    index = avg_tenure - 1

    try:
        # search for value using derived rating and avg_tenor
        dr = derived_rating
        answer = pd_df[dr].iloc[int(index)]*0.5
    except:
        answer = 1
    
    if avg_tenure==0:
        answer = 1

    return answer

# print("DERIVED PD")
# dr = 'BB-'
# at = 24.0
# print(derived_pd(dr,at))


def lgd_worked_score(lgd_normalized_score, derived_pd):

    if lgd_normalized_score<0:
        answer = derived_pd
    else:
        answer = derived_pd * (1+lgd_normalized_score)

    return answer
    # col-68 is BP -> LGD Normalized Score

def alm_score(alm_cumulative_mismatch):
    answer = 0

    try:
        if alm_cumulative_mismatch.lower() == 'alm mismatch concerns':
            answer = 1
    except:
        answer = 0

    return answer

def governance_score(governance_concerns):

    answer = 0
    try:
        governance_concerns = governance_concerns.lower()
        if governance_concerns == 'some governance concerns exists':
            answer = 1
        if governance_concerns == 'significant governance concerns exists':
            answer = 2
    except:
        answer = 0

    return answer

print(governance_score('Significant Governance Concerns Exists'))

def risk_categorisation_score(alm_score, governance_score, lgd_worked_score, networth_runway):
    # =+IF(OR(AH8=1,AG8=2),1,IF(AND(AH8=0,AG8=1),2,IF(OR(AND(AW8<=1.25,AW8>0),AW8<0),2,IF(BR8<=2%,5,IF(OR(AND(BR8>2%,BR8<=5%),(AW8>4)),4,IF(AND(BR8>5%,BR8<=20%),3,4))))))
    # AH - ALM Score
    # AG - Governance Score
    # BR - LGD Worked Score
    # AW - NW Runway

    if alm_score == 1 or governance_score == 2:
        answer = 1
    # (AND(AH8=0,AG8=1),2
    elif alm_score == 0 and governance_score == 1:
        answer = 2
    # (OR(AND(AW8<=1.25,AW8>0),AW8<0)
    elif (networth_runway <= 1.25 and networth_runway > 0) or networth_runway < 0:
        answer = 2
    # BR8<=2%,5
    elif lgd_worked_score <= 0.02:
        answer = 5
    # OR(AND(BR8>2%,BR8<=5%),(AW8>4)
    elif (lgd_worked_score > 0.02 and lgd_worked_score <= 0.05) or networth_runway > 4:
        answer = 4
    # AND(BR8>5%,BR8<=20%)
    elif lgd_worked_score > 0.05 and lgd_worked_score <= 0.2:
        answer = 3
    else:
        answer = 4
    return answer


def exposure_limits(lgd_worked_score):

    df = pd.read_pickle('./data/Final_LGD_Limits.pickle')


    find_num = lgd_worked_score

    df['LGD+Gov Score'] = df['LGD+Gov Score']

    answer = df['Pro Rata Limits'].iloc[0]

    for i in range(1,len(df)):
        if find_num == df['LGD+Gov Score'].iloc[i]:
            answer = df['Pro Rata Limits'].iloc[i]
        if find_num < df['LGD+Gov Score'].iloc[i]:
            answer = df['Pro Rata Limits'].iloc[i-1]
            break
    return answer

# print("EXPOSURE LIMITS")
# print(exposure_limits(0.1189))

# def ead_limits(lgd_worked_score):
#     df = pd.read_pickle('./data/Final_LGD_Limits.pickle')

#     for i,j in zip(df['LGD+Gov Score'],df['EAD Limits']):
#         print(i)
#         if lgd_worked_score>=i:
#             answer = j
#             break
#     return answer

def ead_limits(lgd_worked_score):

    df = pd.read_pickle('./data/Final_LGD_Limits.pickle')
    find_num = lgd_worked_score

    df['LGD+Gov Score'] = df['LGD+Gov Score']

    answer = df['EAD Limits'].iloc[0]

    for i in range(1,len(df)):
        if find_num == df['LGD+Gov Score'].iloc[i]:
            answer = df['EAD Limits'].iloc[i]
        if find_num < df['LGD+Gov Score'].iloc[i]:
            answer = df['EAD Limits'].iloc[i-1]
            break
    return answer


# print("EXPOSURE LIMITS")
# exposure_limits(0.0039)

# def find_largest_equal_or_less(x, numbers):
#     valid_numbers = [num for num in numbers if num <= x]
    
#     if valid_numbers:
#         largest_number = max(valid_numbers)
#         return largest_number
#     else:
#         return None  
    
# def find_smallest_equal_or_less(x, numbers):
#     valid_numbers = [num for num in numbers if num <= x]
    
#     if valid_numbers:
#         smallest_number = max(valid_numbers, default=None)
#         return smallest_number
#     else:
#         return None
    
def find_smallest_equal_or_greater(x, numbers): # excel match type 1
    valid_numbers = [num for num in numbers if num >= x]
    
    if valid_numbers:
        smallest_number = min(valid_numbers, default=None)
        return smallest_number
    else:
        return None

def find_largest_equal_or_less(x, numbers): # excel match type -1
    valid_numbers = [num for num in numbers if num <= x]
    
    if valid_numbers:
        largest_number = max(valid_numbers, default=None)
        return largest_number
    else:
        return None

def final_exposure_limits_wip(pf_making, exposure_limits_value, networth, nw_runway, deflator):

    df = pd.read_pickle('./data/Final_LGD_Limits.pickle')
    # limit1 = nw_prorata * networth
    # limit2 = nw_cap * networth

    nw_range = find_smallest_equal_or_greater(networth, df['NW Range'])
    index_nw_prorata = df[df['NW Range'] == nw_range].index
    networth_prorata = df['NW Cap-Prorata'].iloc[index_nw_prorata].to_list()[0]
    limit1 = networth * networth_prorata

    limits = find_largest_equal_or_less(exposure_limits_value, df['Limits'])
    print("LIMITS")
    print(exposure_limits_value)
    print(limits)
    index_nw_cap = df[df['Limits'] == limits].index
    nw_cap = df['NW Cap'].iloc[index_nw_cap].to_list()[0]
    limit2 = networth * nw_cap

    if pf_making == 'Yes' or (pf_making=='No' and nw_runway>2):
        # min of 3 values
        result = min(exposure_limits_value, limit1, limit2)
    else:
        # (min of 3) * 0.75
        result = min(exposure_limits_value, limit1, limit2) * 0.75

    # answer = result_from_if * (1-Deflator)
    answer = result * (1-deflator)

    return answer

# print("FINAL EXP LIMITS WIP")
# print(final_exposure_limits_wip('Yes',40,14208,0,0))

def final_exposure_ead_limits_wip(pf_making, ead_limits_value, exposure_limits_value, networth, nw_runway, deflator):

    df = pd.read_pickle('./data/Final_LGD_Limits.pickle')
    # limit1 = nw_prorata * networth
    # limit2 = nw_cap * networth

    nw_range = find_smallest_equal_or_greater(networth, df['NW Range'])
    index_nw_ead = df[df['NW Range'] == nw_range].index
    networth_ead = df['NW Cap-EAD'].iloc[index_nw_ead].to_list()[0]
    limit1 = networth * networth_ead

    limits = find_largest_equal_or_less(exposure_limits_value, df['Limits'])
    print("LIMITS - EAD")
    print(limits)
    index_nw_cap = df[df['Limits'] == limits].index
    nw_cap = df['NW Cap'].iloc[index_nw_cap].to_list()[0]
    limit2 = networth * nw_cap

    if pf_making == 'Yes' or (pf_making=='No' and nw_runway>2):
    # min of 3 values
        result = min(ead_limits_value, limit1, limit2)
    else:
        # (min of 3) * 0.75
        result = min(ead_limits_value, limit1, limit2) * 0.75

    answer = result * (1-deflator)

    print("EAD LIMITS")
    print(exposure_limits_value)
    print(limit1)
    print(limit2)

    return answer

# print(final_exposure_ead_limits_wip("Yes",37.5,25,22.1795515,0,0))




# df = pd.read_pickle('./data/Final_LGD_Limits.pickle')
# nw_range = find_largest_equal_or_less(14208, df['NW Range'])
# index_nw_prorata = df[df['NW Range'] == nw_range].index
# networth_prorata = df['NW Cap-Prorata'].iloc[index_nw_prorata]
# print(networth_prorata.to_list()[0])

def range_limiter(val1, val2, x):
    while True:
        if x >= val1:
            return val1
        elif x < val2:
            return x
        elif x >= val1 - 5 and x < val1:
            return val1 - 5
        else:
            val1 -= 5
            if val1 == val2:
                return val2

def final_exposure_limits(pe_investor_score, fel_wip, sub_asset_class):

    if math.isnan(fel_wip):
        return np.nan

    if pe_investor_score == 0:
        answer = range_limiter(50,5,fel_wip)
    else:
        if sub_asset_class=='EF':
            val1 = 25
        else:
            val1 = 20
        
        val2 = range_limiter(50,5,fel_wip)
        answer = min(val1,val2)
    return answer

def final_exposure_ead_limits(fel_ead_wip,fel_wip,fel):

    if fel_ead_wip == fel_wip:
        return fel
    else:
        return fel*1.5
        









