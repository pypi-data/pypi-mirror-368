import sys
import os.path as osp
import socket

import torch

machine_name = socket.gethostname()
torch.set_default_dtype(torch.bfloat16)
if torch.cuda.is_available():
    if machine_name == '4090':
        device = torch.device("cuda:0")
    else:
        device = torch.device("cuda:0")
else:
    device = torch.device("cpu")


# Initialize paths.
if machine_name == '4090':
    project_root = '/home/zzy/docker_envs/pretrain/proj'
    sys.path.append(osp.join(project_root, 'hotpot'))
elif machine_name == 'DESKTOP-G9D9UUB':
    project_root = '/mnt/d/zhang/OneDrive/Papers/BayesDesign/results'
    sys.path.append(osp.join(project_root, 'hotpot'))
elif machine_name == 'docker':
    project_root = '/app/proj'
    sys.path.append(osp.join(project_root, 'hotpot'))
elif machine_name == '3090':
    project_root = '/home/zz1/docker/proj'
    sys.path.append(osp.join(project_root, 'hotpot'))

# Running in Super
elif str.split(__file__, '/')[1:4] == ['data', 'run01', 'scz0s3z']:
    print('In Super')
    project_root = '/HOME/scz0s3z/run/proj/'
    sys.path.append(osp.join(project_root, 'hotpot-zzy'))
else:
    raise ValueError(__file__)

from hotpot.plugins.ComplexFormer import (
    models as M,
    train as pretrain
)
from hotpot.plugins.ComplexFormer.data import dataset as D

models_dir = osp.join(project_root, 'models')
# dataset save paths
_tmqm_data_dir = osp.join(project_root, 'datasets', 'tmqm_data0207')

if str.split(__file__, '/')[1:4] == ['data', 'run01', 'scz0s3z']:
    print('in /dev/shm')
    tmqm_getter = D.DatasetGetter('/dev/shm', 'tmqm')
    mono_getter = D.DatasetGetter('/dev/shm', "mono")
else:
    tmqm_getter = D.DatasetGetter(project_root, "tmqm")
    mono_getter = D.DatasetGetter(project_root, "mono")

ds_tqdm, dst_tqdm = tmqm_getter.get_datasets()
ds_mono, dst_mono = mono_getter.get_datasets()

dataset = D.MConcatDataset((ds_tqdm,))
dataset_test = D.MConcatDataset((dst_tqdm,))

INPUT_X_INDEX = tmqm_getter.get_index('x', ('atomic_number', 'n', 's', 'p', 'd', 'f', 'g', 'x', 'y', 'z'))


EPOCHS = 50
OPTIMIZER = torch.optim.Adam
X_DIM = len(INPUT_X_INDEX)
EDGE_DIM = ds_tqdm[0].edge_attr.shape[-1]
VEC_DIM = 64
MASK_VEC = (-1 * torch.ones(X_DIM)).to(device)
RING_LAYERS = 1
RING_HEADS = 2
MOL_LAYERS = 1
MOL_HEADS = 2

ATOM_TYPES = 119  # Arguments for atom type loss


hypers = pretrain.Hypers()
hypers.batch_size = 1024
hypers.lr = 2e-4
hypers.weight_decay = 4e-5

core = M.Core(
    x_dim=X_DIM,
    edge_dim=EDGE_DIM,
    vec_dim=VEC_DIM,
    x_label_nums=ATOM_TYPES,
    ring_layers=RING_LAYERS,
    ring_nheads=RING_HEADS,
    mol_layers=MOL_LAYERS,
    mol_nheads=MOL_HEADS,
)

def atom_types():
    pretrain.run(
        work_name="AtomType",
        work_dir=models_dir,
        core=core,
        train_dataset=ds_tqdm,
        test_dataset=dst_tqdm,
        hypers=hypers,
        epochs=EPOCHS,
        device=device,
        eval_steps=1,
        # checkpoint_path=-1,
        load_core_only=True,
        # save_model=False,
        # x_masker=pretrain.x_masker_func,
        load_all_data=True,
        show_batch_pbar=True,
        constant_lr=True,
        other_metric='macc',
        early_stopping=True,
        loss_weight_calculator=True,
        loss_weight_method='cross-entropy',
        debug=True,
    )

def atom_charges():
    pretrain.run(
        work_name="AtomCharge",
        work_dir=models_dir,
        core=core,
        train_dataset=ds_tqdm,
        test_dataset=dst_tqdm,
        hypers=hypers,  # pretrain.Hyper instance
        epochs=EPOCHS,  # int
        device=device,  # cuda or cpu
        eval_steps=1,  # the interval (epoch) steps to eval
        # checkpoint_path=-1,  # (path or index)
        load_core_only=True,  # if just load core params
        with_xyz=True,  # xyz as input
        # save_model=False,
        # x_masker=pretrain.x_masker_func,  # predict masked nodes
        load_all_data=True,  # if load all data before training
        constant_lr=True,  #
        # other_metric='metal_accuracy',
        early_stopping=True,
        # debug=True,
    )

