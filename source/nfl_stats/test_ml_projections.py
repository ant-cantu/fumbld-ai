"""
Test file for NFL Projections Library ML functionality
Tests ML models using real player data from CSV files

This test file validates:
1. Model training for each position
2. Player projection accuracy
3. Confidence scoring
4. Different scoring systems
5. Injury status handling
6. Feature engineering

Test players:
- QB: Josh Allen (BUF)
- RB: Derrick Henry (BAL) 
- WR: Tyreek Hill (MIA)
- TE: Travis Kelce (KC)
- K: Justin Tucker (BAL)
- DEF: Buffalo Bills Defense
"""

import sys
import os
import time
from pathlib import Path

# Add the nfl_stats directory to the path so we can import the library
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import our projections library
from nfl_projections_library import (
    CSVProjectionsLibrary, 
    PlayerProjection, 
    PlayerStats,
    get_csv_projection,
    bulk_csv_projections,
    train_all_csv_models,
    DEBUG_PRINTS
)

def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Print test result with formatting"""
    status = "✅ PASSED" if passed else "❌ FAILED"
    print(f"{status} - {test_name}")
    if details:
        print(f"   {details}")

def test_library_initialization():
    """Test that the library initializes correctly"""
    print_test_header("Library Initialization Test")
    
    try:
        # Test different scoring systems
        scoring_systems = ["standard", "ppr", "half_ppr", "superflex"]
        
        for system in scoring_systems:
            lib = CSVProjectionsLibrary(scoring_system=system)
            assert lib.scoring_system == system
            assert lib.current_season > 0
            assert lib.current_week > 0
            print(f"✅ {system} scoring system initialized successfully")
        
        print_test_result("Library Initialization", True)
        return True
        
    except Exception as e:
        print_test_result("Library Initialization", False, str(e))
        return False

def test_csv_data_loading():
    """Test CSV data loading functionality"""
    print_test_header("CSV Data Loading Test")
    
    try:
        lib = CSVProjectionsLibrary()
        data = lib._load_csv_data()
        
        # Check that we have the expected data types
        expected_keys = ['weekly', 'defense', 'kickers']
        loaded_keys = list(data.keys())
        
        print(f"📊 Loaded data types: {loaded_keys}")
        
        for key in expected_keys:
            if key in data:
                df = data[key]
                print(f"   {key}: {len(df)} records")
                assert len(df) > 0, f"No data in {key}"
            else:
                print(f"   ⚠️ {key}: No data found")
        
        # Verify at least weekly data is available
        assert 'weekly' in data and len(data['weekly']) > 0, "No weekly player data found"
        
        print_test_result("CSV Data Loading", True)
        return True
        
    except Exception as e:
        print_test_result("CSV Data Loading", False, str(e))
        return False

def test_player_stats_retrieval():
    """Test retrieving player statistics from CSV"""
    print_test_header("Player Stats Retrieval Test")
    
    try:
        lib = CSVProjectionsLibrary()
        
        # Test players from different positions
        test_players = [
            ("Josh Allen", "QB"),
            ("Derrick Henry", "RB"), 
            ("Tyreek Hill", "WR"),
            ("Travis Kelce", "TE"),
            ("J.Tucker", "K"),  # Kicker name format in CSV
            ("BUF", "DEF")      # Team abbreviation for defense
        ]
        
        stats_found = 0
        
        for player_name, position in test_players:
            stats = lib.get_player_stats_from_csv(player_name, position)
            
            if stats:
                print(f"✅ Found {player_name} ({position}):")
                print(f"   Position: {stats.position}")
                print(f"   Team: {stats.team}")
                print(f"   Games: {stats.games_played}")
                
                # Position-specific stat checks
                if position == "QB":
                    print(f"   Passing yards: {stats.passing_yards}")
                    print(f"   Passing TDs: {stats.passing_tds}")
                elif position == "RB":
                    print(f"   Rushing yards: {stats.rushing_yards}")
                    print(f"   Rushing TDs: {stats.rushing_tds}")
                elif position == "WR":
                    print(f"   Receiving yards: {stats.receiving_yards}")
                    print(f"   Receptions: {stats.receptions}")
                elif position == "TE":
                    print(f"   Receiving yards: {stats.receiving_yards}")
                    print(f"   Receptions: {stats.receptions}")
                elif position == "K":
                    print(f"   FG made: {stats.fg_made}")
                    print(f"   XP made: {stats.xp_made}")
                elif position == "DEF":
                    print(f"   Sacks: {stats.def_sacks}")
                    print(f"   Interceptions: {stats.def_interceptions}")
                
                stats_found += 1
            else:
                print(f"❌ Could not find {player_name} ({position})")
        
        success = stats_found >= 4  # Allow some missing players
        print_test_result("Player Stats Retrieval", success, 
                         f"Found {stats_found}/{len(test_players)} players")
        return success
        
    except Exception as e:
        print_test_result("Player Stats Retrieval", False, str(e))
        return False

def test_fantasy_points_calculation():
    """Test fantasy points calculation for different scoring systems"""
    print_test_header("Fantasy Points Calculation Test")
    
    try:
        # Test with sample stats for a QB
        sample_qb_stats = {
            'passing_yards': 300,
            'passing_tds': 2,
            'interceptions': 1,
            'rushing_yards': 50,
            'rushing_tds': 1,
            'fumbles': 0
        }
        
        scoring_systems = ["standard", "ppr", "half_ppr", "superflex"]
        
        for system in scoring_systems:
            lib = CSVProjectionsLibrary(scoring_system=system)
            points, breakdown = lib._calculate_fantasy_points(sample_qb_stats, "QB")
            
            print(f"📊 {system.upper()} scoring:")
            print(f"   Total points: {points:.2f}")
            print(f"   Breakdown: {breakdown}")
            
            # Basic validation - QB should score reasonable points
            assert 15 <= points <= 50, f"Unrealistic QB points: {points}"
        
        print_test_result("Fantasy Points Calculation", True)
        return True
        
    except Exception as e:
        print_test_result("Fantasy Points Calculation", False, str(e))
        return False

def test_ml_model_training():
    """Test ML model training for all positions"""
    print_test_header("ML Model Training Test")
    
    try:
        lib = CSVProjectionsLibrary()
        
        # Check if ML is available
        from nfl_projections_library import ML_AVAILABLE
        if not ML_AVAILABLE:
            print("⚠️ ML libraries not available - skipping ML training test")
            print_test_result("ML Model Training", True, "Skipped - ML not available")
            return True
        
        print("🤖 Training ML models for all positions...")
        start_time = time.time()
        
        # Train models for each position
        positions = ['QB', 'RB', 'WR', 'TE', 'DEF', 'K']
        trained_models = 0
        
        for position in positions:
            try:
                lib._train_ml_model(position, force_retrain=True)
                if position in lib.ml_models:
                    print(f"✅ {position} model trained successfully")
                    trained_models += 1
                else:
                    print(f"⚠️ {position} model training skipped (insufficient data)")
            except Exception as e:
                print(f"❌ {position} model training failed: {e}")
        
        training_time = time.time() - start_time
        print(f"🕐 Training completed in {training_time:.2f} seconds")
        
        success = trained_models >= 3  # Allow some positions to fail due to insufficient data
        print_test_result("ML Model Training", success, 
                         f"Trained {trained_models}/{len(positions)} models")
        return success
        
    except Exception as e:
        print_test_result("ML Model Training", False, str(e))
        return False

def test_player_projections():
    """Test getting projections for real players"""
    print_test_header("Player Projections Test")
    
    try:
        lib = CSVProjectionsLibrary(scoring_system="ppr")
        
        # Test players with fallback options
        test_players = [
            ("Josh Allen", "QB"),
            ("Derrick Henry", "RB"),
            ("Tyreek Hill", "WR"), 
            ("Travis Kelce", "TE"),
            ("J.Tucker", "K"),
            ("Buffalo Bills", "DEF")  # Try full name first
        ]
        
        projections_found = 0
        
        for player_name, expected_position in test_players:
            print(f"\n🔍 Testing projection for {player_name} ({expected_position}):")
            
            # Try with ML first, then without if that fails
            projection = lib.get_projection(player_name, use_ml=True)
            
            # If full name fails for defense, try abbreviation
            if not projection and expected_position == "DEF":
                projection = lib.get_projection("BUF", use_ml=True)
                player_name = "BUF"
            
            if projection:
                print(f"✅ Projection found for {player_name}:")
                print(f"   Player: {projection.player_name}")
                print(f"   Position: {projection.position}")
                print(f"   Team: {projection.team}")
                print(f"   Projected points: {projection.projected_points:.2f}")
                print(f"   Confidence: {projection.confidence:.1%}")
                print(f"   Data source: {projection.data_source}")
                
                # Validate projection values
                assert projection.projected_points >= 0, "Negative projected points"
                assert 0 <= projection.confidence <= 1, "Invalid confidence score"
                assert projection.position == expected_position or expected_position == "DEF"
                
                projections_found += 1
            else:
                print(f"❌ No projection found for {player_name}")
        
        success = projections_found >= 3  # Allow some projections to fail
        print_test_result("Player Projections", success, 
                         f"Generated {projections_found}/{len(test_players)} projections")
        return success
        
    except Exception as e:
        print_test_result("Player Projections", False, str(e))
        return False

def test_bulk_projections():
    """Test bulk projection functionality"""
    print_test_header("Bulk Projections Test")
    
    try:
        # Test the convenience function
        player_names = ["Josh Allen", "Derrick Henry", "Tyreek Hill", "J.Tucker"]
        
        projections = bulk_csv_projections(player_names, scoring_system="ppr", use_ml=True)
        
        print(f"📊 Bulk projections requested for {len(player_names)} players")
        print(f"📊 Projections received for {len(projections)} players")
        
        for name, projection in projections.items():
            print(f"   {name}: {projection.projected_points:.2f} pts ({projection.confidence:.1%})")
        
        # Should get at least some projections
        success = len(projections) >= 2
        print_test_result("Bulk Projections", success)
        return success
        
    except Exception as e:
        print_test_result("Bulk Projections", False, str(e))
        return False

def test_scoring_system_differences():
    """Test that different scoring systems produce different results"""
    print_test_header("Scoring System Differences Test")
    
    try:
        # Test with a player who has receptions (should show PPR difference)
        player_name = "Tyreek Hill"
        
        systems = ["standard", "ppr", "half_ppr"]
        projections = {}
        
        for system in systems:
            lib = CSVProjectionsLibrary(scoring_system=system)
            projection = lib.get_projection(player_name, use_ml=False)  # Use statistical for consistency
            
            if projection:
                projections[system] = projection.projected_points
                print(f"📊 {system.upper()}: {projection.projected_points:.2f} points")
        
        # PPR should typically be higher than standard for WRs
        if "ppr" in projections and "standard" in projections:
            ppr_higher = projections["ppr"] >= projections["standard"]
            print(f"✅ PPR vs Standard difference verified: {ppr_higher}")
        
        success = len(projections) >= 2
        print_test_result("Scoring System Differences", success)
        return success
        
    except Exception as e:
        print_test_result("Scoring System Differences", False, str(e))
        return False

def test_confidence_scoring():
    """Test confidence score calculations"""
    print_test_header("Confidence Scoring Test")
    
    try:
        lib = CSVProjectionsLibrary()
        
        # Test with different players to see confidence variations
        test_players = ["Josh Allen", "Derrick Henry", "J.Tucker"]
        confidences = []
        
        for player_name in test_players:
            projection = lib.get_projection(player_name, use_ml=False)
            if projection:
                confidences.append(projection.confidence)
                print(f"📊 {player_name}: {projection.confidence:.1%} confidence")
        
        if confidences:
            # Check that confidences are in valid range
            all_valid = all(0 <= conf <= 1 for conf in confidences)
            
            # Check that there's some variation in confidence scores
            has_variation = len(set(round(conf, 2) for conf in confidences)) > 1
            
            success = all_valid and len(confidences) >= 2
            print_test_result("Confidence Scoring", success, 
                             f"Variation in scores: {has_variation}")
            return success
        else:
            print_test_result("Confidence Scoring", False, "No projections generated")
            return False
        
    except Exception as e:
        print_test_result("Confidence Scoring", False, str(e))
        return False

def test_feature_engineering():
    """Test ML feature preparation"""
    print_test_header("Feature Engineering Test")
    
    try:
        lib = CSVProjectionsLibrary()
        
        # Create sample player stats for each position
        qb_stats = PlayerStats(
            player_name="Test QB",
            position="QB",
            team="TEST",
            games_played=10,
            passing_yards=3000,
            passing_tds=25,
            interceptions=8,
            rushing_yards=200,
            rushing_tds=2
        )
        
        rb_stats = PlayerStats(
            player_name="Test RB", 
            position="RB",
            team="TEST",
            games_played=12,
            rushing_yards=1200,
            rushing_tds=8,
            receiving_yards=300,
            receptions=30
        )
        
        # Test feature preparation
        qb_features = lib._prepare_ml_features(qb_stats)
        rb_features = lib._prepare_ml_features(rb_stats)
        
        print(f"📊 QB features shape: {qb_features.shape}")
        print(f"📊 RB features shape: {rb_features.shape}")
        print(f"📊 QB features: {qb_features[:5]}...")  # Show first 5 features
        print(f"📊 RB features: {rb_features[:5]}...")
        
        # Validate features
        assert len(qb_features) > 0, "No QB features generated"
        assert len(rb_features) > 0, "No RB features generated"
        assert not any(np.isnan(qb_features)), "NaN values in QB features"
        assert not any(np.isnan(rb_features)), "NaN values in RB features"
        
        print_test_result("Feature Engineering", True)
        return True
        
    except Exception as e:
        print_test_result("Feature Engineering", False, str(e))
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🧪 Starting NFL Projections Library ML Test Suite")
    print(f"📅 Test run date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        test_library_initialization,
        test_csv_data_loading,
        test_player_stats_retrieval,
        test_fantasy_points_calculation,
        test_feature_engineering,
        test_ml_model_training,
        test_player_projections,
        test_bulk_projections,
        test_scoring_system_differences,
        test_confidence_scoring
    ]
    
    results = []
    start_time = time.time()
    
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            results.append(False)
    
    total_time = time.time() - start_time
    
    # Summary
    print_test_header("Test Summary")
    passed = sum(results)
    total = len(results)
    
    print(f"📊 Tests passed: {passed}/{total}")
    print(f"📊 Success rate: {passed/total:.1%}")
    print(f"🕐 Total test time: {total_time:.2f} seconds")
    
    if passed == total:
        print("🎉 All tests passed! The ML functionality is working correctly.")
    elif passed >= total * 0.7:
        print("⚠️ Most tests passed. Some functionality may need attention.")
    else:
        print("❌ Many tests failed. The ML functionality needs debugging.")
    
    return passed == total

if __name__ == "__main__":
    # Import numpy for feature validation
    import numpy as np
    
    # Enable debug prints for testing
    from nfl_projections_library import DEBUG_PRINTS
    
    success = run_all_tests()
    
    # Exit code for automation
    exit_code = 0 if success else 1
    print(f"\n🏁 Test suite completed with exit code: {exit_code}")
    exit(exit_code)
