#!/usr/bin/env python3
"""
Complete Uber Fare Analysis Script
This script performs comprehensive analysis of Uber fare data including:
- Data cleaning and preprocessing
- Exploratory data analysis
- Feature engineering
- Visualization generation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

print("🚖 Starting Uber Fare Analysis...")
print("=" * 50)

# 1. Load the raw data
print("\n📊 Step 1: Loading raw data...")
df = pd.read_csv("Data/raw/uber.csv")
print(f"✓ Loaded dataset with {df.shape[0]} rows and {df.shape[1]} columns")

# 2. Initial data exploration
print("\n🔍 Step 2: Initial data exploration...")
print("\nFirst 5 rows:")
print(df.head())
print("\nDataset info:")
print(df.info())
print("\nSummary statistics:")
print(df.describe())

# 3. Data cleaning
print("\n🧹 Step 3: Data cleaning...")
print(f"Initial missing values:\n{df.isnull().sum()}")

# Drop missing values
df = df.dropna()
print(f"✓ Dropped missing values. New shape: {df.shape}")

# Convert pickup time to datetime
df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'])
print("✓ Converted pickup_datetime to datetime format")

# Remove invalid fares and outliers
initial_count = len(df)
df = df[df['fare_amount'] > 0]  # Remove negative fares
df = df[df['fare_amount'] < 200]  # Remove extremely high fares (likely errors)
df = df[df['passenger_count'] > 0]  # Remove rides with 0 passengers
df = df[df['passenger_count'] <= 6]  # Remove unrealistic passenger counts

print(f"✓ Removed {initial_count - len(df)} invalid records")
print(f"✓ Final cleaned dataset: {df.shape[0]} rows")

# Save cleaned data
df.to_csv("Data/cleaned/uber_cleaned.csv", index=False)
print("✓ Saved cleaned data to Data/cleaned/uber_cleaned.csv")

# 4. Feature Engineering
print("\n⚙️ Step 4: Feature engineering...")

# Extract time-based features
df['hour'] = df['pickup_datetime'].dt.hour
df['day'] = df['pickup_datetime'].dt.day
df['month'] = df['pickup_datetime'].dt.month
df['year'] = df['pickup_datetime'].dt.year
df['weekday'] = df['pickup_datetime'].dt.day_name()
df['weekday_num'] = df['pickup_datetime'].dt.dayofweek

# Create peak time feature
df['is_peak'] = df['hour'].apply(lambda x: 'Peak' if (7 <= x <= 9) or (17 <= x <= 19) else 'Off-Peak')

# Create time of day categories
def time_category(hour):
    if 5 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 17:
        return 'Afternoon'
    elif 17 <= hour < 21:
        return 'Evening'
    else:
        return 'Night'

df['time_category'] = df['hour'].apply(time_category)

# Calculate distance (simplified Euclidean distance)
df['distance'] = np.sqrt((df['dropoff_longitude'] - df['pickup_longitude'])**2 + 
                        (df['dropoff_latitude'] - df['pickup_latitude'])**2)

print("✓ Created time-based features")
print("✓ Created peak time indicator")
print("✓ Created time category feature")
print("✓ Calculated trip distance")

# Save enhanced data
df.to_csv("Data/enhanced/uber_enhanced.csv", index=False)
print("✓ Saved enhanced data to Data/enhanced/uber_enhanced.csv")

# 5. Descriptive Statistics
print("\n📈 Step 5: Descriptive statistics...")
print(f"Mean fare: ${df['fare_amount'].mean():.2f}")
print(f"Median fare: ${df['fare_amount'].median():.2f}")
print(f"Standard deviation: ${df['fare_amount'].std():.2f}")
print(f"Min fare: ${df['fare_amount'].min():.2f}")
print(f"Max fare: ${df['fare_amount'].max():.2f}")

# Outlier detection using IQR
Q1 = df['fare_amount'].quantile(0.25)
Q3 = df['fare_amount'].quantile(0.75)
IQR = Q3 - Q1
outliers = df[(df['fare_amount'] < Q1 - 1.5 * IQR) | (df['fare_amount'] > Q3 + 1.5 * IQR)]
print(f"Outliers detected: {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")

# 6. Generate Visualizations
print("\n📊 Step 6: Generating visualizations...")

# Create powerbi directory if it doesn't exist
import os
os.makedirs("powerbi", exist_ok=True)

# 1. Fare Distribution
plt.figure(figsize=(10, 6))
sns.histplot(df['fare_amount'], bins=50, kde=True)
plt.title("Uber Fare Distribution", fontsize=16, fontweight='bold')
plt.xlabel("Fare Amount ($)")
plt.ylabel("Frequency")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("powerbi/fare_distribution.png", dpi=300, bbox_inches='tight')
plt.close()
print("✓ Generated fare distribution histogram")

# 2. Box plot for fare by time category
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='time_category', y='fare_amount')
plt.title("Fare Distribution by Time of Day", fontsize=16, fontweight='bold')
plt.xlabel("Time Category")
plt.ylabel("Fare Amount ($)")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("powerbi/boxPlot.png", dpi=300, bbox_inches='tight')
plt.close()
print("✓ Generated box plot by time category")

# 3. Average fare by hour
hourly_fare = df.groupby('hour')['fare_amount'].mean().reset_index()
plt.figure(figsize=(12, 6))
plt.plot(hourly_fare['hour'], hourly_fare['fare_amount'], marker='o', linewidth=2, markersize=6)
plt.title("Average Fare by Hour of Day", fontsize=16, fontweight='bold')
plt.xlabel("Hour of Day")
plt.ylabel("Average Fare ($)")
plt.grid(True, alpha=0.3)
plt.xticks(range(0, 24))
plt.tight_layout()
plt.savefig("powerbi/fare_hour.png", dpi=300, bbox_inches='tight')
plt.close()
print("✓ Generated hourly fare trend")

# 4. Number of rides by hour
hourly_rides = df.groupby('hour').size().reset_index(name='ride_count')
plt.figure(figsize=(12, 6))
plt.bar(hourly_rides['hour'], hourly_rides['ride_count'], alpha=0.7)
plt.title("Number of Rides by Hour of Day", fontsize=16, fontweight='bold')
plt.xlabel("Hour of Day")
plt.ylabel("Number of Rides")
plt.grid(True, alpha=0.3)
plt.xticks(range(0, 24))
plt.tight_layout()
plt.savefig("powerbi/rides_hour.png", dpi=300, bbox_inches='tight')
plt.close()
print("✓ Generated hourly ride count")

# 5. Average fare by weekday
weekday_fare = df.groupby('weekday')['fare_amount'].mean().reindex([
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
])
plt.figure(figsize=(10, 6))
weekday_fare.plot(kind='bar', color='skyblue', alpha=0.8)
plt.title("Average Fare by Day of Week", fontsize=16, fontweight='bold')
plt.xlabel("Day of Week")
plt.ylabel("Average Fare ($)")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("powerbi/fare_week.png", dpi=300, bbox_inches='tight')
plt.close()
print("✓ Generated weekly fare analysis")

# 6. Number of rides by weekday
weekday_rides = df.groupby('weekday').size().reindex([
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
])
plt.figure(figsize=(10, 6))
weekday_rides.plot(kind='bar', color='lightcoral', alpha=0.8)
plt.title("Number of Rides by Day of Week", fontsize=16, fontweight='bold')
plt.xlabel("Day of Week")
plt.ylabel("Number of Rides")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("powerbi/rides_weekday.png", dpi=300, bbox_inches='tight')
plt.close()
print("✓ Generated weekly ride count")

# 7. Monthly fare trends
monthly_fare = df.groupby('month')['fare_amount'].mean().reset_index()
plt.figure(figsize=(10, 6))
plt.plot(monthly_fare['month'], monthly_fare['fare_amount'], marker='o', linewidth=2, markersize=8)
plt.title("Average Fare by Month", fontsize=16, fontweight='bold')
plt.xlabel("Month")
plt.ylabel("Average Fare ($)")
plt.grid(True, alpha=0.3)
plt.xticks(range(1, 13))
plt.tight_layout()
plt.savefig("powerbi/fare_monthly.png", dpi=300, bbox_inches='tight')
plt.close()
print("✓ Generated monthly fare trends")

# 8. Peak vs Off-peak comparison
peak_comparison = df.groupby('is_peak')['fare_amount'].agg(['mean', 'count']).reset_index()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Average fare
ax1.bar(peak_comparison['is_peak'], peak_comparison['mean'], color=['orange', 'blue'], alpha=0.7)
ax1.set_title("Average Fare: Peak vs Off-Peak", fontweight='bold')
ax1.set_ylabel("Average Fare ($)")
ax1.grid(True, alpha=0.3)

# Ride count
ax2.bar(peak_comparison['is_peak'], peak_comparison['count'], color=['orange', 'blue'], alpha=0.7)
ax2.set_title("Number of Rides: Peak vs Off-Peak", fontweight='bold')
ax2.set_ylabel("Number of Rides")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("powerbi/peak_analysis.png", dpi=300, bbox_inches='tight')
plt.close()
print("✓ Generated peak vs off-peak analysis")

# 9. Passenger count analysis
passenger_stats = df.groupby('passenger_count')['fare_amount'].agg(['mean', 'count']).reset_index()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Average fare by passenger count
ax1.bar(passenger_stats['passenger_count'], passenger_stats['mean'], alpha=0.7)
ax1.set_title("Average Fare by Passenger Count", fontweight='bold')
ax1.set_xlabel("Number of Passengers")
ax1.set_ylabel("Average Fare ($)")
ax1.grid(True, alpha=0.3)

# Number of rides by passenger count
ax2.bar(passenger_stats['passenger_count'], passenger_stats['count'], alpha=0.7, color='green')
ax2.set_title("Number of Rides by Passenger Count", fontweight='bold')
ax2.set_xlabel("Number of Passengers")
ax2.set_ylabel("Number of Rides")
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("powerbi/passenger_analysis.png", dpi=300, bbox_inches='tight')
plt.close()
print("✓ Generated passenger count analysis")

# 10. Summary statistics visualization
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Fare statistics
stats_data = [df['fare_amount'].mean(), df['fare_amount'].median(), 
              df['fare_amount'].std(), df['fare_amount'].max()]
stats_labels = ['Mean', 'Median', 'Std Dev', 'Max']
axes[0,0].bar(stats_labels, stats_data, color=['blue', 'green', 'orange', 'red'], alpha=0.7)
axes[0,0].set_title("Fare Statistics", fontweight='bold')
axes[0,0].set_ylabel("Amount ($)")
axes[0,0].grid(True, alpha=0.3)

# Distance distribution
axes[0,1].hist(df['distance'], bins=50, alpha=0.7, color='purple')
axes[0,1].set_title("Trip Distance Distribution", fontweight='bold')
axes[0,1].set_xlabel("Distance (degrees)")
axes[0,1].set_ylabel("Frequency")
axes[0,1].grid(True, alpha=0.3)

# Fare vs Distance scatter
sample_df = df.sample(n=min(5000, len(df)))  # Sample for better performance
axes[1,0].scatter(sample_df['distance'], sample_df['fare_amount'], alpha=0.5, s=10)
axes[1,0].set_title("Fare vs Distance", fontweight='bold')
axes[1,0].set_xlabel("Distance (degrees)")
axes[1,0].set_ylabel("Fare Amount ($)")
axes[1,0].grid(True, alpha=0.3)

# Correlation heatmap
numeric_cols = ['fare_amount', 'distance', 'passenger_count', 'hour', 'month']
corr_matrix = df[numeric_cols].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[1,1])
axes[1,1].set_title("Correlation Matrix", fontweight='bold')

plt.tight_layout()
plt.savefig("powerbi/summary_analysis.png", dpi=300, bbox_inches='tight')
plt.close()
print("✓ Generated summary analysis dashboard")

# 7. Generate Analysis Report
print("\n📝 Step 7: Generating analysis report...")

report = f"""
# Uber Fare Analysis Report

