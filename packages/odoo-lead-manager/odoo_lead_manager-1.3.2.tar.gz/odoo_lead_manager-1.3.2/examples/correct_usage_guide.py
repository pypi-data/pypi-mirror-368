#!/usr/bin/env python3
"""
Correct Usage Guide for odlm update

This guide demonstrates the correct data types and usage patterns
for the odlm update command, addressing the confusion around
user name vs user ID parameters.
"""

def print_usage_guide():
    """Print comprehensive usage guide with data type clarifications."""
    
    guide = """
🎯 Correct Usage Guide: odlm update Command
==========================================

📊 Data Type Reference
----------------------

Lead IDs:
- Type: Integer
- Examples: 40109, 143996, 179711, 192417
- Usage: --ids 40109,143996,179711

User Assignment Fields:
┌─────────────────┬─────────────────────┬─────────────────────────────┐
│ Parameter       │ Type                │ Description                 │
├─────────────────┼─────────────────────┼─────────────────────────────┤
│ --user-id       │ Integer or String   │ User ID or name             │
│ --user-name     │ String              │ User name (auto-resolved)   │
│ --closer-id     │ Integer or String   │ Closer ID or name           │
│ --closer-name   │ String              │ Closer name (auto-resolved) │
│ --open-user-id  │ Integer or String   │ Open user ID or name        │
│ --open-user-name│ String              │ Open user name (auto-resolved)│
└─────────────────┴─────────────────────┴─────────────────────────────┘

Status Field:
- Type: String
- Examples: new, assigned, in_progress, won, lost
- Usage: --status assigned

✅ Correct Usage Examples
-------------------------

1. Using User IDs (integers):
odlm update --ids 40109,143996,179711 \
    --user-id 1 \
    --closer-id 2 \
    --open-user-id 1

2. Using User Names (strings - now supported!):
odlm update --ids 40109,143996,179711 \
    --user-id "Administrator" \
    --closer-id "Sales Team Lead" \
    --open-user-id "Administrator"

3. Mixed usage (IDs and names work together):
odlm update --ids 40109,143996 \
    --user-id 1 \
    --closer-id "Senior Sales" \
    --status assigned

4. Status update only:
odlm update --ids 192417,290502 \
    --status in_progress

5. CSV file with name resolution:
odlm update --from-csv leads.csv \
    --user-name "Alice Smith" \
    --status new

🔍 Finding User IDs
------------------

Get user list with IDs:
odlm users --list

Example output:
┌─────┬──────────────────────┬─────────────────────┬─────────────────┐
│ ID  │ Name                 │ Email               │ Login           │
├─────┼──────────────────────┼─────────────────────┼─────────────────┤
│ 1   │ Administrator      │ admin@example.com   │ admin           │
│ 2   │ Sales Team Lead    │ sales@example.com   │ sales           │
│ 3   │ Alice Smith        │ alice@example.com   │ alice           │
└─────┴──────────────────────┴─────────────────────┴─────────────────┘

🚀 Practical Workflows
----------------------

Scenario 1: Assign new leads to sales team
odlm leads --format csv --output new_leads.csv --status new
odlm update --from-csv new_leads.csv --user-name "Sales Team Lead"

Scenario 2: Reassign leads to senior closer
odlm update --ids 40109,143996,179711 \
    --closer-name "Senior Sales" \
    --status assigned

Scenario 3: Batch update with file input
echo "192417\\n290502\\n291147" > lead_ids.txt
odlm update --from-file lead_ids.txt \
    --user-name "Alice Smith" \
    --status in_progress

💡 Best Practices
-----------------

1. Always use --user-name/--closer-name/--open-user-name for names
2. Use --user-id/--closer-id/--open-user-id only when you know the exact ID
3. Check user IDs first with: odlm users --list
4. Use exact names to avoid ambiguity
5. Test with single lead before batch updates

🎯 Quick Reference Card
-----------------------

# Get user IDs first
odlm users --list

# Correct usage patterns:
odlm update --ids LEAD_IDS [OPTIONS]
odlm update --from-csv FILE [OPTIONS]
odlm update --from-tsv FILE [OPTIONS]
odlm update --from-file FILE [OPTIONS]

Where OPTIONS are:
  --user-id ID         (integer)
  --user-name NAME     (string, auto-resolved)
  --closer-id ID       (integer)
  --closer-name NAME   (string, auto-resolved)
  --open-user-id ID    (integer)
  --open-user-name NAME (string, auto-resolved)
  --status STATUS      (string)
"""
    
    print(guide)

def main():
    """Main function to show the usage guide."""
    print("🎯 odlm update - Data Type Clarification Guide")
    print("=" * 60)
    print_usage_guide()
    print("\n✨ Remember: Use -name parameters for names, -id parameters for integers!")

if __name__ == "__main__":
    main()