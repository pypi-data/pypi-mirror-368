import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from scipy import stats
from scipy.stats import skew, kurtosis, jarque_bera, shapiro, mstats
import warnings
from numba import jit, prange
warnings.filterwarnings('ignore')

# Numba-optimized functions for Monte Carlo and quality scoring
@jit(nopython=True)
def _dirichlet_sample(alpha, n_samples, random_state=None):
    """Fast Dirichlet sampling using Numba"""
    if random_state is not None:
        np.random.seed(random_state)
    
    samples = np.empty((n_samples, len(alpha)))
    for i in prange(n_samples):
        # Generate gamma samples
        gamma_samples = np.empty(len(alpha))
        for j in range(len(alpha)):
            # Simple gamma generation using numpy's exponential
            gamma_samples[j] = np.random.gamma(alpha[j])
        
        # Normalize to get Dirichlet sample
        total = np.sum(gamma_samples)
        if total > 0:
            samples[i] = gamma_samples / total
        else:
            # Fallback uniform distribution
            samples[i] = np.ones(len(alpha)) / len(alpha)
    
    return samples

@jit(nopython=True)
def _apply_transform(x, beta, global_shift, epsilon=1e-12):
    """Numba-optimized Feng's shifted log transformation"""
    x_shifted = x + global_shift
    
    min_shifted = np.min(x_shifted)
    if min_shifted <= 0:
        additional_shift = abs(min_shifted) + 1.0
        x_shifted = x_shifted + additional_shift
        global_shift += additional_shift
    
    result = np.empty_like(x_shifted)
    
    if abs(beta) < epsilon:
        result = np.log(x_shifted + 1.0)
    elif beta > 0:
        result = np.log(x_shifted + beta)
    else:
        max_val = np.max(x_shifted)
        temp_result = np.log(max_val - x_shifted + abs(beta) + 1.0)
        # Check if any values are <= 0
        if np.any(temp_result <= 0):
            result = np.log(x_shifted + abs(beta) + 1.0)
        else:
            result = temp_result
    
    # Check if all finite
    all_finite = True
    for i in range(len(result)):
        if not np.isfinite(result[i]):
            all_finite = False
            break
    
    if all_finite:
        return result, global_shift, True
    else:
        return result, global_shift, False

@jit(nopython=True)
def _compute_shift_robust(x, epsilon=1e-12):
    """Numba-optimized robust global shift calculation"""
    # Remove non-finite values
    finite_mask = np.isfinite(x)
    x_clean = x[finite_mask]
    
    if len(x_clean) == 0:
        return 1.0
    
    min_val = np.min(x_clean)
    median = np.median(x_clean)
    
    # Calculate MAD
    abs_deviations = np.abs(x_clean - median)
    mad = np.median(abs_deviations)
    
    if min_val <= 0:
        shift = abs(min_val) + max(1.4826 * mad, 1.0)
    else:
        shift = 0.1 * max(1.4826 * mad, 1.0)
    
    return max(shift, epsilon)

@jit(nopython=True)
def _calculate_skewness(x):
    """Numba-optimized skewness calculation"""
    n = len(x)
    if n < 3:
        return 0.0
    
    mean_x = np.mean(x)
    std_x = np.std(x)
    
    if std_x < 1e-12:
        return 0.0
    
    # Calculate skewness
    sum_cubed = 0.0
    for i in range(n):
        normalized = (x[i] - mean_x) / std_x
        sum_cubed += normalized ** 3
    
    skewness = sum_cubed / n
    return skewness

@jit(nopython=True)
def _calculate_kurtosis(x):
    """Numba-optimized kurtosis calculation"""
    n = len(x)
    if n < 4:
        return 0.0
    
    mean_x = np.mean(x)
    std_x = np.std(x)
    
    if std_x < 1e-12:
        return 0.0
    
    # Calculate kurtosis (Fisher's definition - excess kurtosis)
    sum_fourth = 0.0
    for i in range(n):
        normalized = (x[i] - mean_x) / std_x
        sum_fourth += normalized ** 4
    
    kurtosis_val = sum_fourth / n - 3.0  # Fisher's kurtosis (excess)
    return kurtosis_val

