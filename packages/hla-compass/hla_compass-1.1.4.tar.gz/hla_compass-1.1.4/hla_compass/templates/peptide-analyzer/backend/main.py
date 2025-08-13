"""
Peptide Analyzer Module

A ready-to-run HLA-Compass module that analyzes peptide sequences,
searches for similar peptides in the database, and predicts HLA binding affinity.
"""

from hla_compass import Module
from typing import Dict, Any, List
import re

class PeptideAnalyzer(Module):
    """
    Analyzes peptide sequences and predicts HLA binding affinity
    """
    
    # Standard amino acids
    AMINO_ACIDS = set('ACDEFGHIKLMNPQRSTVWY')
    
    # Hydrophobic amino acids
    HYDROPHOBIC = set('AVILMFYW')
    
    # Charged amino acids
    CHARGED = set('DEKRH')
    
    def __init__(self):
        """Initialize the peptide analyzer"""
        super().__init__()
        self.logger.info("PeptideAnalyzer module initialized")
    
    def validate_sequence(self, sequence: str) -> bool:
        """
        Validate that the sequence contains only valid amino acids
        
        Args:
            sequence: Peptide sequence to validate
            
        Returns:
            True if valid, False otherwise
        """
        sequence = sequence.upper().strip()
        return all(aa in self.AMINO_ACIDS for aa in sequence)
    
    def analyze_sequence(self, sequence: str) -> Dict[str, Any]:
        """
        Perform basic analysis on a peptide sequence
        
        Args:
            sequence: Peptide sequence to analyze
            
        Returns:
            Dictionary with sequence properties
        """
        sequence = sequence.upper().strip()
        
        # Calculate basic properties
        length = len(sequence)
        molecular_weight = self.calculate_molecular_weight(sequence)
        
        # Calculate composition
        hydrophobic_count = sum(1 for aa in sequence if aa in self.HYDROPHOBIC)
        charged_count = sum(1 for aa in sequence if aa in self.CHARGED)
        
        hydrophobicity = (hydrophobic_count / length) * 100 if length > 0 else 0
        charge_ratio = (charged_count / length) * 100 if length > 0 else 0
        
        return {
            'sequence': sequence,
            'length': length,
            'molecular_weight': round(molecular_weight, 2),
            'hydrophobicity': round(hydrophobicity, 1),
            'charge_ratio': round(charge_ratio, 1),
            'hydrophobic_residues': hydrophobic_count,
            'charged_residues': charged_count,
            'composition': self.get_aa_composition(sequence)
        }
    
    def calculate_molecular_weight(self, sequence: str) -> float:
        """
        Calculate approximate molecular weight of a peptide
        
        Args:
            sequence: Peptide sequence
            
        Returns:
            Molecular weight in Daltons
        """
        # Average molecular weights of amino acids (in Daltons)
        mw_table = {
            'A': 89.09, 'R': 174.20, 'N': 132.12, 'D': 133.10,
            'C': 121.15, 'E': 147.13, 'Q': 146.15, 'G': 75.07,
            'H': 155.16, 'I': 131.17, 'L': 131.17, 'K': 146.19,
            'M': 149.21, 'F': 165.19, 'P': 115.13, 'S': 105.09,
            'T': 119.12, 'W': 204.23, 'Y': 181.19, 'V': 117.15
        }
        
        # Calculate total MW minus water molecules for peptide bonds
        mw = sum(mw_table.get(aa, 0) for aa in sequence)
        # Subtract water for each peptide bond
        mw -= (len(sequence) - 1) * 18.015 if len(sequence) > 1 else 0
        
        return mw
    
    def get_aa_composition(self, sequence: str) -> Dict[str, int]:
        """
        Get amino acid composition of a sequence
        
        Args:
            sequence: Peptide sequence
            
        Returns:
            Dictionary with amino acid counts
        """
        composition = {}
        for aa in sequence:
            composition[aa] = composition.get(aa, 0) + 1
        return composition
    
    def predict_hla_binding(self, sequence: str, hla_allele: str) -> Dict[str, Any]:
        """
        Simple HLA binding prediction based on sequence features
        This is a simplified example - real predictions would use ML models
        
        Args:
            sequence: Peptide sequence
            hla_allele: HLA allele
            
        Returns:
            Prediction results
        """
        # Simplified scoring based on known motifs
        score = 50.0  # Base score
        
        # HLA-A*02:01 prefers L at position 2 and V/L at C-terminus
        if hla_allele == 'HLA-A*02:01':
            if len(sequence) >= 2 and sequence[1] == 'L':
                score += 20
            if sequence[-1] in ['V', 'L']:
                score += 15
            # Penalize if too short or too long
            if len(sequence) < 8 or len(sequence) > 11:
                score -= 20
        
        # Normalize score to 0-100
        score = max(0, min(100, score))
        
        # Classification based on score
        if score >= 70:
            binding_class = 'Strong Binder'
        elif score >= 50:
            binding_class = 'Weak Binder'
        else:
            binding_class = 'Non-Binder'
        
        return {
            'hla_allele': hla_allele,
            'score': round(score, 2),
            'binding_class': binding_class,
            'percentile_rank': round(100 - score, 1)  # Simplified percentile
        }
    
    def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution function
        
        Args:
            input_data: Input containing sequence, HLA allele, and limit
            context: Execution context
            
        Returns:
            Analysis results
        """
        try:
            # Extract input parameters
            sequence = input_data.get('sequence', '').upper().strip()
            hla_allele = input_data.get('hla_allele', 'HLA-A*02:01')
            limit = input_data.get('limit', 10)
            
            # Validate sequence
            if not sequence:
                return self.error("No sequence provided")
            
            if not self.validate_sequence(sequence):
                return self.error(f"Invalid sequence: {sequence}. Use only standard amino acids.")
            
            if len(sequence) < 7 or len(sequence) > 15:
                return self.error("Sequence length should be between 7 and 15 amino acids")
            
            # Log the analysis
            self.logger.info(f"Analyzing peptide: {sequence} for {hla_allele}")
            
            # Perform sequence analysis
            analysis = self.analyze_sequence(sequence)
            
            # Search for similar peptides in database
            similar_peptides = []
            try:
                # Search for peptides with similar length
                peptides = self.peptides.search(
                    min_length=len(sequence) - 1,
                    max_length=len(sequence) + 1,
                    limit=limit * 2  # Get more to filter
                )
                
                # Calculate similarity and filter
                for peptide in peptides:
                    similarity = self.calculate_similarity(sequence, peptide.sequence)
                    if similarity > 0.3:  # At least 30% similar
                        similar_peptides.append({
                            'sequence': peptide.sequence,
                            'length': peptide.length,
                            'molecular_weight': peptide.molecular_weight,
                            'source': getattr(peptide, 'source', 'Unknown'),
                            'similarity': round(similarity * 100, 1)
                        })
                
                # Sort by similarity and limit
                similar_peptides = sorted(
                    similar_peptides, 
                    key=lambda x: x['similarity'], 
                    reverse=True
                )[:limit]
                
            except Exception as e:
                self.logger.warning(f"Database search failed: {e}")
                similar_peptides = []
            
            # Predict HLA binding
            prediction = self.predict_hla_binding(sequence, hla_allele)
            
            # Prepare response
            result = {
                'analysis': analysis,
                'similar_peptides': similar_peptides,
                'predictions': prediction,
                'metadata': {
                    'module': 'peptide-analyzer',
                    'version': '1.0.0',
                    'job_id': context.get('job_id', 'local')
                }
            }
            
            # Save results to storage if available
            try:
                self.storage.save(f"results/{context.get('job_id', 'local')}.json", result)
                self.logger.info("Results saved to storage")
            except:
                pass  # Storage might not be available in local testing
            
            return self.success(result)
            
        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}")
            return self.error(f"Analysis failed: {str(e)}")
    
    def calculate_similarity(self, seq1: str, seq2: str) -> float:
        """
        Calculate sequence similarity using simple identity matching
        
        Args:
            seq1: First sequence
            seq2: Second sequence
            
        Returns:
            Similarity score (0-1)
        """
        if not seq1 or not seq2:
            return 0.0
        
        # Simple identity-based similarity
        matches = sum(1 for a, b in zip(seq1, seq2) if a == b)
        max_len = max(len(seq1), len(seq2))
        
        return matches / max_len if max_len > 0 else 0.0


# Lambda handler for AWS Lambda execution
def lambda_handler(event, context):
    """AWS Lambda handler"""
    module = PeptideAnalyzer()
    return module.handle_lambda(event, context)