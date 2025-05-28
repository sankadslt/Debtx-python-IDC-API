from loggers.loggers import get_logger
from Config.database.DB_Config import money_transactions_collection, settlement_collection, ro_negotiation_collection, case_settlement_collection, case_details_collection, money_transactions_rejected_collection
from openApi.routes.money_transaction_type import variables_by_money_transaction_type
from openApi.routes.add_drc_bonus import add_to_drc_bonus
from openApi.routes.manage_cheque_payment_for_completing_settlement import Cheque_payment_for_completing_settlement
from openApi.routes.add_commission import add_to_commission 
from openApi.routes.update_db_status import update_db_status
from pymongo import DESCENDING
from fastapi import HTTPException

logger = get_logger("Money_Manager")

def existing_case_transaction(request, db, unique_key, money_transaction_details, settlement_plan, commission_eligible, created_dtm, transaction_data_dict, money_transaction_id, get_settlement, start_time, commission_type, drc_id, ro_id):
    
    # Already atleast one money transaction exists 
    # Assume 
    #       settlement plan in ascending order
    #       money transaction and settlement plans are the last ones

    logger.debug(f"{unique_key} - Obtain Money Transaction - Case exists in the money transaction collection")
    cumulative_settled_balance = variables_by_money_transaction_type(money_transaction_details, request)[2] 
    commission_seq = 0
    installment_seq = 0;       
    # Find the installment_seq where cumulative_settled_balance matches accumulated_amount
    for plan in settlement_plan:
        if cumulative_settled_balance <= plan["accumulated_amount"] :
            installment_seq = plan["installment_seq"]
            if cumulative_settled_balance == plan["accumulated_amount"] and installment_seq == 1 and commission_eligible:
                commission_type = "Commissioned" 
            elif installment_seq > 1 and commission_eligible:
                commission_type = "Commissioned"
            else:
                commission_type = "Unresolved Commission" if commission_eligible else "No Commission"    
            break
    
    commission_effective_amount = 0 
    # cumulative_settled_balance = 0 
    if request.money_transaction_type in ["Adjustment","Dispute","Cash","Cheque"]: 
        cumulative_settled_balance = cumulative_settled_balance
        if request.money_transaction_type in ["Adjustment","Dispute"]:
            commission_eligible = False     
            commission_type = "No Commission" 
    
    if request.money_transaction_type in ["Bill"]:
        cumulative_settled_balance = 0 
        commission_eligible = False     
        commission_type = "No Commission" 
    
    if money_transaction_details["money_transaction_type"] in ["Adjustment","Dispute","Cash","Cheque"] and commission_eligible:
        
        logger.info(f"{unique_key} - Obtain Money Transaction - Commissioned amount calculation when previous transaction is not a bill or return cheque")
        if request.money_transaction_type in ["Return Cheque"]:
            commission_effective_amount = -request.money_transaction_amount       
        else:
            commission_effective_amount = cumulative_settled_balance - money_transaction_details["cumulative_settled_balance"]
        # commission_seq = money_transaction_details["bonus_1"] + 1 if money_transaction_details["bonus_1"] is not None else 1
        
    elif money_transaction_details["money_transaction_type"] in ["Bill","Return Cheque"] and commission_eligible:
        logger.info(f"{unique_key} - Obtain Money Transaction - Commissioned amount calculation when previous transaction is a bill or return cheque")
        
        # Find the latest transaction that is NOT a "Bill" or "Return Cheque"
        last_effective_transaction = db[money_transactions_collection].find_one(
            {   "case_id": request.case_id,
                "settlement_id": request.settlement_id,
                "money_transaction_type": {"$nin": ["Bill", "Return Cheque"]}  # Exclude Bill & Return Cheque
            }, sort=[("created_dtm", DESCENDING)]  # Get the most recent valid transaction
        )

        if last_effective_transaction:
            commission_effective_amount = cumulative_settled_balance - last_effective_transaction["cumulative_settled_balance"]
                
        else:
            logger.warning(f"{unique_key} - No valid previous transaction found for commission calculation.")
            commission_effective_amount = cumulative_settled_balance
        
    year_month_format = int(created_dtm.strftime("%Y%m"))  
    transaction_data_dict.update({
        "money_transaction_id": money_transaction_id,
        "installment_seq": installment_seq,
        "commission_type": commission_type,
        "running_credit": variables_by_money_transaction_type(money_transaction_details, request)[0],
        "running_debt": variables_by_money_transaction_type(money_transaction_details, request)[1],
        "cumulative_settled_balance": cumulative_settled_balance,
        "commissioning_amount": commission_effective_amount,
        "drc_id": drc_id,
        "ro_id": ro_id
    })
    
    logger.info(f"{unique_key} - Obtain Money Transaction - commission_type: {commission_type}, commission_eligible: {commission_eligible}") 
    completion = False
    if cumulative_settled_balance >= get_settlement["settlement_amount"]:
        completion = True
        transaction_data_dict["bonus_2"] = year_month_format
        
    if commission_type != "No Commission":
        first_settlement = add_to_drc_bonus(unique_key, request.money_transaction_type, commission_type, created_dtm, request.settlement_id, request.case_id, ro_id, request.money_transaction_amount, installment_seq, money_transaction_id, completion, request.money_transaction_amount)
        add_to_commission(unique_key, request.case_id, money_transaction_id, commission_type, commission_effective_amount, drc_id, ro_id)
        if first_settlement:
            transaction_data_dict["bonus_1"] = year_month_format  
    
    db[money_transactions_collection].insert_one(transaction_data_dict)
    logger.info(f"{unique_key} - Obtain Money Transaction - Money Transaction added successfully to existing Case")
    
    if completion and request.money_transaction_type != "Cheque":
        #settlenment amount has been settled
        update_db_status(db, request)               
        logger.info(f"{unique_key} - Obtain Money Transaction - Settlement amount has been settled")  
        end_time = start_time.now()
        logger.info(f"{unique_key} - Obtain Money Transaction - total time taken: {end_time - start_time}")
        return HTTPException(status_code=200, detail="Obtained Money Transaction added successfully - settlement amount has been settled")
    
    if completion and request.money_transaction_type == "Cheque":
        #settlenment amount has been settled by a cheque
        Cheque_payment_for_completing_settlement(unique_key, created_dtm, request)
        logger.info(f"{unique_key} - Obtain Money Transaction - Settlement amount has been settled by a cheque, monitoring started until the waiting period is over")
        end_time = start_time.now()
        logger.info(f"{unique_key} - Obtain Money Transaction - total time taken: {end_time - start_time}")
        return {"message": "Obtained Money Transaction added successfully - settlement amount has been settled by a cheque, monitoring started until the waiting period is over"}
    
    end_time = start_time.now()
    logger.info(f"{unique_key} - Obtain Money Transaction - total time taken: {end_time - start_time}")
    return HTTPException(status_code=200, detail="Obtained Money Transaction added successfully - existing case")