from loggers.loggers import get_logger
from Config.database.DB_Config import money_transactions_collection, settlement_collection, ro_negotiation_collection, case_settlement_collection, case_details_collection, money_transactions_rejected_collection
from openApi.routes.money_transaction_type import variables_by_money_transaction_type
from openApi.routes.add_drc_bonus import add_to_drc_bonus
from openApi.routes.update_db_status import update_db_status
from openApi.routes.manage_cheque_payment_for_completing_settlement import Cheque_payment_for_completing_settlement
from openApi.routes.add_commission import add_to_commission
from datetime import datetime, timezone, timedelta

logger = get_logger("Money_Manager")

def new_case_transaction(request, db, unique_key, start_time, created_dtm, commission_eligible, get_settlement, existing_settlement_plan, transaction_data_dict, money_transaction_id, commission_type, drc_id, ro_id):
    
    logger.info(f"{unique_key} - Obtain Money Transaction - Case does not exist in the money transaction collection")
    negotiation = db[ro_negotiation_collection].find_one({"drc_id": drc_id})
    commission_effective_amount = 0
    installment_seq = 0   
    year_month_format = int(created_dtm.strftime("%Y%m"))  
    #if a negotiation has happened
    if negotiation:                   
        #Check if the money_transaction_date is earlier than the created_dtm of the negotiation
        negotiation_created_dtm = negotiation["created_dtm"]
        #region Convert string to datetime
        if isinstance(negotiation_created_dtm, str):
            try:
                negotiation_created_dtm = datetime.fromisoformat(negotiation_created_dtm)
            except ValueError:
                negotiation_created_dtm = datetime.strptime(negotiation_created_dtm, "%Y-%m-%dT%H:%M:%S.%f%z")  # Adjust format if needed
        
        if negotiation_created_dtm.tzinfo is None:
            negotiation_created_dtm = negotiation_created_dtm.replace(tzinfo=timezone.utc)

        if request.money_transaction_date.tzinfo is None:
            request.money_transaction_date = request.money_transaction_date.replace(tzinfo=timezone.utc)
        #endregion
        if request.money_transaction_date < negotiation_created_dtm and commission_eligible:
            commission_type = "Pending Commission"
            logger.info(f"{unique_key} - Obtain Money Transaction - Money Transaction has been recieved before the created_dtm of the negotiation")
            
        #payment is after the negotiation     
        elif request.money_transaction_date > negotiation_created_dtm and commission_eligible:
            # #if the payment is after the negotiation, then check the transaction amount to determine the commission type 
            if get_settlement["settlement_plan_received"][0] > request.money_transaction_amount:
                commission_type = "Unresolved Commission"    
                commission_effective_amount = request.money_transaction_amount        
            else:    
                commission_type = "Commissioned"
                logger.info(f"{unique_key} - Obtain Money Transaction - Money Transaction has been recieved after the created_dtm of the negotiation") 
                
    #If negotiation has not happened yet                
    else:
        logger.error(f"{unique_key} - Obtain Money Transaction - Negotiation has not happened yet")    
        return {"message": "Negotiation has not happened yet"}
    #determine the installment_seq
    for plan in existing_settlement_plan:
        if request.money_transaction_amount <= plan["accumulated_amount"] :
            installment_seq = plan["installment_seq"]
            break
        
    transaction_data_dict.update({
        "money_transaction_id": money_transaction_id,
        "installment_seq": installment_seq,
        "commission_type": commission_type,
        "running_credit": variables_by_money_transaction_type(None, request)[0],
        "running_debt": variables_by_money_transaction_type(None, request)[1],
        "cumulative_settled_balance": request.money_transaction_amount,
        "commissioning_amount": commission_effective_amount,
        "drc_id": drc_id,
        "ro_id": ro_id
    })
    db[money_transactions_collection].insert_one(transaction_data_dict)
    
    completion = True if request.money_transaction_amount >= get_settlement["settlement_plan_received"][0] else False
    #Add to DRC Bonus
    if commission_type != "No commission":
        first_settlement = add_to_drc_bonus(unique_key, request.money_transaction_type,commission_type, created_dtm, request.settlement_id, request.case_id, ro_id, commission_effective_amount, 1, money_transaction_id, completion, request.money_transaction_amount)
        add_to_commission(unique_key, request.case_id, money_transaction_id, commission_type, commission_effective_amount, drc_id, ro_id)    
        if first_settlement:
            transaction_data_dict["bonus_1"] = year_month_format 
            
    end_time = start_time.now()
    logger.info(f"{unique_key} - Obtain Money Transaction - total time taken: {end_time - start_time}")
    logger.info(f"{unique_key} - Obtain Money Transaction - Money Transaction added successfully to New Case") 
    return {"message": "Obtained Money Transaction added successfully - New case"}   