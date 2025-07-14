# FeedMiner Cost Tracking Guide

**Version**: 1.0  
**Last Updated**: July 13, 2025  
**Purpose**: Practical guide for monitoring and optimizing AWS costs using comprehensive tagging

## 📊 Cost Explorer Configuration

### Essential Filter Combinations

**Primary Cost Filters**:
```
Group by: Tag -> Project
Filter: Project = feedMiner
Time Range: Last 30 days
```

**Environment Breakdown**:
```
Group by: Tag -> Environment
Filter: Project = feedMiner
Granularity: Daily
Chart Type: Stacked Area
```

**Technology Stack Analysis**:
```
Group by: Tag -> Technology
Filter: Project = feedMiner AND Environment = prod
Include: Service breakdown
```

### Cost Allocation Reports

**Team-Based Allocation**:
```
Primary Dimension: Tag -> Team
Secondary Dimension: Tag -> CostCenter
Filter: BusinessUnit = Engineering
```

**Component Cost Analysis**:
```
Primary Dimension: Tag -> Component
Secondary Dimension: Service
Filter: Project = feedMiner
Include: Usage quantity and costs
```

## 💰 Budget Setup

### Environment-Based Budgets

**Development Environment**:
```
Budget Name: FeedMiner-Dev-Monthly
Amount: $200 USD
Period: Monthly
Filters: 
  - Project = feedMiner
  - Environment = dev
Alerts:
  - 50% of budget ($100)
  - 80% of budget ($160)
  - 100% of budget ($200)
```

**Production Environment**:
```
Budget Name: FeedMiner-Prod-Monthly
Amount: $500 USD
Period: Monthly
Filters:
  - Project = feedMiner
  - Environment = prod
Alerts:
  - 50% of budget ($250)
  - 80% of budget ($400)
  - 100% of budget ($500)
  - 110% forecasted ($550)
```

**Team-Based Budget**:
```
Budget Name: AI-Platform-Team-Quarterly
Amount: $3000 USD
Period: Quarterly
Filters:
  - Team = AI-Platform
  - CostCenter = CC-1001
Alerts:
  - 75% of budget ($2250)
  - 90% of budget ($2700)
  - 100% of budget ($3000)
```

### Component-Specific Budgets

**Lambda Compute Budget**:
```
Budget Name: FeedMiner-Lambda-Monthly
Amount: $150 USD
Filters:
  - Project = feedMiner
  - Technology = Serverless
  - Component = Lambda-Function
```

**Storage Budget**:
```
Budget Name: FeedMiner-Storage-Monthly
Amount: $100 USD
Filters:
  - Project = feedMiner
  - Purpose = Primary-Content-Storage OR Content-Object-Storage
```

## 📈 Cost Monitoring Queries

### AWS Cost Explorer Queries

**Monthly Cost Trend by Environment**:
```sql
-- Pseudo-SQL for Cost Explorer
SELECT 
  Environment,
  SUM(UnblendedCost) as Cost,
  DATE_TRUNC('month', UsageStartDate) as Month
FROM CostAndUsage
WHERE 
  Tag:Project = 'feedMiner'
  AND UsageStartDate >= '2025-01-01'
GROUP BY Environment, Month
ORDER BY Month DESC, Cost DESC
```

**Top Cost Drivers by Component**:
```sql
SELECT 
  Component,
  Technology,
  SUM(UnblendedCost) as TotalCost,
  AVG(UnblendedCost) as DailyCost
FROM CostAndUsage
WHERE 
  Tag:Project = 'feedMiner'
  AND Tag:Environment = 'prod'
  AND UsageStartDate >= DATEADD(day, -30, GETDATE())
GROUP BY Component, Technology
ORDER BY TotalCost DESC
LIMIT 10
```

### CloudWatch Insights for Cost Analysis

**Lambda Cost Analysis**:
```
fields @timestamp, @message
| filter @message like /REPORT/
| stats count() by bin(5m)
| sort @timestamp desc
```

**DynamoDB Usage Patterns**:
```
fields @timestamp, requestId, billedDuration
| filter @type = "REPORT"
| stats avg(billedDuration), max(billedDuration), count() by bin(1h)
```

## 🎯 Cost Optimization Strategies

### Automated Cost Controls

**Tag-Based Resource Scheduling**:
```yaml
# CloudWatch Events Rule for Development Shutdown
AutoShutdownRule:
  Type: AWS::Events::Rule
  Properties:
    ScheduleExpression: "cron(0 20 * * 1-5)"  # 8 PM weekdays
    Targets:
      - Arn: !GetAtt ShutdownLambda.Arn
        Id: "ShutdownTarget"
        Input: |
          {
            "action": "shutdown",
            "filters": {
              "Project": "feedMiner",
              "Environment": "dev",
              "AutoShutdown": "Enabled"
            }
          }
```

