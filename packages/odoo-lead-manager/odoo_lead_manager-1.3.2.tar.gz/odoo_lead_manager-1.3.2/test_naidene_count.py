#!/usr/bin/env python3
"""
Test script to understand Naidene Salgado's lead count difference
"""

from src.odoo_lead_manager import OdooClient

def test_naidene_counts():
    """Test different queries to understand the 521 vs 510 difference."""
    
    client = OdooClient()
    client.connect()
    client.authenticate()
    
    naidene_id = 1175
    
    print("=== NAIDENE SALGADO LEAD COUNT ANALYSIS ===\n")
    
    # Query 1: Only user_id (like CLI does)
    user_id_leads = client.search_read(
        'crm.lead',
        domain=[('user_id', '=', naidene_id)],
        fields=['id']
    )
    user_id_count = len(user_id_leads) if user_id_leads else 0
    print(f"1. Leads where user_id = {naidene_id}: {user_id_count}")
    
    # Query 2: Only closer_id
    closer_id_leads = client.search_read(
        'crm.lead',
        domain=[('closer_id', '=', naidene_id)],
        fields=['id']
    )
    closer_id_count = len(closer_id_leads) if closer_id_leads else 0
    print(f"2. Leads where closer_id = {naidene_id}: {closer_id_count}")
    
    # Query 3: Combined OR query (like daily distribution does)
    combined_leads = client.search_read(
        'crm.lead',
        domain=[
            '|',
            ('user_id', '=', naidene_id),
            ('closer_id', '=', naidene_id)
        ],
        fields=['id']
    )
    combined_count = len(combined_leads) if combined_leads else 0
    print(f"3. Combined (user_id OR closer_id) = {naidene_id}: {combined_count}")
    
    # Query 4: Only open_user_id
    open_user_leads = client.search_read(
        'crm.lead',
        domain=[('open_user_id', '=', naidene_id)],
        fields=['id']
    )
    open_user_count = len(open_user_leads) if open_user_leads else 0
    print(f"4. Leads where open_user_id = {naidene_id}: {open_user_count}")
    
    # Query 5: Check for overlap (leads where she's both user_id AND closer_id)
    both_leads = client.search_read(
        'crm.lead',
        domain=[
            ('user_id', '=', naidene_id),
            ('closer_id', '=', naidene_id)
        ],
        fields=['id']
    )
    both_count = len(both_leads) if both_leads else 0
    print(f"5. Leads where BOTH user_id AND closer_id = {naidene_id}: {both_count}")
    
    # Query 6: All three fields combined
    all_three_leads = client.search_read(
        'crm.lead',
        domain=[
            '|', '|',
            ('user_id', '=', naidene_id),
            ('closer_id', '=', naidene_id),
            ('open_user_id', '=', naidene_id)
        ],
        fields=['id']
    )
    all_three_count = len(all_three_leads) if all_three_leads else 0
    print(f"6. Combined (user_id OR closer_id OR open_user_id) = {naidene_id}: {all_three_count}")
    
    print("\n=== ANALYSIS ===")
    print(f"user_id only: {user_id_count}")
    print(f"closer_id only: {closer_id_count}")
    print(f"open_user_id only: {open_user_count}")
    print(f"user_id OR closer_id: {combined_count}")
    print(f"All three fields OR: {all_three_count}")
    
    print(f"\nPossible 293 lead explanation:")
    print(f"If 293 is the 'active' leads, it might be open_user_id: {open_user_count}")
    
    # Query 7: Let's check some common "active" statuses to see if any give us 293
    active_statuses = ["new", "fpfu", "utr", "fpnc", "mfpnc", "call_back", "in_program"]
    for status in active_statuses:
        status_leads = client.search_read(
            'crm.lead',
            domain=[
                ('user_id', '=', naidene_id),
                ('status', '=', status)
            ],
            fields=['id']
        )
        status_count = len(status_leads) if status_leads else 0
        if status_count > 0:
            print(f"7. Leads where user_id = {naidene_id} AND status = '{status}': {status_count}")
    
    print(f"\nDaily distribution (521) vs CLI (510) vs open_user_id ({open_user_count}):")
    print(f"Daily distribution: user_id OR closer_id = {combined_count}")
    print(f"CLI: user_id only = {user_id_count}")
    print(f"Open user: open_user_id only = {open_user_count}")
    
    print(f"\nNote: The 293 you mentioned might be:")
    print(f"- A specific status filter")
    print(f"- A time-based filter (recent leads)")
    print(f"- A different field or view in Odoo")

if __name__ == "__main__":
    test_naidene_counts()