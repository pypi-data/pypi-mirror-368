"""
Data access utilities for HLA-Compass modules
"""

import logging
from typing import Any, Union
from datetime import datetime
import pandas as pd


logger = logging.getLogger(__name__)


class DataAccessError(Exception):
    """Error accessing HLA-Compass data"""
    pass


class BaseData:
    """Base class for data access"""
    
    def __init__(self, api_client):
        """
        Initialize data access with API client.
        
        Args:
            api_client: API client from execution context
        """
        self.api = api_client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _handle_api_error(self, error: Exception, operation: str):
        """Handle API errors consistently"""
        self.logger.error(f"API error during {operation}: {error}")
        raise DataAccessError(f"Failed to {operation}: {str(error)}")


class PeptideData(BaseData):
    """Access and query peptide data"""
    
    def search(self,
              sequence: str | None = None,
              min_length: int | None = None,
              max_length: int | None = None,
              mass: float | None = None,
              mass_tolerance: float | None = None,
              modifications: list[str] | None = None,
              limit: int = 1000,
              offset: int = 0) -> list[dict[str, Any]]:
        """
        Search peptides with various filters.
        
        Args:
            sequence: Peptide sequence (supports wildcards: X for any amino acid)
            min_length: Minimum peptide length
            max_length: Maximum peptide length
            mass: Target mass for mass-based search
            mass_tolerance: Mass tolerance (Da or ppm)
            modifications: List of modifications to filter by
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of peptide dictionaries
        """
        try:
            filters = {}
            
            if sequence:
                filters['sequence'] = sequence
            if min_length is not None:
                filters['min_length'] = min_length
            if max_length is not None:
                filters['max_length'] = max_length
            if mass is not None:
                filters['mass'] = mass
                filters['mass_tolerance'] = mass_tolerance or 0.01
            if modifications:
                filters['modifications'] = modifications
                
            self.logger.debug(f"Searching peptides with filters: {filters}")
            
            result = self.api.get_peptides(
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            self.logger.info(f"Found {len(result)} peptides")
            return result
            
        except Exception as e:
            self._handle_api_error(e, "search peptides")
    
    def get_by_id(self, peptide_id: str) -> dict[str, Any]:
        """
        Get peptide by ID.
        
        Args:
            peptide_id: Peptide identifier
            
        Returns:
            Peptide dictionary
        """
        try:
            return self.api.get_peptide(peptide_id)
        except Exception as e:
            self._handle_api_error(e, f"get peptide {peptide_id}")
    
    def get_samples(self, peptide_id: str) -> list[dict[str, Any]]:
        """
        Get all samples where a peptide was found.
        
        Args:
            peptide_id: Peptide identifier
            
        Returns:
            List of sample associations with abundance data
        """
        try:
            return self.api.get_peptide_samples(peptide_id)
        except Exception as e:
            self._handle_api_error(e, f"get samples for peptide {peptide_id}")
    
    def get_proteins(self, peptide_id: str) -> list[dict[str, Any]]:
        """
        Get proteins containing a peptide.
        
        Args:
            peptide_id: Peptide identifier
            
        Returns:
            List of protein associations
        """
        try:
            return self.api.get_peptide_proteins(peptide_id)
        except Exception as e:
            self._handle_api_error(e, f"get proteins for peptide {peptide_id}")
    
    def search_by_mass(self,
                      mass: float,
                      tolerance: float = 0.01,
                      unit: str = 'Da') -> list[dict[str, Any]]:
        """
        Search peptides by mass.
        
        Args:
            mass: Target mass
            tolerance: Mass tolerance
            unit: Unit ('Da' or 'ppm')
            
        Returns:
            List of matching peptides
        """
        try:
            return self.api.search_peptides_by_mass(
                mass=mass,
                tolerance=tolerance,
                unit=unit
            )
        except Exception as e:
            self._handle_api_error(e, "search peptides by mass")
    
    def to_dataframe(self, peptides: list[dict[str, Any]]) -> pd.DataFrame:
        """
        Convert peptide list to pandas DataFrame.
        
        Args:
            peptides: List of peptide dictionaries
            
        Returns:
            DataFrame with peptide data
        """
        if not peptides:
            return pd.DataFrame()
            
        df = pd.DataFrame(peptides)
        
        # Ensure standard columns exist
        standard_cols = ['id', 'sequence', 'length', 'mass', 'charge']
        for col in standard_cols:
            if col not in df.columns:
                df[col] = None
                
        return df


class ProteinData(BaseData):
    """Access and query protein data"""
    
    def search(self,
              accession: str | None = None,
              gene_name: str | None = None,
              organism: str | None = None,
              description: str | None = None,
              min_length: int | None = None,
              max_length: int | None = None,
              limit: int = 1000,
              offset: int = 0) -> list[dict[str, Any]]:
        """
        Search proteins with various filters.
        
        Args:
            accession: UniProt accession number
            gene_name: Gene name (supports wildcards)
            organism: Organism name or taxonomy ID
            description: Text search in protein description
            min_length: Minimum protein length
            max_length: Maximum protein length
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of protein dictionaries
        """
        try:
            filters = {}
            
            if accession:
                filters['accession'] = accession
            if gene_name:
                filters['gene_name'] = gene_name
            if organism:
                filters['organism'] = organism
            if description:
                filters['description'] = description
            if min_length is not None:
                filters['min_length'] = min_length
            if max_length is not None:
                filters['max_length'] = max_length
                
            self.logger.debug(f"Searching proteins with filters: {filters}")
            
            result = self.api.get_proteins(
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            self.logger.info(f"Found {len(result)} proteins")
            return result
            
        except Exception as e:
            self._handle_api_error(e, "search proteins")
    
    def get_by_id(self, protein_id: str) -> dict[str, Any]:
        """
        Get protein by ID.
        
        Args:
            protein_id: Protein identifier
            
        Returns:
            Protein dictionary with full sequence
        """
        try:
            return self.api.get_protein(protein_id)
        except Exception as e:
            self._handle_api_error(e, f"get protein {protein_id}")
    
    def get_peptides(self, 
                    protein_id: str,
                    unique_only: bool = False) -> list[dict[str, Any]]:
        """
        Get all peptides from a protein.
        
        Args:
            protein_id: Protein identifier
            unique_only: Return only peptides unique to this protein
            
        Returns:
            List of peptide dictionaries
        """
        try:
            result = self.api.get_protein_peptides(protein_id)
            
            if unique_only:
                # Filter for unique peptides
                result = [p for p in result if p.get('is_unique', False)]
                
            return result
        except Exception as e:
            self._handle_api_error(e, f"get peptides for protein {protein_id}")
    
    def get_coverage(self, protein_id: str) -> dict[str, Any]:
        """
        Get sequence coverage information for a protein.
        
        Args:
            protein_id: Protein identifier
            
        Returns:
            Coverage statistics and covered regions
        """
        try:
            return self.api.get_protein_coverage(protein_id)
        except Exception as e:
            self._handle_api_error(e, f"get coverage for protein {protein_id}")


class SampleData(BaseData):
    """Access and query sample data"""
    
    def search(self,
              sample_type: str | None = None,
              tissue: str | None = None,
              disease: str | None = None,
              cell_line: str | None = None,
              treatment: str | None = None,
              experiment_type: str | None = None,
              limit: int = 1000,
              offset: int = 0) -> list[dict[str, Any]]:
        """
        Search samples with various filters.
        
        Args:
            sample_type: Type of sample (e.g., 'tissue', 'cell_line', 'fluid')
            tissue: Tissue type
            disease: Disease association
            cell_line: Cell line name
            treatment: Treatment condition
            experiment_type: Type of experiment
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of sample dictionaries
        """
        try:
            filters = {}
            
            if sample_type:
                filters['sample_type'] = sample_type
            if tissue:
                filters['tissue'] = tissue
            if disease:
                filters['disease'] = disease
            if cell_line:
                filters['cell_line'] = cell_line
            if treatment:
                filters['treatment'] = treatment
            if experiment_type:
                filters['experiment_type'] = experiment_type
                
            self.logger.debug(f"Searching samples with filters: {filters}")
            
            result = self.api.get_samples(
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            self.logger.info(f"Found {len(result)} samples")
            return result
            
        except Exception as e:
            self._handle_api_error(e, "search samples")
    
    def get_by_id(self, sample_id: str) -> dict[str, Any]:
        """
        Get sample by ID.
        
        Args:
            sample_id: Sample identifier
            
        Returns:
            Sample dictionary with full metadata
        """
        try:
            return self.api.get_sample(sample_id)
        except Exception as e:
            self._handle_api_error(e, f"get sample {sample_id}")
    
    def get_peptides(self, 
                    sample_id: str,
                    min_abundance: float | None = None) -> list[dict[str, Any]]:
        """
        Get all peptides found in a sample.
        
        Args:
            sample_id: Sample identifier
            min_abundance: Minimum abundance threshold
            
        Returns:
            List of peptides with abundance data
        """
        try:
            result = self.api.get_sample_peptides(sample_id)
            
            if min_abundance is not None:
                result = [
                    p for p in result 
                    if p.get('abundance', 0) >= min_abundance
                ]
                
            return result
        except Exception as e:
            self._handle_api_error(e, f"get peptides for sample {sample_id}")
    
    def compare_samples(self,
                       sample_ids: list[str],
                       metric: str = 'jaccard') -> dict[str, Any]:
        """
        Compare peptide overlap between samples.
        
        Args:
            sample_ids: List of sample IDs to compare
            metric: Comparison metric ('jaccard', 'overlap', 'correlation')
            
        Returns:
            Comparison results with similarity matrix
        """
        try:
            return self.api.compare_samples(
                sample_ids=sample_ids,
                metric=metric
            )
        except Exception as e:
            self._handle_api_error(e, "compare samples")


class HLAData(BaseData):
    """Access HLA-related data"""
    
    def get_alleles(self, 
                   locus: str | None = None,
                   resolution: str = '2-digit') -> list[str]:
        """
        Get list of HLA alleles.
        
        Args:
            locus: HLA locus (e.g., 'A', 'B', 'C', 'DRB1')
            resolution: Allele resolution ('2-digit' or '4-digit')
            
        Returns:
            List of HLA allele names
        """
        try:
            return self.api.get_hla_alleles(
                locus=locus,
                resolution=resolution
            )
        except Exception as e:
            self._handle_api_error(e, "get HLA alleles")
    
    def get_frequencies(self,
                       population: str | None = None) -> dict[str, float]:
        """
        Get HLA allele frequencies.
        
        Args:
            population: Population name (e.g., 'European', 'African', 'Asian')
            
        Returns:
            Dictionary of allele: frequency pairs
        """
        try:
            return self.api.get_hla_frequencies(population=population)
        except Exception as e:
            self._handle_api_error(e, "get HLA frequencies")
    
    def predict_binding(self,
                       peptides: list[str],
                       alleles: list[str],
                       method: str = 'netmhcpan') -> list[dict[str, Any]]:
        """
        Predict HLA-peptide binding.
        
        Args:
            peptides: List of peptide sequences
            alleles: List of HLA alleles
            method: Prediction method
            
        Returns:
            List of predictions with scores
        """
        try:
            return self.api.predict_hla_binding(
                peptides=peptides,
                alleles=alleles,
                method=method
            )
        except Exception as e:
            self._handle_api_error(e, "predict HLA binding")