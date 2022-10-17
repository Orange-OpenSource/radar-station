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

import os
import json
import csv
from alive_progress import alive_bar

class evaluater:

    def __init__(self, goldStandart, output_path, data_path):
        self.goldStandart = goldStandart
        self.output_path = output_path
        self.data_path = data_path


    def evaluator_manager(self):
        if '2T' in self.goldStandart:
            self.Semtab_evaluation()
        if 'T2D' in self.goldStandart:
            a = self.T2D_evaluation()
        if 'Limaye' in self.goldStandart:
            a = self.limaye_evaluation()
        if 'ShortTable' in self.goldStandart:
            a = self.ShortTable_evaluation()
        return a

    def limaye_evaluation(self):

        dir = self.output_path

        files = os.listdir(dir)

        Good_RS_Amb = 0
        Good_SL_Amb = 0

        totol_label = 0

        total_tables = 0

        total_ambiguities = 0
        ambiguity_list = []
        candidates_inside_amb = 0

        total_predictions = 0

        Good_SL_number = 0
        Good_RS_number = 0
        Good_in_Amb = 0

        Good_RS_Bad_SL_number = 0

        Good_SL_Bad_RS_number = 0

        Both_bad_with_ambiguity = 0
        Both_bad_without_ambiguity = 0


        total_diff = 0

        GS_len = 0

        GSnum = 0

        nu = 0
        print('-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')
        print('Limaye evaluation starts.. ')
        with alive_bar(len(files), bar='bubbles', spinner='notes2') as bar:

            for file in files:

                oneTable = 0
                nu += 1
                bar()
                filepath = os.path.join(dir, file)
                with open(filepath, 'r', encoding='latin1') as load_f:
                    annotations = json.load(load_f)

                GS_path = file
                GS_path = self.data_path + '/Wikidata_Ground_Truth/Wikidata_GS_Limaye/' + GS_path
                GS_path = GS_path.replace(".json", ".csv")
                #     print(GS_path)

                GS_lists = {}
                try:
                    csv_reader = csv.reader(open(GS_path, 'r', encoding='latin1'))
                except:
                    continue
                for line in csv_reader:
                    if len(line) < 3:
                        continue
                    if "Q1047711" == line[3]:
                        continue
                    totol_label += 1
                    GS_lists[line[2]] = line[3]
                    GSnum += 1

                GS_len += len(GS_lists)

                total_tables += 1
                total_predictions += len(annotations['Annotations'])

                if len(GS_lists) == 0:
                    continue

                diff = len(annotations['Annotations']) - len(GS_lists)
                total_diff += diff

                nonnnn = 0
                for a_annotation in annotations['Annotations']:

                    if str(a_annotation['row']) in GS_lists.keys():
                        GS = GS_lists[str(a_annotation['row'])]
                    else:
                        continue

                    if a_annotation['presenceOfAmbiguity']:
                        total_ambiguities += 1
                        ambiguity_list.append(a_annotation)
                        candidates_inside_amb += a_annotation["TopCandidatesNumbers"]
                        for oneCandidate in a_annotation["TopCandidates"]:
                            if oneCandidate['id'] in [GS]:
                                Good_in_Amb += 1

                    InSL = False
                    if a_annotation['SL']['id'] == GS:
                        InSL = True
                        Good_SL_number += 1
                        oneTable += 1
                        nonnnn += 1
                        if a_annotation['presenceOfAmbiguity']:
                            Good_SL_Amb += 1

                    InRS = False
                    if a_annotation['RS']['id'] == GS:
                        InRS = True
                        Good_RS_number += 1
                        nonnnn += 1
                        if a_annotation['presenceOfAmbiguity']:
                            Good_RS_Amb += 1

                    if InSL and InRS == False:
                        Good_SL_Bad_RS_number += 1

                    if InRS and InSL == False:
                        Good_RS_Bad_SL_number += 1

                    if InRS == False and InSL == False and a_annotation['presenceOfAmbiguity']:
                        Both_bad_with_ambiguity += 1

                    if InRS == False and InSL == False and a_annotation['presenceOfAmbiguity'] == False:
                        Both_bad_without_ambiguity += 1


        print('total_predictions: ' + str(total_predictions) + '  ')

        print('totol_label: ' + str(totol_label) + '  ')

        print('Global_Good_SL: ' + str(Good_SL_number) + '  ')
        print('Global_precision_SL: ' + str(Good_SL_number / totol_label) + '  ')
        print('Global_Good_RS: ' + str(Good_RS_number) + '  ')
        print('Global_precision_RS: ' + str(Good_RS_number / totol_label) + '  ')

        print('total_ambiguities: ' + str(total_ambiguities) + '  ')
        print('Average_amb_lenth: ' + str(candidates_inside_amb / total_ambiguities) + '  ')
        print('Average_GT_in_amb: ' + str(Good_in_Amb / total_ambiguities) + '  ')
        print('Good_RS_Amb: ' + str(Good_RS_Amb) + '  ')
        print('Ratio_RS_Amb: ' + str(Good_RS_Amb / total_ambiguities) + '  ')
        print('Good_SL_Amb: ' + str(Good_SL_Amb) + '  ')
        print('Ratio_SL_Amb: ' + str(Good_SL_Amb / total_ambiguities) + '  ')

        print('Good_RS_Bad_SL_number: ' + str(Good_RS_Bad_SL_number) + '  ')
        print('Good_SL_Bad_RS_number: ' + str(Good_SL_Bad_RS_number) + '  ')
        print('Both_bad_with_ambiguity: ' + str(Both_bad_with_ambiguity) + '  ')
        print('Both_bad_without_ambiguity: ' + str(Both_bad_without_ambiguity) + '  ')

        a = Good_RS_number / totol_label
        return a


    def Semtab_evaluation(self):

        total_tables = 0

        total_label = 0

        total_ambiguities = 0

        candidates_inside_amb = 0

        total_predictions = 0

        Good_SL_number = 0
        Good_RS_number = 0

        Good_RS_Amb = 0
        Good_SL_Amb = 0

        Good_in_Amb = 0

        Good_RS_Bad_SL_number = 0

        Good_SL_Bad_RS_number = 0

        Both_bad_with_ambiguity = 0

        Both_bad_without_ambiguity = 0

        GSpath = self.data_path + "/Wikidata_Ground_Truth/Wikidata_GS_2T/CEA_2T_WD_gt.csv"
        CurrentFile = ''
        annotationDic = {}

        count = 0
        thefile = open(GSpath)
        while True:
            buffer = thefile.read(1024 * 8192)
            if not buffer:
                break
            count += buffer.count('\n')
        thefile.close()
        print('-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')
        with open(GSpath) as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            print('SemTab evaluation starts.. ')
            with alive_bar(count, bar='bubbles', spinner='notes2') as bar:
                for oneGT in csvreader:
                    bar()
                    total_label += 1
                    if oneGT[0] != CurrentFile:
                        CurrentFile = oneGT[0]
                        total_tables += 1
                        annotationDic = {}
                        out = oneGT[0].replace('\"', '')
                        annotationFile = self.output_path + '/' + out + '.json'
                        with open(annotationFile, "r") as load_f:
                            load_dict = json.load(load_f)
                        load_f.close()
                        for oneAnnotation in load_dict['Annotations']:

                            label = str(oneAnnotation['column']) + "-" + str(oneAnnotation['row'])
                            annotationInfo = {}
                            annotationInfo["presenceOfAmbiguity"] = oneAnnotation["presenceOfAmbiguity"]
                            annotationInfo["TopCandidatesNumbers"] = oneAnnotation["TopCandidatesNumbers"]
                            annotationInfo["TopCandidates"] = oneAnnotation["TopCandidates"]
                            annotationInfo["SL"] = oneAnnotation["SL"]
                            annotationInfo["RS"] = oneAnnotation["RS"]

                            total_predictions += 1


                            annotationDic[label] = annotationInfo

                    label = oneGT[2].replace('\"', '') + "-" + oneGT[1].replace('\"', '')
                    GTS = oneGT[3].replace('\"', '').replace('http://www.wikidata.org/entity/', '')
                    GTS = GTS.split(' ')
                    try:
                        a = annotationDic[label]
                    except:
                        Both_bad_without_ambiguity += 1

                        continue

                    if annotationDic[label]["presenceOfAmbiguity"] == True:
                        total_ambiguities += 1
                        candidates_inside_amb += annotationDic[label]["TopCandidatesNumbers"]
                        for oneCandidate in annotationDic[label]["TopCandidates"]:
                            if oneCandidate['id'] in GTS:
                                Good_in_Amb += 1


                    if annotationDic[label]['SL']['id'] in GTS:
                        Good_SL_number += 1
                        if annotationDic[label]["presenceOfAmbiguity"] == True:
                            Good_SL_Amb += 1
                            if annotationDic[label]['RS']['id'] not in GTS:
                                Good_SL_Bad_RS_number += 1
                            else:
                                Good_RS_number += 1
                                Good_RS_Amb += 1

                        else:
                            Good_RS_number += 1
                        continue


                    if annotationDic[label]['RS']['id'] in GTS:
                        Good_RS_number += 1
                        Good_RS_Amb += 1
                        Good_RS_Bad_SL_number += 1

                        continue

                    if annotationDic[label]["presenceOfAmbiguity"] == True:
                        Both_bad_with_ambiguity += 1

                    else:
                        Both_bad_without_ambiguity += 1




        print('total_predictions: ' + str(total_predictions) + '  ')

        print('Global_Good_SL: ' + str(Good_SL_number) + '  ')
        print('Global_precision_SL: ' + str(Good_SL_number / total_label) + '  ')
        print('Global_Good_RS: ' + str(Good_RS_number) + '  ')
        print('Global_precision_RS: ' + str(Good_RS_number / total_label) + '  ')

        print('total_ambiguities: ' + str(total_ambiguities) + '  ')
        print('Average_amb_lenth: ' + str(candidates_inside_amb/total_ambiguities) + '  ')
        print('Average_GT_in_amb: ' + str(Good_in_Amb / total_ambiguities) + '  ')
        print('Good_RS_Amb: ' + str(Good_RS_Amb) + '  ')
        print('Ratio_RS_Amb: ' + str(Good_RS_Amb/total_ambiguities) + '  ')
        print('Good_SL_Amb: ' + str(Good_SL_Amb) + '  ')
        print('Ratio_SL_Amb: ' + str(Good_SL_Amb/total_ambiguities) + '  ')

        print('Good_RS_Bad_SL_number: ' + str(Good_RS_Bad_SL_number) + '  ')
        print('Good_SL_Bad_RS_number: ' + str(Good_SL_Bad_RS_number) + '  ')
        print('Both_bad_with_ambiguity: ' + str(Both_bad_with_ambiguity) + '  ')
        print('Both_bad_without_ambiguity: ' + str(Both_bad_without_ambiguity) + '  ')

        return Good_RS_number / total_label

    def T2D_evaluation(self):
        dir = self.output_path

        files = os.listdir(dir)

        total_tables = 0

        total_ambiguities = 0
        ambiguity_list = []

        total_predictions = 0

        candidates_inside_amb = 0


        Good_SL_number = 0
        Good_RS_number = 0

        totol_label = 0

        Good_RS_Amb = 0
        Good_SL_Amb = 0

        Good_RS_Bad_SL_number = 0


        Good_SL_Bad_RS_number = 0

        Both_bad_with_ambiguity = 0
        Both_bad_without_ambiguity = 0

        total_diff = 0

        Good_in_Amb = 0

        add = []

        nu = 0
        print('-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')
        print('T2D evaluation starts.. ')
        with alive_bar(len(files), bar='bubbles', spinner='notes2') as bar:
            for file in files:
                bar()
                GS_path = self.data_path + '/Wikidata_Ground_Truth/Wikidata_GS_T2D/' + file
                if not os.path.exists(GS_path):
                    continue
                nu += 1

                filepath = dir + "/" + file

                with open(filepath, 'r', encoding='latin1') as load_f:
                    annotations = json.load(load_f)

                GS_path = file
                GS_path = self.data_path + '/Wikidata_Ground_Truth/Wikidata_GS_T2D/' + file
                with open(GS_path, 'r', encoding='latin1') as load_f:
                    GS_list = json.load(load_f)
                load_f.close()

                thisbad = 0

                GS_lists = {}

                GS_all = []
                for a_GS in GS_list:
                    if len(a_GS) < 3:
                        continue
                    GS_lists[str(int(a_GS[2]))] = a_GS[3]
                    GS_all.append(a_GS[3])
                    totol_label += 1

                total_tables += 1
                total_predictions += len(annotations['Annotations'])

                diff = len(annotations['Annotations']) - len(GS_lists)
                total_diff += diff

                for a_annotation in annotations['Annotations']:

                    if str(a_annotation['row']) in GS_lists.keys():
                        GS = GS_lists[str(a_annotation['row'])]
                    else:
                        continue

                    if a_annotation["presenceOfAmbiguity"] == True:
                        total_ambiguities += 1
                        candidates_inside_amb += a_annotation["TopCandidatesNumbers"]
                        for oneCandidate in a_annotation["TopCandidates"]:
                            if oneCandidate['id'] in [GS]:
                                Good_in_Amb += 1


                    if a_annotation['presenceOfAmbiguity']:
                        total_ambiguities += 1
                        ambiguity_list.append(a_annotation)
                        candidates_inside_amb += a_annotation["TopCandidatesNumbers"]


                    InSL = False
                    if a_annotation['SL']['id'] in GS_all:
                        InSL = True

                        Good_SL_number += 1
                        if a_annotation['presenceOfAmbiguity']:
                            Good_SL_Amb += 1
                    else:
                        thisbad += 1

                    InRS = False
                    if a_annotation['RS']['id'] in GS_all:
                        InRS = True
                        Good_RS_number += 1
                        if a_annotation['presenceOfAmbiguity']:
                            Good_RS_Amb += 1


                    if InSL and InRS == False:
                        Good_SL_Bad_RS_number += 1

                    if InRS and InSL == False:
                        Good_RS_Bad_SL_number += 1


                    if InRS == False and InSL == False and a_annotation['presenceOfAmbiguity']:
                        Both_bad_with_ambiguity += 1

                    if InRS == False and InSL == False and a_annotation['presenceOfAmbiguity'] == False:
                        Both_bad_without_ambiguity += 1

                if thisbad > len(GS_list)*0.8:
                    add.append(file)




        print('total_predictions: ' + str(total_predictions) + '  ')

        print('Global_Good_SL: ' + str(Good_SL_number) + '  ')
        print('Global_precision_SL: ' + str(Good_SL_number / totol_label) + '  ')
        print('Global_Good_RS: ' + str(Good_RS_number) + '  ')
        print('Global_precision_RS: ' + str(Good_RS_number / totol_label) + '  ')

        print('total_ambiguities: ' + str(total_ambiguities) + '  ')
        print('Average_amb_lenth: ' + str(candidates_inside_amb / total_ambiguities) + '  ')
        print('Average_GT_in_amb: ' + str(Good_in_Amb / total_ambiguities) + '  ')
        print('Good_RS_Amb: ' + str(Good_RS_Amb) + '  ')
        print('Ratio_RS_Amb: ' + str(Good_RS_Amb / total_ambiguities) + '  ')
        print('Good_SL_Amb: ' + str(Good_SL_Amb) + '  ')
        print('Ratio_SL_Amb: ' + str(Good_SL_Amb / total_ambiguities) + '  ')

        print('Good_RS_Bad_SL_number: ' + str(Good_RS_Bad_SL_number) + '  ')
        print('Good_SL_Bad_RS_number: ' + str(Good_SL_Bad_RS_number) + '  ')
        print('Both_bad_with_ambiguity: ' + str(Both_bad_with_ambiguity) + '  ')
        print('Both_bad_without_ambiguity: ' + str(Both_bad_without_ambiguity) + '  ')
        print('totol_label:' + str(totol_label))
        return Good_RS_number / totol_label


    def ShortTable_evaluation(self):
        dir = self.output_path

        files = os.listdir(dir)

        total_tables = 0

        total_ambiguities = 0
        ambiguity_list = []

        total_predictions = 0

        candidates_inside_amb = 0

        Good_SL_number = 0
        Good_RS_number = 0

        Good_RS_Amb = 0
        Good_SL_Amb = 0

        Good_RS_Bad_SL_number = 0

        Good_SL_Bad_RS_number = 0

        Both_bad_with_ambiguity = 0
        Both_bad_without_ambiguity = 0

        total_diff = 0
        Good_in_Amb = 0


        totol_label = 0

        nu = 0
        print('-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-')
        print('ST evaluation starts.. ')

        with alive_bar(len(files), bar='bubbles', spinner='notes2') as bar:
            for file in files:
                bar()
                nu += 1
                filepath = os.path.join(dir, file)
                with open(filepath, 'r', encoding='latin1') as load_f:
                    annotations = json.load(load_f)

                GS_path = file
                GS_path = self.data_path + '/Wikidata_Ground_Truth/Wikidata_GS_ST/GS/' + GS_path
                GS_path= GS_path.replace(".json", ".csv")
                #     print(GS_path)

                gnu = 0
                GS_lists = {}
                file = open(GS_path, 'r', encoding='latin1')
                csvReader = csv.reader(file)
                for a_GS in csvReader:
                    GS_lists[str(gnu)] = a_GS[3]
                    gnu += 1
                    totol_label += 1
                file.close()
                #     print(GS[0])


                total_tables += 1
                total_predictions += len(annotations['Annotations'])

                diff = len(annotations['Annotations']) - len(GS_lists)
                total_diff += diff

                for a_annotation in annotations['Annotations']:
                    if str(a_annotation['row']) in GS_lists.keys():
                        GS = GS_lists[str(a_annotation['row'])]
                    else:
                        continue

                    if a_annotation['presenceOfAmbiguity']:
                        total_ambiguities += 1
                        ambiguity_list.append(a_annotation)
                        candidates_inside_amb += a_annotation["TopCandidatesNumbers"]
                        for oneCandidate in a_annotation["TopCandidates"]:
                            if oneCandidate['id'] in [GS]:
                                Good_in_Amb += 1

                    InSL = False
                    if a_annotation['SL']['id'] == GS:
                        InSL = True
                        Good_SL_number += 1
                        if a_annotation['presenceOfAmbiguity']:
                            Good_SL_Amb += 1

                    InRS = False
                    if a_annotation['RS']['id'] == GS:
                        InRS = True
                        Good_RS_number += 1
                        if a_annotation['presenceOfAmbiguity']:
                            Good_RS_Amb += 1

                    if InSL and InRS == False:
                        Good_SL_Bad_RS_number += 1

                    if InRS and InSL == False:
                        Good_RS_Bad_SL_number += 1


                    if InRS == False and InSL == False and a_annotation['presenceOfAmbiguity']:
                        Both_bad_with_ambiguity += 1


                    if InRS == False and InSL == False and a_annotation['presenceOfAmbiguity'] == False:
                        Both_bad_without_ambiguity += 1



        print('total_predictions: ' + str(total_predictions) + '  ')

        print('totol_label: ' + str(totol_label) + '  ')


        print('Global_Good_SL: ' + str(Good_SL_number) + '  ')
        print('Global_precision_SL: ' + str(Good_SL_number / totol_label) + '  ')
        print('Global_Good_RS: ' + str(Good_RS_number) + '  ')
        print('Global_precision_RS: ' + str(Good_RS_number / totol_label) + '  ')

        print('total_ambiguities: ' + str(total_ambiguities) + '  ')
        print('Average_amb_lenth: ' + str(candidates_inside_amb / total_ambiguities) + '  ')
        print('Average_GT_in_amb: ' + str(Good_in_Amb / total_ambiguities) + '  ')
        print('Good_RS_Amb: ' + str(Good_RS_Amb) + '  ')
        print('Ratio_RS_Amb: ' + str(Good_RS_Amb / total_ambiguities) + '  ')
        print('Good_SL_Amb: ' + str(Good_SL_Amb) + '  ')
        print('Ratio_SL_Amb: ' + str(Good_SL_Amb / total_ambiguities) + '  ')

        print('Good_RS_Bad_SL_number: ' + str(Good_RS_Bad_SL_number) + '  ')
        print('Good_SL_Bad_RS_number: ' + str(Good_SL_Bad_RS_number) + '  ')
        print('Both_bad_with_ambiguity: ' + str(Both_bad_with_ambiguity) + '  ')
        print('Both_bad_without_ambiguity: ' + str(Both_bad_without_ambiguity) + '  ')

        return Good_RS_number / totol_label



if __name__ == '__main__':

    pass


