"""Advanced clustering algorithms for semantic chunking."""

from typing import Dict, List, Optional, Any, Union, Tuple
from abc import ABC, abstractmethod
import logging
import numpy as np
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Clustering algorithms
try:
    from sklearn.cluster import (
        AgglomerativeClustering, DBSCAN, KMeans, 
        SpectralClustering, OPTICS
    )
    from sklearn.metrics import (
        silhouette_score, calinski_harabasz_score, 
        davies_bouldin_score, adjusted_rand_score
    )
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available")

# Advanced clustering
try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False
    logging.warning("hdbscan not available")

try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False
    logging.warning("umap-learn not available")

# Optimization
try:
    from scipy.optimize import minimize
    from scipy.spatial.distance import pdist, squareform
    from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("scipy not available")

from ..core.config import ClusteringConfig
from .embeddings import EmbeddingResult


class ClusteringMethod(Enum):
    """Available clustering methods."""
    AGGLOMERATIVE = "agglomerative"
    DBSCAN = "dbscan"
    HDBSCAN = "hdbscan"
    KMEANS = "kmeans"
    SPECTRAL = "spectral"
    OPTICS = "optics"
    ENSEMBLE = "ensemble"
    ADAPTIVE = "adaptive"


@dataclass
class ClusteringResult:
    """Result of clustering operation."""
    labels: np.ndarray
    n_clusters: int
    method: str
    quality_metrics: Dict[str, float]
    cluster_centers: Optional[np.ndarray] = None
    cluster_sizes: Optional[List[int]] = None
    outliers: Optional[List[int]] = None
    processing_time: float = 0.0
    metadata: Dict[str, Any] = None


