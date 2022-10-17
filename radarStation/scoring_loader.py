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
import os
import csv
import ast
import copy


class Data_loader():

    def __init__(self, scoringSystem, annotationSe, goldStandard, tableFolder):

        self.scoringSystem = scoringSystem
        self.annotationSe = annotationSe
        self.goldStandard = goldStandard
        self.tableFolder = tableFolder

    def loader_manager(self, fileName):

        if self.scoringSystem == 'MTab':
            tableRepresentation = self.Mtab_scoring_loader(fileName)
            return tableRepresentation

        if self.scoringSystem == 'DAGOBAHSL':
            tableRepresentation = self.dagobah_scoring_loader(fileName)
            return tableRepresentation

        if self.scoringSystem == 'bbw':
            tableRepresentation = self.bbw_scoring_loader(fileName)
            return tableRepresentation

        if self.scoringSystem == 'semtab2022':
            tableRepresentation = self.semtab2022_scoring_loader(fileName)
            return tableRepresentation

    def semtab2022_scoring_loader(self, tableName):
        fileName =  self.tableFolder + "/BaselineScoring/Semtab2022/Valid/" + tableName + ".json"

        with open(fileName, 'r', encoding='latin1') as load_f:
            annotations = json.load(load_f)
        load_f.close()
        TableRepresentation = {}

        for aCell in annotations["CEA"]:
            ambiguityCandidate = []
            row = aCell["row"]
            column = aCell["column"]

            presenceOfAmbiguity = False

            highestScoring = aCell["annotation"][0]['score']

            for one_candidate in aCell["annotation"]:
                if one_candidate['score'] < (self.annotationSe * highestScoring):
                    break
                id = copy.deepcopy(one_candidate['uri'].replace("http://www.wikidata.org/entity/",""))
                acandidate = {}
                acandidate["id"] = id
                acandidate["score"] = copy.deepcopy(one_candidate['score'])

                ambiguityCandidate.append(acandidate)

            if len(ambiguityCandidate) > 1:
                presenceOfAmbiguity = True

            if aCell['column'] in TableRepresentation:
                TableRepresentation[aCell['column']].append(
                    {"row": row, "column": column, "presenceOfAmbiguity": presenceOfAmbiguity,
                     "TopCandidatesNumbers": len(ambiguityCandidate),
                     "TopCandidates": ambiguityCandidate})
            else:
                TableRepresentation[aCell['column']] = [
                    {"row": row, "column": column, "presenceOfAmbiguity": presenceOfAmbiguity,
                     "TopCandidatesNumbers": len(ambiguityCandidate),
                     "TopCandidates": ambiguityCandidate}]
        return TableRepresentation


    def dagobah_scoring_loader(self, tableName):
        '''
        Loading the table and scoring
        Detection of ambiguities
        '''
        if self.goldStandard in ['2T', 'ShortTable', 'Limaye']:

            fileName = self.tableFolder + "/BaselineScoring/DAGOBAHSL_Scoring/" + self.goldStandard + "_Result" + "/" + tableName + '/scores.json'
            if self.goldStandard in ['T2D']:
                fileName = self.tableFolder + "/BaselineScoring/DAGOBAHSL_Scoring/" + self.goldStandard + "_Result" + "/" + tableName + '/score.json'

            if os.path.exists(fileName) is False:
                return None

            with open(fileName, 'r', encoding='latin1') as load_f:
                annotations = json.load(load_f)
            load_f.close()
            TableRepresentation = {}

            for aCell in annotations:
                ambiguityCandidate = []

                row = aCell["row"]
                column = aCell["column"]

                presenceOfAmbiguity = False

                sorted_candidate = sorted(aCell['scores'], key=lambda i: i['score'], reverse=True)

                highestScoring = sorted_candidate[0]['score']

                for one_candidate in sorted_candidate:

                    if one_candidate['score'] < (self.annotationSe * highestScoring):
                        break

                    ambiguityCandidate.append(one_candidate)

                if len(ambiguityCandidate) > 1:
                    presenceOfAmbiguity = True

                if aCell['column'] in TableRepresentation:
                    TableRepresentation[aCell['column']].append(
                        {"row": row, "column": column, "presenceOfAmbiguity": presenceOfAmbiguity,
                         "TopCandidatesNumbers": len(ambiguityCandidate),
                         "TopCandidates": ambiguityCandidate})
                else:
                    TableRepresentation[aCell['column']] = [
                        {"row": row, "column": column, "presenceOfAmbiguity": presenceOfAmbiguity,
                         "TopCandidatesNumbers": len(ambiguityCandidate),
                         "TopCandidates": ambiguityCandidate}]
            return TableRepresentation

        else:
            tablePath = self.tableFolder + "/BaselineScoring/DAGOBAHSL_Scoring/" + self.goldStandard + "_Result" + "/" + tableName + '.json'
            with open(tablePath, 'r', encoding='latin1') as load_f:
                jsonFile = json.load(load_f)
            TableRepresentation = {}

            candidateList = jsonFile['annotated']['CEA']

            # ambiguities detection from Dagobah-SL
            for aCell in candidateList:
                ambiguityCandidate = []
                highestScoring = 0
                row = aCell["row"]
                column = aCell["column"]
                presenceOfAmbiguity = False

                sorted_candidate = sorted(aCell['annotation'], key=lambda i: i['score'], reverse=True)

                highestScoring = sorted_candidate[0]['score']

                for one_candidate in sorted_candidate:

                    if one_candidate['score'] < self.annotationSe * highestScoring:
                        break

                    ambiguityCandidate.append(one_candidate)

                if len(ambiguityCandidate) > 1:
                    presenceOfAmbiguity = True

                if aCell['column'] in TableRepresentation:
                    TableRepresentation[aCell['column']].append(
                        {"row": row, "column": column, "presenceOfAmbiguity": presenceOfAmbiguity,
                         "TopCandidatesNumbers": len(ambiguityCandidate),
                         "TopCandidates": ambiguityCandidate})
                else:
                    TableRepresentation[aCell['column']] = [
                        {"row": row, "column": column, "presenceOfAmbiguity": presenceOfAmbiguity,
                         "TopCandidatesNumbers": len(ambiguityCandidate),
                         "TopCandidates": ambiguityCandidate}]
            return TableRepresentation

    def bbw_scoring_loader(self, fileName):
        fileName = fileName.replace(".json","").replace(".csv","")
        tablePath = self.tableFolder + "/BaselineScoring/BBW_Scoring/" + self.goldStandard + '/' + fileName + ".csv"
        if self.goldStandard == "T2D":
            tablePath = tablePath.replace(".csv",".json")


        TableRepresentation = {}

        csv_reader = csv.reader(open(tablePath))
        for line in csv_reader:
            if len(line) == 0:
                continue

            row = int(line[0])
            column = int(line[1])
            presenceOfAmbiguity = False

            line[2] = ast.literal_eval(line[2])

            if len(line[2]) == 0:
                continue

            highestScoring = line[2][0][1]
            ambiguityCandidate = []

            for one_candidate in line[2]:
                if one_candidate[1] < (self.annotationSe * highestScoring):
                    break

                formedcandidate = {}
                formedcandidate['id'] = one_candidate[0]
                formedcandidate['score'] = one_candidate[1] / highestScoring
                ambiguityCandidate.append(formedcandidate)

            if len(ambiguityCandidate) > 1:
                presenceOfAmbiguity = True

            if column in TableRepresentation:
                TableRepresentation[column].append(
                    {"row": row, "column": column, "presenceOfAmbiguity": presenceOfAmbiguity,
                     "TopCandidatesNumbers": len(ambiguityCandidate),
                     "TopCandidates": ambiguityCandidate})
            else:
                TableRepresentation[column] = [
                    {"row": row, "column": column, "presenceOfAmbiguity": presenceOfAmbiguity,
                     "TopCandidatesNumbers": len(ambiguityCandidate),
                     "TopCandidates": ambiguityCandidate}]
        return TableRepresentation


    def Mtab_scoring_loader(self, fileName):

        fileName = fileName.replace(".json","")

        tablePath = self.tableFolder + "/BaselineScoring/MTab_Scoring/" + self.goldStandard + '/' + fileName + '.json'

        with open(tablePath, 'r', encoding='latin1') as load_f:
            load_dict = json.load(load_f)
            load_dict = load_dict.replace('\n','').replace('\t','')
            MtabScores = json.loads(load_dict)

            TableRepresentation = {}

            for aCell in MtabScores['semantic']['cea']:
                ambiguityCandidate = []
                row = aCell[0]
                column = aCell[1]
                presenceOfAmbiguity = False

                highestScoring = aCell[2][0][1]

                for one_candidate in aCell[2]:

                    if one_candidate[1] < (self.annotationSe * highestScoring):
                        break

                    formedcandidate = {}
                    formedcandidate['id'] = one_candidate[0]
                    formedcandidate['score'] = one_candidate[1]
                    ambiguityCandidate.append(formedcandidate)

                if len(ambiguityCandidate) > 1:
                    presenceOfAmbiguity = True

                if column in TableRepresentation:
                    TableRepresentation[column].append({"row":row, "column": column, "presenceOfAmbiguity": presenceOfAmbiguity,
                                            "TopCandidatesNumbers": len(ambiguityCandidate),
                                            "TopCandidates" : ambiguityCandidate})
                else:
                    TableRepresentation[column] = [{"row":row, "column": column, "presenceOfAmbiguity": presenceOfAmbiguity,
                                            "TopCandidatesNumbers": len(ambiguityCandidate),
                                            "TopCandidates" : ambiguityCandidate}]

            return TableRepresentation




if __name__ == '__main__':
    pass

