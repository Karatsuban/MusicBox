# !/usr/bin/python3
#coding: utf-8

import torch
from torch import nn
import numpy as np
import time
from math import ceil
import random
from matplotlib import pyplot as plt

class RNN():

  def __init__(self, type, input_list, param_list):
    self.type = type                          # type du RNN
    self.input_list = input_list              # liste des entree
    self.lr = float(param_list[0]) 		        # taux d'apprentissage du RNN
    self.nb_epochs = int(param_list[1])	      # nombre de cycles d'entraînement
    self.len_hidden_dim = int(param_list[2])  # taille de la dimension cachée
    self.nb_layers = int(param_list[3])	      # nombre de couches
    self.seq_len = int(param_list[4])	        # longueur d'une séquence
    self.is_batch = bool(param_list[5])     	# entraînement sous forme de batch ou non
    self.batch_len = int(param_list[6])	      # nombre de séquences dans un batch
    self.nb_morceaux = int(param_list[7])     # nombre de morceaux à produire
    self.duree_morceaux = int(param_list[8])  # longueur des morceaux 

    self.device = self.device_choice()        # choix de l'appareil

    if self.type == "Rythme et mélodie":
      self.input_list = [a.split() for a in self.input_list]
    
    self.dict_int2val = None           # liste des dictionnaires de traduction de int vers val
    self.dict_val2int = None           # liste des dictionnaires de traduction de val vers int
    self.dict_size = None                 # liste des taille des dictionnaires

    # définition du modèle, de la fonction d'éavluation de l'erreur et de l'optimiseur
    self.model = None
    self.criterion = None
    self.optimizer = None 

    self.train()


  class Model(nn.Module):
      def __init__(self, input_size, output_size, hidden_dim, n_layers, device):
          super(RNN.Model, self).__init__()

          # Defining some parameters
          self.hidden_dim = hidden_dim
          self.n_layers = n_layers
          self.device = device

          #Defining the layers
          # RNN Layer
          self.rnn = nn.RNN(input_size, hidden_dim, n_layers, batch_first=True)
          # Fully connected layer
          self.fc = nn.Linear(hidden_dim, output_size)
      
      def forward(self, x):
          
          batch_size = x.size(0)

          # Initializing hidden state for first input using method defined below
          hidden = self.init_hidden(batch_size)

          # Passing in the input and hidden state into the model and obtaining outputs
          out, hidden = self.rnn(x, hidden)
          
          # Reshaping the outputs such that it can be fit into the fully connected layer
          out = out.contiguous().view(-1, self.hidden_dim)
          out = self.fc(out)
          
          return out, hidden
      
      def init_hidden(self, batch_size):
          # This method generates the first hidden state of zeros which we'll use in the forward pass
          # We'll send the tensor holding the hidden state to the device we specified earlier as well
          hidden = torch.zeros(self.n_layers, batch_size, self.hidden_dim).to(self.device)
          return hidden


  def one_hot_encode(self, sequence, dict_size, seq_len, batch_size):
      # Creating a multi-dimensional array of zeros with the desired output shape
      features = np.zeros((batch_size, seq_len, dict_size), dtype=np.float32)
      
      # Replacing the 0 at the relevant character index with a 1 to represent that character
      for i in range(batch_size):
          for u in range(seq_len):
              features[i, u, sequence[i][u]] = 1
      return features


  #return nb_samples samples from input_t & target_t
  def sample_seq(self, nb_samples, total, input_t, target_t):
      print("DEBUG : nb_samples, total = ", nb_samples, total)
      indexes = np.random.randint(0, total-1, nb_samples)
      input_shape = input_t.size()
      target_shape = target_t.size()
      new_input = torch.randn((nb_samples, input_shape[1], input_shape[2]), dtype=torch.float32)
      new_target = torch.randn((nb_samples, target_shape[1]), dtype=torch.float32)

      for a in range(len(indexes)):
          new_input[a] = input_t[indexes[a]].detach().clone()
          new_target[a] = target_t[indexes[a]].detach().clone()
      return new_input.to(self.device), new_target.to(self.device)

  def distribution_pick(self, vecteur):
      # prend un vecteur de probabilités et renvoie un indice après un tirage
      vecteur = vecteur.detach().to('cpu').numpy()
      nb_elt = len(vecteur)
      val = random.random()
      cumul = 0
      for a in range(nb_elt):
          cumul += vecteur[a]
          if(val < cumul):
              return a
      return a


  # This function takes in the model and character as arguments and returns the next character prediction and hidden state
  def predict(self, character):
      # One-hot encoding our input to fit into the model
      character = np.array([[self.dict_val2int[c] for c in character]])
      character = self.one_hot_encode(character, self.dict_size, character.shape[1], 1)
      character = torch.from_numpy(character)
      character = character.to(self.device)
      
      out, hidden = self.model(character)
      prob = nn.functional.softmax(out[-1], dim=0).data
      char_ind = self.distribution_pick(prob)

      return self.dict_int2val[char_ind], hidden


  # This function takes the desired output length and input characters as arguments, returning the produced sentence
  def sample(self, out_len, start):
      self.model.eval() # eval mode
      # First off, run through the starting characters
      chars = [ch for ch in start]
      size = out_len - len(chars)
      # Now pass in the previous characters and get a new one
      for ii in range(size):
          char, h = self.predict(chars)
          chars.append(char)

      if self.type == "Rythme seulement":
        return ''.join(chars)
      else:
        return ' '.join(chars)


  def device_choice(self):
    # torch.cuda.is_available() checks and returns a Boolean True if a GPU is available, else it'll return False
    is_cuda = torch.cuda.is_available()

    # If we have a GPU available, we'll set our device to GPU. We'll use this device variable later in our code.
    if is_cuda:
      device = torch.device("cuda")
      print("GPU is available")
    else:
      device = torch.device("cpu")
      print("GPU not available, CPU used")
    return device


  def training_file_number_choice(self, total):
    #retourne le nombre de fichiers qui seront utilisés pour l'entrainement du RNN mais pas pour les tests
    return ceil(total * 80/100) # 80% des fichiers sont utilisés pour l'entraînement


  def training_file_choice(self, liste, nb):
    #retourne une liste composée des fichiers utilisées pour l'entraînement et des fichiers utilisés pour les tests
    L = [i for i in range(len(liste))] #liste d'index
    L_id = random.sample(L, nb) #sample de taille nb d'index
    training = [liste[i] for i in L_id] #liste de training
    test = [liste[i] for i in range(len(liste)) if i not in L_id] #liste de test
    return [training, test]

  def decoupe_morceau(self, morceau, taille):
    #morceau est sous la forme d'un tableau
    #découpe un morceau en plusieurs sous-parties de longueur taille+1
    #si la longueur du morceau n'est pas un multiple de taille+1, la partie restante sera ignorée
    return [morceau[i:i+taille+1] for i in range(0,len(morceau)-taille, taille+1)]



  def train(self): 

    training_text = [] # liste des training files de longueur taille+1 que l'on va découper
    test_text = [] # liste des tests files de longueur taille+1 que l'on va découper 

    if(self.type == "Rythme seulement"):
      chars = set(''.join(self.input_list))                            # on joint les text et on extrait les caractères de manière unique
    elif(self.type == "Rythme et mélodie"):
      #on parcourt tous les n-uplets un par un et on crée les dictionnaires associés à chaque valeur du n-uplet
      chars = set()
      for a in self.input_list:
        chars = chars.union(set(a))


    self.dict_int2val = dict(enumerate(chars))                           # on crée un dictionnaire pour maper les entiers aux caractères
    self.dict_val2int = {val: ind for ind, val in self.dict_int2val.items()} 	  # on crée un autre dictionnaire qui map les caractères aux entiers


    print("self.dict_int2val = ", self.dict_int2val, len(self.dict_int2val))

    self.dict_size = len(self.dict_int2val)             # on ajoute les longueurs des dictionnaires

    nb_training_files = self.training_file_number_choice(len(self.input_list))
    training_files, test_files = self.training_file_choice(self.input_list, nb_training_files)


    for i in training_files:
      training_text += self.decoupe_morceau(i, self.seq_len)

    for i in test_files:
      test_text += self.decoupe_morceau(i, self.seq_len)


    training_batch_size = len(training_text) # nombre de séquences de training
    test_batch_size = len(test_text) # nombre de séquences de test

    # Création des listes qui vont contenir les séquences de test et d'entraînement
    training_input_seq = []
    training_target_seq = []
    test_input_seq = []
    test_target_seq = []


    for i in range(training_batch_size):
      # Remove last character for input sequence
      training_input_seq.append(training_text[i][:-1])

      # Remove first character for target sequence
      training_target_seq.append(training_text[i][1:])

    for i in range(test_batch_size):
      # Remove last character for input sequence
      test_input_seq.append(test_text[i][:-1])

      # Remove first character for target sequence
      test_target_seq.append(test_text[i][1:])


    for i in range(training_batch_size):
      training_input_seq[i] = [self.dict_val2int[char] for char in training_input_seq[i]]
      training_target_seq[i] = [self.dict_val2int[char] for char in training_target_seq[i]]

    for i in range(test_batch_size):
      test_input_seq[i] = [self.dict_val2int[char] for char in test_input_seq[i]]
      test_target_seq[i] = [self.dict_val2int[char] for char in test_target_seq[i]]



    #encodage des input de training
    training_input_seq = self.one_hot_encode(training_input_seq, self.dict_size, self.seq_len, training_batch_size)
    training_input_seq = torch.from_numpy(training_input_seq)
    training_target_seq = torch.Tensor(training_target_seq)

    #encodage des input de test
    test_input_seq = self.one_hot_encode(test_input_seq, self.dict_size, self.seq_len, test_batch_size)
    test_input_seq = torch.from_numpy(test_input_seq)
    test_target_seq = torch.Tensor(test_target_seq)


    # on crée le modèle avec les hyperparamètres
    self.model = self.Model(input_size=self.dict_size, output_size=self.dict_size, hidden_dim=self.len_hidden_dim, n_layers=self.nb_layers, device=self.device)
    self.model = self.model.to(self.device) # on déplace le modèle vers le device utilisé

    # définition de la fontcion d'erreur et de l'optimiseur
    self.criterion = nn.CrossEntropyLoss()
    self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)

    # on déplace les input et target des tests et entraînements vers le device utilisé
    training_input_seq = training_input_seq.to(self.device) 
    training_target_seq = training_target_seq.to(self.device)
    test_input_seq = test_input_seq.to(self.device) 
    test_target_seq = test_target_seq.to(self.device)


    print("Début de l'Entraînement")

    old_training_loss = 100
    old_test_loss = 100
    list_training_loss = []
    list_test_loss = []
    list_lr = []

    # Boucle d'entraînement
    t1 = time.time()
    for epoch in range(1, self.nb_epochs):
      self.optimizer.zero_grad() # on efface les gradients de l'entraînement précédent
      print("DEBUG : is_batch = ", self.is_batch)
      if (self.is_batch):
        # si on utilise des batch, alors on récupère une fraction des inputs et des targets
        training_input_sample, training_target_sample = self.sample_seq(self.batch_len, training_batch_size, training_input_seq, training_target_seq)
        output, hidden = self.model(training_input_sample)
        new_training_loss = self.criterion(output, training_target_sample.view(-1).long())
      else:
        output, hidden = self.model(training_input_seq)
        new_training_loss = self.criterion(output, training_target_seq.view(-1).long())


      new_training_loss.backward() # backpropagation et calcul du nouveau gradient
      self.optimizer.step() # mise à jour des poids
      
      if epoch%1 == 0:
        t2 = time.time()-t1
        t1 = time.time()
        print('Epoch: {}/{}.............'.format(epoch, self.nb_epochs), end=' ')
        print("Loss: {:.4f}   {:.4f}".format(new_training_loss.item(), t2))

        if(test_batch_size != 0):
          if(self.is_batch):
            test_input_sample, test_target_sample = self.sample_seq(self.batch_len, test_batch_size, test_input_seq, test_target_seq)
            output, hidden = self.model(test_input_sample)
            new_test_loss = self.criterion(output, test_target_sample.view(-1).long())
          else:
            output, hidden = self.model(test_input_seq)
            new_test_loss = self.criterion(output, test_target_seq.view(-1).long())

          if(new_test_loss < old_test_loss):
            print("Test sur les données de test \t Loss : {} BAISSE".format(new_test_loss))
          else:
            print("Test sur les données de test \t Loss : {} AUGMENTATION".format(new_test_loss))

          old_test_loss = new_test_loss
          list_test_loss.append(new_test_loss)

      old_training_loss = new_training_loss.item()
      list_training_loss.append(new_training_loss.item())
      list_lr.append(self.lr)
      self.lr -= (1/100) * self.lr #mise à jour du learning rate
    
    print("Entraînement fini")

  def generate(self):

    print("Génération des morceaux")
    # on retourne le résultat sous la forme d'une liste
    out = []
    for a in range(self.nb_morceaux):
      note_aleatoire = str(self.dict_int2val[random.randint(0,self.dict_size-1)])
      out.append(self.sample(self.duree_morceaux, [note_aleatoire]))

    return out
