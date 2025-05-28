"""
API :  C-1P48
Name : Obtain Money Transaction
Description : Get all money related transactions (Check RO-Negotiation, Settlement Plan)
Created By :  Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP : 
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
from fastapi import APIRouter, HTTPException, BackgroundTasks
from http import HTTPStatus
from openApi.models.obtain_money_transaction_class import Money_Transaction_Model
from openApi.routes.process_money_transaction import process_money_transaction


router = APIRouter()
logger = get_logger("Money_Manager")

@router.post("/Obtain_Money_Transaction", summary="Get all the money related transactions", description = """**Mandatory Fields**<br>          
- `case_id` <br>
- `account_num` <br>
- `settlement_id` <br>
- `money_transaction_type` <br>
- `money_transaction_ref` <br>
- `money_transaction_amount` <br>
- `money_transaction_date` (MM/DD/YYYY HH24:MM:SS) <br>
- `bill_payment_status` <br><br>

**Valid money_transaction_type values:** - "Bill","Adjustment","Dispute","Cash","Cheque","Return Cheque"  <br><br>
""")
#All above fields mandatory
async def obtain_money_transaction(request:Money_Transaction_Model, background_tasks: BackgroundTasks):
    # Check if the request is valid    
    filtered_request_data = {
        key: value for key, value in request.model_dump().items()
        if key in {
            "case_id",
            "account_num",
            "settlement_id",
            "money_transaction_type",
            "money_transaction_ref",
            "money_transaction_amount",
            "money_transaction_date",
            "bill_payment_status"
        } and value is not None
    }
    logger.debug("C-1P48 - Obtain Money Transaction - Request received %s",filtered_request_data)

    #log the request details
    background_tasks.add_task(process_money_transaction, request)
    return HTTPException(status_code=HTTPStatus.ACCEPTED, detail=f"Money Transaction accepted")


    
    