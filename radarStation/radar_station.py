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

import json
import copy
import os

from scipy import spatial
from alive_progress import alive_bar

import random
import csv

import radarstation.embedding_loader as el
import radarstation.scoring_loader as scl


class Radar_Station:

    def __init__(self, tableFolder, embeddingDiction, goldStandard, scoringSystem, annotationSe, outputfile, dataPath):
        self.goldStandard = goldStandard
        self.tableFolder = tableFolder
        self.embeddingDic = embeddingDiction
        self.annotationSe = annotationSe
        self.outputfile = outputfile
        self.dataPath = dataPath
        self.scoringSystem = scoringSystem

        if self.goldStandard == 'Limaye':
            self.KeycloDic = {}
            Tar_path = self.dataPath + "/Datasets/Key_Column_Index/Limaye_Keycolumns.csv"
            #Tar_path = "/dataZ/RadarStation/KeyColumns/Keycolumns.csv"
            csv_reader = csv.reader(open(Tar_path, 'r', encoding='latin1'),delimiter=';')
            for line in csv_reader:

                self.KeycloDic[line[0]] = int(line[1])

    def file_extration(self):
        '''
        Loding the file names from a given document
        '''
        if self.scoringSystem == 'DAGOBAHSL':
            tabledir = self.tableFolder + "/BaselineScoring/DAGOBAHSL_Scoring/" + self.goldStandard + "_Result"
        if self.scoringSystem == 'MTab':
            tabledir = self.tableFolder + "/BaselineScoring/MTab_Scoring/" + self.goldStandard
        if self.scoringSystem == 'bbw':
            tabledir = self.tableFolder + "/BaselineScoring/BBW_Scoring/" + self.goldStandard
        if self.scoringSystem == 'semtab2022':
            tabledir = self.tableFolder + "/BaselineScoring/Semtab2022/Valid/"
        files = os.listdir(tabledir)
        return files

    def T2D_KeycolumnExtraction(self, tableName):
        tablePath = self.dataPath + "/Datasets/Key_Column_Index/extended_instance_goldstandard/tables/" + tableName  + '.json'
        # tablePath = "/dataZ/RadarStation/KeyColumns/extended_instance_goldstandard/tables/" + tableName

        if self.goldStandard == 'ShortTable':
            tablePath = self.dataPath + "/Datasets/ShortTables/" + tableName + '.json'

        tablePath.replace(".csv",".json")
        with open(tablePath, 'r', encoding='latin1') as load_f:
            load_dict = json.load(load_f)
            keyColumnIndex = load_dict['keyColumnIndex']
        return keyColumnIndex

    def RadarStation(self, ColoneRepresentation):

        activationAm = False

        Outputlist = []

        label = True

        for aScoring in ColoneRepresentation:

            if aScoring["presenceOfAmbiguity"] == False:
                aScoring["SL"] = aScoring["TopCandidates"][0]
                aScoring["RS"] = aScoring["TopCandidates"][0]
                aScoring["SL0"] = aScoring["TopCandidates"][0]
                Outputlist.append(aScoring)
            else:
                activationAm = True

        if activationAm == True:
            ambiguitiesList = []
            outside_row_candidates = {}
            Embedding2Qid = {}
            studied_embeddings = []
            nu = 0

            for aScoring in ColoneRepresentation:

                if aScoring["presenceOfAmbiguity"] == True:
                    ambiguitiesList.append(aScoring)


                for aCandidate in aScoring["TopCandidates"]:

                    if aCandidate["id"] in outside_row_candidates:
                        continue

                    try:
                        embeddings = self.embeddingDic.LoadEmbeddings(aCandidate["id"])
                        embeddings = embeddings.tolist()
                    except:
                        continue

                    outside_row_candidates[aCandidate["id"]] = "Yes"
                    Embedding2Qid[nu] = {'id': aCandidate["id"],
                                         'score': aCandidate["score"]}
                    studied_embeddings.append(embeddings)
                    nu += 1

            BuitTree = False


            if len(studied_embeddings) > 2:
                try:
                    tree = spatial.KDTree(studied_embeddings)
                    BuitTree = True

                except:
                    BuitTree = False

            for aAmbiguities in ambiguitiesList:
                if BuitTree is False:
                    aAmbiguities["SL"] = aAmbiguities["TopCandidates"][0]
                    aAmbiguities["RS"] = aAmbiguities["TopCandidates"][0]
                    aAmbiguities["SL0"] = aAmbiguities["TopCandidates"][0]
                    Outputlist.append(aAmbiguities)
                    continue

                # targetDic = aAmbiguities["TopCandidates"].deepcopy()
                targetDic = copy.deepcopy(aAmbiguities["TopCandidates"])

                Neighbouring_nodes = {}

                if len(studied_embeddings) == 2:
                    aAmbiguities["SL"] = aAmbiguities["TopCandidates"][0]
                    aAmbiguities["RS"] = aAmbiguities["TopCandidates"][0]
                    aAmbiguities["SL0"] = aAmbiguities["TopCandidates"][0]
                    Outputlist.append(aAmbiguities)
                else:


                    for aCandidate in targetDic:

                        Neighbouring_nodes[aCandidate["id"]] = []
                        try:
                            row_embedding = self.embeddingDic.LoadEmbeddings(aCandidate["id"])
                            row_embedding = row_embedding.tolist()
                        except:
                            continue

                        k_value = len(studied_embeddings)

                        NNs = tree.query(row_embedding, k_value)



                        if k_value > 1:
                            sum_weights = 0
                            distance_idx = 1
                            number = 0
                            for nn_id in NNs[1]:
                                One_neighbouring_node = {}
                                if number == 0:
                                    number += 1
                                    continue
                                embedding_distance = NNs[0][distance_idx]
                                embedding_distance = embedding_distance * embedding_distance * embedding_distance
                                distance_idx += 1
                                lpid = Embedding2Qid[nn_id]
                                new_weights = lpid['score'] / embedding_distance
                                sum_weights += new_weights

                                One_neighbouring_node['Qid'] = lpid['id']
                                One_neighbouring_node['weights'] = lpid['score']
                                One_neighbouring_node['distance'] = embedding_distance
                                One_neighbouring_node['radarScore'] = new_weights
                                Neighbouring_nodes[aCandidate["id"]].append(One_neighbouring_node)

                            sum_weights = sum_weights / k_value / 20
                            aCandidate['score'] += sum_weights
                        if k_value == 1:
                            sum_weights = Embedding2Qid[0]['score'] / NNs[0] / 20
                            aCandidate['score'] += sum_weights

                    sorted_cea_candidates = sorted(targetDic, key=lambda t: t["score"], reverse=True)

                    if aAmbiguities["TopCandidates"][0]['score'] == aAmbiguities["TopCandidates"][1]['score']:
                        index = 1
                    else:
                        index = 0


                    RandomN = random.randint(0, len(aAmbiguities["TopCandidates"]) - 1)
                    aAmbiguities["SL"] = aAmbiguities["TopCandidates"][index]
                    aAmbiguities["RS"] = sorted_cea_candidates[0]

                    aAmbiguities["RadarScoring"] = []
                    """
                    for One_sorted_annotation in sorted_cea_candidates:
                        CandidateAnnotation = {}
                        CandidateAnnotation['Qid'] = One_sorted_annotation['id']
                        CandidateAnnotation['radarScore'] = One_sorted_annotation["score"]
                        #CandidateAnnotation['radarContext'] = Neighbouring_nodes[One_sorted_annotation['id']]
                        aAmbiguities["RadarScoring"].append(CandidateAnnotation)
                    """
                    Outputlist.append(aAmbiguities)
        return Outputlist


    def RadarStation_manager(self):
        fileNames = self.file_extration()

        scoringloader = scl.Data_loader(self.scoringSystem, self.annotationSe, self.goldStandard, self.tableFolder)

        proce = len(fileNames)
        with alive_bar(proce, bar='bubbles', spinner='notes2') as bar:

            for aFile in fileNames:
                bar()

                aFile = aFile.replace('.json', '')
                if self.scoringSystem == 'bbw':
                    aFile = aFile.replace('.csv', '')

                if self.goldStandard == 'T2D':
                    GS_path = self.dataPath + "/Wikidata_Ground_Truth/Wikidata_GS_T2D/" + aFile + ".json"
                    if not os.path.exists(GS_path):

                        continue

                keyColumn = False

                TableRepresentation = scoringloader.loader_manager(aFile)

                if TableRepresentation is None:
                    # print('2')

                    continue

                if self.goldStandard == 'Limaye':

                    KeyFile = aFile + '.csv'
                    if KeyFile in self.KeycloDic:
                        keyColumn = [self.KeycloDic[KeyFile]]
                    else:
                        continue
                elif self.goldStandard in ['T2D','ShortTable']:
                    keyColumn = self.T2D_KeycolumnExtraction(aFile)
                    if aFile == "97941125_0_8220652154649529701":
                        keyColumn = 1
                    if aFile == "78650283_0_5937576517849452289":
                        keyColumn = 1
                    if aFile == "61069974_0_1894536874590565102":
                        keyColumn = 1
                    if aFile == "55961337_0_6548713781034932742":
                        keyColumn = 1

                    keyColumn = [keyColumn]

                if keyColumn == False:
                    keyColumn = TableRepresentation.keys()

                tt = 0
                for akey in keyColumn:
                    try:
                        TableRepresentation[akey] = self.RadarStation(TableRepresentation[akey])
                    except:
                        tt = 1
                        continue

                if tt:
                    continue

                OutputList = []
                for akey in TableRepresentation.keys():
                    for anAnnotation in TableRepresentation[akey]:
                        if "SL" in anAnnotation:
                            OutputList.append(anAnnotation)
                outPutFile = {"keyColumn" : list(keyColumn),
                              "tableName" : aFile,
                              "Annotations": OutputList}

                filePath = self.outputfile + "/" + aFile + '.json'

                with open(filePath, 'w', encoding='latin1') as outfile:
                    json.dump(outPutFile, outfile)

    def ambiguity_statistique(self):
        '''
        Computing the occurence of ambiguities from DAGPBAH Scoring for a given data set
        '''
        fileNames = self.file_extration()
        totalAmbiguity = 0
        Total = 0
        for aFile in fileNames:
            results = self.dagobah_scoring_loader(aFile)
            for aColumn in results:
                for aCell in results[aColumn]:
                    if aCell['presenceOfAmbiguity'] == True:
                        totalAmbiguity += 1
                    Total += 1

        return (Total, totalAmbiguity)

if __name__ == '__main__':
    pass