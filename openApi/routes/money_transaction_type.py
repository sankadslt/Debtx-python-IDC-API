"""
API : C-1P48
Name : Obtain Money Transaction
Description : Get all money related transactions (Check RO-Negotiation, Settlement Plan)
Created By : Gayana Waraketiya (gayana.waraketiya@gmail.com), Dilmi Rangana (dilmirangana1234@gmail.com)
Created No :
Version: 1.0
IP : money_transaction_details, request
        
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

def variables_by_money_transaction_type(money_transaction_details, request):
    
    # Function to calculate running credit, running debt, and cumulative settled balance
    # running_credit: the total amount credited to the account
    # running_debt: the total amount debited from the account
    # cumulative_settled_balance: the total balance after all transactions (The difference between running credit and running debt)
    
    plus_money_transaction_types = ["Adjustment", "Dispute", "Cash", "Cheque"]
    minus_money_transaction_types = ["Bill", "Return Cheque"]

    cumulative_settled_balance = 0

    if money_transaction_details:
        previous_running_credit = money_transaction_details["running_credit"]
        previous_running_debt = money_transaction_details["running_debt"]

        if request.money_transaction_type in ["Adjustment", "Dispute"]:
            if request.money_transaction_amount >= 0:
                running_credit = previous_running_credit + abs(request.money_transaction_amount)
                running_debt = previous_running_debt
            else:
                running_credit = previous_running_credit
                running_debt = previous_running_debt + abs(request.money_transaction_amount)
                
        elif request.money_transaction_type in ["Cash", "Cheque"]:
            running_credit = previous_running_credit + abs(request.money_transaction_amount)
            running_debt = previous_running_debt
            
        elif request.money_transaction_type in ["Bill", "Return Cheque"]:
            running_credit = previous_running_credit
            running_debt = previous_running_debt + abs(request.money_transaction_amount)

        if request.money_transaction_type in ["Bill", "Return Cheque"]:
            cumulative_settled_balance = 0
        else:
            cumulative_settled_balance = running_credit - running_debt

    else:
        if request.money_transaction_type in ["Adjustment", "Dispute"]:
            if request.money_transaction_amount >= 0:
                running_credit = abs(request.money_transaction_amount)
                running_debt = 0
            else:
                running_credit = 0
                running_debt = abs(request.money_transaction_amount)
                
        elif request.money_transaction_type in ["Cash", "Cheque"]:
            running_credit = abs(request.money_transaction_amount)
            running_debt = 0
            
        elif request.money_transaction_type in ["Bill", "Return Cheque"]:
            running_credit = 0
            running_debt = abs(request.money_transaction_amount)

    return running_credit, running_debt, cumulative_settled_balance

    
    
# if request.money_transaction_type not in minus_money_transaction_types else 0