def _anderson_darling_score(x):
    """Anderson-Darling normality score using SciPy"""
    try:
        x = x[np.isfinite(x)]
        n = len(x)
        
        if n < 8 or np.std(x) < 1e-12:
            return 0.0
        
        x_std = (x - np.mean(x)) / np.std(x)
        ad_stat, _, _ = stats.anderson(x_std, dist='norm')
        
        # More forgiving scoring
        score = 1.0 / (1.0 + np.exp((ad_stat - 2.0) * 0.3))
        return score
        
    except Exception:
        return 0.0

@jit(nopython=True)
def _stability_score(x, epsilon=1e-12):
    """Numba-optimized stability score calculation"""
    # Check for finite values
    all_finite = True
    for i in range(len(x)):
        if not np.isfinite(x[i]):
            all_finite = False
            break
        if abs(x[i]) > 1e15:
            return 0.0
    
    if not all_finite:
        return 0.0
    
    x_std = np.std(x)
    x_mean = np.mean(x)
    
    if x_std < epsilon:
        return 0.5
    
    cv = x_std / (abs(x_mean) + epsilon)
    data_range = np.max(x) - np.min(x)
    range_stability = 1.0 / (1.0 + data_range / (abs(x_mean) + epsilon))
    
    stability = (1.0 / (1.0 + cv * 0.5)) * range_stability
    return stability

@jit(nopython=True)
def _quality_score_core(x, w_skewness, w_kurtosis, w_stability, epsilon=1e-12):
    """Numba-optimized core quality score calculation (without Anderson-Darling)"""
    scores = np.empty(3)
    weights = np.array([w_skewness, w_kurtosis, w_stability])
    
    # Skewness evaluation
    skew_val = _calculate_skewness(x)
    scores[0] = np.exp(-abs(skew_val) / 1.5)
    
    # Kurtosis evaluation
    kurt_val = _calculate_kurtosis(x)
    scores[1] = np.exp(-abs(kurt_val) / 2.5)
    
    # Stability score
    scores[2] = _stability_score(x, epsilon)
    
    # Weighted average
    total_weight = np.sum(weights)
    if total_weight == 0:
        return 0.0
    
    weighted_score = np.sum(scores * weights) / total_weight
    return weighted_score

def _hybrid_quality_score(x, w_normality, w_skewness, w_kurtosis, w_stability, epsilon=1e-12):
    """Hybrid quality score using SciPy for Anderson-Darling and Numba for other metrics"""
    # Remove non-finite values
    finite_mask = np.isfinite(x)
    x_clean = x[finite_mask]
    
    if len(x_clean) < 8:
        return 0.0
    
    if np.std(x_clean) < epsilon:
        return 0.0
    
    # Get Anderson-Darling score from SciPy
    ad_score = _anderson_darling_score(x_clean)
    
    # Get other scores from Numba-optimized functions
    core_score = _quality_score_core(x_clean, w_skewness, w_kurtosis, w_stability, epsilon)
    
    # Combine scores with weights
    total_core_weight = w_skewness + w_kurtosis + w_stability
    if total_core_weight > 0:
        # Normalize core weights
        normalized_core_score = core_score
    else:
        normalized_core_score = 0.0
    
    # Final weighted combination
    total_weight = w_normality + total_core_weight
    if total_weight == 0:
        return 0.0
    
    final_score = (ad_score * w_normality + normalized_core_score * total_core_weight) / total_weight
    return final_score

