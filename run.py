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
import argparse
import os
import radarstation.radar_station as rs
import radarstation.embedding_loader as el

# python run.py --data_path=E://Submission/data --output_path=E://Submission/output --scoreSystem=MTab --tolerance=0.97 --dataset=Limaye --model=RotatE --evaluation

def parse_args():
    parser = argparse.ArgumentParser(description='Radar Station Disambiguation')
    parser.add_argument('--data_path', type=str,
                        help='data folder for the candidate scores, embeddings, and ground truth')
    parser.add_argument('--output_path', type=str, help='the output folder for Radar Station disambiguation algorithm')
    parser.add_argument('--tolerance', type=float, help='the tolerence t for the ambiguity selection, 0<=t<=1')
    parser.add_argument('--scoreSystem', type=str, choices=["DAGOBAHSL", "MTab", "bbw"], help='the scoring system using for the calculation')
    parser.add_argument('--dataset', type=str, choices=["T2D", "Limaye", "2T", "ShortTable"],
                        help='the target dataset which aimes to be interpretated, choose between T2D, Limaye, 2T, and ShortTable')
    parser.add_argument('--model', type=str, choices=["RotatE","TransE","DistMult","ComplEx", "BigGraph"],
                        help='the target model for enabling the disambiguation, in this repository, only RotatE is available.')

    parser.add_argument("--evaluation", action="store_true", help="Whether or not to evaluate the output.")
    parser.add_argument("--debug", action="store_true", help="run without loading the embeddings.")


    args = parser.parse_args()

    if args.model not in ["RotatE","TransE","DistMult","ComplEx", "BigGraph"]:
        raise("please reset the input embeddings model")

    if args.tolerance < 0 or args.tolerance > 1:
        raise("please reset the tolerance 0<=t<=1. ")

    if args.dataset not in ["T2D", "Limaye", "2T", "ShortTable"]:
        raise ("the dataset should be choosen inside T2D, Limaye, 2T, and ShortTable")

    return args


if __name__ == '__main__':

    args = parse_args()

    print('Loading embeddings ... ')
    if args.debug:
        import numpy as np
        embeddings = np.array([1,1])
        EmbeddingLoader = ''
    else:
        EmbeddingLoader = el.Embedding_Loader(args.data_path, args.model)
        embeddings = EmbeddingLoader.LoadEmbeddings('Q81')
        print(len(embeddings))

    if embeddings.any():
        print('Embeddings loaded.')

        Radar = rs.Radar_Station(args.data_path, EmbeddingLoader, goldStandard=args.dataset,scoringSystem=args.scoreSystem, annotationSe=args.tolerance, outputfile = args.output_path, dataPath = args.data_path)
        a = Radar.RadarStation_manager()
        print('Radar Station disambiguation finished.')

        if args.evaluation:
            from radarstation.evaluation import evaluater
            print('Evaluation starts...')
            Evaluator = evaluater([args.dataset], args.output_path, args.data_path)
            ingh = Evaluator.evaluator_manager()
            pass
    else:
        raise ('Loading Embeddings failed.')

