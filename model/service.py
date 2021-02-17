from nameko.events import EventDispatcher
from nameko.rpc import rpc

from model.exceptions import NotFound

import json

import tensorflow as tf

class ModelService:

    CHARGING_PERIOD_ENERGY_SPENT_AVG = 2666.817
    CHARGING_PERIOD_ENERGY_SPENT_STDDEV = 221.847

    name = 'model_energysim_charging_period_energy_spent'

    event_dispatcher = EventDispatcher( )

    @rpc
    def get_energy_spent( self, progress ):
        progress_float = float ( progress )
        charging_period_energy_spent = self.generate_energy_spent( progress_float )
        response = json.dumps( { 'charging_period_energy_spent': charging_period_energy_spent } )
        return response

    def generate_energy_spent( self, progress ):
        shape = [ 1,1 ]
        min_charging_period_energy_spent = ModelService.CHARGING_PERIOD_ENERGY_SPENT_AVG - ModelService.CHARGING_PERIOD_ENERGY_SPENT_STDDEV
        max_charging_period_energy_spent = ModelService.CHARGING_PERIOD_ENERGY_SPENT_AVG + ModelService.CHARGING_PERIOD_ENERGY_SPENT_STDDEV

        tf_random = tf.random.uniform(
                shape=shape,
                minval=min_charging_period_energy_spent,
                maxval=max_charging_period_energy_spent,
                dtype=tf.dtypes.float32,
                seed=None,
                name=None
        )
        tf_var = tf.Variable( tf_random )

        tf_init = tf.compat.v1.global_variables_initializer( )
        tf_session = tf.compat.v1.Session( )
        tf_session.run( tf_init )

        tf_return = tf_session.run( tf_var )
        charging_period_peak= float( tf_return[ 0 ][ 0 ] )

        # <= 50% carregamento feito
        # (2 * perc * peak)
        # ex.: 2 * 0.3 * 2800
        # ex.: 2 * 0.5 * 2800
        if progress <= 0.5: 
            charging_period_energy_spent = ( 2 * progress ) * charging_period_peak

        # > 50% carregamento feito
        # ( 1 - perc ) * peak
        # ex.: ( 1 - 0.8 ) * 2800
        else:
            charging_period_energy_spent = progress * charging_period_peak

        return charging_period_energy_spent
