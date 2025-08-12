import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, GlobalAveragePooling3D
from neutrophils_core.models.feature_extractor import FeatureExtractor
from neutrophils_core.models.feature_extractor_3d import FeatureExtractor3D
from neutrophils_core.models.model_utils import get_activation_function, get_weight_initializer

@tf.keras.utils.register_keras_serializable()
class SimCLREncoder(tf.keras.Model):
    """
    SimCLR Encoder model that encapsulates the feature extractor and projection head.
    This subclassed model ensures the `training` argument is correctly propagated.
    """
    def __init__(self, config, name='simclr_encoder', **kwargs):
        super(SimCLREncoder, self).__init__(name=name, **kwargs)
        
        self.config = config
        model_config = self.config["model"]
        data_config = self.config["data"]

        if data_config.get("use_mip", False):
            input_shape = (data_config["image_size"], data_config["image_size"], 3)
            self.feature_extractor = FeatureExtractor(config=model_config, input_shape=input_shape)
            self.gap = GlobalAveragePooling2D(name='global_avg_pooling')
        else:
            input_shape = (data_config["image_size"], data_config["image_size"], data_config["image_size"], 1)
            self.feature_extractor = FeatureExtractor3D(config=model_config, input_shape=input_shape)
            self.gap = GlobalAveragePooling3D(name='global_avg_pooling')

        self.fc_layers_list = []
        fc_config_section = model_config.get('fully_connected', {})
        
        if isinstance(fc_config_section, dict) and 'units' in fc_config_section:
            units_list = fc_config_section.get('units', [])
            fc_layers_configs = []
            for units in units_list:
                layer_config = fc_config_section.copy()
                layer_config['units'] = units
                fc_layers_configs.append(layer_config)
        else:
            fc_layers_configs = fc_config_section if isinstance(fc_config_section, list) else []

        for i, fc_config in enumerate(fc_layers_configs):
            activation = get_activation_function(fc_config.get('activation', 'relu'))
            initializer = get_weight_initializer(fc_config.get('kernel_initializer', 'he_normal'))
            
            self.fc_layers_list.append(Dense(
                fc_config['units'],
                activation=activation,
                kernel_initializer=initializer,
                name=f'encoder_dense_{i}'
            ))
            
            dropout_rate = fc_config.get('dropout_rate', fc_config.get('dropout', 0))
            if dropout_rate > 0:
                self.fc_layers_list.append(Dropout(dropout_rate, name=f'encoder_dropout_{i}'))

        if model_config.get("use_projection_head", False):
            hidden_dim = model_config.get("hidden_dim", 128)
            self.projection_head = Dense(hidden_dim, activation='relu', name='projection_head')
        else:
            self.projection_head = None

        embedding_dim = model_config.get("embedding_dim", 128)
        self.embedding_layer = Dense(embedding_dim, activation=None, name='embeddings_dense')

    def call(self, inputs, training=None, **kwargs):
        if training is None:
            training = False

        x = self.feature_extractor(inputs, training=training, **kwargs)
        x = self.gap(x)
        
        for layer in self.fc_layers_list:
            if isinstance(layer, Dropout):
                x = layer(x, training=training)
            else:
                x = layer(x)
        
        if self.projection_head:
            x = self.projection_head(x)
            
        embeddings = self.embedding_layer(x)
        return embeddings

    def get_config(self):
        config = super(SimCLREncoder, self).get_config()
        config.update({'config': self.config})
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)

@tf.keras.utils.register_keras_serializable()
class SimCLRModel(tf.keras.Model):
    """
    Keras Functional API-compatible model for SimCLR pre-training.
    This model wraps the SimCLR encoder and handles contrastive loss calculation
    internally, allowing the use of `model.fit()`.
    """
    def __init__(self, encoder, temperature=0.1, loss_function='nt_xent', verbose=False, **kwargs):
        super(SimCLRModel, self).__init__(**kwargs)
        self.encoder = encoder
        self.temperature = temperature
        self.loss_function_name = loss_function
        self.verbose = verbose
        # Dummy loss function for loading, not used in eval
        self.loss_fn = lambda z1, z2: 0.0
        self.contrastive_accuracy_fn = lambda z1, z2: 0.0
        self.contrastive_loss_tracker = tf.keras.metrics.Mean(name="contrastive_loss")
        self.contrastive_accuracy_tracker = tf.keras.metrics.Mean(name="contrastive_accuracy")

    @property
    def metrics(self):
        return [self.contrastive_loss_tracker, self.contrastive_accuracy_tracker]

    def call(self, inputs, training=False):
        return self.encoder(inputs, training=training)

    def get_config(self):
        config = super(SimCLRModel, self).get_config()
        config.update({
            'encoder': tf.keras.utils.serialize_keras_object(self.encoder),
            'temperature': self.temperature,
            'loss_function': self.loss_function_name,
            'verbose': self.verbose
        })
        return config

    @classmethod
    def from_config(cls, config):
        config['encoder'] = tf.keras.utils.deserialize_keras_object(config['encoder'], custom_objects={'SimCLREncoder': SimCLREncoder})
        return cls(**config)