## Dataset Overview
- **Total Records**: {len(df):,}
- **Time Period**: {df['pickup_datetime'].min()} to {df['pickup_datetime'].max()}
- **Features**: {df.shape[1]} columns

## Key Findings

### Fare Statistics
- **Average Fare**: ${df['fare_amount'].mean():.2f}
- **Median Fare**: ${df['fare_amount'].median():.2f}
- **Fare Range**: ${df['fare_amount'].min():.2f} - ${df['fare_amount'].max():.2f}
- **Standard Deviation**: ${df['fare_amount'].std():.2f}

### Time-based Patterns
- **Peak Hours**: 7-9 AM and 5-7 PM show different patterns
- **Busiest Day**: {weekday_rides.idxmax()} ({weekday_rides.max():,} rides)
- **Highest Fare Day**: {weekday_fare.idxmax()} (${weekday_fare.max():.2f} avg)

### Passenger Patterns
- **Most Common**: {df['passenger_count'].mode()[0]} passenger(s) per ride
- **Average Passengers**: {df['passenger_count'].mean():.1f}
- **Max Passengers**: {df['passenger_count'].max()}

### Distance Analysis
- **Average Distance**: {df['distance'].mean():.4f} degrees
- **Correlation with Fare**: {df['fare_amount'].corr(df['distance']):.3f}

