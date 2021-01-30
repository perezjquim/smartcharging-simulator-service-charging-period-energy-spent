from nameko.events import EventDispatcher
from nameko.rpc import rpc

from model.exceptions import NotFound

import json

import tensorflow as tf

class ModelService:

    CHARGING_PERIOD_PEAK_AVG = 2666.817
    CHARGING_PERIOD_PEAK_STDDEV = 221.847

    name = 'model_charging_period_peak'

    event_dispatcher = EventDispatcher()

    @rpc
    def get_charging_period_peak(self):
        charging_period_peak = self.generate_charging_period_peak()
        response = json.dumps({'charging_period_peak': charging_period_peak})
        return response

    def generate_charging_period_peak(self):
        shape = [1,1]
        min_charging_period_peak = self.CHARGING_PERIOD_PEAK_AVG - self.CHARGING_PERIOD_PEAK_STDDEV
        max_charging_period_peak = self.CHARGING_PERIOD_PEAK_AVG + self.CHARGING_PERIOD_PEAK_STDDEV

        tf_random = tf.random.uniform(
                shape=shape,
                minval=min_charging_period_peak,
                maxval=max_charging_period_peak,
                dtype=tf.dtypes.float32,
                seed=None,
                name=None
        )
        tf_var = tf.Variable( tf_random )

        tf_init = tf.compat.v1.global_variables_initializer()
        tf_session = tf.compat.v1.Session()
        tf_session.run(tf_init)

        tf_return = tf_session.run(tf_var)
        charging_period_peak = float( tf_return[ 0 ][ 0 ] )

        return charging_period_peak
