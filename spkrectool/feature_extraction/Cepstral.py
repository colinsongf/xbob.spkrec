#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Features for speaker recognition"""

import numpy,math
import bob
import os
import time
from .. import utils

class Cepstral:
  """Extracts Cepstral coefficents"""
  def __init__(self, config):
    self.m_config = config
    

  def normalize_features(self, params):
  #########################
  ## Initialisation part ##
  #########################
  
    normalized_vector = [ [ 0 for i in range(params.shape[1]) ] for j in range(params.shape[0]) ] 
    for index in range(params.shape[1]):
      vector = numpy.array([row[index] for row in params])
      n_samples = len(vector)
      norm_vector = utils.normalize_std_array(vector)
      
      for i in range(n_samples):
        normalized_vector[i][index]=numpy.asscalar(norm_vector[i])    
    data = numpy.array(normalized_vector)
    return data
  
 


  def __call__(self, input_file, vad_file):
    """Computes and returns normalized cepstral features for the given input wave file"""
    
    print "Input file : ", input_file
    rate_wavsample = utils.read(input_file)
    
    # Feature extraction
    
    # Set parameters
    wl = self.m_config.win_length_ms
    ws = self.m_config.win_shift_ms
    nf = self.m_config.n_filters
    nc = self.m_config.n_ceps
    f_min = self.m_config.f_min
    f_max = self.m_config.f_max
    dw = self.m_config.delta_win
    pre = self.m_config.pre_emphasis_coef

    ceps = bob.ap.Ceps(rate_wavsample[0], wl, ws, nf, nc, f_min, f_max, dw, pre)
    ceps.dct_norm = self.m_config.dct_norm
    ceps.mel_scale = self.m_config.mel_scale
    ceps.with_energy = self.m_config.withEnergy
    ceps.with_delta = self.m_config.withDelta
    ceps.with_delta_delta = self.m_config.withDeltaDelta
       
    cepstral_features = ceps(rate_wavsample[1] )
 
    # Voice activity detection
    labels=bob.io.load(str(vad_file))

    features_mask = self.m_config.features_mask
    filtered_features = numpy.ndarray(shape=((labels == 1).sum(),len(features_mask)), dtype=numpy.float64)
    i=0
    cur_i=0
   
    for row in cepstral_features:
      if labels[i]==1:
        for k in range(len(features_mask)):
          filtered_features[cur_i,k] = row[features_mask[k]]
        cur_i = cur_i + 1
      i = i+1

    if self.m_config.normalizeFeatures:
      normalized_features = self.normalize_features(filtered_features)
    else:
      normalized_features = filtered_features
    return normalized_features