## Recommendations
1. **Peak Hour Pricing**: Consider dynamic pricing during peak hours
2. **Weekend Strategy**: Weekend patterns differ from weekdays
3. **Distance-based Pricing**: Strong correlation suggests distance-based pricing optimization
4. **Passenger Optimization**: Multi-passenger rides could be encouraged

## Data Quality
- **Missing Values**: {df.isnull().sum().sum()} (after cleaning)
- **Outliers**: {len(outliers)} records ({len(outliers)/len(df)*100:.1f}%)
- **Data Completeness**: {(1 - df.isnull().sum().sum()/df.size)*100:.1f}%
"""

# Save report
with open("Documents/analysis_report.txt", "w") as f:
    f.write(report)

print("✓ Generated comprehensive analysis report")

print("\n" + "=" * 50)
print("🎉 Analysis Complete!")
print(f"✓ Cleaned data saved to: Data/cleaned/uber_cleaned.csv")
print(f"✓ Enhanced data saved to: Data/enhanced/uber_enhanced.csv")
print(f"✓ Visualizations saved to: powerbi/ directory")
print(f"✓ Analysis report saved to: Documents/analysis_report.txt")
print("=" * 50)

# Display final summary
print(f"\n📊 FINAL SUMMARY:")
print(f"   Records processed: {len(df):,}")
print(f"   Visualizations created: 10")
print(f"   Average fare: ${df['fare_amount'].mean():.2f}")
print(f"   Peak hours identified: 7-9 AM, 5-7 PM")
print(f"   Busiest day: {weekday_rides.idxmax()}")
print(f"   Analysis complete! 🚖")
