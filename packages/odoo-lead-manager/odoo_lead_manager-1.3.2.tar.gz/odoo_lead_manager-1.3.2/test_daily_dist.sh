

set -ex 
##	 --dry-run \

odlm dailydist --config config/test_campaign_config.yaml \
	 --generate-report   --report-format html \
	 --report-location run_daily_dist_report.html 	 \
	 --stages-output-dir filter_analysis  --export-before-filter  --show-filter-delta  \
	 --export-leads  --leads-output daily_leads.csv 


