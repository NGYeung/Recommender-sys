# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 18:12:11 2024

@author: Yiyang Liu
"""

import numpy as np

import torch
import torch.nn as nn
import math

from fastkan import FastKANLayer
'''
git clone https://github.com/ZiyaoLi/fast-kan
cd fast-kan
pip install .

'''



# Denoiseing Autoencoder to reconstruct the CF interaction matrix given known ratings.
class DAE(nn.Module):
    
    
    def __init__(self, matrix_size, hidden_size, noise = 0.05):
        ''' 
        Parameters
        ----------
        matrix_size : int
            the number of items
           
        hidden_size : int
            the size of hidden representation
            (recommendation: calculate with SVD)
            
        noise: float
            the strength of the noise add to the input. Default = 0.05
            if set to zero then it's a regular autoencoder.

        Returns
        -------
        None.

        '''
        
        
        super(DAE, self).__init__()
        
        self.hidden = hidden_size
        self.mu = nn.Parameter(torch.randn(self.hidden))
        self.noise_strength = noise
        
        self.encoder = nn.Sequential(
            nn.Linear(matrix_size, self.hidden),
            )
        
        self.decoder = nn.Sequential(
            nn.Linear(self.hidden, matrix_size),
            )
        self.b = nn.Parameter(torch.randn(matrix_size))


    
    def forward(self, da_CF_matrix):
        '''
        da_CF_matrix size: batch_size x 1 x num_items
        '''
        
    
        gaussian_noise = torch.rand_like(da_CF_matrix) #create the gaussian noise. std = 1 mean = 0

        noise = gaussian_noise*self.noise_strength
        hidden_rep = self.encoder(da_CF_matrix + noise) + self.mu
        decoded  = self.decoder(hidden_rep) + self.b
        decoded =  torch.sign(decoded)*decoded
        
        return decoded, None, None # return both
        
    
    



class DAE_KAN(nn.Module):
    
    
    def __init__(self, matrix_size, hidden_size, noise = 0.05):
        ''' 
        Parameters
        ----------
        matrix_size : int
            the number of items
           
        hidden_size : int
            the size of hidden representation
            
        noise: float
            the strength of the noise add to the input. Default = 0.05
            if set to zero then it's a regular autoencoder.

        Returns
        -------
        None.

        '''
        
        
        super(DAE_KAN, self).__init__()
        
        self.hidden = hidden_size
        self.mu = nn.Parameter(torch.randn(self.hidden))
        self.noise_strength = noise
        
        self.encoder = nn.Sequential(
            FastKANLayer(matrix_size, self.hidden),
            )
        
        self.decoder = nn.Sequential(
            nn.Dropout(0.1),
            FastKANLayer(self.hidden, matrix_size),
            )
        self.b = nn.Parameter(torch.randn(matrix_size))

    
    def forward(self, da_CF_matrix):
        '''
        batch_size x 1 x num_items
        '''

        gaussian_noise = torch.rand_like(da_CF_matrix) #create the gaussian noise. std = 1 mean = 0

        noise = gaussian_noise*self.noise_strength
        hidden_rep = self.encoder(da_CF_matrix + noise)
   
        decoded  = self.decoder(hidden_rep + self.mu) 
   
        decoded = decoded + self.b
        decoded =  torch.sign(decoded)*decoded
        
        return decoded, None, None # return both
