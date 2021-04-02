from nameko.events import EventDispatcher
from nameko.rpc import rpc

from model.exceptions import NotFound

import json

import tensorflow as tf

class ModelService:

    CHARGING_PERIOD_PEAK_AVG = 2666.817
    CHARGING_PERIOD_PEAK_STDDEV = 221.847

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
        min_charging_period_energy_spent = ModelService.CHARGING_PERIOD_PEAK_AVG - ModelService.CHARGING_PERIOD_PEAK_STDDEV
        max_charging_period_energy_spent = ModelService.CHARGING_PERIOD_PEAK_AVG + ModelService.CHARGING_PERIOD_PEAK_STDDEV

        tf_random = tf.random_uniform(
                shape=shape,
                minval=min_charging_period_energy_spent,
                maxval=max_charging_period_energy_spent,
                dtype=tf.float32,
                seed=None,
                name=None
        )
        tf_var = tf.Variable( tf_random )

        tf_init = tf.global_variables_initializer( )
        tf_session = tf.Session( )
        tf_session.run( tf_init )

        tf_return = tf_session.run( tf_var )
        charging_period_peak= float( tf_return[ 0 ][ 0 ] )

        eq_a = ( charging_period_peak / -0.25 )
        eq_b = - eq_a
        eq_c = 0

        #parábola: ax2 + bx + c
        charging_period_energy_spent = ( eq_a * progress * progress ) + ( eq_b * progress ) + eq_c

        return charging_period_energy_spent
