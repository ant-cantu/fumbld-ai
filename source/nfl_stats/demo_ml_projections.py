"""
NFL Projections Library - ML Demonstration Script
Shows how to use the ML functionality with real player data

This script demonstrates:
1. Getting individual player projections
2. Bulk projections for multiple players
3. Comparing different scoring systems
4. Training and using ML models
5. Confidence scoring analysis
"""

import sys
from pathlib import Path

# Add the nfl_stats directory to the path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from nfl_projections_library import (
    CSVProjectionsLibrary,
    get_csv_projection,
    bulk_csv_projections,
    train_all_csv_models
)

def demo_individual_projections():
    """Demonstrate individual player projections"""
    print("🎯 Individual Player Projections Demo")
    print("=" * 50)
    
    # Test players from each position
    players = [
        ("Josh Allen", "QB", "Buffalo Bills quarterback"),
        ("Derrick Henry", "RB", "Baltimore Ravens running back"),
        ("Tyreek Hill", "WR", "Miami Dolphins wide receiver"),
        ("Travis Kelce", "TE", "Kansas City Chiefs tight end"),
        ("J.Tucker", "K", "Baltimore Ravens kicker"),
        ("BUF", "DEF", "Buffalo Bills defense")
    ]
    
    for player_name, position, description in players:
        print(f"\n📊 {description}:")
        
        # Get projection using the convenience function
        projection = get_csv_projection(player_name, scoring_system="ppr", use_ml=True)
        
        if projection:
            print(f"   Player: {projection.player_name}")
            print(f"   Position: {projection.position}")
            print(f"   Projected Points: {projection.projected_points:.2f}")
            print(f"   Confidence: {projection.confidence:.1%}")
            print(f"   Week: {projection.week}, Season: {projection.season}")
            
            # Show top scoring categories
            if projection.scoring_breakdown:
                top_categories = sorted(projection.scoring_breakdown.items(), 
                                      key=lambda x: abs(x[1]), reverse=True)[:3]
                print(f"   Top categories: {', '.join([f'{cat}: {pts:.1f}' for cat, pts in top_categories])}")
        else:
            print(f"   ❌ No projection available for {player_name}")

def demo_bulk_projections():
    """Demonstrate bulk projections"""
    print("\n\n📦 Bulk Projections Demo")
    print("=" * 50)
    
    # Fantasy lineup of players
    lineup = [
        "Josh Allen",      # QB
        "Derrick Henry",   # RB1
        "Tyreek Hill",     # WR1
        "Travis Kelce",    # TE
        "J.Tucker"         # K
    ]
    
    print("🏈 Fantasy Lineup Projections (PPR scoring):")
    projections = bulk_csv_projections(lineup, scoring_system="ppr", use_ml=True)
    
    total_points = 0
    for player_name in lineup:
        if player_name in projections:
            proj = projections[player_name]
            print(f"   {proj.position:3s} {player_name:15s}: {proj.projected_points:6.2f} pts ({proj.confidence:.0%})")
            total_points += proj.projected_points
        else:
            print(f"   ??? {player_name:15s}: No projection available")
    
    print(f"\n🎯 Total Projected Points: {total_points:.2f}")

def demo_scoring_systems():
    """Demonstrate different scoring systems"""
    print("\n\n⚖️ Scoring Systems Comparison")
    print("=" * 50)
    
    # Use a player with receptions to show PPR differences
    player_name = "Tyreek Hill"
    scoring_systems = ["standard", "ppr", "half_ppr", "superflex"]
    
    print(f"📊 {player_name} projections across scoring systems:")
    
    for system in scoring_systems:
        projection = get_csv_projection(player_name, scoring_system=system, use_ml=True)
        if projection:
            print(f"   {system.upper():10s}: {projection.projected_points:6.2f} points")
        else:
            print(f"   {system.upper():10s}: No projection available")

def demo_ml_vs_statistical():
    """Compare ML predictions vs statistical averages"""
    print("\n\n🤖 ML vs Statistical Projections")
    print("=" * 50)
    
    lib = CSVProjectionsLibrary(scoring_system="ppr")
    player_name = "Josh Allen"
    
    # Get ML projection
    ml_projection = lib.get_projection(player_name, use_ml=True)
    
    # Get statistical projection (no ML)
    stat_projection = lib.get_projection(player_name, use_ml=False)
    
    if ml_projection and stat_projection:
        print(f"📊 {player_name} Projection Comparison:")
        print(f"   ML Prediction:     {ml_projection.projected_points:6.2f} pts (confidence: {ml_projection.confidence:.0%})")
        print(f"   Statistical Avg:   {stat_projection.projected_points:6.2f} pts (confidence: {stat_projection.confidence:.0%})")
        
        difference = ml_projection.projected_points - stat_projection.projected_points
        print(f"   Difference:        {difference:+6.2f} pts")
        
        if abs(difference) > 1:
            direction = "higher" if difference > 0 else "lower"
            print(f"   🎯 ML prediction is {direction} than statistical average")
    else:
        print("❌ Could not generate both projections for comparison")

def demo_confidence_analysis():
    """Analyze confidence scores across positions"""
    print("\n\n📈 Confidence Score Analysis")
    print("=" * 50)
    
    players_by_position = {
        "QB": ["Josh Allen"],
        "RB": ["Derrick Henry"], 
        "WR": ["Tyreek Hill"],
        "TE": ["Travis Kelce"],
        "K": ["J.Tucker"],
        "DEF": ["BUF"]
    }
    
    print("📊 Confidence scores by position:")
    
    for position, player_list in players_by_position.items():
        confidences = []
        for player in player_list:
            projection = get_csv_projection(player, scoring_system="ppr", use_ml=True)
            if projection:
                confidences.append(projection.confidence)
        
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            print(f"   {position:3s}: {avg_confidence:.1%} average confidence")
        else:
            print(f"   {position:3s}: No data available")

def demo_model_training():
    """Demonstrate ML model training"""
    print("\n\n🧠 ML Model Training Demo")
    print("=" * 50)
    
    print("🤖 Training ML models for all positions...")
    print("   (This may take a minute...)")
    
    # Train models using the convenience function
    train_all_csv_models(force_retrain=True)
    
    print("✅ Model training completed!")
    print("   Models are now available for enhanced projections")

def main():
    """Run all demonstrations"""
    print("🏈 NFL Projections Library - ML Functionality Demo")
    print("=" * 60)
    print("This demo shows the ML capabilities using real 2024 NFL data")
    print("=" * 60)
    
    # Run all demonstrations
    demo_individual_projections()
    demo_bulk_projections()
    demo_scoring_systems()
    demo_ml_vs_statistical()
    demo_confidence_analysis()
    
    # Optional: Train models (commented out to save time)
    # demo_model_training()
    
    print("\n\n🎉 Demo completed!")
    print("\nKey Features Demonstrated:")
    print("✅ Individual player projections with ML")
    print("✅ Bulk projections for fantasy lineups")
    print("✅ Multiple scoring system support")
    print("✅ ML vs statistical comparison")
    print("✅ Confidence score analysis")
    print("✅ Real 2024 NFL data integration")
    
    print("\nTo use this library in your own code:")
    print("```python")
    print("from nfl_projections_library import get_csv_projection")
    print("projection = get_csv_projection('Josh Allen', scoring_system='ppr')")
    print("print(f'{projection.player_name}: {projection.projected_points:.2f} pts')")
    print("```")

if __name__ == "__main__":
    main()
