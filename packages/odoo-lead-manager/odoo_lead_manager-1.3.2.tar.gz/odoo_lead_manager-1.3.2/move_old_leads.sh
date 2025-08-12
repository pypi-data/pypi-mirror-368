#!/bin/bash

pattern=$1

set -ex
 odlm leads   --date-from 2024-01-01 --date-to 2025-05-24 --user "$pattern"  --format csv  --fields id,status,activity_date_deadline,team_id,partner_name,contact_name,partner_id,stage_id,closer_id,open_user_id,user_id --limit 5000 --count
 odlm leads   --date-from 2024-01-01 --date-to 2025-05-24 --user "$pattern"  --format csv  --fields id,status,activity_date_deadline,team_id,partner_name,contact_name,partner_id,stage_id,closer_id,open_user_id,user_id --limit 5000 --output $pattern.csv

 odlm update --from-csv $pattern.csv --closer-id Administrator --open-user-id Administrator --user-name Administrator --closer-name Administrator