class ClusteringBase(ABC):
    """Base class for clustering algorithms."""
    
    def __init__(self, config: ClusteringConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.method_name = ""
    
    @abstractmethod
    def fit_predict(self, embeddings: np.ndarray) -> ClusteringResult:
        """Fit the clustering algorithm and predict cluster labels."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the clustering method is available."""
        pass
    
    def _calculate_quality_metrics(self, embeddings: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """Calculate clustering quality metrics."""
        metrics = {}
        
        if not SKLEARN_AVAILABLE:
            return metrics
        
        try:
            # Remove noise points for metric calculation
            valid_mask = labels >= 0
            if np.sum(valid_mask) < 2:
                return metrics
            
            valid_embeddings = embeddings[valid_mask]
            valid_labels = labels[valid_mask]
            
            # Only calculate if we have multiple clusters
            n_clusters = len(np.unique(valid_labels))
            if n_clusters > 1:
                metrics['silhouette_score'] = silhouette_score(valid_embeddings, valid_labels)
                metrics['calinski_harabasz_score'] = calinski_harabasz_score(valid_embeddings, valid_labels)
                metrics['davies_bouldin_score'] = davies_bouldin_score(valid_embeddings, valid_labels)
            
            metrics['n_clusters'] = n_clusters
            metrics['n_noise'] = np.sum(labels == -1)
            metrics['noise_ratio'] = metrics['n_noise'] / len(labels)
        
        except Exception as e:
            self.logger.warning(f"Failed to calculate quality metrics: {e}")
        
        return metrics
    
    def _get_cluster_info(self, labels: np.ndarray) -> Tuple[int, List[int], List[int]]:
        """Get cluster information."""
        unique_labels = np.unique(labels)
        n_clusters = len(unique_labels[unique_labels >= 0])  # Exclude noise (-1)
        
        cluster_sizes = []
        outliers = []
        
        for label in unique_labels:
            if label == -1:
                outliers = np.where(labels == label)[0].tolist()
            else:
                cluster_sizes.append(np.sum(labels == label))
        
        return n_clusters, cluster_sizes, outliers


class AgglomerativeClusterer(ClusteringBase):
    """Agglomerative clustering implementation."""
    
    def __init__(self, config: ClusteringConfig):
        super().__init__(config)
        self.method_name = "agglomerative"
    
    def is_available(self) -> bool:
        return SKLEARN_AVAILABLE
    
    def fit_predict(self, embeddings: np.ndarray) -> ClusteringResult:
        """Perform agglomerative clustering."""
        import time
        start_time = time.time()
        
        if not self.is_available():
            raise RuntimeError("scikit-learn is not available")
        
        try:
            # Determine number of clusters
            n_clusters = self._determine_n_clusters(embeddings)
            
            # Perform clustering
            clusterer = AgglomerativeClustering(
                n_clusters=n_clusters,
                linkage=self.config.agglomerative_linkage,
                metric=self.config.agglomerative_metric
            )
            
            labels = clusterer.fit_predict(embeddings)
            
            # Calculate metrics
            quality_metrics = self._calculate_quality_metrics(embeddings, labels)
            n_clusters_actual, cluster_sizes, outliers = self._get_cluster_info(labels)
            
            return ClusteringResult(
                labels=labels,
                n_clusters=n_clusters_actual,
                method=self.method_name,
                quality_metrics=quality_metrics,
                cluster_sizes=cluster_sizes,
                outliers=outliers,
                processing_time=time.time() - start_time,
                metadata={
                    "linkage": self.config.agglomerative_linkage,
                    "metric": self.config.agglomerative_metric,
                    "target_clusters": n_clusters
                }
            )
        
        except Exception as e:
            self.logger.error(f"Agglomerative clustering failed: {e}")
            raise
    
    def _determine_n_clusters(self, embeddings: np.ndarray) -> int:
        """Determine optimal number of clusters."""
        if self.config.n_clusters and self.config.n_clusters > 0:
            return self.config.n_clusters
        
        # Use elbow method or silhouette analysis
        n_samples = len(embeddings)
        max_clusters = min(self.config.max_clusters, n_samples // 2)
        
        if max_clusters < 2:
            return 2
        
        best_score = -1
        best_n_clusters = 2
        
        for n in range(2, max_clusters + 1):
            try:
                clusterer = AgglomerativeClustering(n_clusters=n)
                labels = clusterer.fit_predict(embeddings)
                score = silhouette_score(embeddings, labels)
                
                if score > best_score:
                    best_score = score
                    best_n_clusters = n
            
            except Exception:
                continue
        
        return best_n_clusters


class DBSCANClusterer(ClusteringBase):
    """DBSCAN clustering implementation."""
    
    def __init__(self, config: ClusteringConfig):
        super().__init__(config)
        self.method_name = "dbscan"
    
    def is_available(self) -> bool:
        return SKLEARN_AVAILABLE
    
    def fit_predict(self, embeddings: np.ndarray) -> ClusteringResult:
        """Perform DBSCAN clustering."""
        import time
        start_time = time.time()
        
        if not self.is_available():
            raise RuntimeError("scikit-learn is not available")
        
        try:
            # Optimize eps if not provided
            eps = self.config.dbscan_eps
            if eps is None:
                eps = self._optimize_eps(embeddings)
            
            # Perform clustering
            clusterer = DBSCAN(
                eps=eps,
                min_samples=self.config.dbscan_min_samples,
                metric=self.config.dbscan_metric
            )
            
            labels = clusterer.fit_predict(embeddings)
            
            # Calculate metrics
            quality_metrics = self._calculate_quality_metrics(embeddings, labels)
            n_clusters, cluster_sizes, outliers = self._get_cluster_info(labels)
            
            return ClusteringResult(
                labels=labels,
                n_clusters=n_clusters,
                method=self.method_name,
                quality_metrics=quality_metrics,
                cluster_sizes=cluster_sizes,
                outliers=outliers,
                processing_time=time.time() - start_time,
                metadata={
                    "eps": eps,
                    "min_samples": self.config.dbscan_min_samples,
                    "metric": self.config.dbscan_metric
                }
            )
        
        except Exception as e:
            self.logger.error(f"DBSCAN clustering failed: {e}")
            raise
    
    def _optimize_eps(self, embeddings: np.ndarray) -> float:
        """Optimize eps parameter using k-distance graph."""
        if not SKLEARN_AVAILABLE:
            return 0.5  # Default value
        
        try:
            from sklearn.neighbors import NearestNeighbors
            
            k = self.config.dbscan_min_samples
            neighbors = NearestNeighbors(n_neighbors=k)
            neighbors.fit(embeddings)
            distances, _ = neighbors.kneighbors(embeddings)
            
            # Sort distances to k-th nearest neighbor
            k_distances = np.sort(distances[:, k-1])
            
            # Find elbow point (simple heuristic)
            # Use the point where the rate of change is maximum
            diff = np.diff(k_distances)
            elbow_idx = np.argmax(diff)
            
            eps = k_distances[elbow_idx]
            
            self.logger.info(f"Optimized eps: {eps}")
            return eps
        
        except Exception as e:
            self.logger.warning(f"Failed to optimize eps: {e}")
            return 0.5


class HDBSCANClusterer(ClusteringBase):
    """HDBSCAN clustering implementation."""
    
    def __init__(self, config: ClusteringConfig):
        super().__init__(config)
        self.method_name = "hdbscan"
    
    def is_available(self) -> bool:
        return HDBSCAN_AVAILABLE
    
    def fit_predict(self, embeddings: np.ndarray) -> ClusteringResult:
        """Perform HDBSCAN clustering."""
        import time
        start_time = time.time()
        
        if not self.is_available():
            raise RuntimeError("hdbscan is not available")
        
        try:
            # Perform clustering
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=self.config.hdbscan_min_cluster_size,
                min_samples=self.config.hdbscan_min_samples,
                metric=self.config.hdbscan_metric,
                cluster_selection_epsilon=self.config.hdbscan_cluster_selection_epsilon
            )
            
            labels = clusterer.fit_predict(embeddings)
            
            # Calculate metrics
            quality_metrics = self._calculate_quality_metrics(embeddings, labels)
            n_clusters, cluster_sizes, outliers = self._get_cluster_info(labels)
            
            # Add HDBSCAN-specific metrics
            if hasattr(clusterer, 'cluster_persistence_'):
                quality_metrics['cluster_persistence'] = np.mean(clusterer.cluster_persistence_)
            
            return ClusteringResult(
                labels=labels,
                n_clusters=n_clusters,
                method=self.method_name,
                quality_metrics=quality_metrics,
                cluster_sizes=cluster_sizes,
                outliers=outliers,
                processing_time=time.time() - start_time,
                metadata={
                    "min_cluster_size": self.config.hdbscan_min_cluster_size,
                    "min_samples": self.config.hdbscan_min_samples,
                    "metric": self.config.hdbscan_metric
                }
            )
        
        except Exception as e:
            self.logger.error(f"HDBSCAN clustering failed: {e}")
            raise


class AdaptiveClusterer(ClusteringBase):
    """Adaptive clustering that selects best method based on data characteristics."""
    
    def __init__(self, config: ClusteringConfig):
        super().__init__(config)
        self.method_name = "adaptive"
        
        # Initialize available clusterers
        self.clusterers = {}
        
        if SKLEARN_AVAILABLE:
            self.clusterers['agglomerative'] = AgglomerativeClusterer(config)
            self.clusterers['dbscan'] = DBSCANClusterer(config)
        
        if HDBSCAN_AVAILABLE:
            self.clusterers['hdbscan'] = HDBSCANClusterer(config)
    
    def is_available(self) -> bool:
        return len(self.clusterers) > 0
    
    def fit_predict(self, embeddings: np.ndarray) -> ClusteringResult:
        """Perform adaptive clustering by selecting the best method."""
        if not self.is_available():
            raise RuntimeError("No clustering methods are available")
        
        # Analyze data characteristics
        data_characteristics = self._analyze_data(embeddings)
        
        # Select best method based on characteristics
        best_method = self._select_best_method(data_characteristics)
        
        self.logger.info(f"Selected clustering method: {best_method}")
        
        # Perform clustering with selected method
        clusterer = self.clusterers[best_method]
        result = clusterer.fit_predict(embeddings)
        
        # Update metadata
        result.method = f"adaptive_{best_method}"
        if result.metadata is None:
            result.metadata = {}
        result.metadata['selected_method'] = best_method
        result.metadata['data_characteristics'] = data_characteristics
        
        return result
    
    def _analyze_data(self, embeddings: np.ndarray) -> Dict[str, Any]:
        """Analyze data characteristics to guide method selection."""
        n_samples, n_features = embeddings.shape
        
        characteristics = {
            'n_samples': n_samples,
            'n_features': n_features,
            'density': self._estimate_density(embeddings),
            'dimensionality_ratio': n_features / n_samples if n_samples > 0 else 0,
            'has_outliers': self._detect_outliers(embeddings)
        }
        
        return characteristics
    
    def _estimate_density(self, embeddings: np.ndarray) -> float:
        """Estimate data density."""
        if not SKLEARN_AVAILABLE:
            return 0.5
        
        try:
            from sklearn.neighbors import NearestNeighbors
            
            k = min(10, len(embeddings) // 2)
            if k < 2:
                return 0.5
            
            neighbors = NearestNeighbors(n_neighbors=k)
            neighbors.fit(embeddings)
            distances, _ = neighbors.kneighbors(embeddings)
            
            # Average distance to k-th nearest neighbor
            avg_distance = np.mean(distances[:, -1])
            
            # Normalize by feature space dimension
            normalized_density = 1.0 / (1.0 + avg_distance)
            
            return normalized_density
        
        except Exception:
            return 0.5
    
    def _detect_outliers(self, embeddings: np.ndarray) -> bool:
        """Detect if data contains significant outliers."""
        if not SKLEARN_AVAILABLE:
            return False
        
        try:
            from sklearn.ensemble import IsolationForest
            
            # Use isolation forest for outlier detection
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outlier_labels = iso_forest.fit_predict(embeddings)
            
            # Check if more than 5% are outliers
            outlier_ratio = np.sum(outlier_labels == -1) / len(outlier_labels)
            
            return outlier_ratio > 0.05
        
        except Exception:
            return False
    
    def _select_best_method(self, characteristics: Dict[str, Any]) -> str:
        """Select the best clustering method based on data characteristics."""
        n_samples = characteristics['n_samples']
        density = characteristics['density']
        has_outliers = characteristics['has_outliers']
        
        # Decision logic based on data characteristics
        if has_outliers and 'hdbscan' in self.clusterers:
            # HDBSCAN is good with outliers
            return 'hdbscan'
        
        elif density < 0.3 and 'dbscan' in self.clusterers:
            # DBSCAN for sparse data
            return 'dbscan'
        
        elif n_samples < 1000 and 'agglomerative' in self.clusterers:
            # Agglomerative for small datasets
            return 'agglomerative'
        
        elif 'hdbscan' in self.clusterers:
            # HDBSCAN as general purpose
            return 'hdbscan'
        
        elif 'dbscan' in self.clusterers:
            return 'dbscan'
        
        else:
            # Fallback to agglomerative
            return 'agglomerative'


class EnsembleClusterer:
    """Ensemble clustering combining multiple algorithms."""
    
    def __init__(self, config: ClusteringConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize clusterers
        self.clusterers = []
        
        if SKLEARN_AVAILABLE:
            self.clusterers.append(AgglomerativeClusterer(config))
            self.clusterers.append(DBSCANClusterer(config))
        
        if HDBSCAN_AVAILABLE:
            self.clusterers.append(HDBSCANClusterer(config))
        
        if not self.clusterers:
            raise RuntimeError("No clustering algorithms are available")
    
    def fit_predict(self, embeddings: np.ndarray) -> ClusteringResult:
        """Perform ensemble clustering."""
        import time
        start_time = time.time()
        
        # Run all clusterers
        results = []
        for clusterer in self.clusterers:
            try:
                result = clusterer.fit_predict(embeddings)
                results.append(result)
                self.logger.debug(f"Completed {clusterer.method_name} clustering")
            except Exception as e:
                self.logger.warning(f"Clusterer {clusterer.method_name} failed: {e}")
        
        if not results:
            raise RuntimeError("All clustering methods failed")
        
        # Select best result based on quality metrics
        best_result = self._select_best_result(results)
        
        # Update metadata
        best_result.method = "ensemble"
        if best_result.metadata is None:
            best_result.metadata = {}
        
        best_result.metadata['ensemble_methods'] = [r.method for r in results]
        best_result.metadata['ensemble_scores'] = {
            r.method: r.quality_metrics.get('silhouette_score', 0) for r in results
        }
        best_result.processing_time = time.time() - start_time
        
        return best_result
    
    def _select_best_result(self, results: List[ClusteringResult]) -> ClusteringResult:
        """Select the best clustering result based on quality metrics."""
        if len(results) == 1:
            return results[0]
        
        # Score each result
        scores = []
        for result in results:
            score = self._calculate_ensemble_score(result)
            scores.append(score)
        
        # Select result with highest score
        best_idx = np.argmax(scores)
        best_result = results[best_idx]
        
        self.logger.info(f"Selected {best_result.method} as best clustering result (score: {scores[best_idx]:.3f})")
        
        return best_result
    
    def _calculate_ensemble_score(self, result: ClusteringResult) -> float:
        """Calculate ensemble score for a clustering result."""
        metrics = result.quality_metrics
        
        score = 0.0
        weight_sum = 0.0
        
        # Silhouette score (higher is better)
        if 'silhouette_score' in metrics:
            score += 0.4 * metrics['silhouette_score']
            weight_sum += 0.4
        
        # Calinski-Harabasz score (higher is better, normalize)
        if 'calinski_harabasz_score' in metrics:
            normalized_ch = min(1.0, metrics['calinski_harabasz_score'] / 1000.0)
            score += 0.3 * normalized_ch
            weight_sum += 0.3
        
        # Davies-Bouldin score (lower is better, invert)
        if 'davies_bouldin_score' in metrics:
            normalized_db = max(0.0, 1.0 - metrics['davies_bouldin_score'] / 10.0)
            score += 0.2 * normalized_db
            weight_sum += 0.2
        
        # Penalize high noise ratio
        if 'noise_ratio' in metrics:
            noise_penalty = max(0.0, 1.0 - 2.0 * metrics['noise_ratio'])
            score += 0.1 * noise_penalty
            weight_sum += 0.1
        
        # Normalize score
        if weight_sum > 0:
            score /= weight_sum
        
        return score


class SemanticClusterer:
    """Main semantic clustering interface."""
    
    def __init__(self, config: ClusteringConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize clusterer based on method
        if config.method == ClusteringMethod.ENSEMBLE:
            self.clusterer = EnsembleClusterer(config)
        elif config.method == ClusteringMethod.ADAPTIVE:
            self.clusterer = AdaptiveClusterer(config)
        elif config.method == ClusteringMethod.AGGLOMERATIVE:
            self.clusterer = AgglomerativeClusterer(config)
        elif config.method == ClusteringMethod.DBSCAN:
            self.clusterer = DBSCANClusterer(config)
        elif config.method == ClusteringMethod.HDBSCAN:
            self.clusterer = HDBSCANClusterer(config)
        else:
            # Default to adaptive
            self.clusterer = AdaptiveClusterer(config)
    
    def cluster_embeddings(self, embedding_result: EmbeddingResult) -> ClusteringResult:
        """Cluster embeddings and return result."""
        self.logger.info(f"Starting clustering with method: {self.config.method.value}")
        
        # Preprocess embeddings if needed
        embeddings = self._preprocess_embeddings(embedding_result.embeddings)
        
        # Perform clustering
        result = self.clusterer.fit_predict(embeddings)
        
        self.logger.info(f"Clustering completed: {result.n_clusters} clusters, {len(result.outliers or [])} outliers")
        
        return result
    
    def _preprocess_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """Preprocess embeddings before clustering."""
        processed = embeddings.copy()
        
        # Dimensionality reduction if needed
        if self.config.reduce_dimensions and processed.shape[1] > self.config.max_dimensions:
            processed = self._reduce_dimensions(processed)
        
        # Standardization
        if self.config.standardize and SKLEARN_AVAILABLE:
            scaler = StandardScaler()
            processed = scaler.fit_transform(processed)
        
        return processed
    
    def _reduce_dimensions(self, embeddings: np.ndarray) -> np.ndarray:
        """Reduce embedding dimensions."""
        target_dim = self.config.max_dimensions
        
        if self.config.reduction_method == "pca" and SKLEARN_AVAILABLE:
            pca = PCA(n_components=target_dim, random_state=42)
            return pca.fit_transform(embeddings)
        
        elif self.config.reduction_method == "umap" and UMAP_AVAILABLE:
            reducer = umap.UMAP(n_components=target_dim, random_state=42)
            return reducer.fit_transform(embeddings)
        
        elif self.config.reduction_method == "tsne" and SKLEARN_AVAILABLE:
            # t-SNE is computationally expensive, use PCA first if needed
            if embeddings.shape[1] > 50:
                pca = PCA(n_components=50, random_state=42)
                embeddings = pca.fit_transform(embeddings)
            
            tsne = TSNE(n_components=min(target_dim, 3), random_state=42)
            return tsne.fit_transform(embeddings)
        
        else:
            # Fallback to simple truncation
            return embeddings[:, :target_dim]
    
    def get_cluster_summaries(self, texts: List[str], result: ClusteringResult) -> Dict[int, Dict[str, Any]]:
        """Generate summaries for each cluster."""
        summaries = {}
        
        for cluster_id in range(result.n_clusters):
            cluster_mask = result.labels == cluster_id
            cluster_texts = [texts[i] for i in range(len(texts)) if cluster_mask[i]]
            
            if cluster_texts:
                summaries[cluster_id] = {
                    'size': len(cluster_texts),
                    'texts': cluster_texts[:5],  # Sample texts
                    'avg_length': np.mean([len(text) for text in cluster_texts]),
                    'representative_text': self._get_representative_text(cluster_texts)
                }
        
        return summaries
    
    def _get_representative_text(self, texts: List[str]) -> str:
        """Get the most representative text from a cluster."""
        if not texts:
            return ""
        
        # Simple heuristic: choose text closest to median length
        lengths = [len(text) for text in texts]
        median_length = np.median(lengths)
        
        best_idx = np.argmin([abs(length - median_length) for length in lengths])
        return texts[best_idx]