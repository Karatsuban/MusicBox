# !/usr/bin/python3
# coding: utf-8

import torch
from torch import nn
import numpy as np
import time
from math import ceil, log, exp
import random


class RNN:

    def __init__(self, input_list, param_list, ensemble_list, load_param=None):
        self.input_list = input_list                # liste des entrees
        self.lr = float(param_list[0]) 		        # taux d'apprentissage du RNN
        self.nb_epochs = int(param_list[1])         # nombre de cycles d'entraînement

        self.hidden_dim = int(param_list[2])        # taille de la dimension cachée
        self.nb_layers = int(param_list[3])         # nombre de couches
        self.batch_size = int(param_list[4])        # nombre de séquences dans un batch
        self.type_gen = param_list[5]               # type de génération choisi

        self.total_epoch = 0                        # nombre total d'epoch depuis la création du modèle

        # définition des dictionaires de notes vers index et inversement et des marqueurs de début et de fin
        self.list_dict_int2val = [dict(enumerate(k)) for k in ensemble_list]  # liste des dictionnaires de traduction de int vers val
        self.list_dict_val2int = [{val: ind for ind, val in k.items()} for k in self.list_dict_int2val]  # liste des dictionnaires de traduction de val vers int
        self.list_dict_size = [len(k) for k in self.list_dict_val2int]  # liste des taille des dictionnaires
        self.sum_dict_size = sum(self.list_dict_size)  # somme des longueurs de chaque dictionnaire
        self.bos = input_list[0].split()[0].split(":")[0]  # le premier élément est toujours une note comportant que des BOS
        self.eos = input_list[-1].split()[-1].split(":")[0]  # le dernier élément est toujours une note comportant que des EOS

        # définition des paramètres d'embedding
        self.list_embed_size = []  # liste des tailles des vecteurs d'embedding
        self.list_embed = []  # liste des fonctions d'embedding
        self.sum_embed_size = None  # somme des tailles des vecteurs d'embedding

        self.nb_elements = len(ensemble_list)  # nombre d'éléments dans une notre représentée par un N-uplet

        # définition du RNN, de la fonction d'évaluation de l'erreur, de la couche linéaire et de l'optimiseur
        self.lstm = None
        self.cls = None
        self.loss_function = None
        self.optimizer = None

        # définition des variables pour la création des batch
        self.shuffle = False
        self.debut_pick = 0

        # pré-traitement de la liste des morceaux et création des listes des morceaux d'entraînement et de test
        self.input_list = [a.split() for a in self.input_list]
        self.training_files = None
        self.test_files = None
        self.split_input()  # découpage de input_list

        # correction du nombre de morceaux par batch
        self.batch_size = 2 ** ceil(log(min(self.batch_size, len(self.input_list)), 2))  # la taille est la puissance de 2 la plus proche du min entre batch_size et le nombre de sequences d'entrée
        # à mettre plus bas (dans le train ?)

        self.device = device_choice()  # choix de l'appareil utilisé pour l'entraînement (CPU/GPU)

        if load_param is not None:
            self.setParametres(load_param)  # on est en train de charger un RNN
        else:
            self.prepare()

    def getParametres(self):
        # renvoie les paramètres du modèle
        parametres = {
            "NombreDimensionCachee": self.hidden_dim,
            "NombreLayer": self.nb_layers,
            "dict_int2val": self.list_dict_int2val,
            "dict_val2int": self.list_dict_val2int,
            "dict_size": self.list_dict_size,
            "embed_size": self.list_embed_size,
            "embed": self.list_embed,
            "lstm_state_dict": self.lstm.state_dict(),
            "cls": self.cls,
            "loss_function": self.loss_function,
            "optimizer_state_dict": self.optimizer.state_dict(),
            "TypeGeneration": self.type_gen,
            "sum_embed_size": self.sum_embed_size,
            "TotalEpoch": self.total_epoch,
        }
        return parametres

    def setParametres(self, param):
        # applique les paramètres au modèle
        try:
            self.total_epoch = param["TotalEpoch"]
        except KeyError:
            self.total_epoch = 0
        self.type_gen = param["TypeGeneration"]
        self.hidden_dim = param["NombreDimensionCachee"]
        self.nb_layers = param["NombreLayer"]
        self.list_dict_int2val = param["dict_int2val"]
        self.list_dict_val2int = param["dict_val2int"]
        self.list_dict_size = param["dict_size"]
        self.list_embed_size = param["embed_size"]
        self.list_embed = param["embed"]
        for a in range(len(self.list_embed)):
            self.list_embed[a].to(self.device)
        self.sum_embed_size = param["sum_embed_size"]
        self.cls = param["cls"]
        self.cls.to(self.device)
        self.loss_function = param["loss_function"]

        self.lstm = nn.LSTM(input_size=self.sum_embed_size, hidden_size=self.hidden_dim, num_layers=self.nb_layers).to(self.device)
        self.lstm.load_state_dict(param["lstm_state_dict"])

        self.optimizer = torch.optim.Adam(self.lstm.parameters(), lr=self.lr)
        self.optimizer.load_state_dict(param["optimizer_state_dict"])
        return

    def prepare(self):
        # création des embeddings, du modèle
        for a in range(self.nb_elements):  # on crée tous les embeddings
            self.list_embed_size.append(ceil(log(self.list_dict_size[a], 2)))  # log du nombre d'éléments dans le dico en base 2
            self.list_embed.append(nn.Embedding(self.list_dict_size[a], self.list_embed_size[a]))
            self.list_embed[a] = self.list_embed[a].to(self.device)  # on passe tous les embeddings sur le device

        self.sum_embed_size = sum(self.list_embed_size)  # on calcule la somme des longueurs des embeddings

        # on crée le modèle avec les hyperparamètres
        self.lstm = nn.LSTM(input_size=self.sum_embed_size, hidden_size=self.hidden_dim, num_layers=self.nb_layers)
        self.lstm = self.lstm.to(self.device)  # on déplace le modèle vers le device utilisé

        # définition de la fonction d'erreur de la couche linéaire et de l'optimiseur
        self.loss_function = nn.CrossEntropyLoss().to(self.device)
        self.cls = nn.Linear(self.hidden_dim, self.sum_dict_size).to(self.device)
        self.optimizer = torch.optim.Adam(self.lstm.parameters(), lr=self.lr)
        return

    def distribution_pick(self, vecteur):
        # prend un vecteur de probabilités et renvoie un indice après un tirage
        l_idx = [0]
        for a in self.list_dict_size:
            l_idx.append(l_idx[-1] + a)  # on crée la liste des indexes de début et de fin des chaque vecteur

        list_test = [True] * self.nb_elements  # liste utilisée pour vérifier qu'une note générée est correcte
        indices = []
        while list_test.count(True) != 0:
            indices = []
            for idx in range(self.nb_elements):
                vec = vecteur[0][l_idx[idx]:l_idx[idx+1]]  # récupère le bon vecteur de probabilité
                prob = nn.functional.softmax(vec, dim=0).data  # transformation en vecteur unitaire
                idx = torch.multinomial(prob, 1).item()  # tirage d'un index dans le vecteur
                indices.append(idx)
            list_test = [a == self.list_dict_val2int[k][self.eos] for k, a in enumerate(indices)]
            if list_test.count(True) >= self.nb_elements:
                break  # si on a autant de marqueurs EOS que d'éléments, on sort de la boucle
        return indices  # on renvoie la liste des indices

    def predict(self, indexes, parametres):
        # prend en paramètres les indexes des élements et les paramètres du modèle et prédit la note suivante
        model_input = torch.zeros((1, 1, self.sum_embed_size)).to(self.device)
        char = torch.tensor(indexes).to(self.device)

        list_embeddings = [self.list_embed[idx](a) for idx, a in enumerate(char)]  # embedding des éléments de input_index
        if self.nb_elements != 1:
            embedding = torch.cat(tuple(list_embeddings))  # concaténation des vecteurs d'embedding
        else:
            embedding = list_embeddings[0]

        model_input[0][0] = embedding

        out, (hidden, cell) = self.lstm(model_input, parametres)  # récupération du vecteur de probabilité des éléments de la nouvelle note
        out = self.cls(out).to(self.device)  # on met le vecteur sur le bon device
        prob = out[0]  # on récupère le vecteur de probabilité

        char_ind = []  # self.list_dict_val2int[k][self.bos] for k in range(self.nb_elements)]  # indices du BOS
        fin = False
        while not fin:  # tant qu'on trouve un BOS, on recommence
            char_ind = self.distribution_pick(prob)  # on récupère les nouveaux indices des éléments de la note suivante
            test_list = [char_ind[k] != self.list_dict_val2int[k][self.bos] for k in range(self.nb_elements)]  # on teste la présence de marqueurs de début
            fin = False not in test_list  # s'il n'y a pas de marqueur de début, on peut sortir de la boucle

        return char_ind, (hidden, cell)

    def sample(self, max_len):
        # renvoie une séquence d'une longueur maximale longueur max_len
        self.lstm.eval()  # mode d'évaluation du modèle
        chars = []
        while not chars:  # tant que chars est vide (pour éviter de renvoyer un morceau généré vide)
            model_input = [self.list_dict_val2int[k][self.bos] for k in range(self.nb_elements)]  # note composée uniquement de marqueurs BOS

            hidden = torch.zeros(self.nb_layers, 1, self.hidden_dim).to(self.device)  # création du vecteur caché
            cell = torch.zeros(self.nb_layers, 1, self.hidden_dim).to(self.device)

            for ii in range(max_len):
                modele_output, (hidden, cell) = self.predict(model_input, (hidden, cell))  # on prédit la note suivante
                list_test = [modele_output[k] == self.list_dict_val2int[k][self.eos] for k in range(self.nb_elements)]  # on vérifie l'égalité de chaque indice avec l'indice de EOS
                if True in list_test:
                    break  # au moins un EOS a été généré, on arrête le morceau
                else:
                    note = ":".join([self.list_dict_int2val[k][modele_output[k]] for k in range(self.nb_elements)])
                    chars.append(note)
                model_input = modele_output  # la nouvelle note générée est la nouvelle entrée du modèle

        return ' '.join(chars)

    def pick_batch(self):
        # sélectionne des séquences parmi toutes les séquences d'entraînement
        L = []
        to_pick = self.batch_size
        is_epoch = False
        while to_pick != 0:  # tant qu'on a pas pas self.batch_size sequences
            if self.shuffle:  # on doit mélanger la liste
                self.shuffle = False
                np.random.shuffle(self.training_files)  # on mélange les séquences

            seq_left = len(self.training_files) - self.debut_pick  # nombre de séquences non choisies
            a_prendre = min(to_pick, seq_left)  # nombre de séquences maximum que l'on peut prendre parmi les restantes
            L += self.training_files[self.debut_pick:self.debut_pick+a_prendre]  # on prend ces séquences
            to_pick -= a_prendre  # on diminue le nombre de séquences à prendre
            self.debut_pick += a_prendre  # on déplace l'index à partir duquel on prendre les séquences
            if self.debut_pick >= len(self.training_files):  # si l'indice est trop grand
                self.debut_pick = 0  # on le ramène au début
                self.shuffle = True  # il faudra mélanger à nouveau
                is_epoch = True
        return L, is_epoch  # on renvoie les séquences

    def train(self, nb_epochs, batch_size, queue, finQueue):
        # fonction permettant au modèle de s'entraîner
        self.lstm.train()  # mode d'entraînement
        print("Début de l'Entraînement")

        self.nb_epochs = nb_epochs
        self.batch_size = batch_size

        list_losses = [[] for _ in range(self.nb_elements)]  # contient les loss de chaque élément sur toutes les epoch
        losses_epoch = [0 for _ in range(self.nb_elements)]  # contient les loss de chaque élément pour une seule époch
        nb_batch = 0  # nombre de batch dans une epoch
        list_acc = []  # contient les accuracy de tous les batchs d'une epoch
        acc_epoch = []  # contient les accuracy de chaque epoch
        continu = True  # variable gérant la sortie de la boucle d'entraînement
        epoch = 0  # compteur d'epoch
        info = ""
        printInterval = 1  # affichage des info toutes les "printInterval" epoch
        lrInterval = 1  # mise à jour du lr toutes les "lrInterval" epoch
        
        l_idx = [0]
        for a in self.list_dict_size:
            l_idx.append(l_idx[-1] + a)  # on crée la liste des indexes de début et de fin des chaque vecteur
            
        scheduler = torch.optim.lr_scheduler.StepLR(self.optimizer, step_size=lrInterval, gamma=0.99)  # permet de mettre à jour le learning rate

        start = time.time()
        previous = start

        # Boucle d'entraînement
        while continu:
            batch_seq, is_epoch = self.pick_batch()  # on récupère les séquences de batch et un booléen pour savoir si on a fini une epoch
            nb_batch += 1
            target_seq = []

            lengths = [len(s)-1 for s in batch_seq]  # liste des longueurs des séquences
            input_tensor = torch.zeros((len(batch_seq), max(lengths), self.sum_embed_size), dtype=torch.float).to(self.device)  # création du vecteur input
            target2_tensor = torch.zeros((sum(lengths), self.sum_dict_size), dtype=torch.float).to(self.device)  # création du vecteur target pour calculer l'erreur

            num_note = 0

            for idx, seq in enumerate(batch_seq):  # seq est une séquence complète
                list_notes_decomp = []
                for pos, note in enumerate(seq):  # note est une note de la séquence
                    decomp = [self.list_dict_val2int[idx][a] for idx, a in enumerate(note.split(":"))]  # decomposition de la note selon chacun de ses éléments
                    if pos != len(seq) - 1:  # on ne prend pas en compte la dernière note de la séquence dans l'input
                        decomp_emb = [self.list_embed[idx](torch.tensor(a).to(self.device)) for idx, a in enumerate(decomp)]  # embedding des éléments de decomp
                        decomp_emb_tensor = torch.cat(tuple(decomp_emb))  # concaténation des vecteurs d'embedding
                        input_tensor[idx, :lengths[idx]] = decomp_emb_tensor  # ajout du tenseur d'embedding dans le tenseur d'input
                    if pos != 0:  # on ne prend pas en compte la première note de la séquence dans le target
                        list_notes_decomp.append(decomp)
                        
                        for i, k in enumerate(decomp):
                            target2_tensor[num_note, l_idx[i]+k] = 1  # on rajoute un "1" dans chaque vecteur unitaire
                        num_note += 1
                                           
                target_seq += list_notes_decomp

            target_seq = [list(a) for a in zip(*target_seq)]  # création d'une liste de "nb_elements" elements contenant chacun tous les index de leur élément de chaque note associé
            tensor_target = torch.tensor(target_seq).to(self.device)

            packed_input = nn.utils.rnn.pack_padded_sequence(input_tensor, lengths, batch_first=True, enforce_sorted=False).to(self.device)  # on pack les séquences
            h0 = torch.zeros(self.nb_layers, self.batch_size, self.hidden_dim).to(self.device)  # vecteur hidden et cell initiaux
            c0 = torch.zeros(self.nb_layers, self.batch_size, self.hidden_dim).to(self.device)
            packed_out, _ = self.lstm(packed_input, (h0, c0))  # récupération de la prédiction du modèle
            out, input_sizes = nn.utils.rnn.pad_packed_sequence(packed_out, batch_first=True)  # on dépack la sortie

            out = torch.cat([out[i, :l] for i, l in enumerate(lengths)])  # on récupère seulement des parties des séquences de sorties de même longueur que leurs séquences d'entrées correspondantes
            out = self.cls(out)  # passage par la couche linéaire (changement de dimension)

            out_cut = []
            for idx in range(self.nb_elements):
                indexes = torch.tensor([k for k in range(l_idx[idx], l_idx[idx+1])]).to(self.device)
                elem_tensor = nn.functional.softmax(torch.index_select(out, 1, indexes), dim=1)  # on récupère la bonne partie du tenseur qu'on ajoute à la liste
                out_cut.append(elem_tensor)
                out.index_copy_(1, indexes, elem_tensor)
            acc = 100 * (1 - (out - target2_tensor).pow(2).sum()/(self.nb_elements*sum(lengths))).float()  # calcul de la précision du modèle
            acc_epoch.append(acc)  # ajout de l'accuracy du batch à la liste des accuracy sur une epoch

            l_err = [self.loss_function(out_cut[k], tensor_target[k]).to(self.device) for k in range(self.nb_elements)]   # calcul de la loss pour chaque élément d'une note

            for a in range(self.nb_elements):
                losses_epoch[a] += l_err[a]  # on ajoute les erreurs à la liste

            if is_epoch:  # on a fini une epoch
                for a in range(self.nb_elements):
                    list_losses[a].append(losses_epoch[a].item() / nb_batch)  # on ajoute les nouvelles erreurs à la liste complète des loss
                err = torch.mul(sum(losses_epoch), 1 / (self.nb_elements * nb_batch))  # on calcule l'erreur sur toute l'epoch et sur tous les elements
                acc = float(sum(acc_epoch) / nb_batch)  # moyenne de l'accuracy sur tous les batch d'une epoch
                list_acc.append(acc)  # ajout de l'accuracy d'une epoch

                losses_epoch = [0 for _ in range(self.nb_elements)]  # remise à zéro de la liste des loss sur une epoch
                acc_epoch = []  # remise à zéro de la liste des accuracy sur une epoch

                self.optimizer.zero_grad()  # on efface les gradients de l'entraînement précédent
                err.backward()  # propagation de l'erreur
                self.optimizer.step()  # étape de l'optimiseur

                epoch += 1  # incrémentation compteur d'epoch
                nb_batch = 0  # mise à jout du nb_batch
                scheduler.step()
                queue.put(str(epoch) + ":" + str(self.nb_epochs) + ":" + str(time.time() - start))  # envoi des informations d'une epoch

                if epoch % printInterval == 0:
                    print("{}/{} \t Loss = {} \tPerplexity = {} \tAccuracy = {}% \ttime taken = {}".format(epoch, self.nb_epochs, "%.5f" % err, "%.5f" % exp(err), "%.3f" % acc, "%.3f" % (time.time() - previous)))
                    previous = time.time()

            if not finQueue.empty():
                info = finQueue.get()  # récupération des informations envoyées à travers la queue

            if epoch == self.nb_epochs or info == "FIN":
                continu = False  # conditions de fin d'entraînement

        self.total_epoch += epoch  # mise à jour du total d'epoch

        print("Entraînement fini")
        print("Temps total : ", time.time()-start)

        return list_losses, list_acc  # on renvoie la liste des losses et des acc pour chaque epoch

    def generate(self, nombre, duree):
        # génère "nombre" séquences de durées maximales "durée"
        print("Génération des morceaux")
        out = []
        for a in range(nombre):
            out.append(self.sample(duree))
        return out

    def split_input(self):
        # coupe self.input_list en une liste d'entraînement et une liste de test
        nb_training_files = training_file_number_choice(len(self.input_list))  # on récupère le nombre de fichiers d'entraînement
        self.training_files, self.test_files = training_file_choice(self.input_list, nb_training_files)  # on récupère les fichiers de test et d'entraînement


def training_file_number_choice(total):
    # retourne le nombre de fichiers qui seront utilisés pour l'entrainement du RNN mais pas pour les tests
    return ceil(total * 90/100)  # 90% des fichiers sont utilisés pour l'entraînement


def training_file_choice(liste, nb):
    # retourne une liste composée des fichiers utilisées pour l'entraînement et des fichiers utilisés pour les tests
    L = [i for i in range(len(liste))]  # liste d'index
    L_id = random.sample(L, nb)  # sample de taille nb d'index
    training = [liste[i] for i in L_id]  # liste de training
    test = [liste[i] for i in range(len(liste)) if i not in L_id]  # liste de test
    return [training, test]


def device_choice():
    # renvoie l'appareil le plus adapté pour l'entraînement (GPU si disponible, sinon CPU)
    is_cuda = torch.cuda.is_available()

    if is_cuda:
        device = torch.device("cuda")
        print("GPU is available")
    else:
        device = torch.device("cpu")
        print("GPU not available, CPU used")
    return device
