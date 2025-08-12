# Sale Status Exclusion Feature

## Overview

The Sale Status Exclusion feature allows you to automatically exclude leads from distribution when their status indicates that a sale has already been made. This prevents leads that have already been converted or closed from being redistributed to salespeople.

## Configuration

### Basic Configuration

Add the `exclude_sale_statuses` section to your configuration under `lead_finding.additional_filters`:

```yaml
lead_finding:
  additional_filters:
    exclude_sale_statuses:
      enabled: true
      values:
        - "sale_made"
        - "sold"
        - "completed"
        - "won"
        - "closed_won"
        - "deal_closed"
        - "sale_complete"
        - "deal_done"
        - "converted"
        - "deal_won"
        - "sale_finalized"
      case_sensitive: false
      match_mode: "partial"
      description: "Exclude leads with statuses indicating a sale has been made"
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable/disable sale status exclusion |
| `values` | list | `[]` | List of status values to exclude |
| `case_sensitive` | boolean | `false` | Whether to match case-sensitively |
| `match_mode` | string | `"exact"` | Matching mode: `exact`, `partial`, or `regex` |
| `description` | string | `""` | Description of the exclusion rule |

### Match Modes

1. **exact**: Only excludes leads with exact status matches
2. **partial**: Excludes leads where the status contains any of the excluded values
3. **regex**: Uses regular expressions for pattern matching

## Usage Examples

### Example 1: Basic Exclusion

```yaml
exclude_sale_statuses:
  enabled: true
  values:
    - "sale_made"
    - "sold"
    - "completed"
  case_sensitive: false
  match_mode: "exact"
```

This will exclude leads with statuses exactly matching "sale_made", "sold", or "completed".

### Example 2: Partial Matching

```yaml
exclude_sale_statuses:
  enabled: true
  values:
    - "sale"
    - "sold"
    - "won"
    - "closed"
  case_sensitive: false
  match_mode: "partial"
```

This will exclude leads with statuses containing any of these words (e.g., "sale_pending", "sold_to_customer", "won_deal", "closed_won").

### Example 3: Case-Sensitive Matching

```yaml
exclude_sale_statuses:
  enabled: true
  values:
    - "SALE_MADE"
    - "SOLD"
    - "COMPLETED"
  case_sensitive: true
  match_mode: "exact"
```

This will only exclude leads with exact uppercase status matches.

## Testing

### Run the Test Script

```bash
python test_sale_status_exclusion.py
```

This will test various lead statuses against the exclusion criteria and show which ones would be included or excluded.

### Run Dry-Run Test

```bash
python run_dry_run_test.py --config config/test_dry_run_config.yaml
```

This will run a complete dry-run test using the test configuration that includes sale status exclusion.

### Step-by-Step Analysis

```bash
python run_dry_run_test.py --config config/test_dry_run_config.yaml --step-mode
```

This will run the test in step-through mode, allowing you to review each step of the distribution process.

## Integration with Existing Filters

The sale status exclusion is applied **before** the regular status filtering. This means:

1. **Sale Status Check**: First, check if the lead status indicates a sale
2. **Regular Status Check**: Then, check if the lead status matches the allowed statuses
3. **Other Filters**: Finally, apply all other filtering criteria

## Status Examples

### Excluded Statuses (Sale Made)
- `sale_made`
- `sold`
- `completed`
- `won`
- `closed_won`
- `deal_closed`
- `sale_complete`
- `deal_done`
- `converted`
- `deal_won`
- `sale_finalized`

### Included Statuses (No Sale Made)
- `new`
- `in_progress`
- `call_back`
- `utr`
- `pending_sale`
- `sale_pending`
- `pre_sale`
- `negotiating`
- `proposal_sent`

## Configuration Files

### Test Configuration

Use `config/test_dry_run_config.yaml` for testing with dry-run mode enabled:

```yaml
execution:
  dry_run: true
```

### Production Configuration

Use `config/daily_distribution_config.yaml` for production runs:

```yaml
execution:
  dry_run: false
```

## Monitoring and Reporting

The dry-run report includes a section showing sale status exclusion statistics:

```
🔍 Sale Status Exclusion Summary:
   ✅ Sale status exclusion is ENABLED
   📝 Excluded statuses (11):
      • sale_made
      • sold
      • completed
      • won
      • closed_won
      • deal_closed
      • sale_complete
      • deal_done
      • converted
      • deal_won
      • sale_finalized
   ⚙️  Match mode: partial
   🔤 Case sensitive: false
```

## Troubleshooting

### Common Issues

1. **No leads being distributed**: Check if sale status exclusion is too broad
2. **Wrong leads being excluded**: Review the status values and match mode
3. **Case sensitivity issues**: Ensure case_sensitive setting matches your data

### Debug Mode

Enable verbose logging to see detailed filter information:

```bash
python run_dry_run_test.py --verbose
```

### Configuration Validation

The system validates the configuration and will show errors if:
- Required fields are missing
- Invalid match modes are specified
- No status values are provided when enabled

## Best Practices

1. **Start with exact matching** for precise control
2. **Use partial matching** for broader exclusion patterns
3. **Test thoroughly** with dry-run mode before production
4. **Monitor results** to ensure desired behavior
5. **Document custom statuses** used in your system

## Migration from Previous Versions

If you're upgrading from a version without sale status exclusion:

1. Add the `exclude_sale_statuses` configuration
2. Set `enabled: false` initially
3. Test with dry-run mode
4. Gradually enable and adjust as needed
5. Monitor distribution results

## Support

For issues or questions about the sale status exclusion feature:

1. Check the test results: `python test_sale_status_exclusion.py`
2. Review the dry-run report for detailed analysis
3. Verify configuration syntax and values
4. Test with different match modes and case sensitivity settings 