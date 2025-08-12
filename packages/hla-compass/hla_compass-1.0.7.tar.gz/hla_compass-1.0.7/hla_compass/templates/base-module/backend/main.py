"""
HLA-Compass Module: Simple Peptide Analyzer
Description: Analyzes peptide sequences to calculate basic biophysical properties
Author: External Developer Template
Version: 1.0.0

This is a complete, production-ready template for developing HLA-Compass modules.
The module calculates various biophysical properties of peptide sequences including:
- Molecular weight
- Isoelectric point
- Net charge at pH 7
- Hydrophobicity (optional)
- Aromaticity
- Instability index
- Charge distribution at different pH values (optional)
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter
import sys
import traceback

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler if not already present
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Amino acid properties
# Format: (molecular_weight, pKa_COOH, pKa_NH3, pKa_side_chain, hydropathy_index, is_aromatic)
AA_PROPERTIES = {
    'A': (89.09, 2.34, 9.69, None, 1.8, False),       # Alanine
    'R': (174.20, 2.17, 9.04, 12.48, -4.5, False),    # Arginine
    'N': (132.12, 2.02, 8.80, None, -3.5, False),     # Asparagine
    'D': (133.10, 1.88, 9.60, 3.65, -3.5, False),     # Aspartic acid
    'C': (121.15, 1.96, 10.28, 8.18, 2.5, False),     # Cysteine
    'E': (147.13, 2.19, 9.67, 4.25, -3.5, False),     # Glutamic acid
    'Q': (146.15, 2.17, 9.13, None, -3.5, False),     # Glutamine
    'G': (75.07, 2.34, 9.60, None, -0.4, False),      # Glycine
    'H': (155.16, 1.82, 9.17, 6.00, -3.2, False),     # Histidine
    'I': (131.17, 2.36, 9.60, None, 4.5, False),      # Isoleucine
    'L': (131.17, 2.36, 9.60, None, 3.8, False),      # Leucine
    'K': (146.19, 2.18, 8.95, 10.53, -3.9, False),    # Lysine
    'M': (149.21, 2.28, 9.21, None, 1.9, False),      # Methionine
    'F': (165.19, 1.83, 9.13, None, 2.8, True),       # Phenylalanine
    'P': (115.13, 1.99, 10.60, None, -1.6, False),    # Proline
    'S': (105.09, 2.21, 9.15, None, -0.8, False),     # Serine
    'T': (119.12, 2.09, 9.10, None, -0.7, False),     # Threonine
    'W': (204.23, 2.83, 9.39, None, -0.9, True),      # Tryptophan
    'Y': (181.19, 2.20, 9.11, 10.07, -1.3, True),     # Tyrosine
    'V': (117.15, 2.32, 9.62, None, 4.2, False)       # Valine
}

# Instability index dipeptide weights (Guruprasad et al., 1990)
# Values represent the probability of instability for each dipeptide
INSTABILITY_WEIGHTS = {
    'WW': 1.0, 'WC': 1.0, 'WM': 24.68, 'WH': 24.68, 'WY': 1.0,
    'WF': 1.0, 'CW': 24.68, 'CC': 1.0, 'CM': 33.60, 'CH': 33.60,
    'CY': 1.0, 'CF': 1.0, 'MW': 1.0, 'MC': 1.0, 'MM': -1.88,
    'MH': 58.28, 'MY': 24.68, 'MF': 1.0, 'HW': -1.88, 'HC': 1.0,
    'HM': -1.88, 'HH': 1.0, 'HY': 44.94, 'HF': -1.88, 'YW': -9.37,
    'YC': 1.0, 'YM': 44.94, 'YH': 13.34, 'YY': 1.0, 'YF': 1.0,
    'FW': 1.0, 'FC': 1.0, 'FM': 1.0, 'FH': 1.0, 'FY': 33.60, 'FF': 1.0
}

# Module constants
MODULE_NAME = "simple-analyzer"
MODULE_VERSION = "1.0.0"
MAX_SEQUENCES_PER_BATCH = 1000
DEFAULT_TIMEOUT_SECONDS = 60


def execute(input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for the peptide analysis module.
    
    This function serves as the primary interface for the HLA-Compass platform.
    It validates inputs, processes peptide sequences, and returns comprehensive
    analysis results.
    
    Args:
        input_data (Dict[str, Any]): Input parameters containing:
            - peptide_sequences (List[str]): Array of peptide sequences to analyze
            - include_hydropathy (bool, optional): Include hydropathy calculations
            - include_charge_distribution (bool, optional): Calculate charge at different pH
            
        context (Dict[str, Any]): Execution context containing:
            - job_id (str): Unique job identifier
            - user_id (str, optional): User identifier
            - organization_id (str, optional): Organization identifier
            
    Returns:
        Dict[str, Any]: Analysis results containing:
            - status (str): 'success' or 'error'
            - peptide_properties (List[Dict]): Individual peptide analysis results
            - summary (Dict): Aggregate statistics
            - metadata (Dict): Execution metadata
            - error (str, optional): Error message if status is 'error'
    """
    start_time = datetime.utcnow()
    job_id = context.get('job_id', 'unknown')
    
    try:
        logger.info(f"Starting peptide analysis for job {job_id}")
        
        # Validate inputs
        validation_result = validate_inputs(input_data)
        if not validation_result['valid']:
            logger.error(f"Input validation failed: {validation_result['error']}")
            return create_error_response(f"Invalid input: {validation_result['error']}")
        
        # Extract and validate parameters
        peptide_sequences = input_data.get('peptide_sequences', [])
        include_hydropathy = input_data.get('include_hydropathy', True)
        include_charge_distribution = input_data.get('include_charge_distribution', False)
        
        logger.info(
            f"Processing {len(peptide_sequences)} sequences with "
            f"hydropathy={include_hydropathy}, charge_dist={include_charge_distribution}"
        )
        
        # Analyze peptides
        peptide_properties = []
        errors_count = 0
        
        for i, sequence in enumerate(peptide_sequences):
            try:
                properties = analyze_peptide(
                    sequence.upper().strip(), 
                    include_hydropathy=include_hydropathy,
                    include_charge_distribution=include_charge_distribution
                )
                peptide_properties.append(properties)
                
                # Log progress for large batches
                if len(peptide_sequences) > 50 and (i + 1) % 50 == 0:
                    logger.info(f"Processed {i + 1}/{len(peptide_sequences)} sequences")
                    
            except Exception as e:
                errors_count += 1
                logger.warning(f"Failed to analyze peptide {i+1} ({sequence}): {str(e)}")
                peptide_properties.append({
                    'sequence': sequence,
                    'error': str(e),
                    'peptide_index': i
                })
        
        # Generate summary statistics
        summary = generate_summary(peptide_properties)
        
        # Calculate execution metrics
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        logger.info(
            f"Analysis completed: {len(peptide_sequences)} sequences, "
            f"{errors_count} errors, {execution_time:.2f}s"
        )
        
        return {
            'status': 'success',
            'peptide_properties': peptide_properties,
            'summary': summary,
            'metadata': {
                'module_name': MODULE_NAME,
                'module_version': MODULE_VERSION,
                'execution_time': execution_time,
                'execution_timestamp': start_time.isoformat(),
                'job_id': job_id,
                'parameters': {
                    'total_sequences': len(peptide_sequences),
                    'include_hydropathy': include_hydropathy,
                    'include_charge_distribution': include_charge_distribution
                },
                'performance': {
                    'sequences_per_second': len(peptide_sequences) / execution_time if execution_time > 0 else 0,
                    'errors_count': errors_count,
                    'success_rate': (len(peptide_sequences) - errors_count) / len(peptide_sequences)
                }
            }
        }
        
    except Exception as e:
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        error_msg = str(e)
        logger.error(f"Module execution failed after {execution_time:.2f}s: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return create_error_response(
            error_msg,
            metadata={
                'module_name': MODULE_NAME,
                'module_version': MODULE_VERSION,
                'execution_time': execution_time,
                'job_id': job_id,
                'error_type': type(e).__name__
            }
        )