def combined_training():
    work_name = 'MultiTask'
    feature_extractors = {
        'AtomType': 'atom',
        'AtomCharge': 'atom',
        'RingsAromatic': 'ring',
    }
    predictors = {
        'AtomType': 'onehot',
        'AtomCharge': 'num',
        'RingsAromatic': 'binary',
    }
    target_getters = {
        'AtomType': pretrain.TargetGetter(ds_tqdm[0], 'x', 'atomic_number'),
        'AtomCharge': pretrain.TargetGetter(ds_tqdm[0], 'x', 'partial_charge'),
        'RingsAromatic': pretrain.TargetGetter(ds_tqdm[0], 'rings_attr', 'is_aromatic'),
    }
    loss_fn = {
        'AtomType': 'cross_entropy',
        'AtomCharge': 'mse',
        'RingsAromatic': 'binary_cross_entropy',
    }
    primary_metric = {
        'AtomType': 'acc',
        'AtomCharge': 'r2',
        'RingsAromatic': 'bacc',
    }

    pretrain.run(
        work_name=work_name,
        work_dir=models_dir,
        core=core,
        train_dataset=ds_tqdm,
        test_dataset=dst_tqdm,
        hypers=hypers,  # pretrain.Hyper instance
        epochs=EPOCHS,  # int
        device=device,  # cuda or cpu
        eval_steps=1,  # the interval (epoch) steps to eval
        load_all_data=True,
        target_getter=target_getters,
        feature_extractor=feature_extractors,
        predictor=predictors,
        loss_fn=loss_fn,
        primary_metric=primary_metric,
        debug=True
    )

def combined_training_():
    work_name = 'MultiTask'
    feature_extractors = {
        'AT': 'atom',  # AtomType
        'AC': 'atom',  # AtomCharge
        'MT': 'metal', # MetalType
        'ME': 'mol',   # MolEnergy
        'MDs': 'mol',  # MolDisp
        'MDi': 'mol',  # MolDipole
        'MMQ': 'mol',  # MolMetalQ
        'MH': 'mol',   # MolHl
        'MHM': 'mol',  # MolHOMO
        'MLM': 'mol',  # MolLOMO
        'MP': 'mol',   # MolPolar
        # 'RingsAromatic': 'ring',
    }
    predictors = {
        'AT': 'onehot',
        'AC': 'num',
        'MT': 'onehot',
        'ME': 'num',
        'MDs': 'num',
        'MDi': 'num',
        'MMQ': 'num',
        'MH': 'num',
        'MHM': 'num',
        'MLM': 'num',
        'MP': 'num',
        # 'RingsAromatic': 'binary',
    }
    target_getters = {
        'AT': pretrain.TargetGetter(ds_tqdm[0], 'x', 'atomic_number'),
        'AC': pretrain.TargetGetter(ds_tqdm[0], 'x', 'partial_charge'),
        'MT': lambda batch: batch.x[:, 0][M.where_metal(batch.x[:, 0])],
        'ME': pretrain.TargetGetter(ds_tqdm[0], 'y', 'energy'),
        'MDs': pretrain.TargetGetter(ds_tqdm[0], 'y', 'dispersion'),
        'MDi': pretrain.TargetGetter(ds_tqdm[0], 'y', 'dipole'),
        'MMQ': pretrain.TargetGetter(ds_tqdm[0], 'y', 'metal_q'),
        'MH': pretrain.TargetGetter(ds_tqdm[0], 'y', 'Hl'),
        'MHM': pretrain.TargetGetter(ds_tqdm[0], 'y', 'HOMO'),
        'MLM': pretrain.TargetGetter(ds_tqdm[0], 'y', 'LUMO'),
        'MP': pretrain.TargetGetter(ds_tqdm[0], 'y', 'polarizability'),

        # 'RingsAromatic': pretrain.TargetGetter(dataset[0], 'rings_attr', 'is_aromatic'),
    }
    loss_fn = {
        'AT': 'cross_entropy',
        'AC': 'mse',
        'MT': 'cross_entropy',
        'ME': 'mse',
        'MDs': 'mse',
        'MDi': 'mse',
        'MMQ': 'mse',
        'MH': 'mse',
        'MHM': 'mse',
        'MLM': 'mse',
        'MP': 'mse',
        # 'RingsAromatic': 'binary_cross_entropy',
    }
    primary_metric = {
        'AT': 'acc',
        'AC': 'r2',
        'MT': 'macc',
        'ME': 'r2',
        'MDs': 'r2',
        'MDi': 'r2',
        'MMQ': 'r2',
        'MH': 'r2',
        'MHM': 'r2',
        'MLM': 'r2',
        'MP': 'r2',
        # 'RingsAromatic': 'bacc',
    }

    pretrain.run(
        work_name=work_name,
        work_dir=models_dir,
        core=core,
        train_dataset=dataset,
        test_dataset=dataset_test,
        hypers=hypers,  # pretrain.Hyper instance
        epochs=EPOCHS,  # int
        device=device,  # cuda or cpu
        eval_steps=1,  # the interval (epoch) steps to eval
        load_all_data=True,
        target_getter=target_getters,
        feature_extractor=feature_extractors,
        predictor=predictors,
        loss_fn=loss_fn,
        primary_metric=primary_metric,
        checkpoint_path=-1,
        # debug=True
    )

if __name__ == '__main__':
    # atom_types()
    # atom_charges()
    combined_training_()
