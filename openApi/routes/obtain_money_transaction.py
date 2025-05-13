"""
API :  C-1P48
Name : Obtain Money Transaction
Description : Get all money related transactions (Check RO-Negotiation, Settlement Plan)
Created By :  Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP :  money_transaction_id
      case_id
      account_num
      settlement_id
      money_transaction_type  
      money_transaction_ref
      money_transaction_amount
      money_transaction_date
      bill_payment_status
      case_phase
      drc_id
      ro_id
        
OP : None
"""

"""
    Version: Python 3.12.4
    Dependencies: Library
    Related Files: obtain_money_transaction.py, obtain_money_transaction_class.py, add_drc_bonus.py, 
                   update_db_status.py, manage_cheque_payment_for_completing_settlement.py, 
                   money_transaction_type.py, add_commission.py
    Purpose:    
    Version:
        version: 1.0
        Last Modified Date: 2025-03-23
        Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)  
        Changes:     

    Notes:
"""
from loggers.loggers import get_logger
from fastapi import APIRouter, HTTPException
from http import HTTPStatus
from datetime import datetime, timezone, timedelta
import pytz  
from utils.database.connectDB import get_db_connection
from openApi.models.obtain_money_transaction_class import Money_Transaction_Model
from Config.database.DB_Config import money_transactions_collection, settlement_collection, ro_negotiation_collection, case_settlement_collection, case_details_collection, money_transactions_rejected_collection
from openApi.routes.money_transaction_type import variables_by_money_transaction_type
from openApi.routes.add_drc_bonus import add_to_drc_bonus
from openApi.routes.update_db_status import update_db_status
from openApi.routes.manage_cheque_payment_for_completing_settlement import Cheque_payment_for_completing_settlement
from openApi.routes.add_commission import add_to_commission 
from pydantic import ValidationError
from pymongo import DESCENDING
from pymongo.errors import PyMongoError
from utils.exceptions_handler.custom_exception_handle import DatabaseError, ValidationError

router = APIRouter()
logger = get_logger("Money_Manager")
db = get_db_connection()