def validate_inputs(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive input validation with detailed error reporting.
    
    Args:
        input_data (Dict[str, Any]): Input data to validate
        
    Returns:
        Dict[str, Any]: Validation result with 'valid' boolean and 'error' message
    """
    # Check for required parameters
    if not isinstance(input_data, dict):
        return {'valid': False, 'error': 'Input data must be a dictionary'}
    
    if 'peptide_sequences' not in input_data:
        return {'valid': False, 'error': 'Missing required parameter: peptide_sequences'}
    
    sequences = input_data['peptide_sequences']
    
    # Validate sequences parameter
    if not isinstance(sequences, list):
        return {'valid': False, 'error': 'peptide_sequences must be an array'}
    
    if len(sequences) == 0:
        return {'valid': False, 'error': 'peptide_sequences array cannot be empty'}
    
    if len(sequences) > MAX_SEQUENCES_PER_BATCH:
        return {
            'valid': False, 
            'error': f'Maximum {MAX_SEQUENCES_PER_BATCH} sequences allowed per batch, got {len(sequences)}'
        }
    
    # Validate each sequence
    valid_amino_acids = set(AA_PROPERTIES.keys())
    
    for i, seq in enumerate(sequences):
        if not isinstance(seq, str):
            return {'valid': False, 'error': f'Sequence {i+1} must be a string, got {type(seq).__name__}'}
        
        if len(seq.strip()) == 0:
            return {'valid': False, 'error': f'Sequence {i+1} cannot be empty'}
        
        if len(seq.strip()) > 10000:  # Reasonable upper limit
            return {'valid': False, 'error': f'Sequence {i+1} is too long (>10000 amino acids)'}
        
        # Check for invalid amino acids
        seq_upper = seq.upper().strip()
        invalid_chars = set(seq_upper) - valid_amino_acids
        if invalid_chars:
            return {
                'valid': False, 
                'error': f'Sequence {i+1} contains invalid amino acids: {sorted(invalid_chars)}'
            }
    
    # Validate optional boolean parameters
    for param in ['include_hydropathy', 'include_charge_distribution']:
        if param in input_data:
            if not isinstance(input_data[param], bool):
                return {
                    'valid': False, 
                    'error': f'Parameter {param} must be a boolean, got {type(input_data[param]).__name__}'
                }
    
    return {'valid': True}


def analyze_peptide(
    sequence: str, 
    include_hydropathy: bool = True, 
    include_charge_distribution: bool = False
) -> Dict[str, Any]:
    """
    Comprehensive analysis of a single peptide sequence.
    
    Args:
        sequence (str): Amino acid sequence in single-letter code
        include_hydropathy (bool): Calculate hydropathy-related properties
        include_charge_distribution (bool): Calculate charge at different pH values
        
    Returns:
        Dict[str, Any]: Analysis results containing all calculated properties
    """
    if not sequence:
        raise ValueError("Sequence cannot be empty")
    
    # Initialize result dictionary
    result = {
        'sequence': sequence,
        'length': len(sequence)
    }
    
    try:
        # Core properties (always calculated)
        result['molecular_weight'] = round(calculate_molecular_weight(sequence), 2)
        result['isoelectric_point'] = round(calculate_isoelectric_point(sequence), 2)
        result['net_charge_ph7'] = round(calculate_net_charge(sequence, 7.0), 2)
        result['aromaticity'] = round(calculate_aromaticity(sequence), 3)
        result['instability_index'] = round(calculate_instability_index(sequence), 2)
        
        # Add stability classification
        result['stability_classification'] = 'stable' if result['instability_index'] < 40 else 'unstable'
        
        # Optional hydropathy calculations
        if include_hydropathy:
            hydrophobicity = calculate_hydrophobicity(sequence)
            result['hydrophobicity'] = round(hydrophobicity, 2)
            result['gravy'] = round(hydrophobicity / len(sequence), 3)  # Grand Average of Hydropathy
            
            # Hydropathy classification
            if result['gravy'] > 0:
                result['hydropathy_class'] = 'hydrophobic'
            elif result['gravy'] < -0.5:
                result['hydropathy_class'] = 'hydrophilic'
            else:
                result['hydropathy_class'] = 'neutral'
        
        # Optional charge distribution
        if include_charge_distribution:
            charge_distribution = {}
            ph_values = [3.0, 5.0, 7.0, 9.0, 11.0]
            
            for ph in ph_values:
                charge_distribution[f'pH_{ph}'] = round(calculate_net_charge(sequence, ph), 2)
            
            result['charge_distribution'] = charge_distribution
            
            # Find approximate pI from charge distribution
            result['charge_analysis'] = {
                'most_positive_ph': min(ph_values, key=lambda ph: charge_distribution[f'pH_{ph}']),
                'most_negative_ph': max(ph_values, key=lambda ph: charge_distribution[f'pH_{ph}']),
                'zero_charge_ph_range': [
                    ph for ph in ph_values 
                    if abs(charge_distribution[f'pH_{ph}']) < 0.1
                ]
            }
        
        # Additional amino acid composition analysis
        result['composition'] = calculate_aa_composition(sequence)
        
    except Exception as e:
        logger.error(f"Error analyzing peptide {sequence}: {str(e)}")
        raise RuntimeError(f"Analysis failed for sequence {sequence}: {str(e)}")
    
    return result


def calculate_molecular_weight(sequence: str) -> float:
    """
    Calculate the molecular weight of a peptide.
    
    Accounts for peptide bond formation by subtracting water molecules.
    
    Args:
        sequence (str): Amino acid sequence
        
    Returns:
        float: Molecular weight in Daltons
    """
    if not sequence:
        return 0.0
    
    # Water molecular weight (lost during peptide bond formation)
    water_mw = 18.015
    
    # Sum individual amino acid molecular weights
    total_mw = sum(AA_PROPERTIES[aa][0] for aa in sequence)
    
    # Subtract water molecules lost in peptide bond formation
    # (n-1 peptide bonds for n amino acids)
    peptide_mw = total_mw - (len(sequence) - 1) * water_mw
    
    return peptide_mw


def calculate_net_charge(sequence: str, ph: float) -> float:
    """
    Calculate net charge of peptide at given pH using Henderson-Hasselbalch equation.
    
    Args:
        sequence (str): Amino acid sequence
        ph (float): pH value for calculation
        
    Returns:
        float: Net charge at specified pH
    """
    if not sequence:
        return 0.0
    
    charge = 0.0
    
    # N-terminus contribution (always positive)
    # Using average pKa for alpha-amino group
    pka_nterm = 9.69
    charge += 1 / (1 + 10**(ph - pka_nterm))
    
    # C-terminus contribution (always negative) 
    # Using average pKa for carboxyl group
    pka_cterm = 2.34
    charge -= 1 / (1 + 10**(pka_cterm - ph))
    
    # Side chain contributions
    for aa in sequence:
        pka_side = AA_PROPERTIES[aa][3]  # Side chain pKa
        
        if pka_side is not None:
            if aa in ['K', 'R', 'H']:  # Basic residues (positive when protonated)
                charge += 1 / (1 + 10**(ph - pka_side))
            elif aa in ['D', 'E', 'C', 'Y']:  # Acidic residues (negative when deprotonated)
                charge -= 1 / (1 + 10**(pka_side - ph))
    
    return charge


def calculate_isoelectric_point(sequence: str) -> float:
    """
    Calculate isoelectric point (pI) using bisection method.
    
    The pI is the pH at which the peptide has zero net charge.
    
    Args:
        sequence (str): Amino acid sequence
        
    Returns:
        float: Isoelectric point
    """
    if not sequence:
        return 7.0  # Neutral pH for empty sequence
    
    # Binary search for pH where net charge ≈ 0
    ph_low, ph_high = 0.0, 14.0
    tolerance = 0.01
    max_iterations = 100
    
    for _ in range(max_iterations):
        if ph_high - ph_low <= tolerance:
            break
        
        ph_mid = (ph_low + ph_high) / 2
        charge = calculate_net_charge(sequence, ph_mid)
        
        if abs(charge) < 0.001:  # Close enough to zero
            return ph_mid
        elif charge > 0:
            ph_low = ph_mid  # Net positive, increase pH
        else:
            ph_high = ph_mid  # Net negative, decrease pH
    
    return (ph_low + ph_high) / 2


def calculate_hydrophobicity(sequence: str) -> float:
    """
    Calculate total hydrophobicity using Kyte-Doolittle scale.
    
    Args:
        sequence (str): Amino acid sequence
        
    Returns:
        float: Total hydrophobicity value
    """
    if not sequence:
        return 0.0
    
    return sum(AA_PROPERTIES[aa][4] for aa in sequence)


def calculate_aromaticity(sequence: str) -> float:
    """
    Calculate fraction of aromatic amino acids (F, W, Y).
    
    Args:
        sequence (str): Amino acid sequence
        
    Returns:
        float: Fraction of aromatic amino acids (0.0 to 1.0)
    """
    if not sequence:
        return 0.0
    
    aromatic_count = sum(1 for aa in sequence if AA_PROPERTIES[aa][5])
    return aromatic_count / len(sequence)


def calculate_instability_index(sequence: str) -> float:
    """
    Calculate instability index based on dipeptide frequencies.
    
    Based on Guruprasad et al. (1990). A protein with instability index > 40
    is predicted to be unstable in a test tube.
    
    Args:
        sequence (str): Amino acid sequence
        
    Returns:
        float: Instability index
    """
    if len(sequence) < 2:
        return 0.0
    
    # Calculate weighted score based on dipeptide frequencies
    score = 0.0
    dipeptide_count = 0
    
    for i in range(len(sequence) - 1):
        dipeptide = sequence[i:i+2]
        
        # Use known weight if available, otherwise use neutral value
        weight = INSTABILITY_WEIGHTS.get(dipeptide, 1.0)
        score += weight
        dipeptide_count += 1
    
    # Normalize by sequence length (Guruprasad formula)
    if dipeptide_count == 0:
        return 0.0
    
    instability_index = (10.0 / len(sequence)) * score
    
    return max(0.0, instability_index)  # Ensure non-negative


def calculate_aa_composition(sequence: str) -> Dict[str, float]:
    """
    Calculate amino acid composition as percentages.
    
    Args:
        sequence (str): Amino acid sequence
        
    Returns:
        Dict[str, float]: Amino acid frequencies as percentages
    """
    if not sequence:
        return {}
    
    composition = {}
    total_length = len(sequence)
    
    for aa in AA_PROPERTIES.keys():
        count = sequence.count(aa)
        composition[aa] = round((count / total_length) * 100, 1)
    
    return composition


def generate_summary(peptide_properties: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate comprehensive summary statistics from peptide analysis results.
    
    Args:
        peptide_properties (List[Dict]): List of peptide analysis results
        
    Returns:
        Dict[str, Any]: Summary statistics and aggregate data
    """
    if not peptide_properties:
        return {'total_peptides': 0, 'valid_peptides': 0, 'error_count': 0}
    
    # Separate valid peptides from errors
    valid_peptides = [p for p in peptide_properties if 'error' not in p]
    error_count = len(peptide_properties) - len(valid_peptides)
    
    if not valid_peptides:
        return {
            'total_peptides': len(peptide_properties),
            'valid_peptides': 0,
            'error_count': error_count,
            'errors': [p.get('error', 'Unknown error') for p in peptide_properties if 'error' in p]
        }
    
    # Calculate basic statistics
    lengths = [p['length'] for p in valid_peptides]
    molecular_weights = [p['molecular_weight'] for p in valid_peptides]
    isoelectric_points = [p['isoelectric_point'] for p in valid_peptides]
    net_charges = [p['net_charge_ph7'] for p in valid_peptides]
    aromaticities = [p['aromaticity'] for p in valid_peptides]
    instability_indices = [p['instability_index'] for p in valid_peptides]
    
    # Length distribution
    length_counter = Counter(lengths)
    length_distribution = {str(k): v for k, v in sorted(length_counter.items())}
    
    # Overall amino acid frequency
    aa_counter = Counter()
    total_amino_acids = 0
    
    for peptide in valid_peptides:
        sequence = peptide['sequence']
        aa_counter.update(sequence)
        total_amino_acids += len(sequence)
    
    aa_frequency = {
        aa: round((count / total_amino_acids) * 100, 2)
        for aa, count in sorted(aa_counter.items())
    } if total_amino_acids > 0 else {}
    
    # Statistical measures
    summary = {
        'total_peptides': len(peptide_properties),
        'valid_peptides': len(valid_peptides),
        'error_count': error_count,
        'success_rate': round(len(valid_peptides) / len(peptide_properties), 3),
        
        # Length statistics
        'length_statistics': {
            'min': min(lengths),
            'max': max(lengths),
            'mean': round(sum(lengths) / len(lengths), 1),
            'median': sorted(lengths)[len(lengths) // 2],
            'distribution': length_distribution
        },
        
        # Molecular weight statistics
        'molecular_weight_statistics': {
            'min': round(min(molecular_weights), 2),
            'max': round(max(molecular_weights), 2),
            'mean': round(sum(molecular_weights) / len(molecular_weights), 2),
            'median': round(sorted(molecular_weights)[len(molecular_weights) // 2], 2)
        },
        
        # Chemical properties averages
        'average_properties': {
            'isoelectric_point': round(sum(isoelectric_points) / len(isoelectric_points), 2),
            'net_charge_ph7': round(sum(net_charges) / len(net_charges), 2),
            'aromaticity': round(sum(aromaticities) / len(aromaticities), 3),
            'instability_index': round(sum(instability_indices) / len(instability_indices), 2)
        },
        
        # Stability analysis
        'stability_analysis': {
            'stable_count': sum(1 for p in valid_peptides if p.get('instability_index', 0) < 40),
            'unstable_count': sum(1 for p in valid_peptides if p.get('instability_index', 0) >= 40),
            'percent_unstable': round(
                sum(1 for p in valid_peptides if p.get('instability_index', 0) >= 40) / len(valid_peptides) * 100,
                1
            )
        },
        
        # Amino acid composition
        'amino_acid_frequency': aa_frequency
    }
    
    # Add hydropathy statistics if available
    hydropathies = [p.get('gravy') for p in valid_peptides if 'gravy' in p]
    if hydropathies and None not in hydropathies:
        summary['hydropathy_statistics'] = {
            'min': round(min(hydropathies), 3),
            'max': round(max(hydropathies), 3),
            'mean': round(sum(hydropathies) / len(hydropathies), 3),
            'hydrophobic_count': sum(1 for gravy in hydropathies if gravy > 0),
            'hydrophilic_count': sum(1 for gravy in hydropathies if gravy < -0.5)
        }
    
    return summary


def create_error_response(error_message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        error_message (str): Error description
        metadata (Dict, optional): Additional error metadata
        
    Returns:
        Dict[str, Any]: Standardized error response
    """
    response = {
        'status': 'error',
        'error': error_message,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    if metadata:
        response['metadata'] = metadata
    
    return response


def main():
    """
    Main function for local testing and development.
    
    Loads sample input data and runs the analysis module.
    """
    # Sample test data
    test_input = {
        'peptide_sequences': [
            'SIINFEKL',     # OVA peptide (8 aa)
            'GILGFVFTL',    # Flu M1 peptide (9 aa)
            'YLQPRTFLL',    # HBV core peptide (9 aa)
            'FLPSDFFPSV',   # HBV pol peptide (10 aa)
            'GLCTLVAML',    # BMLF1 peptide (9 aa)
            'MLLSVPLLL',    # Test peptide (9 aa)
            'KVAELVHFL',    # Another test peptide (9 aa)
        ],
        'include_hydropathy': True,
        'include_charge_distribution': True
    }
    
    test_context = {
        'job_id': 'test-execution-' + str(int(datetime.utcnow().timestamp())),
        'user_id': 'test-user',
        'organization_id': 'test-org'
    }
    
    print(f"🧬 Running Simple Peptide Analyzer v{MODULE_VERSION}")
    print(f"📊 Testing with {len(test_input['peptide_sequences'])} peptide sequences")
    print("-" * 60)
    
    # Execute the analysis
    result = execute(test_input, test_context)
    
    # Display results
    if result['status'] == 'success':
        print("✅ Analysis completed successfully!")
        print(f"⏱️  Execution time: {result['metadata']['execution_time']:.2f} seconds")
        print(f"📈 Success rate: {result['summary']['success_rate']:.1%}")
        print(f"🔬 Average molecular weight: {result['summary']['molecular_weight_statistics']['mean']:.1f} Da")
        print(f"⚡ Average instability index: {result['summary']['average_properties']['instability_index']:.1f}")
        print()
        
        # Show individual results
        print("Individual peptide results:")
        for i, peptide in enumerate(result['peptide_properties'][:3]):  # Show first 3
            if 'error' not in peptide:
                print(f"  {i+1}. {peptide['sequence']} ({peptide['length']} aa)")
                print(f"     MW: {peptide['molecular_weight']:.1f} Da, pI: {peptide['isoelectric_point']:.1f}")
                print(f"     Stability: {peptide['stability_classification']}")
        
        if len(result['peptide_properties']) > 3:
            print(f"     ... and {len(result['peptide_properties']) - 3} more peptides")
        
    else:
        print("❌ Analysis failed!")
        print(f"Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("Full JSON output:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()