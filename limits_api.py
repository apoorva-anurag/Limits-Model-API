from fastapi import FastAPI, HTTPException
from math_module import *
import uvicorn
from pydantic import BaseModel

app = FastAPI()

answer_dict = dict()

class LimitsInput(BaseModel):
    inputs_dict: dict

@app.post("/")
async def root(inp: LimitsInput):
    try:
        annualized_revenue_value = annualized_revenue(inp.inputs_dict["revenue"],inp.inputs_dict["revenue_period"])
        answer_dict["annualized_revenue"] = annualized_revenue_value

        annualized_ebitda_value = annualized_ebitda(inp.inputs_dict["ebitda"], inp.inputs_dict["ebitda_period"])
        answer_dict["annualized_ebitda"] = annualized_ebitda_value

        annualized_pat_value = annualized_pat(inp.inputs_dict["pat"],inp.inputs_dict["pat_period"])
        answer_dict["annualized_pat"] = annualized_pat_value

        answer_dict["networth"] = networth(inp.inputs_dict["networth"])

        if inp.inputs_dict['fi_ef'] == 'EF':
            managed_debt_value = managed_debt(inp.inputs_dict['fi_ef'], inp.inputs_dict["on_bs_borrowings"], contingent_liability =  inp.inputs_dict['contingent_liability'])
            answer_dict["managed_debt_wo_contingent_liability"] = inp.inputs_dict["on_bs_borrowings"]

            managed_leverage_value = managed_leverage(on_bs_borrowings=inp.inputs_dict["on_bs_borrowings"], 
                                                      contingent_liability=inp.inputs_dict["contingent_liability"], 
                                                      networth=inp.inputs_dict["networth"], fi_ef=inp.inputs_dict["fi_ef"])
            
            on_bs_leverage_value = on_bs_leverage(inp.inputs_dict["on_bs_borrowings"], inp.inputs_dict["networth"])
            answer_dict["on_bs_leverage"] = on_bs_leverage_value

            debt_ebitda_value = debt_ebitda(managed_debt_value, inp.inputs_dict["ebitda"], inp.inputs_dict["ebitda_period"])
            answer_dict["debt_ebitda"] = debt_ebitda_value

            debt_ebitda_score_value = debt_ebitda_score(answer_dict["debt_ebitda"], inp.inputs_dict["fi_ef"])
            answer_dict["debt_ebitda_score"] = debt_ebitda_score_value
        
        if inp.inputs_dict['fi_ef'] == 'FS':
            managed_debt_value = managed_debt(inp.inputs_dict['fi_ef'], off_bs_aum=inp.inputs_dict['off_bs_aum'],
                                               on_bs_borrowings=inp.inputs_dict["on_bs_borrowings"])
            managed_leverage_value = managed_leverage(off_bs_aum=inp.inputs_dict["off_bs_aum"], on_bs_borrowings=inp.inputs_dict["on_bs_borrowings"], networth=inp.inputs_dict["networth"], fi_ef=inp.inputs_dict["fi_ef"])
            
            managed_aum_value = managed_aum(inp.inputs_dict["off_bs_aum"], inp.inputs_dict["on_bs_aum"])
            answer_dict["managed_aum"] = managed_aum_value

            debt_ebitda_value = debt_ebitda(managed_debt_value, inp.inputs_dict["ebitda"], inp.inputs_dict["ebitda_period"])
            answer_dict["debt_ebitda"] = debt_ebitda_value

            debt_ebitda_score_value = debt_ebitda_score(answer_dict["debt_ebitda"], inp.inputs_dict["fi_ef"])
            answer_dict["debt_ebitda_score"] = debt_ebitda_score_value

        answer_dict["managed_debt"] = managed_debt_value
        answer_dict["managed_leverage"] = managed_leverage_value

        try:
            networth_runway_value = networth_runway(answer_dict["annualized_pat"], inp.inputs_dict["fi_ef"],
                                                    inp.inputs_dict["networth"])
        except:
            networth_runway_value = networth_runway(answer_dict["annualized_pat"], inp.inputs_dict["fi_ef"],
                                                    on_bs_aum=inp.inputs_dict["on_bs_aum"], 
                                                    off_bs_aum=inp.inputs_dict["off_bs_aum"])
        
        answer_dict["networth_runway"] = networth_runway_value

        answer_dict["profit_making"] = profit_making(inp.inputs_dict["pat"], answer_dict["networth_runway"])

        asset_class_score_value = asset_class_score(inp.inputs_dict["secure_status"], inp.inputs_dict["sub_asset_class"], inp.inputs_dict["fi_ef"])
        answer_dict["asset_class_score"] = asset_class_score_value

        answer_dict["governance_score"] = governance_score(inp.inputs_dict["governance_concerns"])

        pe_investor_score_value = pe_investor_score(inp.inputs_dict["pe_investor"], answer_dict["governance_score"])
        answer_dict["pe_investor_score"] = pe_investor_score_value

        answer_dict["pat_score"] = pat_score(answer_dict["profit_making"])

        managed_leverage_score_value = managed_leverage_score(answer_dict["managed_leverage"], inp.inputs_dict["fi_ef"],
                                                              inp.inputs_dict["asset_class"], inp.inputs_dict["sub_asset_class"])
        answer_dict["managed_leverage_score"] = managed_leverage_score_value

        lgd_score_value = lgd_score(answer_dict["asset_class_score"], 
                                    answer_dict["pe_investor_score"],
                                    answer_dict["pat_score"],
                                    answer_dict["managed_leverage_score"],
                                    answer_dict["debt_ebitda_score"],
                                    inp.inputs_dict["fi_ef"])
        answer_dict["lgd_score"] = lgd_score_value

        lgd_normalized_score_value = lgd_normalized_score(inp.inputs_dict["entity_name"], answer_dict["lgd_score"])
        answer_dict["lgd_normalized_score"] = lgd_normalized_score_value

        derived_rating_value = derived_rating(inp.inputs_dict["external_rating"], 
                                              inp.inputs_dict["external_rating_agency"], 
                                              inp.inputs_dict["internal_rating"])
        answer_dict["derived_rating"] = derived_rating_value

        derived_pd_value = derived_pd(answer_dict["derived_rating"], inp.inputs_dict["avg_tenure"])
        answer_dict["derived_pd"] = derived_pd_value

        answer_dict["lgd_worked_score"] = lgd_worked_score(lgd_normalized_score_value, derived_pd_value)

        answer_dict["alm_score"] = alm_score(inp.inputs_dict["alm_cumulative_mismatch"])

        answer_dict["risk_categorisation_score"] = risk_categorisation_score(answer_dict["alm_score"],
                                                                             answer_dict["governance_score"],
                                                                             answer_dict["lgd_worked_score"],
                                                                             answer_dict["networth_runway"])
        
        exposure_limits_value = exposure_limits(answer_dict["lgd_worked_score"])
        answer_dict["exposure_limits"] = exposure_limits_value
        answer_dict["final_exposure_limits_wip"] = final_exposure_limits_wip(answer_dict["profit_making"],
                                                                             exposure_limits_value,
                                                                             answer_dict["networth"],
                                                                             answer_dict["networth_runway"],
                                                                             inp.inputs_dict["deflator"])
        
        answer_dict["final_exposure_limits"] = final_exposure_limits(answer_dict["pe_investor_score"],
                                                                     answer_dict["final_exposure_limits_wip"],
                                                                     inp.inputs_dict["sub_asset_class"])
        
        ead_limits_value = ead_limits(answer_dict["lgd_worked_score"]) 
        answer_dict["ead_limits"] = ead_limits_value
        answer_dict["final_exposure_ead_limits_wip"] = final_exposure_ead_limits_wip(answer_dict["profit_making"],
                                                                                     ead_limits_value,
                                                                                 exposure_limits_value,
                                                                                 answer_dict["networth"],
                                                                                 answer_dict["networth_runway"],
                                                                                 inp.inputs_dict["deflator"])
        
        answer_dict["final_exposure_ead_limits"] = final_exposure_ead_limits(answer_dict["final_exposure_ead_limits_wip"],
                                                                             answer_dict["final_exposure_limits_wip"],
                                                                             answer_dict["final_exposure_limits"])

        return answer_dict

    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid JSON format. 'number' key is required.")
    
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)