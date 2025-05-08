"""
API : C-1P48
Name : Obtain Money Transaction
Description : Get all money related transactions (Check RO-Negotiation, Settlement Plan)
Created By : Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP : created_dtm, request
        
OP : None
"""

"""
    Version: Python 3.12.4
    Dependencies: Library
    Related Files: obtain_money_transaction.py, obtain_money_transaction_class.py, add_drc_bonus.py, 
                   update_db_status.py, manage_cheque_payment_for_completing_settlement.py, 
                   money_transaction_type.py
    Purpose: 
    Version:
        version: 1.0
        Last Modified Date: 2025-03-13
        Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)  
        Changes:     

    Notes:
"""

import requests
from datetime import datetime, timedelta
from loggers.loggers import get_logger

logger = get_logger("Money_Manager")

def Cheque_payment_for_completing_settlement(created_dtm, request):
    end_date = (created_dtm + timedelta(days=14)).strftime("%d/%m/%Y %H:%M:%S")
    # API details
    api_url = "http://127.0.0.1:8001/api/v1/Create_SLT_Order"  # API URL
    payload = {
    
        "case_id": request.case_id,
        "order_id": 4,
        "account_num": request.account_num,
        "parameters": {
            "case_id":request.case_id,
            "end_date": end_date
        },
        "request_status": "Open"
        }


    try:
        response = requests.post(api_url, json=payload, timeout=10)  # Sending a POST request

        if response.status_code == 200:
            logger.info("C-1P48 - Successfully triggered the cheque monitoring API")
        else:
            logger.error(f"C-1P48 - Failed to trigger cheque monitoring API: {response.status_code}, {response.text}")

    except requests.exceptions.RequestException as e:
        logger.error(f"C-1P48 - Error calling cheque monitoring API: {e}")
                