**Storage Lifecycle Management**:
```yaml
# Based on RetentionPeriod tags
LifecycleRules:
  - Id: "ContentArchival"
    Status: Enabled
    Filter:
      Tag:
        Key: "RetentionPeriod"
        Value: "7-years"
    Transitions:
      - Days: 30
        StorageClass: STANDARD_IA
      - Days: 90
        StorageClass: GLACIER
      - Days: 365
        StorageClass: DEEP_ARCHIVE
```

### Resource Right-Sizing

**Lambda Memory Optimization**:
```bash
# Use tags to identify optimization candidates
aws logs insights start-query \
  --log-group-name "/aws/lambda/feedminer-content-upload-dev" \
  --start-time $(date -d '7 days ago' +%s) \
  --end-time $(date +%s) \
  --query-string '
    fields @timestamp, @duration, @billedDuration, @memorySize, @maxMemoryUsed
    | filter @type = "REPORT"
    | stats avg(@maxMemoryUsed), max(@maxMemoryUsed), count() by bin(1h)
  '
```

**DynamoDB Capacity Planning**:
```bash
# Analyze usage patterns by component
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedReadCapacityUnits \
  --dimensions Name=TableName,Value=feedminer-content-dev \
  --start-time $(date -d '30 days ago' -Iseconds) \
  --end-time $(date -Iseconds) \
  --period 3600 \
  --statistics Average,Maximum
```

## 📊 Cost Reporting Templates

### Executive Summary Report

**Monthly Cost Summary**:
```
FeedMiner Cost Report - July 2025
=====================================

Total Monthly Cost: $687.45
Budget: $900.00 (76% utilized)
Trend: ↗️ +12% vs June 2025

Environment Breakdown:
├── Production: $425.32 (62%)
├── Development: $156.78 (23%)
└── Staging: $105.35 (15%)

Top Cost Drivers:
1. Lambda Execution: $245.67 (36%)
2. DynamoDB Storage: $189.23 (28%)
3. S3 Storage: $134.56 (20%)
4. API Gateway: $87.99 (13%)
5. CloudWatch Logs: $29.99 (4%)

Optimization Opportunities:
- Dev environment auto-shutdown: -$45/month
- DynamoDB reserved capacity: -$62/month
- S3 intelligent tiering: -$28/month
```

### Team Allocation Report

**AI Platform Team - July 2025**:
```
Team: AI-Platform
Cost Center: CC-1001
Business Unit: Engineering

Total Allocation: $687.45
Budget: $750.00 (92% utilized)
Projects: 1 active (feedMiner)

Project Breakdown:
feedMiner: $687.45 (100%)
├── Infrastructure: $456.78 (66%)
├── AI Processing: $156.89 (23%)
├── Storage: $73.78 (11%)

Resource Utilization:
├── High Impact: $512.31 (75%)
├── Medium Impact: $123.45 (18%)
└── Low Impact: $51.69 (7%)

Recommendations:
- Consider reserved instances for consistent workloads
- Implement auto-scaling for variable demand
- Review data retention policies
```

## 🔧 Implementation Commands

### Cost Explorer API Usage

**Get Monthly Costs by Environment**:
```bash
aws ce get-cost-and-usage \
  --time-period Start=2025-07-01,End=2025-07-31 \
  --granularity MONTHLY \
  --metrics BlendedCost UnblendedCost \
  --group-by Type=TAG,Key=Environment \
  --filter file://filters/feedminer-project.json
```

**Filter Configuration (feedminer-project.json)**:
```json
{
  "Tags": {
    "Key": "Project",
    "Values": ["feedMiner"],
    "MatchOptions": ["EQUALS"]
  }
}
```

### Budget Creation via CLI

**Create Environment Budget**:
```bash
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file://budgets/feedminer-dev-budget.json \
  --notifications-with-subscribers file://budgets/budget-notifications.json
```

**Budget Configuration (feedminer-dev-budget.json)**:
```json
{
  "BudgetName": "FeedMiner-Dev-Monthly",
  "BudgetLimit": {
    "Amount": "200",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {
    "TagKey": [
      "Project"
    ],
    "TagValue": [
      "feedMiner"
    ]
  }
}
```

### Automated Reporting Scripts

