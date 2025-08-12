"""
Comprehensive unit tests for Simple Peptide Analyzer module.

This test suite provides extensive coverage of all module functionality,
including edge cases, error conditions, and performance benchmarks.
"""

import pytest
import json
import time
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to Python path for importing the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import (
    execute,
    validate_inputs,
    analyze_peptide,
    calculate_molecular_weight,
    calculate_net_charge,
    calculate_isoelectric_point,
    calculate_hydrophobicity,
    calculate_aromaticity,
    calculate_instability_index,
    calculate_aa_composition,
    generate_summary,
    create_error_response,
    AA_PROPERTIES,
    MAX_SEQUENCES_PER_BATCH
)


class TestMainExecuteFunction:
    """Test the main execute function with various input scenarios."""
    
    def test_successful_execution(self):
        """Test successful execution with valid input."""
        input_data = {
            'peptide_sequences': ['SIINFEKL', 'GILGFVFTL'],
            'include_hydropathy': True,
            'include_charge_distribution': False
        }
        context = {'job_id': 'test-123'}
        
        result = execute(input_data, context)
        
        assert result['status'] == 'success'
        assert len(result['peptide_properties']) == 2
        assert 'summary' in result
        assert 'metadata' in result
        assert result['metadata']['job_id'] == 'test-123'
        assert result['metadata']['execution_time'] > 0
    
    def test_execution_with_all_options(self):
        """Test execution with all optional features enabled."""
        input_data = {
            'peptide_sequences': ['MLLSVPLLL', 'KVAELVHFL'],
            'include_hydropathy': True,
            'include_charge_distribution': True
        }
        context = {'job_id': 'test-full', 'user_id': 'user123'}
        
        result = execute(input_data, context)
        
        assert result['status'] == 'success'
        assert len(result['peptide_properties']) == 2
        
        # Check that hydropathy is included
        peptide = result['peptide_properties'][0]
        assert 'hydrophobicity' in peptide
        assert 'gravy' in peptide
        assert 'hydropathy_class' in peptide
        
        # Check that charge distribution is included
        assert 'charge_distribution' in peptide
        assert 'charge_analysis' in peptide
    
    def test_execution_with_invalid_input(self):
        """Test execution with invalid input returns error."""
        input_data = {
            'peptide_sequences': ['INVALID_SEQUENCE_WITH_X'],
        }
        context = {'job_id': 'test-error'}
        
        result = execute(input_data, context)
        
        assert result['status'] == 'error'
        assert 'error' in result
        assert 'Invalid input' in result['error']
    
    def test_execution_with_empty_sequences(self):
        """Test execution with empty sequences array."""
        input_data = {'peptide_sequences': []}
        context = {'job_id': 'test-empty'}
        
        result = execute(input_data, context)
        
        assert result['status'] == 'error'
        assert 'empty' in result['error'].lower()
    
    def test_execution_with_mixed_valid_invalid_sequences(self):
        """Test execution handles mix of valid and invalid sequences."""
        input_data = {
            'peptide_sequences': ['SIINFEKL', 'INVALIDX', 'GILGFVFTL'],
            'include_hydropathy': True
        }
        context = {'job_id': 'test-mixed'}
        
        result = execute(input_data, context)
        
        # Should still succeed overall but with some errors
        assert result['status'] == 'success'
        assert len(result['peptide_properties']) == 3
        
        # Check that one peptide has an error
        error_count = sum(1 for p in result['peptide_properties'] if 'error' in p)
        valid_count = sum(1 for p in result['peptide_properties'] if 'error' not in p)
        
        assert error_count == 1
        assert valid_count == 2
        assert result['metadata']['performance']['errors_count'] == 1
    
    def test_large_batch_processing(self):
        """Test processing of larger batches within limits."""
        # Create a batch of 50 sequences
        sequences = ['SIINFEKL'] * 25 + ['GILGFVFTL'] * 25
        input_data = {
            'peptide_sequences': sequences,
            'include_hydropathy': True
        }
        context = {'job_id': 'test-large'}
        
        result = execute(input_data, context)
        
        assert result['status'] == 'success'
        assert len(result['peptide_properties']) == 50
        assert result['summary']['total_peptides'] == 50
        assert result['metadata']['performance']['sequences_per_second'] > 0


