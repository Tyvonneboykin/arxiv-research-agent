#!/usr/bin/env python3
"""
Cache Manager for ArXiv Research Agent
=====================================

Manages caching of analyzed papers to avoid duplicate token usage and improve performance.
"""

import json
import logging
import pickle
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import asdict
import hashlib

from arxiv_fetcher import ArxivPaper
from claude_analyzer import PaperAnalysis


class CacheManager:
    """Manages caching of paper analyses and metadata"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24 * 7):  # 7 days default
        self.cache_dir = Path(cache_dir)
        self.ttl_hours = ttl_hours
        self.logger = logging.getLogger(__name__)
        
        # Create cache directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        (self.cache_dir / "papers").mkdir(exist_ok=True)
        (self.cache_dir / "analyses").mkdir(exist_ok=True)
        (self.cache_dir / "metadata").mkdir(exist_ok=True)
        
        # Cache files
        self.analyzed_papers_file = self.cache_dir / "metadata" / "analyzed_papers.json"
        self.paper_hashes_file = self.cache_dir / "metadata" / "paper_hashes.json"
        
        # Load existing cache metadata
        self.analyzed_papers: Dict[str, Dict[str, Any]] = self._load_analyzed_papers()
        self.paper_hashes: Dict[str, str] = self._load_paper_hashes()
        
        self.logger.info(f"📂 Cache initialized with {len(self.analyzed_papers)} analyzed papers")
    
    def _load_analyzed_papers(self) -> Dict[str, Dict[str, Any]]:
        """Load metadata of previously analyzed papers"""
        try:
            if self.analyzed_papers_file.exists():
                with open(self.analyzed_papers_file, 'r') as f:
                    data = json.load(f)
                # Clean expired entries
                return self._clean_expired_entries(data)
            return {}
        except Exception as e:
            self.logger.warning(f"Failed to load analyzed papers cache: {e}")
            return {}
    
    def _load_paper_hashes(self) -> Dict[str, str]:
        """Load paper content hashes to detect changes"""
        try:
            if self.paper_hashes_file.exists():
                with open(self.paper_hashes_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.warning(f"Failed to load paper hashes: {e}")
            return {}
    
    def _clean_expired_entries(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Remove expired cache entries"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.ttl_hours)
        cleaned = {}
        
        for paper_id, metadata in data.items():
            try:
                analyzed_time = datetime.fromisoformat(metadata['analyzed_at'])
                if analyzed_time > cutoff_time:
                    cleaned[paper_id] = metadata
                else:
                    # Clean up associated files
                    self._remove_paper_files(paper_id)
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Invalid cache entry for {paper_id}: {e}")
                continue
        
        if len(cleaned) != len(data):
            self.logger.info(f"🧹 Cleaned {len(data) - len(cleaned)} expired cache entries")
        
        return cleaned
    
    def _remove_paper_files(self, paper_id: str):
        """Remove cached files for a paper"""
        try:
            paper_file = self.cache_dir / "papers" / f"{paper_id}.pkl"
            analysis_file = self.cache_dir / "analyses" / f"{paper_id}.pkl"
            
            if paper_file.exists():
                paper_file.unlink()
            if analysis_file.exists():
                analysis_file.unlink()
        except Exception as e:
            self.logger.warning(f"Failed to remove cache files for {paper_id}: {e}")
    
    def _calculate_paper_hash(self, paper: ArxivPaper) -> str:
        """Calculate hash of paper content to detect changes"""
        content = f"{paper.title}|{paper.abstract}|{paper.updated.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def is_paper_analyzed(self, paper: ArxivPaper) -> bool:
        """Check if paper has been analyzed recently and content hasn't changed"""
        paper_id = paper.id
        
        if paper_id not in self.analyzed_papers:
            return False
        
        # Check if content has changed
        current_hash = self._calculate_paper_hash(paper)
        stored_hash = self.paper_hashes.get(paper_id)
        
        if stored_hash != current_hash:
            self.logger.info(f"📝 Paper {paper_id} content changed, will re-analyze")
            self._remove_from_cache(paper_id)
            return False
        
        # Check if analysis is still valid (not expired)
        metadata = self.analyzed_papers[paper_id]
        try:
            analyzed_time = datetime.fromisoformat(metadata['analyzed_at'])
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=self.ttl_hours)
            
            if analyzed_time <= cutoff_time:
                self.logger.info(f"⏰ Analysis for {paper_id} expired, will re-analyze")
                self._remove_from_cache(paper_id)
                return False
            
            return True
            
        except (KeyError, ValueError) as e:
            self.logger.warning(f"Invalid timestamp for {paper_id}: {e}")
            self._remove_from_cache(paper_id)
            return False
    
    def get_cached_analysis(self, paper_id: str) -> Optional[PaperAnalysis]:
        """Retrieve cached analysis for a paper"""
        if paper_id not in self.analyzed_papers:
            return None
        
        try:
            analysis_file = self.cache_dir / "analyses" / f"{paper_id}.pkl"
            if analysis_file.exists():
                with open(analysis_file, 'rb') as f:
                    analysis = pickle.load(f)
                self.logger.debug(f"📚 Retrieved cached analysis for {paper_id}")
                return analysis
            else:
                # Metadata exists but file doesn't - clean up
                self._remove_from_cache(paper_id)
                return None
                
        except Exception as e:
            self.logger.warning(f"Failed to load cached analysis for {paper_id}: {e}")
            self._remove_from_cache(paper_id)
            return None
    
    def cache_analysis(self, paper: ArxivPaper, analysis: PaperAnalysis):
        """Cache paper and its analysis"""
        paper_id = paper.id
        
        try:
            # Save paper
            paper_file = self.cache_dir / "papers" / f"{paper_id}.pkl"
            with open(paper_file, 'wb') as f:
                pickle.dump(paper, f)
            
            # Save analysis
            analysis_file = self.cache_dir / "analyses" / f"{paper_id}.pkl"
            with open(analysis_file, 'wb') as f:
                pickle.dump(analysis, f)
            
            # Update metadata
            self.analyzed_papers[paper_id] = {
                'analyzed_at': datetime.now(timezone.utc).isoformat(),
                'title': paper.title[:100],  # Truncated for readability
                'significance_score': analysis.significance_score,
                'categories': paper.categories[:3]  # First 3 categories
            }
            
            # Update hash
            self.paper_hashes[paper_id] = self._calculate_paper_hash(paper)
            
            # Save metadata to disk
            self._save_metadata()
            
            self.logger.debug(f"💾 Cached analysis for paper {paper_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to cache analysis for {paper_id}: {e}")
    
    def _remove_from_cache(self, paper_id: str):
        """Remove paper from cache"""
        if paper_id in self.analyzed_papers:
            del self.analyzed_papers[paper_id]
        if paper_id in self.paper_hashes:
            del self.paper_hashes[paper_id]
        
        self._remove_paper_files(paper_id)
        self._save_metadata()
    
    def _save_metadata(self):
        """Save cache metadata to disk"""
        try:
            with open(self.analyzed_papers_file, 'w') as f:
                json.dump(self.analyzed_papers, f, indent=2)
            
            with open(self.paper_hashes_file, 'w') as f:
                json.dump(self.paper_hashes, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save cache metadata: {e}")
    
    def filter_new_papers(self, papers: List[ArxivPaper]) -> List[ArxivPaper]:
        """Filter out papers that have already been analyzed"""
        new_papers = []
        cached_count = 0
        
        for paper in papers:
            if not self.is_paper_analyzed(paper):
                new_papers.append(paper)
            else:
                cached_count += 1
        
        self.logger.info(f"🔍 Found {len(new_papers)} new papers, {cached_count} already analyzed")
        return new_papers
    
    def get_cached_analyses(self, paper_ids: List[str]) -> List[PaperAnalysis]:
        """Retrieve multiple cached analyses"""
        analyses = []
        for paper_id in paper_ids:
            analysis = self.get_cached_analysis(paper_id)
            if analysis:
                analyses.append(analysis)
        return analyses
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_papers = len(self.analyzed_papers)
        cache_size_mb = 0
        
        try:
            # Calculate cache directory size
            for file_path in self.cache_dir.rglob("*"):
                if file_path.is_file():
                    cache_size_mb += file_path.stat().st_size
            cache_size_mb = cache_size_mb / (1024 * 1024)  # Convert to MB
        except Exception:
            cache_size_mb = 0
        
        # Count recent analyses (last 24 hours)
        recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        recent_count = 0
        
        for metadata in self.analyzed_papers.values():
            try:
                analyzed_time = datetime.fromisoformat(metadata['analyzed_at'])
                if analyzed_time > recent_cutoff:
                    recent_count += 1
            except (KeyError, ValueError):
                continue
        
        return {
            'total_cached_papers': total_papers,
            'recent_analyses_24h': recent_count,
            'cache_size_mb': round(cache_size_mb, 2),
            'ttl_hours': self.ttl_hours,
            'cache_directory': str(self.cache_dir)
        }
    
    def cleanup_cache(self, force: bool = False):
        """Clean up expired cache entries and optimize storage"""
        initial_count = len(self.analyzed_papers)
        
        if force:
            # Force cleanup of all entries
            self.analyzed_papers.clear()
            self.paper_hashes.clear()
            
            # Remove all cache files
            for file_path in self.cache_dir.rglob("*.pkl"):
                try:
                    file_path.unlink()
                except Exception as e:
                    self.logger.warning(f"Failed to remove {file_path}: {e}")
        else:
            # Normal cleanup of expired entries
            self.analyzed_papers = self._clean_expired_entries(self.analyzed_papers)
        
        self._save_metadata()
        
        removed_count = initial_count - len(self.analyzed_papers)
        self.logger.info(f"🧹 Cache cleanup complete. Removed {removed_count} entries")
        
        return {
            'removed_entries': removed_count,
            'remaining_entries': len(self.analyzed_papers)
        }