**Weekly Cost Report**:
```bash
#!/bin/bash
# weekly-cost-report.sh

PROJECT="feedMiner"
WEEK_START=$(date -d '7 days ago' +%Y-%m-%d)
WEEK_END=$(date +%Y-%m-%d)

echo "FeedMiner Weekly Cost Report"
echo "Period: $WEEK_START to $WEEK_END"
echo "================================="

# Get total costs
aws ce get-cost-and-usage \
  --time-period Start=$WEEK_START,End=$WEEK_END \
  --granularity DAILY \
  --metrics UnblendedCost \
  --filter "{\"Tags\":{\"Key\":\"Project\",\"Values\":[\"$PROJECT\"]}}" \
  --query 'ResultsByTime[*].Total.UnblendedCost.Amount' \
  --output text | awk '{sum+=$1} END {printf "Total Weekly Cost: $%.2f\n", sum}'

# Get environment breakdown
aws ce get-cost-and-usage \
  --time-period Start=$WEEK_START,End=$WEEK_END \
  --granularity WEEKLY \
  --metrics UnblendedCost \
  --group-by Type=TAG,Key=Environment \
  --filter "{\"Tags\":{\"Key\":\"Project\",\"Values\":[\"$PROJECT\"]}}" \
  --query 'ResultsByTime[0].Groups[*].[Keys[0],Total.UnblendedCost.Amount]' \
  --output text | while read env cost; do
    printf "  %-12s: $%.2f\n" "$env" "$cost"
  done
```

## 📱 Cost Alerting Setup

### CloudWatch Alarms for Cost Thresholds

**Daily Spend Alarm**:
```yaml
DailySpendAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: !Sub "${AWS::StackName}-daily-spend-${Environment}"
    AlarmDescription: "Daily spend exceeds threshold"
    MetricName: EstimatedCharges
    Namespace: AWS/Billing
    Statistic: Maximum
    Period: 86400  # 24 hours
    EvaluationPeriods: 1
    Threshold: 50  # $50 daily threshold
    ComparisonOperator: GreaterThanThreshold
    Dimensions:
      - Name: Currency
        Value: USD
    AlarmActions:
      - !Ref CostAlertTopic
```

**SNS Topic for Cost Alerts**:
```yaml
CostAlertTopic:
  Type: AWS::SNS::Topic
  Properties:
    TopicName: !Sub "${AWS::StackName}-cost-alerts-${Environment}"
    Subscription:
      - Protocol: email
        Endpoint: !Ref ResourceOwner
      - Protocol: slack
        Endpoint: !Ref SlackWebhookUrl
```

### Lambda-Based Cost Monitoring

**Cost Anomaly Detection**:
```python
import boto3
import json
from datetime import datetime, timedelta

def lambda_handler(event, context):
    ce_client = boto3.client('ce')
    
    # Get costs for last 7 days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    response = ce_client.get_cost_and_usage(
        TimePeriod={'Start': start_date, 'End': end_date},
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'TAG', 'Key': 'Component'}],
        Filter={
            'Tags': {
                'Key': 'Project',
                'Values': ['feedMiner']
            }
        }
    )
    
    # Analyze for anomalies
    daily_costs = []
    for result in response['ResultsByTime']:
        total_cost = float(result['Total']['UnblendedCost']['Amount'])
        daily_costs.append(total_cost)
    
    avg_cost = sum(daily_costs) / len(daily_costs)
    latest_cost = daily_costs[-1]
    
    # Alert if latest cost is 50% above average
    if latest_cost > avg_cost * 1.5:
        send_cost_alert(latest_cost, avg_cost)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'latest_cost': latest_cost,
            'average_cost': avg_cost,
            'anomaly_detected': latest_cost > avg_cost * 1.5
        })
    }
```

## 📋 Best Practices Checklist

### Daily Operations ✅
- [ ] Review cost alerts and notifications
- [ ] Check budget utilization in Cost Explorer
- [ ] Monitor high-cost resource usage patterns
- [ ] Verify auto-shutdown policies are working

### Weekly Reviews ✅
- [ ] Generate environment cost comparison report
- [ ] Review top cost drivers and optimization opportunities
- [ ] Validate tag compliance across all resources
- [ ] Update resource right-sizing recommendations

### Monthly Analysis ✅
- [ ] Complete chargeback allocation to business units
- [ ] Update budgets based on usage trends
- [ ] Review and optimize reserved capacity purchases
- [ ] Document cost optimization actions taken

### Quarterly Planning ✅
- [ ] Forecast costs for next quarter based on trends
- [ ] Review and update tagging strategy
- [ ] Assess ROI on cost optimization initiatives
- [ ] Plan budget allocations for new features

---

**This guide enables comprehensive cost tracking and optimization for the FeedMiner project using enterprise-level AWS cost management practices.**