@jit(nopython=True, parallel=True)
def _monte_carlo_optimization(x_clean, beta_sample, n_iterations, epsilon=1e-12, 
                                  convergence_tolerance=1e-4, random_state=None):
    """Numba-optimized Monte Carlo weight optimization"""
    if len(x_clean) < 20:
        # Return balanced default weights
        return 0.35, 0.35, 0.20, 0.10
    
    # Generate weight samples using Dirichlet distribution
    alpha = np.ones(4)  # Uniform prior
    weight_samples = _dirichlet_sample(alpha, n_iterations, random_state)
    
    best_likelihood = -np.inf
    best_weights = np.array([0.35, 0.35, 0.20, 0.10])
    
    # Calculate global shift once
    global_shift = _compute_shift_robust(x_clean, epsilon)
    
    # Evaluate original data score for baseline
    original_score = _quality_score_core(x_clean, 0.35, 0.35, 0.20, 0.10, epsilon)
    
    for i in prange(n_iterations):
        weights = weight_samples[i]
        w_normality, w_skewness, w_kurtosis, w_stability = weights
        
        # Evaluate this weight combination
        likelihood = _evaluate_weight_likelihood(
            x_clean, w_normality, w_skewness, w_kurtosis, w_stability,
            beta_sample, global_shift, epsilon, original_score
        )
        
        if likelihood > best_likelihood:
            best_likelihood = likelihood
            best_weights = weights.copy()
        
        # Early convergence check (simplified for numba)
        if i > 100 and i % 100 == 0:
            recent_improvement = (likelihood - best_likelihood) / (abs(best_likelihood) + epsilon)
            if abs(recent_improvement) < convergence_tolerance:
                break
    
    return best_weights[0], best_weights[1], best_weights[2], best_weights[3]

@jit(nopython=True)
def _evaluate_weight_likelihood(x, w_normality, w_skewness, w_kurtosis, w_stability,
                                    beta_sample, global_shift, epsilon, original_score):
    """Numba-optimized weight likelihood evaluation (using core metrics only)"""
    scores = np.empty(min(11, len(beta_sample) + 1))  # +1 for original, limit for speed
    
    # For original score, use only core metrics in Numba (skip Anderson-Darling for speed)
    core_original = _quality_score_core(x, w_skewness, w_kurtosis, w_stability, epsilon)
    scores[0] = core_original
    
    score_count = 1
    
    # Evaluate various transformations (limit to first 10 for speed)
    max_evals = min(10, len(beta_sample))
    for i in range(max_evals):
        beta = beta_sample[i]
        
        x_transformed, current_global_shift, is_valid = _apply_transform(x, beta, global_shift, epsilon)
        
        if is_valid:
            score = _quality_score_core(x_transformed, w_skewness, w_kurtosis, w_stability, epsilon)
            scores[score_count] = score
            score_count += 1
    
    if score_count < 2:
        return -np.inf
    
    # Use only valid scores
    valid_scores = scores[:score_count]
    
    # Calculate likelihood based on score variance and ranking consistency
    score_var = np.var(valid_scores)
    score_range = np.max(valid_scores) - np.min(valid_scores)
    
    # Good weights should create meaningful score differences
    likelihood = score_var * score_range
    
    # Penalty for extreme weights (regularization)
    weight_entropy = 0.0
    weights = np.array([w_normality, w_skewness, w_kurtosis, w_stability])
    for w in weights:
        if w > epsilon:
            weight_entropy += w * np.log(w + epsilon)
    
    likelihood -= 0.1 * weight_entropy
    
    return likelihood

@jit(nopython=True, parallel=True)
def _optimize_params(x, global_shift, beta_range, min_improvement, 
                         max_iterations, early_stop_threshold, max_skewness, max_kurtosis,
                         w_normality, w_skewness, w_kurtosis, w_stability, epsilon=1e-12):
    """Numba-optimized parameter optimization (using core metrics for speed)"""
    baseline_score = _quality_score_core(x, w_skewness, w_kurtosis, w_stability, epsilon)
    
    # Early stopping if already good enough
    if baseline_score > early_stop_threshold:
        return 0.0, global_shift
    
    best_beta = 0.0
    best_score = baseline_score
    best_global_shift = global_shift
    
    # Create search indices
    n_search = min(max_iterations, len(beta_range))
    search_indices = np.linspace(0, len(beta_range)-1, n_search).astype(np.int64)
    
    for idx in prange(len(search_indices)):
        i = search_indices[idx]
        beta = beta_range[i]
        
        x_transformed, current_global_shift, is_valid = _apply_transform(x, beta, global_shift, epsilon)
        
        if not is_valid:
            continue
        
        # Quick quality checks
        transformed_skew = abs(_calculate_skewness(x_transformed))
        transformed_kurt = abs(_calculate_kurtosis(x_transformed))
        
        if transformed_skew > max_skewness or transformed_kurt > max_kurtosis:
            continue
        
        score = _quality_score_core(x_transformed, w_skewness, w_kurtosis, w_stability, epsilon)
        
        if score > best_score:
            best_score = score
            best_beta = beta
            best_global_shift = current_global_shift
        
        # Early stopping for good enough results
        if score > early_stop_threshold:
            break
    
    # Check if improvement is significant enough
    if best_score - baseline_score < min_improvement:
        return 0.0, global_shift
    
    return best_beta, best_global_shift


