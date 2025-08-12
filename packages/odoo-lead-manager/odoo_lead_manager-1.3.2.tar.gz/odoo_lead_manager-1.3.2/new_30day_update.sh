#!/bin/bash

pat=$1

set -ex 

csv="`echo $pat |perl -pe 's/\s+/_/g'`.csv"

echo $csv
odlm leads --count  --user $pat --date-from 2025-01-01 --date-to 2025-06-29 --output $csv --format csv --fields source_date,id,status,open_user_id               

odlm leads  --user $pat --date-from 2025-01-01 --date-to 2025-06-29 --output $csv --format csv --fields source_date,id,status,open_user_id 


odlm update --from-csv $csv \
	 --closer-id 1 --open-user-id 1 --user-name Administrator --closer-name Administrator  --user-id 1  
