#!/usr/bin/python3
NEPTUNE_API_TOKEN = "YOUR-API-KEY"
NEPTUNE_PROJECT_NAME = "YOUR-PROJECT-NAME"
NEPTUNE_MODEL_NAME = "YOUR-MODEL-NAME"

import matplotlib
from bernn.utils.pool_metrics import log_pool_metrics

matplotlib.use('Agg')
CUDA_VISIBLE_DEVICES = ""

import uuid
import shutil

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import json
import copy
import torch
# torch.set_default_dtype(torch.float64)
from torch import nn
import os

from sklearn import metrics
from tensorboardX import SummaryWriter
from ax.service.managed_loop import optimize
from sklearn.metrics import matthews_corrcoef as MCC
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from bernn.ml.train.params_gp import *
from bernn.utils.data_getters import get_alzheimer, get_amide, get_mice, get_data
from bernn.dl.models.pytorch.aedann import ReverseLayerF
from bernn.dl.models.pytorch.utils.loggings import TensorboardLoggingAE, log_metrics, log_input_ordination, \
    LogConfusionMatrix, log_plots, log_neptune, log_shap, log_mlflow, make_data
from bernn.dl.models.pytorch.utils.dataset import get_loaders, get_loaders_no_pool
from bernn.utils.utils import scale_data, to_csv
from bernn.dl.models.pytorch.utils.utils import get_optimizer, to_categorical, get_empty_dicts, get_empty_traces, \
    log_traces, get_best_values, add_to_logger, add_to_neptune, \
    add_to_mlflow
import mlflow
import warnings
from datetime import datetime


# import StratifiedGroupKFold
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold
from bernn.utils.utils import get_unique_labels

# from fastapi import BackgroundTasks, FastAPI
# from threading import Thread

# app = FastAPI()

warnings.filterwarnings("ignore")

random.seed(1)
torch.manual_seed(1)
np.random.seed(1)


def keep_top_features(data, path, args):
    """
    Keeps the top features according to the precalculated scores
    Args:
        data: The data to be used to keep the top features

    Returns:
        data: The data with only the top features
    """
    top_features = pd.read_csv(f'{path}/{args.best_features_file}', sep=',')
    for group in ['all', 'train', 'valid', 'test']:
        data['inputs'][group] = data['inputs'][group].loc[:, top_features.iloc[:, 0].values[:args.n_features]]

    return data

def binarize_labels(data, controls):
    """
    Binarizes the labels to be used in the classification loss
    Args:
        labels: The labels to be binarized
        controls: The control labels

    Returns:
        labels: The binarized labels
    """
    for group in ['all', 'train', 'valid', 'test']:
        data['labels'][group] = np.array([1 if x not in controls else 0 for x in data['labels'][group]])
        data['cats'][group] = data['labels'][group]
    return data

from train_ae import TrainAE

