# NFL Projections Library - ML Testing

This directory contains comprehensive tests for the Machine Learning functionality of the NFL Projections Library using real player data from CSV files.

## Test Files

### `test_ml_projections.py`
A comprehensive test suite that validates all ML functionality:

- **Library Initialization**: Tests different scoring systems
- **CSV Data Loading**: Validates data import from CSV files
- **Player Stats Retrieval**: Tests finding players by name and position
- **Fantasy Points Calculation**: Validates scoring across different systems
- **Feature Engineering**: Tests ML feature preparation
- **ML Model Training**: Trains and validates models for all positions
- **Player Projections**: Tests projection generation with real players
- **Bulk Projections**: Tests multiple player projections at once
- **Scoring System Differences**: Validates PPR vs Standard scoring
- **Confidence Scoring**: Tests confidence calculation algorithms

### `demo_ml_projections.py`
A demonstration script showing practical usage:

- Individual player projections
- Bulk fantasy lineup projections  
- Scoring system comparisons
- ML vs statistical projection comparison
- Confidence score analysis

## Test Players Used

The tests use these real NFL players from the 2024 CSV data:

- **QB**: Josh Allen (Buffalo Bills)
- **RB**: Derrick Henry (Baltimore Ravens)
- **WR**: Tyreek Hill (Miami Dolphins)  
- **TE**: Travis Kelce (Kansas City Chiefs)
- **K**: Justin Tucker (Baltimore Ravens) - Listed as "J.Tucker" in CSV
- **DEF**: Buffalo Bills Defense - Listed as "BUF" in CSV

## Running the Tests

### Prerequisites
Ensure you have the required Python packages:
```bash
pip install pandas numpy scikit-learn
```

### Run the Test Suite
```bash
python test_ml_projections.py
```

### Run the Demo
```bash
python demo_ml_projections.py
```

## Expected Test Results

When all tests pass, you should see:
- ✅ 10/10 tests passing
- 100% success rate
- All ML models trained successfully
- Realistic projection values for all players
- Confidence scores between 75-98%

## Sample Output

```
🧪 Starting NFL Projections Library ML Test Suite
📅 Test run date: 2025-08-01 20:28:16

✅ PASSED - Library Initialization
✅ PASSED - CSV Data Loading (5597 weekly records, 570 defense, 567 kickers)
✅ PASSED - Player Stats Retrieval (Found 6/6 players)
✅ PASSED - Fantasy Points Calculation
✅ PASSED - Feature Engineering
✅ PASSED - ML Model Training (Trained 6/6 models)
✅ PASSED - Player Projections (Generated 6/6 projections)
✅ PASSED - Bulk Projections
✅ PASSED - Scoring System Differences
✅ PASSED - Confidence Scoring

🎉 All tests passed! The ML functionality is working correctly.
```

## Key Features Tested

### Machine Learning Models
- **RandomForestRegressor**: Primary model for most positions
- **GradientBoostingRegressor**: Alternative ensemble method
- **LinearRegression**: Baseline comparison model
- **Cross-validation**: 5-fold CV for model selection
- **Feature scaling**: StandardScaler for input normalization

### Scoring Systems
- **Standard**: No PPR, standard fantasy scoring
- **PPR**: Full point per reception
- **Half PPR**: 0.5 points per reception  
- **Superflex**: Enhanced QB scoring (6pt passing TDs)

### Data Sources
- **Weekly Stats**: Player performance by week
- **Defense Stats**: Team defense statistics
- **Kicker Stats**: Field goal and extra point data
- **Injury Data**: Player injury status by week

### Confidence Factors
- Games played (more games = higher confidence)
- Position-specific predictability 
- Data quality assessment
- ML model agreement with statistical averages
- Season progression bonus

## Troubleshooting

### Common Issues

1. **"No CSV data available"**
   - Ensure CSV files exist in the `data/` directory
   - Check file permissions

2. **"ML not available"**
   - Install scikit-learn: `pip install scikit-learn`
   - Check Python environment

3. **"Player not found"**
   - Verify player name spelling matches CSV data
   - Check position parameter
   - Some players may use abbreviated names (e.g., "J.Tucker")

4. **"Insufficient data for training"**
   - Normal for some positions with limited data
   - Models will skip training but statistical projections still work

### Debug Mode

Enable debug prints in the library:
```python
# In nfl_projections_library.py
DEBUG_PRINTS = True
```

This will show detailed information about:
- Data loading progress
- Player search results  
- Model training status
- Projection calculations

## Integration with Main Application

The test validates that the library can be imported and used in the main Flask application:

```python
from nfl_stats.nfl_projections_library import get_csv_projection

# Get a projection
projection = get_csv_projection("Josh Allen", scoring_system="ppr")
print(f"{projection.player_name}: {projection.projected_points:.2f} pts")
```

This ensures the ML functionality integrates seamlessly with the existing fumbld-ai application architecture.
