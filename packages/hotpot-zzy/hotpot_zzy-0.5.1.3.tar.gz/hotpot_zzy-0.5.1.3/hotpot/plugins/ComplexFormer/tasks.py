import functools
from abc import ABC, abstractmethod
from typing import Union, Callable, Optional, Iterable, Any
from typing_extensions import override

import numpy as np

import torch
import torch.nn as nn
import torch.optim.lr_scheduler as lrs

from torch_geometric.data import Batch

import lightning as L

from hotpot.utils import fmt_print
from . import (
    types as tp,
    models as M
)


class BaseTask(ABC):
    ############################# General Task Utils #################################
    @staticmethod
    def _preprocess_batch(task: 'Task', batch: Batch) -> Batch:
        if (preprocessor := getattr(task, '_batch_preprocessor', None)) and isinstance(preprocessor, Callable):
            return preprocessor(batch)
        return batch

    #################### Preprocessor before forward #################################
    @staticmethod
    def batch_dtype_preprocessor(batch):
        for name in batch.keys():
            if "index" in name:
                batch[name] = batch[name].long()
            elif name in ['batch', 'ptr']:
                batch[name] = batch[name].int()
            elif 'nums' in name:
                batch[name] = batch[name].int()
            elif isinstance(batch[name], torch.Tensor) and torch.is_floating_point(batch[name]):
                batch[name] = batch[name].bfloat16()

    @abstractmethod
    def batch_preprocessor(self, batch: Batch) -> Batch:
        raise NotImplementedError

    @abstractmethod
    def inputs_getter(self, batch: Batch) -> torch.Tensor:
        raise NotImplementedError

    @abstractmethod
    def get_xyz(self, inputs: tuple[torch.Tensor, ...]) -> Optional[torch.Tensor]:
        raise NotImplementedError

    @abstractmethod
    def perturb_xyz(self, xyz):
        raise NotImplementedError

    @abstractmethod
    def inputs_preprocessor(self, inputs: tuple[torch.Tensor, ...], **kwargs) -> tuple[torch.Tensor, ...]:
        raise NotImplementedError

    @abstractmethod
    def x_masker(self, inputs: tuple[torch.Tensor, ...]) -> (tuple[torch.Tensor, ...], torch.Tensor):
        raise NotImplementedError

    #########################################################################################################
    #########################################################################################################
    ################################### PostProcessor after forward #########################################
    @abstractmethod
    def feature_extractor(self, *args, **kwargs) -> Union[torch.Tensor, dict[str, torch.Tensor]]:
        raise NotImplementedError

    @abstractmethod
    def target_getter(self, batch: Batch) -> Union[torch.Tensor, dict[str, torch.Tensor]]:
        raise NotImplementedError

    @abstractmethod
    def loss_weight_calculator(self, target):
        raise NotImplementedError

    @abstractmethod
    def loss_fn(self, pred, target, loss_weight):
        raise NotImplementedError

    @abstractmethod
    def label2oh_conversion(self, target: Union[torch.Tensor, dict[str, torch.Tensor]]):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def peel_unmaksed_obj(
            feature_target: Union[torch.Tensor, dict[str, torch.Tensor]],
            mask_idx: Optional[Union[torch.Tensor, dict[str, torch.Tensor]]] = None,
    ):
        raise NotImplementedError

    @abstractmethod
    def log_on_train_batch_end(
            self,
            pl_module: L.LightningModule,
            loss: Union[torch.Tensor, dict[str, torch.Tensor]],
            pred: Union[torch.Tensor, dict[str, torch.Tensor]],
            target: Union[torch.Tensor, dict[str, torch.Tensor]],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_val_pred_target(
            self,
            pred: Union[torch.Tensor, dict[str, torch.Tensor]],
            target: Union[torch.Tensor, dict[str, torch.Tensor]]
    ):
        raise NotImplementedError

    @abstractmethod
    def eval_on_val_end(self,pl_module: L.LightningModule):
        raise NotImplementedError

    @staticmethod
    def _print_and_log_metrics(pl_module: L.LightningModule, metrics_dict: dict[str, float]):
        for metric_name, metric_value in metrics_dict.items():
            pl_module.log(metric_name, metric_value, sync_dist=True)  # Log metrics
        pl_module.val_metrics.update(metrics_dict)


class Task(BaseTask, ABC):
    _expect_types = {}

    def __init__(
            self,
            inputs_getter: Callable,
            feature_extractor: Union[Callable, dict[str, Callable]],
            target_getter: Union[tp.TargetGetter, dict[str, tp.TargetGetter]],
            loss_fn: Callable[[torch.Tensor, torch.Tensor, Optional[Any]], torch.Tensor],
            primary_metric: Union[str, dict[str, str]],
            metrics: dict[str, Callable[[tp.TensorArray, tp.TensorArray], Union[float, tp.TensorArray]]],
            batch_preprocessor: Optional[tp.BatchPreProcessor] = None,
            inputs_preprocessor: Optional[Callable] = None,
            xyz_index: Optional[Iterable[int]] = None,
            xyz_perturb_sigma: Optional[float] = None,
            extractor_attr_getter: Union[tp.ExtractorAttrGetter, dict[str, tp.ExtractorAttrGetter]] = None,
            loss_weight_calculator: Optional[Union[tp.LossWeightCalculator, dict[str, tp.LossWeightCalculator]]] = None,
            to_onehot: Union[bool, Iterable[str]] = False,
            onehot_types: Optional[Union[int, dict[str, int]]] = None,
            x_masker: Callable[[tuple[torch.Tensor, ...], torch.Tensor], tuple[torch.Tensor, torch.Tensor]] = None,
            mask_need_task: Optional[list[str]] = None,
            **kwargs
    ):
        # Inputs process control arguments
        self._batch_preprocessor = batch_preprocessor
        self._inputs_getter = inputs_getter
        self.xyz_index = xyz_index
        self._xyz_perturb_sigma = xyz_perturb_sigma
        self._inputs_preprocessor = inputs_preprocessor

        # Mask
        self._x_masker = x_masker
        self._mask_need_task = mask_need_task if mask_need_task else []
        self._masked_idx = None

        # Feature extract
        self._feature_extractor = feature_extractor
        self._extractor_attr_getter = extractor_attr_getter

        # get target
        self._target_getter = target_getter

        # Onehot
        self._to_onehot = to_onehot
        self._onehot_types = onehot_types

        # Loss
        self._loss_fn = loss_fn
        self._loss_weight_calculator = loss_weight_calculator
        self.atl_weights: Optional[dict[str, float]] = None

        # Metrics
        self._primary_metric = primary_metric
        self._metrics = metrics

    def _type_check(self):
        for attr_name, attr_type in self._expect_types.items():
            if not isinstance(getattr(self, attr_name), attr_type):
                raise TypeError(
                    f'The type of  {self.__class__.__name__}.{attr_name} should be {attr_type}, '
                    f'got {type(getattr(self, attr_name))}')

    #################### Preprocessor before forward #################################
    def batch_preprocessor(self, batch: Batch) -> Batch:
        if isinstance(self._batch_preprocessor, Callable):
            return self._batch_preprocessor(batch)
        return batch

    def inputs_getter(self, batch: Batch) -> torch.Tensor:
        return self._inputs_getter(batch)

    def get_xyz(self, inputs: tuple[torch.Tensor, ...]) -> Optional[torch.Tensor]:
        if self.xyz_index is None:
            return None
        else:
            return self.perturb_xyz(inputs[0][:, self.xyz_index])

    def perturb_xyz(self, xyz):
        if isinstance(self._xyz_perturb_sigma, float):
            return M.perturb_xyz(xyz, self._xyz_perturb_sigma)
        return xyz

    def inputs_preprocessor(self, inputs: tuple[torch.Tensor, ...], **kwargs) -> tuple[torch.Tensor, ...]:
        if self._inputs_preprocessor:
            return self._inputs_preprocessor(*inputs, **kwargs)
        return inputs

    def x_masker(self, inputs: tuple[torch.Tensor, ...]) -> (tuple[torch.Tensor, ...], torch.Tensor):
        if self._x_masker:
            return self._x_masker(inputs)
        return inputs, None

    @property
    def slr_metric_track(self):
        return "metric_to_track"

    def configure_optimizers(self, pl_module: L.LightningModule):
        optimizer = pl_module.t.optimizer(
            pl_module.parameters(),
            lr=pl_module.t.hypers.lr,
            weight_decay=pl_module.t.hypers.weight_decay
        )

        if pl_module.t.constant_lr:
            return optimizer

        if pl_module.t.lr_scheduler:
            scheduler = pl_module.t.lr_scheduler(optimizer, **pl_module.t.lrs_kwargs)
        else:
            scheduler = lrs.ReduceLROnPlateau(optimizer, **pl_module.t.lrs_kwargs)

        return {
            'optimizer': optimizer,
            "lr_scheduler": {
            "scheduler": scheduler,
                "monitor": self.slr_metric_track,
                "frequency": pl_module.t.lr_scheduler_frequency,  # indicates how often the metric is updated
                # If "monitor" references validation metrics, then "frequency" should be set to a
                # multiple of "trainer.check_val_every_n_epoch".
            },
        }

    @staticmethod
    def dict_fmt_print(dict_: dict[str, float], print_func=fmt_print.bold_magenta, prefix=''):
        msg = f'{prefix}[' + ', '.join([f'{k}={v:.3g}' for k, v in dict_.items()]) + ']'
        print(type(print_func))
        print_func(msg)


class SingleTask(Task):
    """"""
    _expect_types = {
        '_feature_extractor': Callable,
        '_extractor_attr_getter': Callable,
        '_target_getter': Callable,
        '_loss_fn': Callable,
        '_primary_metric': str,
        '_metrics': dict[str, Callable],
        '_x_masker': Callable,
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.val_pred = []
        self.val_target = []

    def feature_extractor(self, *args, **kwargs) -> torch.Tensor:
        return self._feature_extractor(*args, batch_getter=self._extractor_attr_getter, **kwargs)

    @staticmethod
    def predict(predictor: nn.Module, features: torch.Tensor) -> torch.Tensor:
        return predictor(features)

    def label2oh_conversion(self, target: Union[torch.Tensor, dict[str, torch.Tensor]]):
        return target.view(-1, 1)

    @staticmethod
    def peel_unmaksed_obj(
            feature_target: torch.Tensor,
            mask_idx: Optional[torch.Tensor] = None,
    ):
        if mask_idx is None:
            return feature_target
        elif isinstance(mask_idx, torch.Tensor):
            return feature_target[mask_idx]
        else:
            raise NotImplementedError('The mask_idx must be None or a torch.Tensor')

    def loss_weight_calculator(self, target) -> Optional[torch.Tensor]:
        if self._loss_weight_calculator:
            return self._loss_weight_calculator(target)
        return None

    def loss_fn(self, pred, target, loss_weight):
        return self._loss_fn(pred, target, loss_weight) \
            if isinstance(loss_weight, torch.Tensor) \
            else self._loss_fn(pred, target)

    @override
    def log_on_train_batch_end(
            self,
            pl_module: L.LightningModule,
            loss: torch.Tensor,
            pred: torch.Tensor,
            target: torch.Tensor,
    ) -> None:
        p_metric = self._metrics[self._primary_metric](pred, target)
        pl_module.log('loss', loss.item(), prog_bar=True)
        pl_module.log(self._primary_metric, p_metric, prog_bar=True)

    @override
    def add_val_pred_target(
            self,
            pred: torch.Tensor,
            target: torch.Tensor
    ):
        self.val_pred.append(pred.cpu().detach().float().numpy())
        self.val_target.append(target.cpu().detach().float().numpy())

    @override
    def eval_on_val_end(self, pl_module: L.LightningModule):
        pred = np.concatenate(self.val_pred)
        target = np.concatenate(self.val_target)

        # Calculating the metrics
        metrics_dict = {
            metric_name: metric_func(pred, target)
            for metric_name, metric_func in self._metrics.items()
        }

        metrics_dict['lr'] = pl_module.optimizers().param_groups[0]['lr']

        # Print and log metrics
        self._print_and_log_metrics(pl_module, metrics_dict)

        # free memory
        self.val_pred.clear()
        self.val_target.clear()


class MultiTask(Task):
    """"""
    _expect_types = {
        '_feature_extractor': dict[str, Callable],
        '_extractor_attr_getter': dict[str, Callable],
        'target_getter': dict[str, Callable],
        'loss_fn': dict[str, Callable],
        '_primary_metric': dict[str, str],
        '_metrics': dict[str, dict[str, Callable]],
        '_x_masker': dict[str, Callable],
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.loss_dict = None
        self.val_pred = {}
        self.val_target = {}

        try:
            self.atl_weights_calculators = kwargs['atl_weights_calculators']
        except KeyError:
            self.atl_weights_calculators = M.atl_calculator

        if not self.atl_weights_calculators:
            self.atl_weights_calculators = M.atl_calculator

    def feature_extractor(self, *args, **kwargs) -> dict[str, torch.Tensor]:
        if self._extractor_attr_getter is None:
            extractor = {}
        elif isinstance(self._extractor_attr_getter, dict):
            extractor = self._extractor_attr_getter
        else:
            raise NotImplementedError

        return {
            k: ext(*args, batch_getter=extractor.get(k, None), **kwargs)
            for k, ext in self._feature_extractor.items()
        }

    @staticmethod
    def predict(predictor: dict[str, nn.Module], features: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        return {n: predictor[n](f) for n, f in features.items()}

    def target_getter(self, batch: Batch) -> dict[str, torch.Tensor]:
        return {k: tg(batch) for k, tg in self._target_getter.items()}

    @override
    def label2oh_conversion(self, target: dict[str, torch.Tensor]):
        return {k: t.view(-1, 1) for k, t in target.items()}

    def peel_unmaksed_obj(
            self,
            feature_target: dict[str, torch.Tensor],
            mask_idx: Union[torch.Tensor] = None,
    ):
        if mask_idx is None and self._mask_need_task is None:
            return feature_target
        elif isinstance(mask_idx, torch.Tensor):
            for mask_task in self._mask_need_task:
                feature_target[mask_task] = feature_target[mask_task][mask_idx]
            return feature_target
        else:
            raise NotImplementedError('The mask_idx must be None or a torch.Tensor')

    def loss_weight_calculator(self, target) -> Optional[dict[str, torch.Tensor]]:
        if self._loss_weight_calculator is None:
            return None
        elif isinstance(self._loss_weight_calculator, dict):
            return {
                k: calculator(target[k])
                for k, calculator in self._loss_weight_calculator.items()
            }

    def loss_fn(
            self,
            pred: dict[str, torch.Tensor],
            target: dict[str, torch.Tensor],
            loss_weight: dict[str, torch.Tensor]
    ):
        """ Calculate the loss value for multi-task """
        assert len(pred) == len(target)
        assert all((kp in target and kt in pred) for kp, kt in zip(target.keys(), pred.keys()))

        # Calculate loss individually
        self.loss_dict = {}
        for k, p in pred.items():
            if (lw := loss_weight.get(k, None)) is not None:
                self.loss_dict[k] = self._loss_fn[k](p, target[k], lw)
            else:
                self.loss_dict[k] = self._loss_fn[k](p, target[k])

        # Calculate the total loss
        if isinstance(self.atl_weights, dict):
            return sum(lo * self.atl_weights.get(k, 1.) for k, lo in self.loss_dict.items())
        else:
            return sum(lo for lo in self.loss_dict.values())

    @override
    def log_on_train_batch_end(
            self,
            pl_module: L.LightningModule,
            loss: torch.Tensor,
            pred: dict[str, torch.Tensor],
            target: dict[str, torch.Tensor],
    ) -> None:
        # Log total loss
        pl_module.log('loss', loss.item(), prog_bar=True)

        # Calculate primary metrics for each task
        for k, t in target.items():
            pm = self._metrics[k][self._primary_metric[k]](pred[k], t)
            pl_module.log(
                # f"{k}-{self._primary_metric[k]}",
                k,
                pm,
                prog_bar=True
            )

    @override
    def add_val_pred_target(
            self,
            pred: dict[str, torch.Tensor],
            target: dict[str, torch.Tensor]
    ):
        for k, t in target.items():
            self.val_pred.setdefault(k, []).append(pred[k].cpu().detach().float().numpy())
            self.val_target.setdefault(k, []).append(t.cpu().detach().float().numpy())

    @override
    def eval_on_val_end(self,pl_module: L.LightningModule):
        val_target = {k: np.concatenate(t) for k, t in self.val_target.items()}
        val_pred = {k: np.concatenate(p) for k, p in self.val_pred.items()}

        # Calculate metrics
        metrics_dict = {
            k: self._metrics[k][self._primary_metric[k]](val_pred[k], t)
            # self._primary_metric[k]: self._metrics[k][self._primary_metric[k]](val_pred[k], t)
            for k, t in val_target.items()}

        # Update across loss weights
        if pl_module.current_epoch < 1 or not isinstance(self.atl_weights_calculators, Callable):
            self.atl_weights = None
        else:
            self.atl_weights = self.atl_weights_calculators(metrics_dict)
            # logging.debug(self.atl_weights)
            self.dict_fmt_print(self.atl_weights, prefix='\nalt_weights: ')

        # Add sum metrics
        metrics_dict['smtrc'] = np.mean([v for v in metrics_dict.values()])

        # Add learning rate information
        metrics_dict['lr'] = pl_module.optimizers().param_groups[0]['lr']

        # Print and log metrics
        self._print_and_log_metrics(pl_module, metrics_dict)

        self.val_pred.clear()
        self.val_target.clear()

    @property
    def slr_metric_track(self):
        return "smtrc"


class TestTask(BaseTask):
    """"""
    def batch_preprocessor(self, batch: Batch) -> Batch:
        print(f'Test batch_preprocessor successful')

    def inputs_getter(self, batch: Batch) -> torch.Tensor:
        print(f'Test input getter successful')

    def get_xyz(self, inputs: tuple[torch.Tensor, ...]) -> Optional[torch.Tensor]:
        print(f'Test get_xyz successful')

    def perturb_xyz(self, xyz):
        print(f'Test perturb_xyz successful')

    def inputs_preprocessor(self, inputs: tuple[torch.Tensor, ...], **kwargs) -> tuple[torch.Tensor, ...]:
        print(f'Test inputs_preprocessor successful')

    def x_masker(self, inputs: tuple[torch.Tensor, ...]) -> (tuple[torch.Tensor, ...], torch.Tensor):
        print(f'Test x_masker successful')

    def feature_extractor(self, *args, **kwargs) -> Union[torch.Tensor, dict[str, torch.Tensor]]:
        print(f'Test feature_extractor successful')

    def target_getter(self, batch: Batch) -> Union[torch.Tensor, dict[str, torch.Tensor]]:
        print(f'Test target_getter successful')

    def loss_weight_calculator(self, target):
        print(f'Test loss_weight_calculator successful')

    def loss_fn(self, pred, target, loss_weight):
        print(f'Test loss_fn successful')

    def label2oh_conversion(self, target: Union[torch.Tensor, dict[str, torch.Tensor]]):
        print(f'Test label2oh_conversion successful')

    @staticmethod
    def peel_unmaksed_obj(feature_target: Union[torch.Tensor, dict[str, torch.Tensor]],
                          mask_idx: Optional[Union[torch.Tensor, dict[str, torch.Tensor]]] = None):
        print(f'Test peel_unmaksed_obj successful')

    def log_on_train_batch_end(self, pl_module: L.LightningModule, loss: Union[torch.Tensor, dict[str, torch.Tensor]],
                               pred: Union[torch.Tensor, dict[str, torch.Tensor]],
                               target: Union[torch.Tensor, dict[str, torch.Tensor]]) -> None:
        print(f'Test log_on_train_batch_end successful')

    def add_val_pred_target(self, pred: Union[torch.Tensor, dict[str, torch.Tensor]],
                            target: Union[torch.Tensor, dict[str, torch.Tensor]]):
        print(f'Test add_val_pred_target successful')

    def eval_on_val_end(self, pl_module: L.LightningModule):
        print(f'Test eval_on_val_end successful')


def _perform_current_task(md_task_method: Callable):
    @functools.wraps(md_task_method)
    def wrapper(self, *args, **kwargs):
        return getattr(self.current_task, md_task_method.__name__)(*args, **kwargs)
    return wrapper


class MultiDataTask(BaseTask):
    def __init__(self, *tasks: MultiTask):
        self._tasks = tasks
        self.current_task = None

    # @staticmethod
    # def _perform_current_task(md_task_method: Callable):
    #     @functools.wraps(md_task_method)
    #     def wrapper(self, *args, **kwargs):
    #         return getattr(self.current_task, md_task_method.__name__)(*args, **kwargs)
    #     return wrapper

    def choose_task(self, batch):
        assert hasattr(batch, 'dataset_idx'), "The task choice depends on batch attr `dataset_idx`, but it's not found"
        dataset_idx = batch.dataset_idx
        assert len(torch.unique(dataset_idx)), (f'The implementation of MultiDataTask requires all Data in the Batch '
            f'from a same dataset\n, but they are from various Dataset: Index{torch.unique(dataset_idx)}')
        self.current_task = self._tasks[dataset_idx[0]]

    def batch_preprocessor(self, batch: Batch) -> Batch:
        self.choose_task(batch)
        self.current_task.batch_preprocessor(batch)

    # @_perform_current_task
    # def inputs_getter(self, batch: Batch) -> torch.Tensor:
    #     """"""
    #
    # @_perform_current_task
    # def get_xyz(self, inputs: tuple[torch.Tensor, ...]) -> Optional[torch.Tensor]:
    #     """"""
    #
    # @_perform_current_task
    # def perturb_xyz(self, xyz):
    #     """"""
    #
    # @_perform_current_task
    # def inputs_preprocessor(self, inputs: tuple[torch.Tensor, ...], **kwargs) -> tuple[torch.Tensor, ...]:
    #     pass
    #
    # @_perform_current_task
    # def x_masker(self, inputs: tuple[torch.Tensor, ...]) -> (tuple[torch.Tensor, ...], torch.Tensor):
    #     pass
    #
    # @_perform_current_task
    # def feature_extractor(self, *args, **kwargs) -> Union[torch.Tensor, dict[str, torch.Tensor]]:
    #     pass
    #
    # @_perform_current_task
    # def target_getter(self, batch: Batch) -> Union[torch.Tensor, dict[str, torch.Tensor]]:
    #     pass
    #
    # @_perform_current_task
    # def loss_weight_calculator(self, target):
    #     pass
    #
    # @_perform_current_task
    # def loss_fn(self, pred, target, loss_weight):
    #     pass
    #
    # @_perform_current_task
    # def label2oh_conversion(self, target: Union[torch.Tensor, dict[str, torch.Tensor]]):
    #     pass
    #
    # @staticmethod
    # @_perform_current_task
    # def peel_unmaksed_obj(feature_target: Union[torch.Tensor, dict[str, torch.Tensor]],
    #                       mask_idx: Optional[Union[torch.Tensor, dict[str, torch.Tensor]]] = None):
    #     pass
    #
    # @_perform_current_task
    # def log_on_train_batch_end(self, pl_module: L.LightningModule, loss: Union[torch.Tensor, dict[str, torch.Tensor]],
    #                            pred: Union[torch.Tensor, dict[str, torch.Tensor]],
    #                            target: Union[torch.Tensor, dict[str, torch.Tensor]]) -> None:
    #     pass
    #
    # @_perform_current_task
    # def add_val_pred_target(self, pred: Union[torch.Tensor, dict[str, torch.Tensor]],
    #                         target: Union[torch.Tensor, dict[str, torch.Tensor]]):
    #     pass
    #
    # @_perform_current_task
    # def eval_on_val_end(self, pl_module: L.LightningModule):
    #     pass

# Set all abstractmethod to do current tasks
for abc_method in MultiDataTask.__abstractmethods__:
    setattr(MultiDataTask, abc_method, _perform_current_task(getattr(MultiDataTask, abc_method)))
MultiDataTask.__abstractmethods__ = frozenset([])

# print(MultiDataTask.__abstractmethods__)
# assert len(MultiDataTask.__abstractmethods__) == 0