class TrainAEClassifierHoldout(TrainAE):

    def __init__(self, args, path, fix_thres=-1, load_tb=False, log_metrics=False, keep_models=True, log_inputs=True,
                 log_plots=False, log_tb=False, log_neptune=False, log_mlflow=True, groupkfold=True, pools=True):
        """

        Args:
            args: contains multiple arguments passed in the command line
            log_path (str): Path where the tensorboard logs are saved
            path (str): Path to the data (in .csv format)
            fix_thres (float): If 1 > fix_thres >= 0 then the threshold is fixed to that value.
                       any other value means the threshold won't be fixed and will be
                       learned as an hyperparameter
            load_tb (bool): If True, loads previous runs already saved
            log_metrics (bool): Whether or not to keep the batch effect metrics
            keep_models (bool): Whether or not to save the models trained
                                (can take a lot of space if training a lot of models)
            log_inputs (bool): Whether or not to log graphs or batch effect metrics
                                of the scaled inputs
            log_plots (bool): For each optimization iteration, on the first iteration, wether or
                              not to plot PCA, UMAP, CCA and LDA of the encoded and reconstructed
                              representations.
            log_tb (bool): Whether or not to use tensorboard.
            log_mlflow (bool): Wether or not to use mlflow.
        """

        super(TrainAEClassifierHoldout, self).__init__(args, path, fix_thres, load_tb, log_metrics, keep_models,
                                                       log_inputs, log_plots, log_tb, log_neptune, log_mlflow, groupkfold, pools)

    def train(self, params):
        """
        Args:
            params: Contains the hyperparameters to be optimized

        Returns:
            best_closs: The best classification loss on the valid set

        """
        start_time = datetime.now()

        print(params)

        # Assigns the hyperparameters getting optimized
        smooth = params['smoothing']
        layer1 = params['layer1']
        layer2 = params['layer2']
        scale = params['scaler']
        self.gamma = params['gamma']
        self.beta = params['beta']
        self.zeta = params['zeta']
        thres = params['thres']
        wd = params['wd']
        nu = params['nu']
        lr = params['lr']
        self.l1 = params['l1']
        self.reg_entropy = params['reg_entropy']

        dropout = params['dropout']
        margin = params['margin']

        self.args.scaler = scale
        self.args.warmup = params['warmup']
        self.args.disc_b_warmup = params['disc_b_warmup']

        # ncols = params['ncols']
        # if ncols > self.data['inputs']['all'].shape[1]:
        #     ncols = self.data['inputs']['all'].shape[1]

        optimizer_type = 'adam'
        metrics = {'pool_metrics': {}}
        # self.log_path is where tensorboard logs are saved
        self.foldername = str(uuid.uuid4())

        self.complete_log_path = f'logs/ae_classifier_holdout/{self.foldername}'
        loggers = {'cm_logger': LogConfusionMatrix(self.complete_log_path)}
        print(f'See results using: tensorboard --logdir={self.complete_log_path} --port=6006')

        hparams_filepath = self.complete_log_path + '/hp'
        os.makedirs(hparams_filepath, exist_ok=True)
        self.args.model_name = 'ae_classifier_holdout'
        if self.log_tb:
            loggers['tb_logging'] = TensorboardLoggingAE(hparams_filepath, params, variational=self.args.variational,
                                                         zinb=self.args.zinb,
                                                         tw=self.args.tied_weights,
                                                         dloss=self.args.dloss,
                                                         tl=0,  # to remove, useless now
                                                         pseudo=self.args.predict_tests,
                                                         train_after_warmup=self.args.train_after_warmup,
                                                         berm='none',  # to remove, useless now
                                                         args=self.args)
        else:
            model = None
            run = None

        if self.log_neptune:
            # Create a Neptune run object
            run = neptune.init_run(
                project=NEPTUNE_PROJECT_NAME,
                api_token=NEPTUNE_API_TOKEN,
            )  # your credentials
            model = neptune.init_model_version(
                model=NEPTUNE_MODEL_NAME,
                project=NEPTUNE_PROJECT_NAME,
                api_token=NEPTUNE_API_TOKEN,
                # your credentials
            )
            run["dataset"].track_files(f"{self.path}/{self.args.csv_file}")
            run["metadata"].track_files(
                f"{self.path}/subjects_experiment_ATN_verified_diagnosis.csv"
            )
            # Track metadata and hyperparameters by assigning them to the run
            model["inputs_type"] = run["inputs_type"] = args.csv_file.split(".csv")[0]
            model["best_unique"] = run["best_unique"] = args.best_features_file.split(".tsv")[0]
            model["use_valid"] = run["use_valid"] = args.use_valid
            model["use_test"] = run["use_test"] = args.use_test
            model["tied_weights"] = run["tied_weights"] = args.tied_weights
            model["random_recs"] = run["random_recs"] = args.random_recs
            model["train_after_warmup"] = run["train_after_warmup"] = args.train_after_warmup
            model["dloss"] = run["dloss"] = args.dloss
            model["predict_tests"] = run["predict_tests"] = args.predict_tests
            model["variational"] = run["variational"] = args.variational
            model["zinb"] = run["zinb"] = args.zinb
            model["threshold"] = run["threshold"] = args.threshold
            model["rec_loss_type"] = run["rec_loss_type"] = args.rec_loss
            model["strategy"] = run["strategy"] = args.strategy
            model["bad_batches"] = run["bad_batches"] = args.bad_batches
            model["remove_zeros"] = run["remove_zeros"] = args.remove_zeros
            model["parameters"] = run["parameters"] = params
            model["csv_file"] = run["csv_file"] = args.csv_file
            model["model_name"] = run["model_name"] = 'ae_classifier_holdout'
            model["n_meta"] = run["n_meta"] = args.n_meta
            model["n_emb"] = run["n_emb"] = args.embeddings_meta
            model["groupkfold"] = run["groupkfold"] = args.groupkfold
            model["embeddings_meta"] = run["embeddings_meta"] = args.embeddings_meta
            model["foldername"] = run["foldername"] = self.foldername
            model["use_mapping"] = run["use_mapping"] = args.use_mapping
            model["dataset_name"] = run["dataset_name"] = args.dataset
            model["n_agg"] = run["n_agg"] = args.n_agg
            model["kan"] = run["kan"] = args.kan
        else:
            model = None
            run = None

        if self.log_mlflow:
            mlflow.set_experiment(
                self.args.exp_id,
            )
            try:
                mlflow.start_run()
            except:
                mlflow.end_run()
                mlflow.start_run()
            mlflow.log_params({
                "inputs_type": args.csv_file.split(".csv")[0],
                "best_unique": args.best_features_file.split(".tsv")[0],
                "tied_weights": args.tied_weights,
                "random_recs": args.random_recs,
                "train_after_warmup": args.train_after_warmup,
                "warmup_after_warmup": args.warmup_after_warmup,
                "dloss": args.dloss,
                "predict_tests": args.predict_tests,
                "variational": args.variational,
                "zinb": args.zinb,
                "threshold": args.threshold,
                "rec_loss_type": args.rec_loss,
                "bad_batches": args.bad_batches,
                "remove_zeros": args.remove_zeros,
                "parameters": params,
                "scaler": params['scaler'],
                "csv_file": args.csv_file,
                "model_name": args.model_name,
                "n_meta": args.n_meta,
                "n_emb": args.embeddings_meta,
                "groupkfold": args.groupkfold,
                "foldername": self.foldername,
                "use_mapping": args.use_mapping,
                "dataset_name": args.dataset,
                "n_agg": args.n_agg,
                "lr": lr,
                "wd": wd,
                "dropout": dropout,
                "margin": margin,
                "smooth": smooth,
                "layer1": layer1,
                "layer2": layer2,
                "gamma": self.gamma,
                "beta": self.beta,
                "zeta": self.zeta,
                "thres": thres,
                "nu": nu,
                "kan": args.kan,
                "l1": self.l1,
                "reg_entropy": self.reg_entropy,
                "use_l1": args.use_l1,
                "clip_val": args.clip_val,
                "update_grid": args.update_grid,
                "prune_threshold": args.prune_threshold,
            })
        else:
            model = None
            run = None
        seed = 0
        combinations = []
        h = 0
        best_closses = []
        best_mccs = []
        while h < self.args.n_repeats:
            prune_threshold = self.args.prune_threshold
            print(f'Rep: {h}')
            epoch = 0
            self.best_loss = np.inf
            self.best_closs = np.inf
            self.best_dom_loss = np.inf
            self.best_dom_acc = np.inf
            self.best_acc = 0
            self.best_mcc = -1
            self.warmup_counter = 0
            self.warmup_b_counter = 0
            self.warmup_disc_b = False
            # best_acc = 0
            # best_mcc = -1
            # warmup_counter = 0
            # warmup_b_counter = 0
            if self.args.warmup > 0:
                warmup = True
            else:
                warmup = False
            if self.args.dataset == 'alzheimer':
                self.data, self.unique_labels, self.unique_batches = get_alzheimer(self.path, args, seed=seed)
                self.pools = True
            elif self.args.dataset in ['amide', 'adenocarcinoma']:
                self.data, self.unique_labels, self.unique_batches = get_amide(self.path, args, seed=seed)
                self.pools = True

            elif self.args.dataset == 'mice':
                # This seed split the data to have n_samples in train: 96, valid:52, test: 23
                self.data, self.unique_labels, self.unique_batches = get_mice(self.path, args, seed=seed)
            elif self.args.dataset == 'multi':
                self.data, self.unique_labels, self.unique_batches = get_data3(self.path, args, seed=seed)
                self.pools = self.args.pool
            else:
                self.data, self.unique_labels, self.unique_batches = get_data(self.path, args, seed=seed)
                self.pools = self.args.pool
            if args.best_features_file != '':
                self.data = keep_top_features(self.data, self.path, self.args)
            if self.args.controls != '':
                self.data = binarize_labels(self.data, self.args.controls)
                self.unique_labels = np.unique(self.data['labels']['all'])
            self.n_cats = len(np.unique(self.data['cats']['all']))  # + 1  # for pool samples
            if self.args.groupkfold:
                combination = list(np.concatenate((np.unique(self.data['batches']['train']),
                                                np.unique(self.data['batches']['valid']),
                                                np.unique(self.data['batches']['test']))))
                seed += 1
                if combination not in combinations:
                    combinations += [combination]
                else:
                    continue
            # print(combinations)
            self.columns = self.data['inputs']['all'].columns
            h += 1
            self.make_samples_weights()
            # event_acc is used to verify if the hparams have already been tested. If they were,
            # the best classification loss is retrieved and we go to the next trial
            event_acc = EventAccumulator(hparams_filepath)
            event_acc.Reload()
            if len(event_acc.Tags()['tensors']) > 2 and self.load_tb:
                # try:
                #     best_acc = get_best_acc_from_tb(event_acc)
                # except:
                pass
            else:
                # If thres > 0, features that are 0 for a proportion of samples smaller than thres are removed
                # data = self.keep_good_features(thres)

                # Transform the data with the chosen scaler
                data = copy.deepcopy(self.data)
                data, self.scaler = scale_data(scale, data, self.args.device)

                # feature_selection = get_feature_selection_method('mutual_info_classif')
                # mi = feature_selection(data['inputs']['train'], data['cats']['train'])
                for g in list(data['inputs'].keys()):
                    data['inputs'][g] = data['inputs'][g].round(4)
                # Gets all the pytorch dataloaders to train the models
                if self.pools:
                    loaders = get_loaders(data, self.args.random_recs, self.samples_weights, self.args.dloss, None,
                                        None, bs=64)
                else:
                    loaders = get_loaders_no_pool(data, self.args.random_recs, self.samples_weights, self.args.dloss,
                                                  None, None, bs=self.args.bs)

                if h == 1 or self.args.kan == 1:

                    ae = AutoEncoder(data['inputs']['all'].shape[1],
                                    n_batches=self.n_batches,
                                    nb_classes=self.n_cats,
                                    mapper=self.args.use_mapping,
                                    layer1=layer1,
                                    layer2=layer2,
                                    n_layers=self.args.n_layers,
                                    n_meta=self.args.n_meta,
                                    n_emb=self.args.embeddings_meta,
                                    dropout=dropout,
                                    variational=self.args.variational, conditional=False,
                                    zinb=self.args.zinb, add_noise=0, tied_weights=self.args.tied_weights,
                                    use_gnn=0,  # TODO to remove
                                    device=self.args.device,
                                    update_grid=self.args.update_grid
                                    ).to(self.args.device)
                    ae.mapper.to(self.args.device)
                    ae.dec.to(self.args.device)
                    # if self.args.embeddings_meta > 0:
                    #     n_meta = self.n_meta
                    shap_ae = SHAPAutoEncoder(data['inputs']['all'].shape[1],
                                            n_batches=self.n_batches,
                                            nb_classes=self.n_cats,
                                            mapper=self.args.use_mapping,
                                            layer1=layer1,
                                            layer2=layer2,
                                            n_layers=self.args.n_layers,
                                            n_meta=self.args.n_meta,
                                            n_emb=self.args.embeddings_meta,
                                            dropout=dropout,
                                            variational=self.args.variational, conditional=False,
                                            zinb=self.args.zinb, add_noise=0, tied_weights=self.args.tied_weights,
                                            use_gnn=0,  # TODO remove this
                                            device=self.args.device).to(self.args.device)
                    shap_ae.mapper.to(self.args.device)
                    shap_ae.dec.to(self.args.device)
                else:
                    ae.random_init(nn.init.xavier_uniform_)
                loggers['logger_cm'] = SummaryWriter(f'{self.complete_log_path}/cm')
                loggers['logger'] = SummaryWriter(f'{self.complete_log_path}/traces')
                sceloss, celoss, mseloss, triplet_loss = self.get_losses(scale, smooth, margin, args.dloss)

                optimizer_ae = get_optimizer(ae, lr, wd, optimizer_type)

                # Used only if bdisc==1
                optimizer_b = get_optimizer(ae.dann_discriminator, 1e-2, 0, optimizer_type)

                self.hparams_names = [x.name for x in linsvc_space]
                if self.log_inputs and not self.logged_inputs:
                    data['inputs']['all'].to_csv(
                        f'{self.complete_log_path}/{self.args.berm}_inputs.csv')
                    if self.log_neptune:
                        run[f"inputs.csv"].track_files(f'{self.complete_log_path}/{self.args.berm}_inputs.csv')
                    log_input_ordination(loggers['logger'], data, self.scaler, epoch)
                    if self.pools:
                        metrics = log_pool_metrics(data['inputs'], data['batches'], data['labels'], loggers, epoch,
                                                   metrics, 'inputs')
                    self.logged_inputs = True

                values, best_values, _, best_traces = get_empty_dicts()

                early_stop_counter = 0
                best_vals = values
                if h > 1:  # or warmup_counter == 100:
                    ae.load_state_dict(torch.load(f'{self.complete_log_path}/warmup.pth'))
                    print(f"\n\nNO WARMUP\n\n")
                if h == 1:
                    for epoch in range(0, self.args.warmup):
                        no_error = self.warmup_loop(optimizer_ae, ae, celoss, loaders['all'], triplet_loss, mseloss,
                                         self.best_loss, True, epoch,
                                         optimizer_b, values, loggers, loaders, run, self.args.use_mapping)
                        if not no_error:
                            break
                for epoch in range(0, self.args.n_epochs):
                    if early_stop_counter == self.args.early_stop:
                        if self.verbose > 0:
                            print('EARLY STOPPING.', epoch)
                        break
                    lists, traces = get_empty_traces()

                    if self.args.warmup_after_warmup:
                        self.warmup_loop(optimizer_ae, ae, celoss, loaders['all'], triplet_loss, mseloss,
                                            self.best_loss, False, epoch,
                                            optimizer_b, values, loggers, loaders, run, self.args.use_mapping)
                    if not self.args.train_after_warmup:
                        ae = self.freeze_all_but_clayers(ae)
                    closs, _, _ = self.loop('train', optimizer_ae, ae, sceloss,
                                            loaders['train'], lists, traces, nu=nu)
            
                    if torch.isnan(closs):
                        print("NAN LOSS")
                        break
                    ae.eval()
                    ae.mapper.eval()

                    # Below is the loop for all sets
                    with torch.no_grad():
                        for group in list(data['inputs'].keys()):
                            if group in ['all', 'all_pool']:
                                continue
                            closs, lists, traces = self.loop(group, optimizer_ae, ae, sceloss,
                                                             loaders[group], lists, traces, nu=0)
                        # IF KAN and pruning threshold > 0, then prune the network
                        if self.args.kan and prune_threshold > 0:
                            try:
                                self.prune_neurons(ae, prune_threshold)
                            except:
                                print("COULD NOT PRUNE")
                                # if self.log_mlflow:
                                #     mlflow.log_param('finished', 0)
                                break
                        if self.args.kan and self.args.prune_neurites_threshold > 0:
                            self.prune_neurites(ae)
                        if self.args.kan and early_stop_counter % 10 == 0 and early_stop_counter > 0:
                            prune_threshold *= 10
                            print(f"Pruning threshold: {prune_threshold}")

                                
                    traces = self.get_mccs(lists, traces)
                    values = log_traces(traces, values)
                    if self.log_tb:
                        try:
                            add_to_logger(values, loggers['logger'], epoch)
                        except:
                            print("Problem with add_to_logger!")
                    if self.log_neptune:
                        add_to_neptune(values, run, epoch)
                    if self.log_mlflow:
                        add_to_mlflow(values, epoch)
                    if np.mean(values['valid']['mcc'][-self.args.n_agg:]) > self.best_mcc and len(
                            values['valid']['mcc']) > self.args.n_agg:
                        print(f"Best Classification Mcc Epoch {epoch}, "
                              f"Acc: {values['test']['acc'][-1]}"
                              f"VALID Mcc: {values['valid']['mcc'][-1]}"
                              f"TEST Mcc: {values['test']['mcc'][-1]}"
                              f"Classification train loss: {values['train']['closs'][-1]},"
                              f" valid loss: {values['valid']['closs'][-1]},"
                              f" test loss: {values['test']['closs'][-1]}")
                        self.best_mcc = np.mean(values['valid']['mcc'][-self.args.n_agg:])
                        torch.save(ae.state_dict(), f'{self.complete_log_path}/model_{h}_state.pth')
                        torch.save(ae, f'{self.complete_log_path}/model_{h}.pth')
                        best_values = get_best_values(values.copy(), ae_only=False, n_agg=self.args.n_agg)
                        best_vals = values.copy()
                        best_vals['rec_loss'] = self.best_loss
                        best_vals['dom_loss'] = self.best_dom_loss
                        best_vals['dom_acc'] = self.best_dom_acc
                        early_stop_counter = 0

                    if values['valid']['acc'][-1] > self.best_acc:
                        print(f"Best Classification Acc Epoch {epoch}, "
                              f"Acc: {values['test']['acc'][-1]}"
                              f"Mcc: {values['test']['mcc'][-1]}"
                              f"Classification train loss: {values['train']['closs'][-1]},"
                              f" valid loss: {values['valid']['closs'][-1]},"
                              f" test loss: {values['test']['closs'][-1]}")

                        self.best_acc = values['valid']['acc'][-1]
                        early_stop_counter = 0

                    if values['valid']['closs'][-1] < self.best_closs:
                        print(f"Best Classification Loss Epoch {epoch}, "
                              f"Acc: {values['test']['acc'][-1]} "
                              f"Mcc: {values['test']['mcc'][-1]} "
                              f"Classification train loss: {values['train']['closs'][-1]}, "
                              f"valid loss: {values['valid']['closs'][-1]}, "
                              f"test loss: {values['test']['closs'][-1]}")
                        self.best_closs = values['valid']['closs'][-1]
                        early_stop_counter = 0
                    else:
                        # if epoch > self.warmup:
                        early_stop_counter += 1

                    if self.args.predict_tests and (epoch % 10 == 0):
                        loaders = get_loaders(self.data, data, self.args.random_recs, self.args.triplet_dloss, ae,
                                              ae.classifier, bs=self.args.bs)

                best_mccs += [self.best_mcc]

                best_lists, traces = get_empty_traces()
                
                # Verify the model exists
                if not os.path.exists(f'{self.complete_log_path}/model_{h}_state.pth'):
                    return -1
                
                # Loading best model that was saved during training
                ae.load_state_dict(torch.load(f'{self.complete_log_path}/model_{h}_state.pth'))
                # Need another model because the other cant be use to get shap values
                shap_ae.load_state_dict(torch.load(f'{self.complete_log_path}/model_{h}_state.pth'))
                # ae.load_state_dict(sd)
                ae.eval()
                shap_ae.eval()
                ae.mapper.eval()
                shap_ae.mapper.eval()
                with torch.no_grad():
                    for group in list(data['inputs'].keys()):
                        # if group in ['all', 'all_pool']:
                        #     continue
                        closs, best_lists, traces = self.loop(group, None, ae, sceloss,
                                                              loaders[group], best_lists, traces, nu=0, mapping=False)
                if self.log_neptune:
                    model["model"].upload(f'{self.complete_log_path}/model_{h}_state.pth')
                    model["validation/closs"].log(self.best_closs)
                best_closses += [self.best_closs]
                # logs things in the background. This could be problematic if the logging takes more time than each iteration of repetitive holdout
                # daemon = Thread(target=self.log_rep, daemon=True, name='Monitor',
                #                 args=[best_lists, best_vals, best_values, traces, model, metrics, run, cm_logger, ae,
                #                       shap_ae, h,
                #                       epoch])
                # daemon.start()
                self.log_rep(best_lists, best_vals, best_values, traces, model, metrics, run, loggers, ae,
                             shap_ae, h, epoch)

        # Logging every model is taking too much resources and it makes it quite complicated to get information when
        # Too many runs have been made. This will make the notebook so much easier to work with
        if np.mean(best_mccs) > self.best_mcc:
            try:
                if os.path.exists(
                        f'logs/best_models/ae_classifier_holdout/{self.args.dataset}/{self.args.dloss}_vae{self.args.variational}'):
                    shutil.rmtree(
                        f'logs/best_models/ae_classifier_holdout/{self.args.dataset}/{self.args.dloss}_vae{self.args.variational}',
                        ignore_errors=True)
                # os.makedirs(f'logs/best_models/ae_classifier_holdout/{self.args.dloss}_vae{self.args.variational}', exist_ok=True)
                shutil.copytree(f'{self.complete_log_path}',
                                f'logs/best_models/ae_classifier_holdout/{self.args.dataset}/{self.args.dloss}_vae{self.args.variational}')
                # print("File copied successfully.")

            # If source and destination are same
            except shutil.SameFileError:
                # print("Source and destination represents the same file.")
                pass
            self.best_mcc = np.mean(best_mccs)

        # Logs confusion matrices in the background. Also runs RandomForestClassifier on encoded and reconstructed
        # representations. This should be shorter than the actual calculation of the model above in the function,
        # otherwise the number of threads will keep increasing.
        # daemon = Thread(target=self.logging, daemon=True, name='Monitor', args=[run, cm_logger])
        # daemon.start()
        if self.log_mlflow:
            mlflow.log_param('finished', 1)
        self.logging(run, loggers['cm_logger'])

        if not self.keep_models:
            # shutil.rmtree(f'{self.complete_log_path}/traces', ignore_errors=True)
            # shutil.rmtree(f'{self.complete_log_path}/cm', ignore_errors=True)
            # shutil.rmtree(f'{self.complete_log_path}/hp', ignore_errors=True)
            shutil.rmtree(f'{self.complete_log_path}', ignore_errors=True)
        print('\n\nDuration: {}\n\n'.format(datetime.now() - start_time))
        best_closs = np.mean(best_closses)
        if best_closs < self.best_closs:
            self.best_closs = best_closs
            print("Best closs!")

        # It should not be necessary. To remove once certain the "Too many files open" error is no longer a problem
        plt.close('all')

        return self.best_mcc

    def increase_pruning_threshold(self):
        '''
        increase the pruning threshold
        
        Args:
        -----
            threshold : float
                the amount of increase
        
        Returns:
        --------
            None
        '''
        if self.prune_threshold == 0:
            self.prune_threshold = 1e-8
        else:
            self.prune_threshold *= 10

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    # parser.add_argument('--batch_columns', type=str, default='2,3')
    parser.add_argument('--random_recs', type=int, default=0)
    parser.add_argument('--predict_tests', type=int, default=0)
    parser.add_argument('--early_stop', type=int, default=100)
    parser.add_argument('--early_warmup_stop', type=int, default=0, help='If 0, then no early warmup stop')
    parser.add_argument('--train_after_warmup', type=int, default=1, help="Train autoencoder after warmup")
    parser.add_argument('--warmup_after_warmup', type=int, default=1, help="Warmup after warmup")
    parser.add_argument('--threshold', type=float, default=0.)
    parser.add_argument('--n_epochs', type=int, default=1000)
    parser.add_argument('--n_trials', type=int, default=100)
    parser.add_argument('--device', type=str, default='cuda:0')
    parser.add_argument('--rec_loss', type=str, default='mse')
    parser.add_argument('--tied_weights', type=int, default=0)
    parser.add_argument('--variational', type=int, default=0)
    parser.add_argument('--zinb', type=int, default=0)
    parser.add_argument('--use_valid', type=int, default=0, help='Use if valid data is in a seperate file')
    parser.add_argument('--use_test', type=int, default=0, help='Use if test data is in a seperate file')
    parser.add_argument('--use_mapping', type=int, default=1, help="Use batch mapping for reconstruct")
    parser.add_argument('--freeze_ae', type=int, default=0)
    parser.add_argument('--freeze_c', type=int, default=0)
    parser.add_argument('--bdisc', type=int, default=1)
    parser.add_argument('--n_repeats', type=int, default=5)
    parser.add_argument('--dloss', type=str, default='inverseTriplet')  # one of revDANN, DANN, inverseTriplet, revTriplet
    parser.add_argument('--csv_file', type=str, default='matrix.csv')
    parser.add_argument('--best_features_file', type=str, default='')  # best_unique_genes.tsv
    parser.add_argument('--bad_batches', type=str, default='')  # 0;23;22;21;20;19;18;17;16;15
    parser.add_argument('--remove_zeros', type=int, default=1)
    parser.add_argument('--n_meta', type=int, default=0)
    parser.add_argument('--embeddings_meta', type=int, default=0)
    parser.add_argument('--features_to_keep', type=str, default='features_proteins.csv')
    parser.add_argument('--groupkfold', type=int, default=1)
    parser.add_argument('--dataset', type=str, default='custom')
    parser.add_argument('--path', type=str, default='./data/PXD015912/')
    parser.add_argument('--exp_id', type=str, default='reviewer_exp')
    parser.add_argument('--bs', type=int, default=32, help='Batch size')
    parser.add_argument('--n_agg', type=int, default=1, help='Number of trailing values to get stable valid values')
    parser.add_argument('--n_layers', type=int, default=1, help='N layers for classifier')
    parser.add_argument('--log1p', type=int, default=1, help='log1p the data? Should be 0 with zinb')
    parser.add_argument('--strategy', type=str, default='CU_DEM', help='only for alzheimer dataset')
    parser.add_argument('--pool', type=int, default=1, help='only for alzheimer dataset')
    parser.add_argument('--log_plots', type=int, default=1, help='')
    parser.add_argument('--log_metrics', type=int, default=0, help='')
    parser.add_argument('--controls', type=str, default='', help='Which samples are the controls. Empty for not binary')
    parser.add_argument('--n_features', type=int, default=-1, help='')
    parser.add_argument('--kan', type=int, default=1, help='')
    parser.add_argument('--update_grid', type=int, default=1, help='')
    parser.add_argument('--use_l1', type=int, default=1, help='')
    parser.add_argument('--clip_val', type=float, default=1, help='')
    parser.add_argument('--prune_threshold', type=float, default=1.0, help='')
    parser.add_argument('--prune_neurites_threshold', type=float, default=0.0, help='')

    args = parser.parse_args()
    
    if not args.kan:
        from pytorch.aedann import AutoEncoder2 as AutoEncoder
        from pytorch.aedann import SHAPAutoEncoder2 as SHAPAutoEncoder
    elif args.kan == 1:
        from pytorch.aeekandann import KANAutoencoder2 as AutoEncoder
        from pytorch.aeekandann import SHAPKANAutoencoder2 as SHAPAutoEncoder
    elif args.kan == 2:
        # from bernn.dl.models.pytorch.aekandann import KANAutoencoder2 as AutoEncoder
        # from bernn.dl.models.pytorch.aekandann import SHAPKANAutoencoder2 as SHAPAutoEncoder
        from pytorch.aekandann import KANAutoencoder3 as AutoEncoder
        from pytorch.aekandann import SHAPKANAutoencoder3 as SHAPAutoEncoder
    
    try:
        mlflow.create_experiment(
            args.exp_id,
            # artifact_location=Path.cwd().joinpath("mlruns").as_uri(),
            # tags={"version": "v1", "priority": "P1"},
        )
    except:
        print(f"\n\nExperiment {args.exp_id} already exists\n\n")

    # args.batch_columns = [int(x) for x in args.batch_columns.split(',')]

    train = TrainAEClassifierHoldout(args, args.path, fix_thres=-1, load_tb=False, log_metrics=args.log_metrics, keep_models=False,
                    log_inputs=False, log_plots=args.log_plots, log_tb=False, log_neptune=False,
                    log_mlflow=True, groupkfold=args.groupkfold)

    parameters = {
        'nu': 57.62209361696243,
        'lr': 0.0002866874793641167,
        'wd': 2.1707730937174506e-06,
        'smoothing': 0.011093495786190033,
        'margin': 9.637901186943054,
        'warmup': 37,
        'disc_b_warmup': 1,
        'dropout': 0.15570732951164246,
        'layer2': 227,
        'layer1': 956,
        'gamma': 0.013416354045760274,
        'reg_entropy': 0.0018682798787011542,
        'l1': 3.904233171732793e-07,
        'scaler': 'robust_per_batch',
        'beta': 0,
        'zeta': 0,
        'thres': 0
    }

    train.train(parameters)

    # fig = plt.figure()
    # render(plot_contour(model=model, param_x="learning_rate", param_y="weight_decay", metric_name='Loss'))
    # fig.savefig('test.jpg')
    # print('Best Loss:', values[0]['loss'])
    # print('Best Parameters:')
    # print(json.dumps(best_parameters, indent=4))
