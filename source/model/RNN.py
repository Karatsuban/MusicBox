# !/usr/bin/python3
# coding: utf-8

import torch
from torch import nn
import numpy as np
import time
from math import ceil, log
import random
import matplotlib.pyplot as plt


class RNN:

    def __init__(self, input_list, param_list):
        self.input_list = input_list                # liste des entree
        self.lr = float(param_list[0]) 		        # taux d'apprentissage du RNN
        self.nb_epochs = int(param_list[1])         # nombre de cycles d'entraînement
        self.hidden_dim = int(param_list[2])        # taille de la dimension cachée
        self.nb_layers = int(param_list[3])         # nombre de couches
        self.batch_size = int(param_list[4])        # nombre de séquences dans un batch
        self.nb_morceaux = int(param_list[5])       # nombre de morceaux à produire
        self.duree_morceaux = int(param_list[6])    # longueur des morceaux

        self.device = self.device_choice()          # choix de l'appareil

        # correction du nombre de morceaux par batch
        self.batch_size = 2**ceil(log(min(self.batch_size, len(self.input_list)), 2))  # la taille est la puissance de 2 la plus proche du min (inférieure)

        # définition des dictionaires de notes vers index et invers
        self.dict_int2val = None           # liste des dictionnaires de traduction de int vers val
        self.dict_val2int = None           # liste des dictionnaires de traduction de val vers int
        self.dict_size = None              # liste des taille des dictionnaires

        # définition des paramètres d'embeddinh
        self.embed_size = None  # taille du vecteur d'embedding
        self.embed = None  # fonction d'embedding

        # définition du RNN, de la fonction d'évaluation de l'erreur, de la couche linéaire et de l'optimiseur
        self.lstm = None
        self.cls = None
        self.loss_function = None
        self.optimizer = None

        self.prepare()
        self.train()

    def distribution_pick(self, vecteur):
        # prend un vecteur de probabilités et renvoie un indice après un tirage
        vecteur = vecteur.detach().to('cpu').numpy()[0]
        nb_elt = len(vecteur)
        val = random.random()
        cumul = 0
        for a in range(nb_elt):
            cumul += vecteur[a]
            if val < cumul:
                return a
        return a

    # This function takes in the model and character as arguments and returns the next character prediction and hidden state
    def predict(self, id, para):
        # One-hot encoding our input to fit into the model
        char = torch.tensor([[id]]).to(self.device)
        input = self.embed(char).to(self.device)

        out, (hidden,cell) = self.lstm(input, para)
        out = self.cls(out)
        prob = nn.functional.softmax(out[-1], dim=1).data

        char_ind = self.dict_size - 2
        while char_ind == self.dict_size - 2:
            char_ind = self.distribution_pick(prob)

        return char_ind, (hidden,cell)

    # This function takes the desired output length and input characters as arguments, returning the produced sentence
    def sample(self, max_len):
        self.lstm.eval()  # eval mode
        # First off, run through the starting characters
        chars = []
        input = self.dict_size - 2  # indice du BOS
        hidden = torch.zeros(self.nb_layers, 1, self.hidden_dim).to(self.device)
        cell = torch.zeros(self.nb_layers, 1, self.hidden_dim).to(self.device)
        # Now pass in the previous characters and get a new one
        for ii in range(max_len):
            output, (hidden,cell) = self.predict(input, (hidden, cell))
            if output == self.dict_size - 1:
                break  # si c'est EOS, on a fini le morceau
            else:
                chars.append(self.dict_int2val[output])
            input = output

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
        # retourne le nombre de fichiers qui seront utilisés pour l'entrainement du RNN mais pas pour les tests
        return ceil(total * 80/100)  # 80% des fichiers sont utilisés pour l'entraînement

    def training_file_choice(self, liste, nb):
        # retourne une liste composée des fichiers utilisées pour l'entraînement et des fichiers utilisés pour les tests
        L = [i for i in range(len(liste))]  # liste d'index
        L_id = random.sample(L, nb)  # sample de taille nb d'index
        training = [liste[i] for i in L_id]  # liste de training
        test = [liste[i] for i in range(len(liste)) if i not in L_id]  # liste de test
        return [training, test]

    def prepare(self):

        training_text = []  # liste des training files de longueur taille+1 que l'on va découper
        test_text = []  # liste des tests files de longueur taille+1 que l'on va découper

        # on parcourt tous les n-uplets un par un et on crée les dictionnaires associés à chaque valeur du n-uplet
        self.input_list = [a.split() for a in self.input_list]
        print(self.input_list)
        chars = set()  # notre ensemble
        for a in self.input_list:  # on parcourt chaque input
            chars = chars.union(set(a))  # on ajoute les notes trouvées à notre ensemble
        print(chars)

        self.dict_int2val = dict(enumerate(chars))                           # on crée un dictionnaire pour maper les entiers aux caractères
        self.dict_val2int = {val: ind for ind, val in self.dict_int2val.items()} 	  # on crée un autre dictionnaire qui map les caractères aux entiers

        self.dict_size = len(self.dict_int2val) + 2            # on stocke la longueurs du dico (+2 pour BOS et EOS)

        # on crée notre embedding
        self.embed_size = 2 * ceil(log(self.dict_size, 2))
        self.embed = nn.Embedding(self.dict_size, self.embed_size)
        self.embed = self.embed.to(self.device)

        # on crée le modèle avec les hyperparamètres
        self.lstm = nn.LSTM(input_size=self.embed_size, hidden_size=self.hidden_dim, num_layers=self.nb_layers)
        self.lstm = self.lstm.to(self.device)  # on déplace le modèle vers le device utilisé

        # définition de la fonction d'erreur de la couche linéaire et de l'optimiseur
        self.loss_function = nn.CrossEntropyLoss().to(self.device)
        self.cls = nn.Linear(self.hidden_dim*self.nb_layers, self.dict_size).to(self.device)
        self.optimizer = torch.optim.Adam(self.lstm.parameters(), lr=self.lr)

    def pick_batch(self):
        np.random.shuffle(self.input_list)  # on mélange les séquences
        return self.input_list[:self.batch_size]  # on prend les self.batch_size premières séquences

    def train(self):
        print("Début de l'Entraînement")

        nb_training_files = self.training_file_number_choice(len(self.input_list))
        training_files, test_files = self.training_file_choice(self.input_list, nb_training_files)

        list_loss = []

        # Boucle d'entraînement
        start = time.time()
        previous = start

        loss = 0
        for epoch in range(1, self.nb_epochs+1):

            batch_seq = self.pick_batch()  # on récup une ligne au hasard parmi toutes les seq de training (pour l'instant UNE seule)
            input_seq = []
            target_seq = []
            for a in range(len(batch_seq)):
                notes = [self.dict_val2int[k] for k in batch_seq[a]]
                input_seq.append([self.dict_size - 2] + notes)  # on rajoute le BOS au début
                target_seq.append(notes + [self.dict_size - 1])  # on rajoute le EOS à la fin

            lengths = [len(s)+1 for s in batch_seq]
            index_tensor = torch.zeros((len(batch_seq), max(lengths)), dtype=torch.long).to(self.device)

            for idx, (seq, seqlen) in enumerate(zip(input_seq, lengths)):
                index_tensor[idx, :seqlen] = torch.tensor(seq)

            input_tensor = self.embed(index_tensor).to(self.device)
            packed_input = nn.utils.rnn.pack_padded_sequence(input_tensor, lengths, batch_first=True, enforce_sorted=False).to(self.device)
            h0 = torch.zeros(self.nb_layers, self.batch_size, self.hidden_dim).to(self.device)
            c0 = torch.zeros(self.nb_layers, self.batch_size, self.hidden_dim).to(self.device)
            packed_out, _ = self.lstm(packed_input, (h0, c0))
            out, input_sizes = nn.utils.rnn.pad_packed_sequence(packed_out, batch_first=True)

            out = torch.cat([out[i, :l] for i, l in enumerate(lengths)])
            tensor_target = torch.cat(tuple([torch.tensor(a) for a in target_seq])).to(self.device)

            err = self.loss_function(self.cls(out), tensor_target).to(self.device)
            list_loss.append(err.item())
            loss += err.item()

            self.optimizer.zero_grad()  # on efface les gradients de l'entraînement précédent
            err.backward()
            self.optimizer.step()

            if epoch%100 == 0:
                print("{}/{} \t Loss = {} \ttime taken = {}".format(epoch, self.nb_epochs, loss/100, time.time() - previous))
                previous = time.time()
                loss = 0
                self.lr -= (1 / 100) * self.lr  # mise à jour du learning rate
        print("Entraînement fini")
        print("Temps total : ", time.time()-start)
        x = [k for k in range(self.nb_epochs)]
        plt.plot(x, list_loss)
        plt.show(block=False)


    def generate(self):
        print("Génération des morceaux")
        # on retourne le résultat sous la forme d'une liste
        out = []
        for a in range(self.nb_morceaux):
            out.append(self.sample(self.duree_morceaux))
        return out