class AutomaticShiftedLogTransformer(BaseEstimator, TransformerMixin):
    """
    Enhanced Automatic Shifted Log Transformer with Monte Carlo weight optimization
    
    Key improvements:
    1. Fast Monte Carlo optimization for quality score weights
    2. Adaptive strategy based on data complexity assessment
    3. Conservative approach for already-normal data
    """
    
    def __init__(self,
                 # Core adaptive parameters
                 min_improvement_normal=0.001,
                 min_improvement_skewed=0.01,
                 
                 # Monte Carlo optimization
                 mc_iterations=1000,
                 mc_convergence_tolerance=1e-4,
                 
                 # Early stopping and thresholds
                 early_stop_threshold=0.85,
                 normality_threshold=0.8,
                 
                 # Transformation parameters
                 beta_range=None,
                 epsilon=1e-12,
                 max_kurtosis=8.0,
                 max_skewness=1.0,
                 
                 # Outlier handling
                 outlier_threshold_normal=0.05,
                 outlier_threshold_skewed=0.02,
                 max_winsor_limits=0.08,
                 random_state=None):
        
        # Adaptive parameters
        self.min_improvement_normal = min_improvement_normal
        self.min_improvement_skewed = min_improvement_skewed
        self.early_stop_threshold = early_stop_threshold
        self.normality_threshold = normality_threshold
        
        # Monte Carlo optimization
        self.mc_iterations = mc_iterations
        self.mc_convergence_tolerance = mc_convergence_tolerance
        
        # Transformation parameters
        self.beta_range = beta_range if beta_range is not None else np.arange(-8, 8, step=0.01)
        self.epsilon = epsilon
        self.max_kurtosis = max_kurtosis
        self.max_skewness = max_skewness
        
        # Outlier handling
        self.outlier_threshold_normal = outlier_threshold_normal
        self.outlier_threshold_skewed = outlier_threshold_skewed
        self.max_winsor_limits = max_winsor_limits
        self.iqr_multiplier = 3.0 # Based on Tukey(1977)
        self.mad_multiplier = 3.0 # Based on Tukey(1977)
        
        self.random_state = random_state
        if random_state is not None:
            np.random.seed(random_state)
        
        self._reset_state()
    
    def _reset_state(self):
        """Reset fitted parameters."""
        self.params_ = {}
        self.is_fitted_ = False
        self.feature_names_ = None
        self.global_shift_params_ = {}
        self.winsor_params_ = {}
        self.data_profiles_ = {}
        self.optimal_weights_ = {}  # Store MC-optimized weights per feature
    
    def _assess_data_complexity(self, x):
        """
        Assess data complexity to determine transformation strategy
        
        Returns:
        - 'already_normal': Data is already normal, minimal transformation
        - 'mild_issues': Minor issues, light transformation
        - 'needs_transformation': Requires full transformation
        - 'insufficient': Insufficient data
        """
        try:
            x_clean = x[np.isfinite(x)]
            
            if len(x_clean) < 10:
                return 'insufficient'
            
            # Calculate basic statistics
            data_skew = abs(skew(x_clean))
            data_kurt = abs(kurtosis(x_clean, fisher=True))
            
            # Outlier detection
            q1, q3 = np.percentile(x_clean, [25, 75])
            iqr = q3 - q1
            outlier_pct = 0
            
            if iqr > self.epsilon:
                outliers = np.sum((x_clean < q1 - self.iqr_multiplier*iqr) | 
                                (x_clean > q3 + self.iqr_multiplier*iqr))
                outlier_pct = outliers / len(x_clean)
            
            # Data type detection
            is_likely_normal = self._detect_normal_data(x_clean)
            
            # Classification logic
            if is_likely_normal and data_skew < 0.8 and data_kurt < 3 and outlier_pct < 0.03:
                return 'already_normal'
            elif data_skew < 1.5 and data_kurt < 5 and outlier_pct < 0.08:
                return 'mild_issues'  
            else:
                return 'needs_transformation'
                
        except Exception:
            return 'insufficient'
    
    def _detect_normal_data(self, x):
        """Simple heuristic to detect synthetic/dummy or Already Normal data"""
        try:
            unique_ratio = len(np.unique(x)) / len(x)
            data_range = np.max(x) - np.min(x)
            mean_abs = np.mean(np.abs(x))
            range_ratio = data_range / (mean_abs + self.epsilon)
            
            # Simple heuristic for synthetic data
            is_normal = (unique_ratio > 0.7 and range_ratio < 20)
            return is_normal
            
        except Exception:
            return False
    
    def _get_adaptive_parameters(self, complexity):
        """Get adaptive parameters based on data complexity"""
        if complexity == 'already_normal':
            return {
                'min_improvement': self.min_improvement_normal,
                'outlier_threshold': self.outlier_threshold_normal,
                'beta_range': np.arange(-2, 2, step=0.01),
                'max_search_iterations': 500,
                'winsor_aggressive': False
            }
        elif complexity == 'mild_issues':
            return {
                'min_improvement': (self.min_improvement_normal + self.min_improvement_skewed) / 2,
                'outlier_threshold': (self.outlier_threshold_normal + self.outlier_threshold_skewed) / 2,
                'beta_range': np.arange(-5, 5, step=0.01),
                'max_search_iterations': 800,
                'winsor_aggressive': False
            }
        else:  # needs_transformation
            return {
                'min_improvement': self.min_improvement_skewed,
                'outlier_threshold': self.outlier_threshold_skewed,
                'beta_range': self.beta_range,
                'max_search_iterations': 1000,
                'winsor_aggressive': True
            }
    
    def _monte_carlo_weight_optimization(self, x, n_iterations=None):
        """
        Fast Monte Carlo optimization to find optimal weights for quality scoring
        
        Uses maximum likelihood estimation to find weights that best discriminate
        between good and poor transformations
        """
        if n_iterations is None:
            n_iterations = self.mc_iterations
        
        try:
            x_clean = x[np.isfinite(x)]
            if len(x_clean) < 20:  # Need sufficient data for MC optimization
                # Return balanced default weights
                return {
                    'normality': 0.35,
                    'skewness': 0.35,
                    'kurtosis': 0.20,
                    'stability': 0.10
                }
            
            # Sample different beta values for evaluation
            beta_sample = np.random.choice(self.beta_range, size=min(50, len(self.beta_range)))
            
            # Use Numba-optimized Monte Carlo optimization
            w_normality, w_skewness, w_kurtosis, w_stability = _monte_carlo_optimization(
                x_clean, beta_sample, n_iterations, self.epsilon, 
                self.mc_convergence_tolerance, self.random_state
            )
            
            return {
                'normality': w_normality,
                'skewness': w_skewness,
                'kurtosis': w_kurtosis,
                'stability': w_stability
            }
            
        except Exception:
            # Fallback to balanced weights
            return {
                'normality': 0.35,
                'skewness': 0.35, 
                'kurtosis': 0.20,
                'stability': 0.10
            }
    
    def _quality_score(self, x, weights=None):
        """Enhanced normality scoring with optimized weights"""
        try:
            x = x[np.isfinite(x)]
            
            if len(x) < 8 or np.std(x) < self.epsilon:
                return 0.0
            
            if weights is None:
                weights = {
                    'normality': 0.35,
                    'skewness': 0.35,
                    'kurtosis': 0.20,
                    'stability': 0.10
                }
            
            # Use hybrid quality score calculation (SciPy + Numba)
            score = _hybrid_quality_score(
                x, weights['normality'], weights['skewness'], 
                weights['kurtosis'], weights['stability'], self.epsilon
            )
            
            # Additional tests for complex data (fallback to scipy for compatibility)
            if len(x) > 50:
                additional_score = 0.0
                additional_weight = 0.0
                
                try:
                    if 8 <= len(x) <= 5000:
                        _, p_shapiro = shapiro(x)
                        additional_score += min(p_shapiro * 2, 1.0) * 0.1
                        additional_weight += 0.1
                except:
                    pass
                
                try:
                    _, p_jb = jarque_bera(x)
                    additional_score += min(p_jb * 2, 1.0) * 0.1
                    additional_weight += 0.1
                except:
                    pass
                
                if additional_weight > 0:
                    # Blend with main score
                    total_weight = 1.0 + additional_weight
                    score = (score + additional_score) / total_weight
            
            return score
            
        except Exception:
            return 0.0
    
    def _apply_transform(self, x, beta, global_shift=0):
        """Feng's shifted log transformation"""
        try:
            x_transformed, final_global_shift, is_valid = _apply_transform(x, beta, global_shift, self.epsilon)
            
            if is_valid:
                return x_transformed, final_global_shift
            else:
                return None, global_shift
            
        except Exception:
            return None, global_shift
    
    def _reverse_transform(self, x_transformed, beta, global_shift, max_val=None):
        """Enhanced inverse transformation"""
        try:
            if abs(beta) < self.epsilon:
                result = np.exp(x_transformed) - 1.0
            elif beta > 0:
                result = np.exp(x_transformed) - beta
            else:
                if max_val is None:
                    result = np.exp(x_transformed) - abs(beta) - 1.0
                else:
                    result = max_val - np.exp(x_transformed) + abs(beta) + 1.0
            
            result = result - global_shift
            return result
            
        except Exception:
            return None
    
    def _compute_shift_robust(self, x):
        """Calculate robust global shift using MAD"""
        try:
            return _compute_shift_robust(x, self.epsilon)
        except Exception:
            return 1.0
    
    def _adaptive_winsorizing(self, x, adaptive_params):
        """Adaptive winsorizing based on data complexity"""
        x_clean = x[np.isfinite(x)]
        
        if len(x_clean) < 10:
            return x, {'method': 'none', 'reason': 'insufficient_data'}
        
        # Use adaptive outlier threshold
        outlier_threshold = adaptive_params['outlier_threshold']
        
        # IQR-based outlier detection
        q1, q3 = np.percentile(x_clean, [25, 75])
        iqr = q3 - q1
        
        if iqr < self.epsilon:
            return x, {'method': 'none', 'reason': 'no_variation'}
        
        outliers = np.sum((x_clean < q1 - self.iqr_multiplier*iqr) | 
                         (x_clean > q3 + self.iqr_multiplier*iqr))
        outlier_pct = outliers / len(x_clean)
        
        if outlier_pct < outlier_threshold:
            return x, {'method': 'none', 'reason': 'low_outlier_percentage', 'outlier_pct': outlier_pct}
        
        # Apply conservative winsorizing
        if adaptive_params['winsor_aggressive']:
            winsor_limit = min(outlier_pct * 0.6, self.max_winsor_limits)
        else:
            winsor_limit = min(outlier_pct * 0.3, self.max_winsor_limits * 0.5)
        
        x_winsorized = mstats.winsorize(x, limits=(winsor_limit/2, winsor_limit/2))
        
        winsor_info = {
            'method': 'adaptive',
            'limits': (winsor_limit/2, winsor_limit/2),
            'outlier_percentage': outlier_pct,
            'aggressive': adaptive_params['winsor_aggressive']
        }
        
        return x_winsorized, winsor_info
    
    def _optimize_params(self, x, global_shift, adaptive_params, optimal_weights):
        """Adaptive parameter optimization with MC-optimized weights"""
        try:
            beta_range = adaptive_params['beta_range']
            min_improvement = adaptive_params['min_improvement']
            max_iterations = adaptive_params['max_search_iterations']
            
            # Use Numba-optimized parameter optimization
            best_beta, best_global_shift = _optimize_params(
                x, global_shift, beta_range, min_improvement, max_iterations,
                self.early_stop_threshold, self.max_skewness, self.max_kurtosis,
                optimal_weights['normality'], optimal_weights['skewness'],
                optimal_weights['kurtosis'], optimal_weights['stability'], self.epsilon
            )
            
            return best_beta, best_global_shift
            
        except Exception:
            return 0, global_shift
    
    def fit(self, X, y=None):
        """Fit the transformer with Monte Carlo weight optimization"""
        X = pd.DataFrame(X)
        self.feature_names_ = X.columns.tolist()
        self._reset_state()
        
        for col in X.columns:
            x = X[col].values
            
            # Assess data complexity
            complexity = self._assess_data_complexity(x)
            self.data_profiles_[col] = complexity
            
            # Get adaptive parameters
            adaptive_params = self._get_adaptive_parameters(complexity)
            
            # Apply adaptive winsorizing
            x_winsorized, winsor_info = self._adaptive_winsorizing(x, adaptive_params)
            x_clean = x_winsorized[np.isfinite(x_winsorized)]
            
            # Store winsorizing parameters
            self.winsor_params_[col] = winsor_info
            
            if len(x_clean) < 8:
                self.params_[col] = {
                    'beta': 0,
                    'global_shift': 0,
                    'max_val': None,
                    'mean': np.mean(x_clean) if len(x_clean) > 0 else 0,
                    'std': np.std(x_clean) if len(x_clean) > 0 else 1,
                    'transformed': False,
                    'complexity': complexity
                }
                self.optimal_weights_[col] = {
                    'normality': 0.35, 'skewness': 0.35, 'kurtosis': 0.20, 'stability': 0.10
                }
                continue
            
            # Monte Carlo weight optimization
            optimal_weights = self._monte_carlo_weight_optimization(x_clean)
            self.optimal_weights_[col] = optimal_weights
            
            # For already normal data, use minimal processing
            if complexity == 'already_normal':
                self.params_[col] = {
                    'beta': 0,
                    'global_shift': 0,
                    'max_val': None,
                    'mean': np.mean(x_clean),
                    'std': np.std(x_clean) + self.epsilon,
                    'transformed': False,
                    'complexity': complexity
                }
                continue
            
            # Calculate global shift
            global_shift = self._compute_shift_robust(x_clean)
            max_val = np.max(x_clean + global_shift)
            
            # Find optimal beta with MC-optimized weights
            best_beta, best_global_shift = self._optimize_params(
                x_clean, global_shift, adaptive_params, optimal_weights
            )
            
            # Apply final transformation
            if best_beta != 0:
                result = self._apply_transform(x_clean, best_beta, best_global_shift)
                
                if result[0] is not None:
                    x_transformed, final_global_shift = result
                    transformed = True
                else:
                    x_transformed = x_clean
                    best_beta = 0
                    final_global_shift = 0
                    transformed = False
            else:
                x_transformed = x_clean
                final_global_shift = global_shift
                transformed = False
            
            # Store parameters
            self.params_[col] = {
                'beta': best_beta,
                'global_shift': final_global_shift,
                'max_val': max_val,
                'mean': np.mean(x_transformed),
                'std': np.std(x_transformed) + self.epsilon,
                'transformed': transformed,
                'complexity': complexity
            }
        
        self.is_fitted_ = True
        return self
    
    def transform(self, X):
        """Transform data with fitted parameters"""
        if not self.is_fitted_:
            raise ValueError("Transformer must be fitted before transforming")
        
        X = pd.DataFrame(X)
        X_transformed = pd.DataFrame(index=X.index)
        
        for col in X.columns:
            if col not in self.params_:
                raise ValueError(f"Column '{col}' was not seen during fitting")
            
            x = X[col].values
            
            # Apply the same winsorizing as during fitting
            if col in self.winsor_params_:
                winsor_info = self.winsor_params_[col]
                if winsor_info['method'] == 'adaptive' and 'limits' in winsor_info:
                    x = mstats.winsorize(x, limits=winsor_info['limits'])
            
            params = self.params_[col]
            
            # Apply transformation
            if params['transformed'] and params['beta'] != 0:
                result = self._apply_transform(x, params['beta'], params['global_shift'])
                
                if result[0] is not None:
                    x_transformed, _ = result
                else:
                    x_transformed = x
            else:
                x_transformed = x
            
            # Standardize with robust clipping
            x_std = (x_transformed - params['mean']) / params['std']
            x_std = np.clip(x_std, -6, 6)
            
            X_transformed[col] = x_std
        
        return X_transformed
    
    def inverse_transform(self, X):
        """Inverse transform with enhanced stability"""
        if not self.is_fitted_:
            raise ValueError("Transformer must be fitted before inverse transforming")
        
        X = pd.DataFrame(X)
        X_original = pd.DataFrame(index=X.index)
        
        for col in X.columns:
            if col not in self.params_:
                raise ValueError(f"Column '{col}' was not seen during fitting")
            
            params = self.params_[col]
            x_std = X[col].values
            
            # Unstandardize
            x_transformed = x_std * params['std'] + params['mean']
            
            # Apply inverse transformation
            if params['transformed'] and params['beta'] != 0:
                x_original = self._reverse_transform(
                    x_transformed, params['beta'], params['global_shift'], params['max_val']
                )
                
                if x_original is None:
                    x_original = x_transformed
            else:
                x_original = x_transformed
            
            X_original[col] = x_original
        
        return X_original
    
    def get_transformation_summary(self):
        """Get detailed transformation summary including MC-optimized weights"""
        if not self.is_fitted_:
            raise ValueError("Transformer must be fitted first")
        
        summary = {}
        for col, params in self.params_.items():
            col_summary = {
                'complexity': params['complexity'],
                'beta': params['beta'],
                'global_shift': params['global_shift'],
                'transformed': params['transformed'],
                'method': 'feng_shifted_log' if params['transformed'] else 'standardize_only',
                'optimal_weights': self.optimal_weights_.get(col, {})
            }
            
            # Add winsorizing info
            if col in self.winsor_params_:
                col_summary['winsorizing'] = self.winsor_params_[col]
            
            summary[col] = col_summary
        
        return summary
    
    def evaluate_transformation_quality(self, X):
        """Evaluate transformation quality with MC-optimized scoring"""
        if not self.is_fitted_:
            raise ValueError("Transformer must be fitted first")
        
        X_original = pd.DataFrame(X)
        X_transformed = self.transform(X_original)
        
        results = {}
        
        for col in X_transformed.columns:
            original = X_original[col].values
            transformed = X_transformed[col].values
            
            # Remove non-finite values
            mask = np.isfinite(original) & np.isfinite(transformed)
            orig_clean = original[mask]
            trans_clean = transformed[mask]
            
            if len(orig_clean) < 8:
                results[col] = {'status': 'insufficient_data'}
                continue
            
            try:
                complexity = self.data_profiles_[col]
                optimal_weights = self.optimal_weights_[col]
                
                orig_score = self._quality_score(orig_clean, optimal_weights)
                trans_score = self._quality_score(trans_clean, optimal_weights)
                
                orig_skew = skew(orig_clean)
                trans_skew = skew(trans_clean)
                
                orig_kurt = kurtosis(orig_clean, fisher=True)
                trans_kurt = kurtosis(trans_clean, fisher=True)
                
                # Adaptive evaluation based on complexity
                if complexity == 'already_normal':
                    # For normal data, check if we didn't make it worse
                    success_metric = trans_score >= orig_score - 0.05
                elif complexity == 'mild_issues':
                    # For mild issues, expect modest improvement
                    success_metric = trans_score > orig_score + 0.02
                else:
                    # For problematic data, expect significant improvement
                    success_metric = trans_score > orig_score + 0.05
                
                results[col] = {
                    'complexity': complexity,
                    'optimal_weights': optimal_weights,
                    'original_normality_score': orig_score,
                    'transformed_normality_score': trans_score,
                    'improvement': trans_score - orig_score,
                    'original_skewness': orig_skew,
                    'transformed_skewness': trans_skew,
                    'original_kurtosis': orig_kurt,
                    'transformed_kurtosis': trans_kurt,
                    'skewness_improvement': abs(orig_skew) - abs(trans_skew),
                    'kurtosis_improvement': abs(orig_kurt) - abs(trans_kurt),
                    'is_successful': success_metric,
                    'transformation_applied': self.params_[col]['transformed']
                }
                
            except Exception as e:
                results[col] = {'status': f'error: {str(e)}'}
        
        return results