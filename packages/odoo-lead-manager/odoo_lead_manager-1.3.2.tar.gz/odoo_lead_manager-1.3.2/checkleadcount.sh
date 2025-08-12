


pattern=$1

echo $pattern


from="2025-05-22"
to="2025-07-25"

from="2024-01-01"
to="2025-05-22"

set -ex 
odlm leads   --date-from $from --date-to $to  --user "$pattern" --count
