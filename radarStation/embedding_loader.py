"""
* Software Name : DAGOBAH Radar Station
* Version: <1.0.0>
* SPDX-FileCopyrightText: Copyright (c) 2022 Orange
* SPDX-License-Identifier: BSD-3-Clause
* This software is confidential and proprietary information of Orange.
* You shall not disclose such Confidential Information and shall not copy, use or distribute it
* in whole or in part without the prior written consent of Orange
* Author: Jixiong Liu, Viet-Phi Huynh, Yoan Chabot, and Raphael Troncy
* Software description: DAGOBAH Radar Station is a hybrid system that aims to add a semantic disambiguation step after a previously
identified cell-entity annotation. Radar Station takes into account the entire column as context and uses graph embeddings to capture
latent relationships between entities to improve their disambiguation.
"""
import h5py


from sentence_emembeddings import sentenceEmbeddings

class Embedding_Loader:

    def __init__(self, data_path, model):
        self.data_path = data_path
        self.model = model

        if self.model == "sentence_embeddings":
            self.embedding_dic = sentenceEmbeddings()

        if self.model == "RotatE":
            print("Start loading the Embeddings")
            import pickle
            fileName = self.data_path + '/Embeddings/rotate_wikidata5m.pkl'
            # fileName = '/dataZ/distmult_wikidata5m.pkl'
            with open(fileName, "rb") as fin:
                self.embedding_dic = pickle.load(fin)

        elif self.model == "BigGraph":
            print("Start loading the Big Graph Embeddings")

            entity_paths = []
            for i in range(3):

                entity_paths.append(
                    self.data_path + "/Embeddings/BG_20_20iter/Big_Graph_Training/Wikidata_v1/entity_names_all_" + str(i) + ".json")
            embedding_paths = []

            for i in range(3):
                embedding_paths.append(
                    self.data_path + "/Embeddings/BG_20_20iter/embeddings_all_" + str(i) + ".v240.h5")

            self.embedding_v2_full = []
            for embedding_path in embedding_paths:
                hf_v2_1 = h5py.File(embedding_path, "r")
                self.embedding_v2_full.append(hf_v2_1)

            self.embedding_dic = {}
            loops = 0
            for entity_path in entity_paths:
                nu = 0
                entity_name_1op = open(entity_path)
                next(entity_name_1op)
                for line in entity_name_1op:
                    line = line.replace(',\n', '')
                    line = line.replace('"', '')
                    line = line.replace(' ', '')
                    self.embedding_dic[line] = [0, nu]
                    nu += 1
                loops += 1
                print("Indexing " + str(loops) + "/" + str(len(entity_paths)) + " finished")

        else:
            print("Building embeddings index..")


            if self.model == "ComplEx":
                index_file = self.data_path + '/Embeddings/ComplEx/entities_200_12_12.h5'
                embeddings_file = self.data_path + '/Embeddings/ComplEx/complex_200_12_12.h5'

            if self.model == "DistMult":
                index_file = self.data_path + '/Embeddings/DistMult/entities_200_02_22.h5'
                embeddings_file = self.data_path + '/Embeddings/DistMult/dismult_200_02_22.h5'

            if self.model == "TransE":
                index_file = self.data_path + '/Embeddings/TransE/entities_200_01_30_45.h5'
                embeddings_file = self.data_path + '/Embeddings/TransE/transe_200_01_30_45.h5'

            hf_indexing = h5py.File(index_file, "r")
            self.embedding_dic = {}

            for line in hf_indexing['Indexing']:
                split = line.split('\t')
                self.embedding_dic[split[0]] = split[1]

            self.embedding = h5py.File(embeddings_file, "r")


    def LoadEmbeddings(self, ID):

        ## Uses sentence from the entity's Wikipedia description, we extract the embeddings directly from a pre-trained
        ## BERT model and generate the embeddings only for those candidate entities.
        if self.model == "sentence_embeddings":


            embeddings = self.embedding_dic.get_embeddings(ID)
            return embeddings

        if self.model == 'RotatE':
            try:
                id = self.embedding_dic['graph']['entity2id'][ID]
            except:
                return False
            embeddings = self.embedding_dic['solver']['entity_embeddings'][id]
            return embeddings

        elif self.model == "BigGraph":
            try:
                candidate_vector = self.embedding_dic[ID]
            except:
                return False
            embedding = self.embedding_v2_full[candidate_vector[0]]['embeddings'][candidate_vector[1]]
            return embedding

        else:
            try:
                candidate_vector = int(self.embedding_dic[ID])
            except:
                return False
            embedding = self.embedding['embeddings'][candidate_vector]
            return embedding


if __name__ == '__main__':
    pass



