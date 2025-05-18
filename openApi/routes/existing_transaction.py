from loggers.loggers import get_logger
from Config.database.DB_Config import money_transactions_collection, settlement_collection, ro_negotiation_collection, case_settlement_collection, case_details_collection, money_transactions_rejected_collection
from openApi.routes.money_transaction_type import variables_by_money_transaction_type
from openApi.routes.add_drc_bonus import add_to_drc_bonus
from openApi.routes.manage_cheque_payment_for_completing_settlement import Cheque_payment_for_completing_settlement
from openApi.routes.add_commission import add_to_commission 
from openApi.routes.update_db_status import update_db_status
from pymongo import DESCENDING

logger = get_logger("Money_Manager")

def existing_case_transaction(request, db, existing_case, existing_settlement_plan, commission_eligible, created_dtm, transaction_data, money_transaction_id, get_settlement, start_time, commission_type, drc_id, ro_id):
    
    logger.info(f"C-1P48 - Obtain Money Transaction - Case exists in the money transaction collection")
    cumulative_settled_balance = variables_by_money_transaction_type(existing_case, request)[2] 
    commission_seq = 0
    installment_seq = 0;       
    # Find the installment_seq where cumulative_settled_balance matches accumulated_amount
    for plan in existing_settlement_plan:
        if cumulative_settled_balance <= plan["accumulated_amount"] :
            installment_seq = plan["installment_seq"]
            if cumulative_settled_balance == plan["accumulated_amount"] and installment_seq == 1 and commission_eligible:
                commission_type = "Commissioned" 
            elif installment_seq > 1 and commission_eligible:
                commission_type = "Commissioned"
            else:
                commission_type = "Unresolved Commission" if commission_eligible else "No Commission"    
            break
    cumulative_settled_balance = cumulative_settled_balance if request.money_transaction_type not in ["Bill", "Return Cheque"] else 0                 
    #New case
    commissioned_amount = 0 
    
    if existing_case["money_transaction_type"] not in ["Bill","Return Cheque"] and commission_eligible:
        logger.info(f"C-1P48 - Obtain Money Transaction - Commissioned amount calculation when previous transaction is not a bill or return cheque")
        commissioned_amount = cumulative_settled_balance - existing_case["cumulative_settled_balance"]
        commission_seq = existing_case["bonus_1"] + 1 if existing_case["bonus_1"] is not None else 1
        
    elif existing_case["money_transaction_type"] in ["Bill","Return Cheque"] and commission_eligible:
        logger.info(f"C-1P48 - Obtain Money Transaction - Commissioned amount calculation when previous transaction is a bill or return cheque")
        
        # Find the latest transaction that is NOT a "Bill" or "Return Cheque"
        latest_valid_transaction = db[money_transactions_collection].find_one(
            {   "case_id": request.case_id,
                "settlement_id": request.settlement_id,
                "money_transaction_type": {"$nin": ["Bill", "Return Cheque"]}  # Exclude Bill & Return Cheque
            }, sort=[("created_dtm", DESCENDING)]  # Get the most recent valid transaction
        )

        if latest_valid_transaction:
            commissioned_amount = cumulative_settled_balance - latest_valid_transaction["cumulative_settled_balance"]
            commission_seq = latest_valid_transaction["bonus_1"] + 1 if latest_valid_transaction["bonus_1"] is not None else 1
            logger.info(f"C-1P48 - Obtain Money Transaction - commission_seq: {commission_seq}")
        else:
            logger.warning(f"C-1P48 - No valid previous transaction found for commission calculation.")
            commissioned_amount = cumulative_settled_balance
            commission_seq = 1
        
    year_month_format = int(created_dtm.strftime("%Y%m"))  
    transaction_data.update({
        "money_transaction_id": money_transaction_id,
        "installment_seq": installment_seq,
        "commission_type": commission_type,
        "running_credit": variables_by_money_transaction_type(existing_case, request)[0],
        "running_debt": variables_by_money_transaction_type(existing_case, request)[1],
        "cumulative_settled_balance": cumulative_settled_balance,
        "commissioned_amount": commissioned_amount if request.money_transaction_type not in ["Bill","Return Cheque"] else 0,
        "drc_id": drc_id,
        "ro_id": ro_id
    }) 
    
    completion = False
    if cumulative_settled_balance >= get_settlement["settlement_amount"]:
        completion = True
        transaction_data["bonus_2"] = year_month_format
        
    if commission_type != "No commission":
        first_settlement = add_to_drc_bonus(request.money_transaction_type, commission_type, created_dtm, request.settlement_id, request.case_id, ro_id, request.money_transaction_amount, installment_seq, money_transaction_id, completion, request.money_transaction_amount)
        add_to_commission(request.case_id, money_transaction_id, commission_type, request.money_transaction_amount, drc_id, ro_id)
        if first_settlement:
            transaction_data["bonus_1"] = year_month_format  
    
    db[money_transactions_collection].insert_one(transaction_data)
    logger.info(f"C-1P48 - Obtain Money Transaction - Money Transaction added successfully to existing Case")
    
    if completion and request.money_transaction_type != "Cheque":
        #settlenment amount has been settled
        update_db_status(db, request)               
        logger.info(f"C-1P48 - Obtain Money Transaction - Settlement amount has been settled")  
        end_time = start_time.now()
        logger.info(f"C-1P48 - Obtain Money Transaction - total time taken: {end_time - start_time}")
        return {"message": "Obtained Money Transaction added successfully - existing case and settlement amount has been settled"}
    
    if completion and request.money_transaction_type == "Cheque":
        Cheque_payment_for_completing_settlement(created_dtm, request)
        logger.info(f"C-1P48 - Obtain Money Transaction - Settlement amount has been settled by a cheque, monitoring started until the waiting period is over")
        end_time = start_time.now()
        logger.info(f"C-1P48 - Obtain Money Transaction - total time taken: {end_time - start_time}")
        return {"message": "Obtained Money Transaction added successfully - settlement amount has been settled by a cheque, monitoring started until the waiting period is over"}
    
    end_time = start_time.now()
    logger.info(f"C-1P48 - Obtain Money Transaction - total time taken: {end_time - start_time}")
    return {"message": "Obtained Money Transaction added successfully - existing case"}