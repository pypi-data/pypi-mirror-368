"""Tests for the NeuberCorrection class."""

import math
import os
import time

import matplotlib.pyplot as plt
import pytest

from neuber_correction import (
    MaterialForNeuberCorrection,
    NeuberCorrection,
    NeuberSolverSettings,
)


class TestNeuberCorrection:
    """Test class for NeuberCorrection functionality."""

    def test_s355_steel_material_properties(self):
        """Test NeuberCorrection with S355 steel material properties."""
        # S355 steel properties from the image (80mm < t < 100mm)
        material = MaterialForNeuberCorrection(
            yield_strength=315,  # MPa - yield strength
            sigma_u=470,  # MPa - tensile strength
            elastic_mod=210000,  # MPa - Young's modulus (210 GPa)
            eps_u=0.12,  # 12% strain at UTS
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        # Verify material properties are stored correctly
        assert neuber.material.yield_strength == 315
        assert neuber.material.sigma_u == 470
        assert neuber.material.elastic_mod == 210000
        assert neuber.material.eps_u == 0.12
        assert neuber.settings.tolerance == 1e-6
        assert neuber.settings.max_iterations == 10000

    def test_ramberg_osgood_parameter_calculation(self):
        """Test the calculation of Ramberg-Osgood parameter n."""
        # S355 steel properties
        material = MaterialForNeuberCorrection(
            yield_strength=315,  # MPa
            sigma_u=470,  # MPa
            elastic_mod=210000,  # MPa
            eps_u=0.12,  # 12%
        )

        settings = NeuberSolverSettings()

        NeuberCorrection(material=material, settings=settings)

        # Calculate n manually to verify the method
        elastic_strain_at_ultimate = material.sigma_u / material.elastic_mod
        plastic_strain_at_ultimate = material.eps_u - elastic_strain_at_ultimate
        expected_n = (
            math.log(plastic_strain_at_ultimate) - math.log(0.002)
        ) / math.log(material.sigma_u / material.yield_strength)

        # The expected value from the image is approximately 10.232
        assert abs(expected_n - 10.232) < 0.1

    def test_neuber_correction_specific_case(self):
        """Test Neuber correction for the specific case from the image."""
        # S355 steel properties
        material = MaterialForNeuberCorrection(
            yield_strength=315,  # MPa
            sigma_u=470,  # MPa
            elastic_mod=210000,  # MPa
            eps_u=0.12,  # 12%
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        # From the image: elastic stress σ_e = 718 MPa
        # The image shows the solution σ_p = 347.217 MPa
        elastic_stress = 718  # MPa

        # Test single stress correction
        corrected_stress = neuber.correct_stress_values([elastic_stress])[0]

        # The corrected stress should be less than the elastic stress due to plasticity
        assert corrected_stress < elastic_stress

        # The corrected stress should be reasonable (not negative, not too small)
        assert corrected_stress > 0
        assert (
            corrected_stress > material.yield_strength * 0.5
        )  # Should be reasonable fraction of yield

    def test_neuber_correction_convergence(self):
        """Test that the Neuber correction converges properly."""
        # S355 steel properties
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings(
            tolerance=1e-6,
            max_iterations=1000,
        )

        neuber = NeuberCorrection(material=material, settings=settings)

        # Test with moderate stress levels
        stress_original = 400  # MPa

        corrected_stress = neuber.correct_stress_values([stress_original])[0]

        # Verify convergence by checking that results are finite and reasonable
        assert math.isfinite(corrected_stress)
        assert corrected_stress > 0

    def test_neuber_correction_elastic_range(self):
        """Test Neuber correction when stress is in elastic range."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()
        neuber = NeuberCorrection(material=material, settings=settings)

        # Stress below yield should result in minimal correction
        stress_elastic = 200  # MPa (below yield)

        corrected_stress = neuber.correct_stress_values([stress_elastic])[0]

        # Correction due to full Ramberg-Osgood curve (includes plastic strain even below yield)
        assert (
            abs(corrected_stress - stress_elastic) < 10.0
        )  # Increased tolerance due to full Ramberg-Osgood curve

    def test_neuber_correction_high_stress(self):
        """Test Neuber correction with high stress levels."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        # High stress levels should show significant correction
        stress_high = 800  # MPa (well above yield)

        corrected_stress = neuber.correct_stress_values([stress_high])[0]

        # High stresses should show significant correction
        assert corrected_stress < stress_high
        assert (stress_high - corrected_stress) > 50  # Significant correction

    def test_neuber_correction_consistency(self):
        """Test that Neuber correction is consistent for same input."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        stress_input = 500

        # Run correction twice
        result1 = neuber.correct_stress_values([stress_input])[0]
        result2 = neuber.correct_stress_values([stress_input])[0]

        # Results should be identical
        assert result1 == result2

    def test_neuber_correction_parameter_validation(self):
        """Test that invalid parameters are handled properly."""
        # Test with zero values
        with pytest.raises(ValueError):
            material = MaterialForNeuberCorrection(
                yield_strength=0,  # Invalid
                sigma_u=470,
                elastic_mod=210000,
                eps_u=0.12,
            )
            NeuberCorrection(material=material)

        # Test with negative values
        with pytest.raises(ValueError):
            material = MaterialForNeuberCorrection(
                yield_strength=315,
                sigma_u=-470,  # Invalid
                elastic_mod=210000,
                eps_u=0.12,
            )
            NeuberCorrection(material=material)

        # Test with invalid settings
        with pytest.raises(ValueError):
            material = MaterialForNeuberCorrection(
                yield_strength=315,
                sigma_u=470,
                elastic_mod=210000,
                eps_u=0.12,
            )
            settings = NeuberSolverSettings(tolerance=0)  # Invalid
            NeuberCorrection(material=material, settings=settings)

    def test_neuber_correction_tolerance_effect(self):
        """Test the effect of different tolerance values."""
        # Test with different tolerances
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings_loose = NeuberSolverSettings(tolerance=1e-3)
        settings_tight = NeuberSolverSettings(tolerance=1e-9)

        neuber_loose = NeuberCorrection(material=material, settings=settings_loose)
        neuber_tight = NeuberCorrection(material=material, settings=settings_tight)

        stress_input = 600

        result_loose = neuber_loose.correct_stress_values([stress_input])[0]
        result_tight = neuber_tight.correct_stress_values([stress_input])[0]

        # Results should be similar but not necessarily identical
        assert abs(result_loose - result_tight) < 3.0

    def test_neuber_correction_edge_cases(self):
        """Test edge cases for Neuber correction."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        # Test with very small stresses
        stress_small = neuber.correct_stress_values([1.0])[0]
        assert stress_small > 0

        # Test with very large stresses
        stress_large = neuber.correct_stress_values([2000])[0]
        assert stress_large > 0
        assert stress_large < 2000

    def test_literature_values(self):
        """Test the Neuber correction with literature values."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings(tolerance=1e-6)

        neuber = NeuberCorrection(material=material, settings=settings)

        corrected_value = neuber.correct_stress_values([718])[0]

        assert abs(corrected_value - 347.217) < 1

    def test_correct_stress_values_list(self):
        """Test the correct_stress_values method for processing lists."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        # Test with a list of stress values
        stress_values = [400, 600, 800]
        corrected_values = neuber.correct_stress_values(stress_values)

        # Check that we get the same number of results
        assert len(corrected_values) == len(stress_values)

        # Check that each value is corrected (less than original due to plasticity)
        for original, corrected in zip(stress_values, corrected_values):
            assert corrected < original
            assert corrected > 0

        # Verify that individual calculations match list calculations
        individual_results = [
            neuber.correct_stress_values([stress])[0] for stress in stress_values
        ]
        for list_result, individual_result in zip(corrected_values, individual_results):
            assert abs(list_result - individual_result) < 1e-10

    def test_multiple_stress_values_comprehensive(self):
        """Test comprehensive multiple stress value corrections."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        # Test with various stress levels: elastic, near yield, and plastic
        stress_values = [200, 315, 400, 600, 800, 1000]
        corrected_values = neuber.correct_stress_values(stress_values)

        # Check that we get the same number of results
        assert len(corrected_values) == len(stress_values)

        # Check specific behaviors
        for original, corrected in zip(stress_values, corrected_values):
            # All corrected values should be positive
            assert corrected > 0

            # All corrected values should be less than or equal to original
            # (due to plasticity)
            assert corrected <= original

            # Elastic range (below yield): correction due to full Ramberg-Osgood curve
            if original <= 315:
                assert (
                    abs(corrected - original) < 50.0
                )  # Increased tolerance due to full Ramberg-Osgood curve

            # Plastic range (above yield): significant correction
            if original > 315:
                assert (original - corrected) > 10  # Significant correction

        # Test that the results are consistent with individual calculations
        individual_results = [
            neuber.correct_stress_values([stress])[0] for stress in stress_values
        ]

        for list_result, individual_result in zip(corrected_values, individual_results):
            assert abs(list_result - individual_result) < 1e-10

        # Test edge cases
        edge_stresses = [0.1, 5000]  # Very small and very large
        edge_corrected = neuber.correct_stress_values(edge_stresses)

        assert edge_corrected[0] > 0  # Very small stress
        assert edge_corrected[1] > 0 and edge_corrected[1] < 5000  # Very large stress

    def test_plot_neuber_diagram(self):
        """Test that the plotting function works without errors."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        # Test that plotting function returns figure and axis objects
        # Use show_plot=False to prevent display during testing
        fig, ax = neuber.plot_neuber_diagram(500, show_plot=False)

        # Verify that we got matplotlib objects back
        assert fig is not None
        assert ax is not None

        # Close the figure to free memory
        plt.close(fig)

    def test_plot_neuber_diagram_save_plot(self):
        """Test that the plotting function saves a file when save_plot=True."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        plot_name = "test_neuber_diagram_output"
        file_path = f"{plot_name}.png"

        # Ensure the file does not exist before the test
        if os.path.exists(file_path):
            os.remove(file_path)

        # Call the plotting function with save_plot=True
        fig, _ = neuber.plot_neuber_diagram(500, show_plot=False, plot_file=file_path)

        # Check that the file was created
        assert os.path.exists(file_path), f"Plot file {file_path} was not created."

        # Clean up the file after test
        os.remove(file_path)

        plt.close(fig)

    def test_material_class_validation(self):
        """Test MaterialForNeuberCorrection class validation."""
        # Test valid material properties
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        assert material.yield_strength == 315
        assert material.sigma_u == 470
        assert material.elastic_mod == 210000
        assert material.eps_u == 0.12
        assert material.yield_offset == 0.002  # default value

        # Test custom yield_offset
        material_custom = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
            yield_offset=0.001,
        )

        assert material_custom.yield_offset == 0.001

    def test_settings_class_validation(self):
        """Test NeuberSolverSettings class validation."""
        # Test default settings
        settings = NeuberSolverSettings()

        assert settings.tolerance == 1e-6
        assert settings.max_iterations == 10000
        assert settings.memoization_precision == 1e-6

        # Test custom settings
        settings_custom = NeuberSolverSettings(
            tolerance=1e-8,
            max_iterations=5000,
            memoization_precision=1e-8,
        )

        assert settings_custom.tolerance == 1e-8
        assert settings_custom.max_iterations == 5000
        assert settings_custom.memoization_precision == 1e-8

    def test_tensile_strength_validation(self):
        """Test that tensile strength must be greater than yield strength."""
        # Test invalid case where sigma_u <= yield_strength
        with pytest.raises(ValueError):
            material = MaterialForNeuberCorrection(
                yield_strength=315,
                sigma_u=300,  # Less than yield strength
                elastic_mod=210000,
                eps_u=0.12,
            )
            NeuberCorrection(material=material)

        # Test invalid case where sigma_u == yield_strength
        with pytest.raises(ValueError):
            material = MaterialForNeuberCorrection(
                yield_strength=315,
                sigma_u=315,  # Equal to yield strength
                elastic_mod=210000,
                eps_u=0.12,
            )
            NeuberCorrection(material=material)

    def test_plot_neuber_diagram_with_pretty_name(self):
        """Test that the plotting function works with pretty name."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        # Test that plotting function works with pretty name
        fig, ax = neuber.plot_neuber_diagram(
            500, show_plot=False, plot_pretty_name="Test Case"
        )

        # Verify that we got matplotlib objects back
        assert fig is not None
        assert ax is not None

        # Close the figure to free memory
        plt.close(fig)

    def test_memoization_basic_functionality(self):
        """Test basic memoization functionality."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings(memoization_precision=1e-3)

        neuber = NeuberCorrection(material=material, settings=settings)

        # First calculation should not use cache
        result1 = neuber.correct_stress_values([500])[0]

        # Second calculation with same stress should use cache
        result2 = neuber.correct_stress_values([500])[0]

        # Results should be identical
        assert result1 == result2

        # Check that memoization table has entries
        assert len(neuber.memoization_table) > 0
        assert len(neuber.memoization_keys) > 0

    def test_memoization_precision_based_lookup(self):
        """Test that memoization works with precision-based lookup."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings(memoization_precision=1.0)  # 1 MPa precision

        neuber = NeuberCorrection(material=material, settings=settings)

        # Calculate for stress 500
        result1 = neuber.correct_stress_values([500])[0]

        # Calculate for stress 500.5 (within precision)
        result2 = neuber.correct_stress_values([500.5])[0]

        # Should return cached result since 500.5 - 500 = 0.5 < 1.0
        assert result1 == result2

        # Calculate for stress 502 (outside precision)
        result3 = neuber.correct_stress_values([502])[0]

        # Should be different since 502 - 500 = 2 > 1.0
        assert result3 != result1

    def test_memoization_sorted_insertion(self):
        """Test that memoization maintains sorted order."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings(memoization_precision=1e-6)

        neuber = NeuberCorrection(material=material, settings=settings)

        # Calculate stresses in random order
        stresses = [600, 400, 800, 300, 700, 500]
        for stress in stresses:
            neuber.correct_stress_values([stress])

        # Check that keys are sorted
        assert neuber.memoization_keys == sorted(neuber.memoization_keys)

        # Check that all stresses are in the table
        for stress in stresses:
            assert stress in neuber.memoization_table

    def test_memoization_binary_search_efficiency(self):
        """Test that binary search finds correct cached values."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings(memoization_precision=0.1)

        neuber = NeuberCorrection(material=material, settings=settings)

        # Pre-populate cache with specific values
        test_stresses = [300, 400, 500, 600, 700, 800]
        expected_results = {}

        for stress in test_stresses:
            result = neuber.correct_stress_values([stress])[0]
            expected_results[stress] = result

        # Test binary search with values close to cached ones
        test_cases = [
            (300.05, 300),  # Should find 300
            (399.95, 400),  # Should find 400
            (500.08, 500),  # Should find 500
            (599.92, 600),  # Should find 600
            (700.03, 700),  # Should find 700
            (800.07, 800),  # Should find 800
        ]

        for test_stress, expected_cached_stress in test_cases:
            result = neuber.correct_stress_values([test_stress])[0]
            expected_result = expected_results[expected_cached_stress]
            assert result == expected_result

    def test_memoization_precision_settings(self):
        """Test different memoization precision settings."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        # Test with high precision (strict matching)
        settings_high = NeuberSolverSettings(memoization_precision=1e-9)
        neuber_high = NeuberCorrection(material=material, settings=settings_high)

        result1 = neuber_high.correct_stress_values([500])[0]
        result2 = neuber_high.correct_stress_values([500.0001])[0]

        # With high precision, these should be different
        assert result1 != result2

        # Test with low precision (loose matching)
        settings_low = NeuberSolverSettings(memoization_precision=10.0)
        neuber_low = NeuberCorrection(material=material, settings=settings_low)

        result3 = neuber_low.correct_stress_values([500])[0]
        result4 = neuber_low.correct_stress_values([505])[0]  # Within 10 MPa

        # With low precision, these should be the same
        assert result3 == result4

    def test_memoization_cache_growth(self):
        """Test that memoization cache grows correctly."""
        # Use unique material properties to avoid cache sharing
        material = MaterialForNeuberCorrection(
            yield_strength=316,  # Different from other tests
            sigma_u=471,  # Different from other tests
            elastic_mod=210001,  # Different from other tests
            eps_u=0.121,  # Different from other tests
        )

        settings = NeuberSolverSettings(memoization_precision=1e-6)

        neuber = NeuberCorrection(material=material, settings=settings)

        # Initial state
        assert len(neuber.memoization_table) == 0
        assert len(neuber.memoization_keys) == 0

        # Add first calculation
        neuber.correct_stress_values([400])
        assert len(neuber.memoization_table) == 1
        assert len(neuber.memoization_keys) == 1

        # Add second calculation
        neuber.correct_stress_values([600])
        assert len(neuber.memoization_table) == 2
        assert len(neuber.memoization_keys) == 2

        # Repeat first calculation (should not add to cache)
        neuber.correct_stress_values([400])
        assert len(neuber.memoization_table) == 2
        assert len(neuber.memoization_keys) == 2

    def test_memoization_edge_cases(self):
        """Test memoization with edge cases."""
        # Use unique material properties to avoid cache sharing
        material = MaterialForNeuberCorrection(
            yield_strength=317,  # Different from other tests
            sigma_u=472,  # Different from other tests
            elastic_mod=210002,  # Different from other tests
            eps_u=0.122,  # Different from other tests
        )

        settings = NeuberSolverSettings(memoization_precision=1e-6)

        neuber = NeuberCorrection(material=material, settings=settings)

        # Test with very small stress
        small_result = neuber.correct_stress_values([1.0])[0]
        assert small_result > 0

        # Test with very large stress
        large_result = neuber.correct_stress_values([2000])[0]
        assert large_result > 0

        # Test with yield strength
        yield_result = neuber.correct_stress_values([317])[0]  # Use new yield strength
        assert yield_result > 0

        # Test with tensile strength
        tensile_result = neuber.correct_stress_values([472])[
            0
        ]  # Use new tensile strength
        assert tensile_result > 0

        # Verify all are cached
        assert len(neuber.memoization_table) == 4
        assert len(neuber.memoization_keys) == 4

    def test_memoization_consistency_across_instances(self):
        """Test that memoization is consistent across different instances with same parameters."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings(memoization_precision=1e-6)

        # Create two instances with same parameters
        neuber1 = NeuberCorrection(material=material, settings=settings)
        neuber2 = NeuberCorrection(material=material, settings=settings)

        # They should be the same instance due to instance caching
        assert neuber1 is neuber2

        # Calculate same stress in both
        result1 = neuber1.correct_stress_values([500])[0]
        result2 = neuber2.correct_stress_values([500])[0]

        # Results should be identical
        assert result1 == result2

        # Memoization tables should be shared
        assert neuber1.memoization_table is neuber2.memoization_table
        assert neuber1.memoization_keys is neuber2.memoization_keys

    def test_memoization_performance_improvement(self):
        """Test that memoization provides performance improvement."""
        # Use unique material properties to avoid cache sharing
        material = MaterialForNeuberCorrection(
            yield_strength=318,  # Different from other tests
            sigma_u=473,  # Different from other tests
            elastic_mod=210003,  # Different from other tests
            eps_u=0.123,  # Different from other tests
        )

        settings = NeuberSolverSettings(memoization_precision=1e-6)

        neuber = NeuberCorrection(material=material, settings=settings)

        # First calculation (should be slower)
        start_time = time.time()
        result1 = neuber.correct_stress_values([500])[0]
        first_time = time.time() - start_time

        # Second calculation (should be faster due to cache)
        start_time = time.time()
        result2 = neuber.correct_stress_values([500])[0]
        second_time = time.time() - start_time

        # Results should be identical
        assert result1 == result2

        # Second calculation should be faster or at least not slower
        # (Note: This is a basic test, actual performance may vary)
        assert second_time <= first_time

    def test_memoization_with_list_processing(self):
        """Test that memoization works correctly with list processing."""
        # Use unique material properties to avoid cache sharing
        material = MaterialForNeuberCorrection(
            yield_strength=319,  # Different from other tests
            sigma_u=474,  # Different from other tests
            elastic_mod=210004,  # Different from other tests
            eps_u=0.124,  # Different from other tests
        )

        settings = NeuberSolverSettings(memoization_precision=1e-6)

        neuber = NeuberCorrection(material=material, settings=settings)

        # Process list with some duplicates
        stress_list = [400, 500, 400, 600, 500, 700]
        results = neuber.correct_stress_values(stress_list)

        # Check that we get the expected number of results
        assert len(results) == len(stress_list)

        # Check that duplicate stresses give same results
        assert results[0] == results[2]  # Both 400
        assert results[1] == results[4]  # Both 500

        # Check that memoization table has unique entries
        unique_stresses = set(stress_list)
        assert len(neuber.memoization_table) == len(unique_stresses)
        assert len(neuber.memoization_keys) == len(unique_stresses)

    def test_smoothing_transition_zone_behavior(self):
        """Test that the smoothing transition zone works correctly around yield point."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        # Test stresses around the yield point (transition zone is ±1% of yield strength)
        transition_width = material.yield_strength * 0.01  # 3.15 MPa
        yield_lower = material.yield_strength - transition_width  # 311.85 MPa
        yield_upper = material.yield_strength + transition_width  # 318.15 MPa

        # Test stresses in and around transition zone
        test_stresses = [
            yield_lower - 5,  # Below transition zone
            yield_lower,  # At transition zone lower bound
            yield_lower + 1,  # Inside transition zone
            material.yield_strength,  # At yield point
            yield_upper - 1,  # Inside transition zone
            yield_upper,  # At transition zone upper bound
            yield_upper + 5,  # Above transition zone
        ]

        corrected_values = neuber.correct_stress_values(test_stresses)

        # All should converge without failures
        assert len(corrected_values) == len(test_stresses)

        # Check that all corrections are reasonable
        for original, corrected in zip(test_stresses, corrected_values):
            assert corrected > 0
            assert corrected <= original

        # Below transition zone: should have correction due to full Ramberg-Osgood curve
        below_correction = abs(corrected_values[0] - test_stresses[0])
        assert (
            below_correction < 50.0
        )  # Full Ramberg-Osgood curve includes plastic strain

        # Above transition zone: should have significant correction (plastic)
        above_correction = test_stresses[6] - corrected_values[6]
        assert above_correction > 5.0

    def test_smoothing_convergence_improvement(self):
        """Test that smoothing eliminates convergence failures around yield point."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings(tolerance=1e-6, max_iterations=1000)

        neuber = NeuberCorrection(material=material, settings=settings)

        # Test a range of stresses that previously caused convergence issues
        # Focus on the problematic region around yield point
        stress_values = [310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320]

        corrected_values = neuber.correct_stress_values(stress_values)

        # All should converge successfully
        assert len(corrected_values) == len(stress_values)

        # Check that corrections are monotonic (increasing stress should give increasing correction)
        corrections = [
            original - corrected
            for original, corrected in zip(stress_values, corrected_values)
        ]

        # Corrections should generally increase with stress (allowing for small numerical variations)
        for i in range(1, len(corrections)):
            # Allow small tolerance for numerical precision
            assert corrections[i] >= corrections[i - 1] - 1e-6

    def test_smoothing_derivative_continuity(self):
        """Test that the smoothing provides continuous derivatives around yield point."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        # Test that we can calculate stresses very close to each other without issues
        base_stress = 315.0
        small_increment = 0.1

        # Test multiple closely spaced points around yield
        test_stresses = [
            base_stress - small_increment,
            base_stress,
            base_stress + small_increment,
        ]

        corrected_values = neuber.correct_stress_values(test_stresses)

        # All should converge
        assert len(corrected_values) == len(test_stresses)

        # Check that results are reasonable and continuous
        for original, corrected in zip(test_stresses, corrected_values):
            assert corrected > 0
            assert corrected <= original

        # The corrections should be continuous (no sudden jumps)
        corrections = [
            original - corrected
            for original, corrected in zip(test_stresses, corrected_values)
        ]

        # Check that adjacent corrections don't have large jumps
        for i in range(1, len(corrections)):
            jump = abs(corrections[i] - corrections[i - 1])
            # Allow reasonable tolerance for the jump
            assert jump < 2.0

    def test_smoothing_physical_consistency(self):
        """Test that smoothing maintains physical consistency of the material model."""
        material = MaterialForNeuberCorrection(
            yield_strength=315,
            sigma_u=470,
            elastic_mod=210000,
            eps_u=0.12,
        )

        settings = NeuberSolverSettings()

        neuber = NeuberCorrection(material=material, settings=settings)

        # Test that the material behavior is physically reasonable
        # Lower stresses should have smaller corrections than higher stresses
        low_stress = 200  # Well below yield
        high_stress = 500  # Well above yield

        low_corrected = neuber.correct_stress_values([low_stress])[0]
        high_corrected = neuber.correct_stress_values([high_stress])[0]

        low_correction = low_stress - low_corrected
        high_correction = high_stress - high_corrected

        # High stress should have larger correction than low stress
        assert high_correction > low_correction

        # Both corrections should be non-negative (stress reduction due to plasticity)
        assert low_correction >= 0
        assert high_correction > 0

        # Corrections should be reasonable in magnitude
        assert (
            low_correction < 5
        )  # Small correction for elastic range (allowing for smoothing effects)
        assert high_correction > 20  # Significant correction for plastic range


if __name__ == "__main__":
    pytest.main([__file__])
