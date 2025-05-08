"""
API : C-1P48
Name : Obtain Money Transaction
Description : Get all money related transactions (Check RO-Negotiation, Settlement Plan)
Created By : Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP : existing_case, request
        
OP : running_credit, running_debt, cumulative_settled_balance
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
        Last Modified Date: 2025-03-07
        Modified By: Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)  
        Changes:     

    Notes:
"""

def variables_by_money_transaction_type(existing_case, request):
    
    plus_money_transaction_types = ["Adjustment","Dispute","Cash","Cheque"]
    minus_money_transaction_types = ["Bill","Return Cheque"]
    
    if existing_case:
        running_credit = existing_case["running_credit"] + abs(request.money_transaction_amount) if request.money_transaction_type not in minus_money_transaction_types else existing_case["running_credit"]
        running_debt = existing_case["running_debt"] if request.money_transaction_type not in minus_money_transaction_types else existing_case["running_debt"] + abs(request.money_transaction_amount)
        cumulative_settled_balance = (running_credit - running_debt) 
        return running_credit, running_debt, cumulative_settled_balance
    
    else:
        running_credit = abs(request.money_transaction_amount) if request.money_transaction_type not in minus_money_transaction_types else 0
        running_debt = 0 if request.money_transaction_type not in minus_money_transaction_types else abs(request.money_transaction_amount)
        return running_credit, running_debt
    
    
    # if request.money_transaction_type not in minus_money_transaction_types else 0