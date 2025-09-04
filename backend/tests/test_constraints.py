"""
Test SF planning constraints against real scenarios
"""

import pytest
from app.core.constraints import SFPlanningValidator, SFZoneType


class TestSFPlanningValidator:
    
    def setup_method(self):
        self.validator = SFPlanningValidator()
    
    def test_marina_district_zoning_limits(self):
        """Test Marina District (RH-1) zoning constraints"""
        # Typical Marina lot: 25x100 = 2,500 sq ft
        is_valid, violations = self.validator.validate_zoning_proposal(
            zone_type=SFZoneType.RH_1,
            proposed_far=0.8,  # At the limit
            proposed_height_ft=40,  # At the limit  
            lot_area_sf=2500,
            num_units=1
        )
        
        assert is_valid == True
        assert len([v for v in violations if v.severity == "error"]) == 0
    
    def test_marina_overlimit_violations(self):
        """Test violations when exceeding Marina limits"""
        is_valid, violations = self.validator.validate_zoning_proposal(
            zone_type=SFZoneType.RH_1,
            proposed_far=1.5,  # Too high
            proposed_height_ft=60,  # Too tall
            lot_area_sf=2500,
            num_units=1
        )
        
        assert is_valid == False
        error_violations = [v for v in violations if v.severity == "error"]
        assert len(error_violations) == 2  # FAR + Height violations
        
        # Check specific violation details
        far_violation = next((v for v in violations if "Floor Area Ratio" in v.rule), None)
        assert far_violation is not None
        assert far_violation.max_allowed == 0.8
    
    def test_hayes_valley_transit_oriented(self):
        """Test Hayes Valley (NCT-3) allows higher density"""
        is_valid, violations = self.validator.validate_zoning_proposal(
            zone_type=SFZoneType.NCT_3,
            proposed_far=3.0,  # Higher density allowed
            proposed_height_ft=55,
            lot_area_sf=3000,
            num_units=15
        )
        
        # Should be valid with warnings for ground floor commercial
        error_violations = [v for v in violations if v.severity == "error"] 
        assert len(error_violations) == 0
        
        # Should have inclusionary housing warning
        inclusionary_warning = next((v for v in violations if "Inclusionary" in v.rule), None)
        assert inclusionary_warning is not None
    
    def test_mission_high_density(self):
        """Test Mission District (NCT-4) allows highest density"""
        is_valid, violations = self.validator.validate_zoning_proposal(
            zone_type=SFZoneType.NCT_4,
            proposed_far=4.0,
            proposed_height_ft=85,
            lot_area_sf=5000,
            num_units=25
        )
        
        error_violations = [v for v in violations if v.severity == "error"]
        assert len(error_violations) == 0  # Should be valid
        
        # Check affordable housing requirement is higher for Mission
        inclusionary_warning = next((v for v in violations if "Inclusionary" in v.rule), None)
        assert inclusionary_warning is not None
        # NCT-4 requires 25% affordable
        expected_affordable = 25 * 0.25  # 6.25 -> ~6 units
        assert inclusionary_warning.max_allowed >= 6
    
    def test_realistic_unit_estimation(self):
        """Test unit estimation for different neighborhoods"""
        
        # Marina: Large lot, low density
        marina_units = self.validator.estimate_realistic_units(
            SFZoneType.RH_1, 
            lot_area_sf=5000
        )
        assert marina_units["total_units"] <= 3  # Should be very low
        
        # Hayes Valley: Medium density
        hayes_units = self.validator.estimate_realistic_units(
            SFZoneType.NCT_3,
            lot_area_sf=5000  
        )
        assert 10 <= hayes_units["total_units"] <= 20
        assert hayes_units["affordable_units"] > 0
        
        # Mission: High density
        mission_units = self.validator.estimate_realistic_units(
            SFZoneType.NCT_4,
            lot_area_sf=5000
        )
        assert mission_units["total_units"] > hayes_units["total_units"]
        assert mission_units["affordable_units"] > hayes_units["affordable_units"]
    
    def test_neighborhood_zoning_mapping(self):
        """Test neighborhood to zoning mapping"""
        assert self.validator.get_neighborhood_zoning("marina") == SFZoneType.RH_1
        assert self.validator.get_neighborhood_zoning("hayes_valley") == SFZoneType.NCT_3  
        assert self.validator.get_neighborhood_zoning("mission") == SFZoneType.NCT_4
        
        # Test case-insensitive
        assert self.validator.get_neighborhood_zoning("MARINA") == SFZoneType.RH_1
    
    def test_zoning_upzone_suggestions(self):
        """Test upzoning suggestions to meet unit targets"""
        
        # Small lot targeting 50 units - should suggest NCT-4
        suggested_zone = self.validator.suggest_zoning_upzone(
            current_zone=SFZoneType.RH_1,
            target_units=50,
            lot_area_sf=5000
        )
        
        assert suggested_zone == SFZoneType.NCT_4
        
        # Impossible target - should return None
        impossible_zone = self.validator.suggest_zoning_upzone(
            current_zone=SFZoneType.RH_1,
            target_units=500,  # Way too many units
            lot_area_sf=2000   # Small lot
        )
        
        assert impossible_zone is None
    
    def test_real_world_scenario_marina_upzone(self):
        """Test realistic Marina upzoning scenario"""
        # Scenario: "Add affordable housing near Marina transit"
        # Typical Marina parcel: 3000 sq ft
        
        # Current zoning allows very few units
        current_units = self.validator.estimate_realistic_units(
            SFZoneType.RH_1, 3000
        )
        assert current_units["total_units"] <= 2
        
        # Upzone to RM-2 to get ~8-10 units
        upzoned_units = self.validator.estimate_realistic_units(
            SFZoneType.RM_2, 3000
        )
        assert 6 <= upzoned_units["total_units"] <= 12
        assert upzoned_units["affordable_units"] >= 1
        
        # Validate the upzoned proposal
        is_valid, violations = self.validator.validate_zoning_proposal(
            zone_type=SFZoneType.RM_2,
            proposed_far=2.5,
            proposed_height_ft=65,
            lot_area_sf=3000,
            num_units=upzoned_units["total_units"]
        )
        
        error_violations = [v for v in violations if v.severity == "error"]
        assert len(error_violations) == 0  # Should be feasible


if __name__ == "__main__":
    pytest.main([__file__, "-v"])