class TestInputValidation:
    """Test input validation function thoroughly."""
    
    def test_valid_input(self):
        """Test validation with completely valid input."""
        input_data = {
            'peptide_sequences': ['SIINFEKL', 'GILGFVFTL'],
            'include_hydropathy': True,
            'include_charge_distribution': False
        }
        
        result = validate_inputs(input_data)
        
        assert result['valid'] is True
    
    def test_missing_sequences(self):
        """Test validation fails when peptide_sequences is missing."""
        input_data = {'include_hydropathy': True}
        
        result = validate_inputs(input_data)
        
        assert result['valid'] is False
        assert 'peptide_sequences' in result['error']
    
    def test_non_list_sequences(self):
        """Test validation fails when sequences is not a list."""
        input_data = {'peptide_sequences': 'SIINFEKL'}
        
        result = validate_inputs(input_data)
        
        assert result['valid'] is False
        assert 'array' in result['error']
    
    def test_empty_sequences_list(self):
        """Test validation fails with empty sequences list."""
        input_data = {'peptide_sequences': []}
        
        result = validate_inputs(input_data)
        
        assert result['valid'] is False
        assert 'empty' in result['error']
    
    def test_too_many_sequences(self):
        """Test validation fails when exceeding maximum batch size."""
        input_data = {
            'peptide_sequences': ['A'] * (MAX_SEQUENCES_PER_BATCH + 1)
        }
        
        result = validate_inputs(input_data)
        
        assert result['valid'] is False
        assert 'Maximum' in result['error']
    
    def test_invalid_amino_acids(self):
        """Test validation fails with invalid amino acid characters."""
        input_data = {
            'peptide_sequences': ['SIINFEKL', 'INVALIDX', 'GILGFVFTL']
        }
        
        result = validate_inputs(input_data)
        
        assert result['valid'] is False
        assert 'invalid amino acids' in result['error']
        assert 'X' in result['error']
    
    def test_non_string_sequence(self):
        """Test validation fails with non-string sequences."""
        input_data = {
            'peptide_sequences': ['SIINFEKL', 123, 'GILGFVFTL']
        }
        
        result = validate_inputs(input_data)
        
        assert result['valid'] is False
        assert 'must be a string' in result['error']
    
    def test_empty_string_sequence(self):
        """Test validation fails with empty string sequences."""
        input_data = {
            'peptide_sequences': ['SIINFEKL', '', 'GILGFVFTL']
        }
        
        result = validate_inputs(input_data)
        
        assert result['valid'] is False
        assert 'cannot be empty' in result['error']
    
    def test_very_long_sequence(self):
        """Test validation fails with extremely long sequences."""
        input_data = {
            'peptide_sequences': ['A' * 10001]  # Over 10k limit
        }
        
        result = validate_inputs(input_data)
        
        assert result['valid'] is False
        assert 'too long' in result['error']
    
    def test_invalid_boolean_parameters(self):
        """Test validation fails with non-boolean optional parameters."""
        input_data = {
            'peptide_sequences': ['SIINFEKL'],
            'include_hydropathy': 'yes'  # Should be boolean
        }
        
        result = validate_inputs(input_data)
        
        assert result['valid'] is False
        assert 'must be a boolean' in result['error']
    
    def test_case_insensitive_sequences(self):
        """Test validation works with lowercase sequences."""
        input_data = {
            'peptide_sequences': ['siinfekl', 'GILGFVFTL']
        }
        
        result = validate_inputs(input_data)
        
        assert result['valid'] is True


