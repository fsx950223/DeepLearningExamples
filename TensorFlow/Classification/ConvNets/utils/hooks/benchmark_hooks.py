#! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2018, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import tensorflow.compat.v1 as tf

import dllogger

from .training_hooks import MeanAccumulator

__all__ = ['BenchmarkLoggingHook']


class BenchmarkLoggingHook(tf.estimator.SessionRunHook):

    def __init__(self, global_batch_size, warmup_steps=20, logging_steps=1):
        self.latencies = []
        self.warmup_steps = warmup_steps
        self.global_batch_size = global_batch_size
        self.current_step = 0
        self.t0 = None
        self.mean_throughput = MeanAccumulator()
        self.logging_steps = logging_steps

    def before_run(self, run_context):
        self.t0 = time.time()

    def after_run(self, run_context, run_values):
        batch_time = time.time() - self.t0
        ips = self.global_batch_size / batch_time
        if self.current_step >= self.warmup_steps:
            self.latencies.append(batch_time)
            self.mean_throughput.consume(ips)

            if (self.current_step % self.logging_steps) == 0:
                dllogger.log(data={"total_ips": ips}, step=(0, self.current_step))

        self.current_step += 1
