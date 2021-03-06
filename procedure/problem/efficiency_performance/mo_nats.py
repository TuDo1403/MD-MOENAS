from procedure.problem.base import nats as base

import numpy as np

class EfficiencyAccuracyNATS(base.NATS):
    def __init__(self, efficiency, **kwargs):
        super().__init__(n_obj=2, **kwargs)
        self.msg += efficiency + '={:.3f}, ' + 'valid-error' + '={:.3f}'
        self.efficiency = efficiency

    def _calc_F(self, genotype, **kwargs):
        accuracy, latency, _, runtime = self.api.simulate_train_eval(
            genotype, self.dataset, iepoch=self.epoch, hp=self.api.full_train_epochs
        )

        idx = self.api.query_index_by_arch(genotype)
        cost_info = self.api.get_cost_info(idx, self.dataset, hp=self.api.full_train_epochs)
        params, flops = cost_info['params'], cost_info['flops']
        
        efficiency = eval(self.efficiency)
        error = 100 - accuracy

        F = [efficiency, error]
        return F, runtime


    def _convert_to_pf_space(self, X):
        F = []
        dataset = self.pf_dict['dataset']
        for x in X:
            genotype = self._decode(x)
            idx = self.api.query_index_by_arch(genotype)
            efficiency = self.api.get_cost_info(
                idx, dataset, hp=self.api.full_train_epochs
            )[self.efficiency]
            acc = self.api.get_more_info(
                idx, dataset, hp=self.api.full_train_epochs, is_random=False
            )['test-accuracy']
            err = 100 - acc
            f = [efficiency, err]
            F += [np.column_stack(f)]
        F = np.row_stack(F)
        return F

class MDEfficiencyAccuracyNATS(base.NATS):
    def __init__(self, efficiency, **kwargs):
        super().__init__(n_obj=2, **kwargs)
        self.msg += 'avg-' + efficiency + '={:.3f}, avg-val-err={:.3f}'
        self.efficiency = efficiency
        

    def _calc_F(self, genotype, **kwargs):
        idx = self.api.query_index_by_arch(genotype)

        efficiency = []; runtime = []; accuracy = []
        for dts in self.dataset:
            _accuracy, latency, _, _runtime = self.api.simulate_train_eval(
                genotype, dataset=dts, iepoch=self.epoch, hp=self.api.full_train_epochs
            )

            idx = self.api.query_index_by_arch(genotype)
            cost_info = self.api.get_cost_info(idx, dts, hp=self.api.full_train_epochs)
            params, flops = cost_info['params'], cost_info['flops']
            
            _efficiency = eval(self.efficiency)
            efficiency += [_efficiency]
            runtime += [_runtime]
            accuracy += [_accuracy]

        efficiency = np.mean(efficiency)
        runtime = sum(runtime)
        accuracy = np.mean(accuracy)

        err = 100 - accuracy

        F = [efficiency, err]

        return F, runtime

    def _convert_to_pf_space(self, X):
        F = []
        dataset = self.pf_dict['dataset']
        
        for x in X:
            genotype = self._decode(x)
            idx = self.api.query_index_by_arch(genotype)
            efficiency = self.api.get_cost_info(idx, dataset, hp=self.api.full_train_epochs)[self.efficiency]
            acc = \
                self.api.get_more_info(idx, dataset, hp=self.api.full_train_epochs, is_random=False)['test-accuracy']
            err = 100 - acc
            f = [efficiency, err]
            F += [np.column_stack(f)]
        F = np.row_stack(F)
        return F
        
    