class TestPeptideAnalysis:
    """Test individual peptide analysis functions."""
    
    def test_analyze_peptide_basic(self):
        """Test basic peptide analysis without optional features."""
        sequence = 'SIINFEKL'
        
        result = analyze_peptide(sequence, include_hydropathy=False, include_charge_distribution=False)
        
        assert result['sequence'] == sequence
        assert result['length'] == 8
        assert 'molecular_weight' in result
        assert 'isoelectric_point' in result
        assert 'net_charge_ph7' in result
        assert 'aromaticity' in result
        assert 'instability_index' in result
        assert 'stability_classification' in result
        assert 'composition' in result
        
        # Should not have hydropathy features
        assert 'hydrophobicity' not in result
        assert 'gravy' not in result
        assert 'charge_distribution' not in result
    
    def test_analyze_peptide_with_hydropathy(self):
        """Test peptide analysis with hydropathy calculations."""
        sequence = 'MLLSVPLLL'  # Hydrophobic peptide
        
        result = analyze_peptide(sequence, include_hydropathy=True, include_charge_distribution=False)
        
        assert 'hydrophobicity' in result
        assert 'gravy' in result
        assert 'hydropathy_class' in result
        assert result['hydropathy_class'] == 'hydrophobic'  # Should be hydrophobic
    
    def test_analyze_peptide_with_charge_distribution(self):
        """Test peptide analysis with charge distribution."""
        sequence = 'KKKRRR'  # Very basic peptide
        
        result = analyze_peptide(sequence, include_hydropathy=False, include_charge_distribution=True)
        
        assert 'charge_distribution' in result
        assert 'charge_analysis' in result
        
        # Check that all pH values are present
        ph_values = ['pH_3.0', 'pH_5.0', 'pH_7.0', 'pH_9.0', 'pH_11.0']
        for ph in ph_values:
            assert ph in result['charge_distribution']
            assert isinstance(result['charge_distribution'][ph], (int, float))
    
    def test_analyze_peptide_full_features(self):
        """Test peptide analysis with all features enabled."""
        sequence = 'YLQPRTFLL'
        
        result = analyze_peptide(sequence, include_hydropathy=True, include_charge_distribution=True)
        
        # Should have all features
        required_keys = [
            'sequence', 'length', 'molecular_weight', 'isoelectric_point',
            'net_charge_ph7', 'aromaticity', 'instability_index',
            'hydrophobicity', 'gravy', 'hydropathy_class',
            'charge_distribution', 'charge_analysis', 'composition'
        ]
        
        for key in required_keys:
            assert key in result
    
    def test_analyze_empty_sequence(self):
        """Test that empty sequence raises appropriate error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            analyze_peptide("")
    
    def test_analyze_single_amino_acid(self):
        """Test analysis of single amino acid sequence."""
        result = analyze_peptide("A")
        
        assert result['length'] == 1
        assert result['molecular_weight'] > 0
        assert 'aromaticity' in result
        assert result['aromaticity'] == 0.0  # Alanine is not aromatic


class TestMolecularWeightCalculation:
    """Test molecular weight calculation."""
    
    def test_single_amino_acid(self):
        """Test molecular weight of single amino acid."""
        # Alanine: 89.09 Da (no peptide bonds, so no water loss)
        mw = calculate_molecular_weight('A')
        assert abs(mw - 89.09) < 0.01
    
    def test_dipeptide(self):
        """Test molecular weight of dipeptide."""
        # Ala-Ala: 2*89.09 - 18.015 (one peptide bond)
        expected = 2 * 89.09 - 18.015
        mw = calculate_molecular_weight('AA')
        assert abs(mw - expected) < 0.01
    
    def test_known_peptide(self):
        """Test molecular weight of known peptide SIINFEKL."""
        mw = calculate_molecular_weight('SIINFEKL')
        # Should be around 960-970 Da
        assert 950 < mw < 980
    
    def test_empty_sequence(self):
        """Test molecular weight of empty sequence."""
        mw = calculate_molecular_weight('')
        assert mw == 0.0


class TestChargeCalculations:
    """Test charge-related calculations."""
    
    def test_neutral_charge_calculation(self):
        """Test charge calculation at neutral pH."""
        # Glycine should have near-zero charge at its pI
        charge = calculate_net_charge('G', 7.0)
        assert abs(charge) < 1.0
    
    def test_basic_peptide_charge(self):
        """Test charge of basic peptide."""
        # Lysine-rich peptide should be positive at pH 7
        charge = calculate_net_charge('KKK', 7.0)
        assert charge > 2.0
    
    def test_acidic_peptide_charge(self):
        """Test charge of acidic peptide."""
        # Glutamic acid-rich peptide should be negative at pH 7
        charge = calculate_net_charge('EEE', 7.0)
        assert charge < -2.0
    
    def test_isoelectric_point_basic_peptide(self):
        """Test isoelectric point of basic peptide."""
        pi = calculate_isoelectric_point('KKK')
        assert pi > 10.0  # Should be very basic
    
    def test_isoelectric_point_acidic_peptide(self):
        """Test isoelectric point of acidic peptide."""
        pi = calculate_isoelectric_point('EEE')
        assert pi < 4.0  # Should be very acidic
    
    def test_isoelectric_point_neutral_peptide(self):
        """Test isoelectric point of relatively neutral peptide."""
        pi = calculate_isoelectric_point('GGG')
        assert 5.0 < pi < 8.0  # Should be near neutral
    
    def test_charge_at_extreme_ph(self):
        """Test charge calculations at extreme pH values."""
        sequence = 'KE'  # One basic, one acidic
        
        charge_low = calculate_net_charge(sequence, 1.0)  # Very acidic
        charge_high = calculate_net_charge(sequence, 13.0)  # Very basic
        
        assert charge_low > 0  # Should be positive (basic groups protonated)
        assert charge_high < 0  # Should be negative (acidic groups deprotonated)


class TestHydrophobicityCalculations:
    """Test hydrophobicity-related calculations."""
    
    def test_hydrophobic_sequence(self):
        """Test hydrophobicity of known hydrophobic sequence."""
        # Leucine is very hydrophobic (3.8 on Kyte-Doolittle scale)
        hydrophobicity = calculate_hydrophobicity('LLL')
        assert hydrophobicity > 10.0
    
    def test_hydrophilic_sequence(self):
        """Test hydrophobicity of known hydrophilic sequence."""
        # Lysine is very hydrophilic (-3.9 on Kyte-Doolittle scale)
        hydrophobicity = calculate_hydrophobicity('KKK')
        assert hydrophobicity < -10.0
    
    def test_mixed_sequence(self):
        """Test hydrophobicity of mixed sequence."""
        # Mix of hydrophobic and hydrophilic
        hydrophobicity = calculate_hydrophobicity('LK')  # 3.8 + (-3.9) = -0.1
        assert abs(hydrophobicity - (-0.1)) < 0.1
    
    def test_empty_sequence_hydrophobicity(self):
        """Test hydrophobicity of empty sequence."""
        hydrophobicity = calculate_hydrophobicity('')
        assert hydrophobicity == 0.0


class TestAromaticityCalculation:
    """Test aromaticity calculation."""
    
    def test_all_aromatic(self):
        """Test aromaticity of all aromatic sequence."""
        aromaticity = calculate_aromaticity('FWY')  # All aromatic
        assert aromaticity == 1.0
    
    def test_no_aromatic(self):
        """Test aromaticity of non-aromatic sequence."""
        aromaticity = calculate_aromaticity('AGS')  # No aromatic
        assert aromaticity == 0.0
    
    def test_mixed_aromatic(self):
        """Test aromaticity of mixed sequence."""
        aromaticity = calculate_aromaticity('FAGS')  # 1 aromatic out of 4
        assert aromaticity == 0.25
    
    def test_empty_sequence_aromaticity(self):
        """Test aromaticity of empty sequence."""
        aromaticity = calculate_aromaticity('')
        assert aromaticity == 0.0


class TestInstabilityIndex:
    """Test instability index calculation."""
    
    def test_stable_peptide(self):
        """Test instability index of presumably stable peptide."""
        # Short, simple peptide should be relatively stable
        instability = calculate_instability_index('GGG')
        assert instability >= 0
    
    def test_single_amino_acid(self):
        """Test instability of single amino acid."""
        instability = calculate_instability_index('G')
        assert instability == 0.0
    
    def test_empty_sequence_instability(self):
        """Test instability of empty sequence."""
        instability = calculate_instability_index('')
        assert instability == 0.0
    
    def test_known_unstable_dipeptide(self):
        """Test instability with known unstable dipeptides."""
        # Some dipeptides have high instability weights
        instability = calculate_instability_index('MH')  # Known unstable dipeptide
        assert instability > 0


class TestAminoAcidComposition:
    """Test amino acid composition calculation."""
    
    def test_single_type_composition(self):
        """Test composition of sequence with single amino acid type."""
        composition = calculate_aa_composition('AAA')
        assert composition['A'] == 100.0
        assert all(composition[aa] == 0.0 for aa in composition if aa != 'A')
    
    def test_mixed_composition(self):
        """Test composition of mixed sequence."""
        composition = calculate_aa_composition('AABBCC')
        assert composition['A'] == pytest.approx(33.3, rel=0.1)
        assert composition['B'] == pytest.approx(33.3, rel=0.1)
        assert composition['C'] == pytest.approx(33.3, rel=0.1)
    
    def test_empty_sequence_composition(self):
        """Test composition of empty sequence."""
        composition = calculate_aa_composition('')
        assert composition == {}


class TestSummaryGeneration:
    """Test summary statistics generation."""
    
    def test_empty_peptide_list(self):
        """Test summary generation with empty peptide list."""
        summary = generate_summary([])
        assert summary['total_peptides'] == 0
        assert summary['valid_peptides'] == 0
    
    def test_all_valid_peptides(self):
        """Test summary with all valid peptides."""
        peptides = [
            {'sequence': 'AAA', 'length': 3, 'molecular_weight': 200, 'isoelectric_point': 6, 
             'net_charge_ph7': 0, 'aromaticity': 0, 'instability_index': 10},
            {'sequence': 'BBB', 'length': 3, 'molecular_weight': 300, 'isoelectric_point': 7,
             'net_charge_ph7': 1, 'aromaticity': 0.5, 'instability_index': 20}
        ]
        
        summary = generate_summary(peptides)
        
        assert summary['total_peptides'] == 2
        assert summary['valid_peptides'] == 2
        assert summary['error_count'] == 0
        assert summary['success_rate'] == 1.0
        assert 'length_statistics' in summary
        assert 'molecular_weight_statistics' in summary
        assert 'average_properties' in summary
        assert 'stability_analysis' in summary
    
    def test_mixed_valid_invalid_peptides(self):
        """Test summary with mix of valid and invalid peptides."""
        peptides = [
            {'sequence': 'AAA', 'length': 3, 'molecular_weight': 200, 'isoelectric_point': 6,
             'net_charge_ph7': 0, 'aromaticity': 0, 'instability_index': 10},
            {'sequence': 'INVALID', 'error': 'Invalid sequence'},
            {'sequence': 'CCC', 'length': 3, 'molecular_weight': 300, 'isoelectric_point': 7,
             'net_charge_ph7': 1, 'aromaticity': 0.5, 'instability_index': 20}
        ]
        
        summary = generate_summary(peptides)
        
        assert summary['total_peptides'] == 3
        assert summary['valid_peptides'] == 2
        assert summary['error_count'] == 1
        assert summary['success_rate'] == pytest.approx(0.667, rel=0.01)
    
    def test_all_invalid_peptides(self):
        """Test summary with all invalid peptides."""
        peptides = [
            {'sequence': 'INVALID1', 'error': 'Error 1'},
            {'sequence': 'INVALID2', 'error': 'Error 2'}
        ]
        
        summary = generate_summary(peptides)
        
        assert summary['total_peptides'] == 2
        assert summary['valid_peptides'] == 0
        assert summary['error_count'] == 2
        assert 'errors' in summary
        assert len(summary['errors']) == 2
    
    def test_summary_with_hydropathy_data(self):
        """Test summary generation with hydropathy data."""
        peptides = [
            {'sequence': 'AAA', 'length': 3, 'molecular_weight': 200, 'isoelectric_point': 6,
             'net_charge_ph7': 0, 'aromaticity': 0, 'instability_index': 10, 'gravy': 0.5},
            {'sequence': 'BBB', 'length': 3, 'molecular_weight': 300, 'isoelectric_point': 7,
             'net_charge_ph7': 1, 'aromaticity': 0.5, 'instability_index': 20, 'gravy': -0.3}
        ]
        
        summary = generate_summary(peptides)
        
        assert 'hydropathy_statistics' in summary
        assert 'min' in summary['hydropathy_statistics']
        assert 'max' in summary['hydropathy_statistics']
        assert 'mean' in summary['hydropathy_statistics']


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_create_error_response(self):
        """Test error response creation."""
        error_msg = "Test error message"
        metadata = {"test_key": "test_value"}
        
        response = create_error_response(error_msg, metadata)
        
        assert response['status'] == 'error'
        assert response['error'] == error_msg
        assert response['metadata'] == metadata
        assert 'timestamp' in response
    
    def test_create_error_response_no_metadata(self):
        """Test error response creation without metadata."""
        error_msg = "Simple error"
        
        response = create_error_response(error_msg)
        
        assert response['status'] == 'error'
        assert response['error'] == error_msg
        assert 'metadata' not in response
        assert 'timestamp' in response
    
    @patch('main.analyze_peptide')
    def test_execution_handles_analysis_errors(self, mock_analyze):
        """Test that execution handles individual peptide analysis errors gracefully."""
        # Mock analyze_peptide to raise an exception for the second peptide
        def side_effect(sequence, **kwargs):
            if sequence == 'FAIL':
                raise RuntimeError("Analysis failed")
            return {'sequence': sequence, 'length': len(sequence), 'molecular_weight': 100,
                   'isoelectric_point': 7, 'net_charge_ph7': 0, 'aromaticity': 0,
                   'instability_index': 10, 'composition': {}}
        
        mock_analyze.side_effect = side_effect
        
        input_data = {
            'peptide_sequences': ['GOOD', 'FAIL', 'GOOD2'],
        }
        context = {'job_id': 'test-error-handling'}
        
        result = execute(input_data, context)
        
        # Should still succeed overall
        assert result['status'] == 'success'
        assert len(result['peptide_properties']) == 3
        
        # Check error handling
        error_peptides = [p for p in result['peptide_properties'] if 'error' in p]
        valid_peptides = [p for p in result['peptide_properties'] if 'error' not in p]
        
        assert len(error_peptides) == 1
        assert len(valid_peptides) == 2
        assert 'Analysis failed' in error_peptides[0]['error']


class TestPerformanceBenchmarks:
    """Performance and benchmark tests."""
    
    def test_execution_time_small_batch(self):
        """Test execution time for small batch is reasonable."""
        input_data = {
            'peptide_sequences': ['SIINFEKL', 'GILGFVFTL', 'YLQPRTFLL'],
            'include_hydropathy': True,
            'include_charge_distribution': True
        }
        context = {'job_id': 'perf-test-small'}
        
        start_time = time.time()
        result = execute(input_data, context)
        execution_time = time.time() - start_time
        
        assert result['status'] == 'success'
        assert execution_time < 1.0  # Should complete within 1 second
    
    def test_execution_time_medium_batch(self):
        """Test execution time for medium batch is reasonable."""
        # Create 50 sequences
        sequences = ['SIINFEKL'] * 50
        input_data = {
            'peptide_sequences': sequences,
            'include_hydropathy': True
        }
        context = {'job_id': 'perf-test-medium'}
        
        start_time = time.time()
        result = execute(input_data, context)
        execution_time = time.time() - start_time
        
        assert result['status'] == 'success'
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert result['metadata']['performance']['sequences_per_second'] > 10
    
    def test_memory_efficiency_large_sequences(self):
        """Test that large sequences don't cause memory issues."""
        # Create sequences of varying lengths
        sequences = [
            'A' * 100,    # 100 aa
            'A' * 500,    # 500 aa
            'A' * 1000    # 1000 aa
        ]
        input_data = {
            'peptide_sequences': sequences,
            'include_hydropathy': True,
            'include_charge_distribution': True
        }
        context = {'job_id': 'memory-test'}
        
        result = execute(input_data, context)
        
        assert result['status'] == 'success'
        assert len(result['peptide_properties']) == 3
    
    def test_calculation_accuracy(self):
        """Test that calculations remain accurate under stress."""
        # Test with known peptide
        sequence = 'SIINFEKL'
        
        # Run analysis multiple times and check consistency
        results = []
        for _ in range(10):
            result = analyze_peptide(sequence)
            results.append(result)
        
        # All results should be identical
        first_result = results[0]
        for result in results[1:]:
            for key in first_result:
                if isinstance(first_result[key], (int, float)):
                    assert abs(first_result[key] - result[key]) < 1e-10