@router.post("/Obtain_Money_Transaction", summary="Get all the money related transactions", description = """**Mandatory Fields**<br>
- `money_transaction_id` <br>
- `case_id` <br>
- `settlement_id` <br>
- `money_transaction_type` <br>
- `money_transaction_ref` <br>
- `money_transaction_amount` <br>
- `money_transaction_date` (MM/DD/YYYY HH24:MM:SS) <br>
- `bill_payment_status` <br>
- `case_phase` <br>
- `drc_id` <br>
- `ro_id` <br><br>

**Valid money_transaction_type values:** - "Bill","Adjustment","Dispute","Cash","Cheque","Return Cheque"  <br><br>
**Valid case_phase values:** - "Negotiation", "Mediation Board", "LOD", "Litigation", "WRIT" <br><br>
""")
async def obtain_money_transaction(request:Money_Transaction_Model):
    logger.info("C-1P48 - Obtain Money Transaction - Request received")
    start_time = datetime.now()
    try:
        # Checking for the settlement phase to determine the commission eligibility
        commission_eligible = True
        commission_type = "No Commission"
        installment_seq = 0    
        # checking if the money_transaction_ref already exists in the db
        # Check account_num related transactions
        related_transactions = list(db[money_transactions_collection].find({
            "account_num": request.account_num
        }))

        # Check if any of them has the same money_transaction_ref
        existing_money_transaction = next(
            (tx for tx in related_transactions if tx["money_transaction_ref"] == request.money_transaction_ref),
            None
        )
        created_dtm = datetime.now()
        transaction_data = request.model_dump()  
        transaction_data["created_dtm"] = created_dtm
        if existing_money_transaction:
            logger.error(f"C-1P48 - Obtain Money Transaction - Money Transaction already exists")
            db[money_transactions_rejected_collection].insert_one(transaction_data)   #add to rejected collection
            raise ValidationError("Money Transaction already EXISTS with money_transaction_ref or money_transaction_id")
        
        #Check if the case exists in the case details
        existing_case_details = db[case_details_collection].find_one({"case_id":request.case_id})
        if not existing_case_details:
            logger.error(f"C-1P48 - Obtain Money Transaction - Case does not exist in the case details collection")
            db[money_transactions_rejected_collection].insert_one(transaction_data)   #add to rejected collection
            raise ValidationError("Case does not exist in the case details collection - Invalid case_id")               
        
        if request.case_phase not in ["Negotiation", "Mediation Board"]:
            commission_eligible = False
            commission_type = "No Commission"
        
        #Get the case settlement by the settlement_id
        get_settlement = db[case_settlement_collection].find_one({"settlement_id": request.settlement_id})
        if get_settlement["settlement_status"] == "Completed":    
            logger.info(f"Settlement already completed payment accepting")

        if not get_settlement:
            logger.info(f"C-1P48 - Obtain Money Transaction - Settlement plan NOT available")
        
        if get_settlement["settlement_phase"] not in ["Negotiation", "Mediation Board"]:
            logger.info(f"C-1P48 - Obtain Money Transaction - Settlement phase is not in Negotiation or Mediation Board")
            commission_eligible = False
        
        last_transaction = db[money_transactions_collection].find_one(
            {},
            sort=[("money_transaction_id", -1)]
        )
        if last_transaction and "money_transaction_id" in last_transaction:
            money_transaction_id = last_transaction["money_transaction_id"] + 1
        else:
            money_transaction_id = 1
            
        #Check if the case_id exists in the money transaction collection
        existing_case = db[money_transactions_collection].find_one(
            {"case_id": request.case_id, "settlement_id": request.settlement_id},  
            sort=[("created_dtm", DESCENDING)]  # Sort by latest created_dtm
            )
        
        if get_settlement and "settlement_plan" in get_settlement:
                existing_settlement_plan = get_settlement["settlement_plan"]
        
        if existing_case:
            #case found
            logger.info(f"C-1P48 - Obtain Money Transaction - Case exists in the money transaction collection")
            cumulative_settled_balance = variables_by_money_transaction_type(existing_case, request)[2] 
            commission_seq = 0       
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
                "commissioned_amount": commissioned_amount if request.money_transaction_type not in ["Bill","Return Cheque"] else 0
            }) 
            
            completion = False
            if cumulative_settled_balance >= get_settlement["settlement_amount"]:
                completion = True
                transaction_data["bonus_2"] = year_month_format
                
            if commission_type != "No commission":
                first_settlement = add_to_drc_bonus(request.money_transaction_type, commission_type, created_dtm, request.settlement_id, request.case_id, request.ro_id, request.money_transaction_amount, installment_seq, money_transaction_id, completion, request.money_transaction_amount)
                add_to_commission(request.case_id, money_transaction_id, commission_type, request.money_transaction_amount, request.drc_id, request.ro_id)
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
        
        else:
            #case not found
            logger.info(f"C-1P48 - Obtain Money Transaction - Case does not exist in the money transaction collection")
            negotiation = db[ro_negotiation_collection].find_one({"drc_id": request.drc_id})
            commissioned_amount = 0
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
                    logger.info(f"C-1P48 - Obtain Money Transaction - Money Transaction has been recieved before the created_dtm of the negotiation")
                    
                #payment is after the negotiation     
                elif request.money_transaction_date > negotiation_created_dtm and commission_eligible:
                    # #if the payment is after the negotiation, then check the transaction amount to determine the commission type 
                    if get_settlement["settlement_plan_received"][0] > request.money_transaction_amount:
                        commission_type = "Unresolved Commissioned"    
                        commissioned_amount = request.money_transaction_amount        
                    else:    
                        commission_type = "Commissioned"
                        logger.info(f"C-1P48 - Obtain Money Transaction - Money Transaction has been recieved after the created_dtm of the negotiation") 
                        
            #If negotiation has not happened yet                
            else:
                logger.error(f"C-1P48 - Obtain Money Transaction - Negotiation has not happened yet")    
                return {"message": "Negotiation has not happened yet"}
            #determine the installment_seq
            for plan in existing_settlement_plan:
                if request.money_transaction_amount <= plan["accumulated_amount"] :
                    installment_seq = plan["installment_seq"]
                    break
                
            transaction_data.update({
                "money_transaction_id": money_transaction_id,
                "installment_seq": installment_seq,
                "commission_type": commission_type,
                "running_credit": variables_by_money_transaction_type(None, request)[0],
                "running_debt": variables_by_money_transaction_type(None, request)[1],
                "cumulative_settled_balance": request.money_transaction_amount,
                "commissioned_amount": commissioned_amount
            })
            db[money_transactions_collection].insert_one(transaction_data)
            
            completion = True if request.money_transaction_amount >= get_settlement["settlement_plan_received"][0] else False
            #Add to DRC Bonus
            if commission_type != "No commission":
                first_settlement = add_to_drc_bonus(request.money_transaction_type,commission_type, created_dtm, request.settlement_id, request.case_id, request.ro_id, commissioned_amount, 1, money_transaction_id, completion, request.money_transaction_amount)
                add_to_commission(request.case_id, money_transaction_id, commission_type, commissioned_amount, request.drc_id, request.ro_id)    
                if first_settlement:
                    transaction_data["bonus_1"] = year_month_format 
                    
            end_time = start_time.now()
            logger.info(f"C-1P48 - Obtain Money Transaction - total time taken: {end_time - start_time}")
            logger.info(f"C-1P48 - Obtain Money Transaction - Money Transaction added successfully to New Case") 
            return {"message": "Obtained Money Transaction added successfully - New case"}     

    except ValidationError as ve:
        logger.error(f"C-1P48 - Obtain Money Transaction - validation error: {ve}")
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(ve))
        
    except Exception as e:
        logger.error(f"C-1P48 - Obtain Money Transaction - Unexpected error: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")        