class TestIntegrationScenarios:
    """Integration tests with realistic scenarios."""
    
    def test_immunogenic_peptides_analysis(self):
        """Test analysis of known immunogenic peptides."""
        # Known MHC class I binding peptides
        immunogenic_peptides = [
            'SIINFEKL',    # OVA 257-264
            'GILGFVFTL',   # Flu M1 58-66
            'YLQPRTFLL',   # HBV core 18-27
            'FLPSDFFPSV',  # HBV pol 455-463
            'GLCTLVAML',   # BMLF1 280-288
        ]
        
        input_data = {
            'peptide_sequences': immunogenic_peptides,
            'include_hydropathy': True,
            'include_charge_distribution': True
        }
        context = {'job_id': 'immunogenic-test'}
        
        result = execute(input_data, context)
        
        assert result['status'] == 'success'
        assert len(result['peptide_properties']) == 5
        assert result['summary']['valid_peptides'] == 5
        
        # Check that all peptides are in typical MHC I length range
        lengths = [p['length'] for p in result['peptide_properties']]
        assert all(8 <= length <= 11 for length in lengths)
        
        # Check that molecular weights are reasonable for MHC I peptides
        mws = [p['molecular_weight'] for p in result['peptide_properties']]
        assert all(800 <= mw <= 1500 for mw in mws)
    
    def test_cancer_neoantigen_peptides(self):
        """Test analysis of potential cancer neoantigen peptides."""
        # Simulated neoantigen peptides with mutations
        neoantigen_peptides = [
            'KTWGQYWQV',   # Mutated peptide 1
            'RTWGQYWQV',   # Wild type control
            'ALWGPDPAAA',  # Another mutated peptide
        ]
        
        input_data = {
            'peptide_sequences': neoantigen_peptides,
            'include_hydropathy': True,
            'include_charge_distribution': False
        }
        context = {'job_id': 'neoantigen-test', 'user_id': 'researcher1'}
        
        result = execute(input_data, context)
        
        assert result['status'] == 'success'
        assert result['metadata']['parameters']['total_sequences'] == 3
        
        # Compare properties between mutated and wild type
        peptides = result['peptide_properties']
        assert len(peptides) == 3
        
        # All should have hydropathy data
        for peptide in peptides:
            assert 'hydrophobicity' in peptide
            assert 'gravy' in peptide
    
    def test_drug_discovery_peptides(self):
        """Test analysis of therapeutic peptide candidates."""
        # Simulated therapeutic peptides
        therapeutic_peptides = [
            'CYCRGDLAC',      # Cyclic RGD peptide (integrin inhibitor)
            'GHRPLDKKREEAPSLRPAPPPS',  # Longer therapeutic peptide
            'FFVAPFPEVFGK',   # Antimicrobial peptide
        ]
        
        input_data = {
            'peptide_sequences': therapeutic_peptides,
            'include_hydropathy': True,
            'include_charge_distribution': True
        }
        context = {'job_id': 'drug-discovery-test'}
        
        result = execute(input_data, context)
        
        assert result['status'] == 'success'
        
        # Should handle peptides of very different lengths
        lengths = [p['length'] for p in result['peptide_properties']]
        assert min(lengths) < 15
        assert max(lengths) > 15
        
        # Check stability analysis
        stability_data = result['summary']['stability_analysis']
        assert 'stable_count' in stability_data
        assert 'unstable_count' in stability_data
        assert 'percent_unstable' in stability_data
    
    def test_pathogen_derived_peptides(self):
        """Test analysis of pathogen-derived peptides."""
        # Viral and bacterial peptides
        pathogen_peptides = [
            'LPRRSGAAGA',     # SARS-CoV-2 derived
            'MEVTPSGTWL',     # Another viral peptide
            'AAAGAAAAAG',     # Simple bacterial peptide
            'WWWFFFFFF',      # Hydrophobic pathogen peptide
        ]
        
        input_data = {
            'peptide_sequences': pathogen_peptides,
            'include_hydropathy': True,
            'include_charge_distribution': False
        }
        context = {'job_id': 'pathogen-test'}
        
        result = execute(input_data, context)
        
        assert result['status'] == 'success'
        
        # Check that hydrophobic peptide is classified correctly
        hydrophobic_peptide = next(
            p for p in result['peptide_properties'] 
            if p['sequence'] == 'WWWFFFFFF'
        )
        assert hydrophobic_peptide['hydropathy_class'] == 'hydrophobic'
        
        # Check amino acid frequency analysis
        aa_freq = result['summary']['amino_acid_frequency']
        assert 'W' in aa_freq
        assert 'F' in aa_freq
        assert aa_freq['W'] > 0
        assert aa_freq['F'] > 0


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main(['-v', '--tb=short', __file__])