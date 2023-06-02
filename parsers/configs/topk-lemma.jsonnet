# Configuration file for parser.
# See https://guide.allennlp.org/training-and-prediction#2 for guidance.
{
    "train_data_path": "data/train.conllu",
    "validation_data_path": "data/val.conllu",
    "dataset_reader": {
        "type": "compreno_ud_dataset_reader", # Use custom dataset reader.
        "token_indexers": {
            "tokens": {
                "type": "pretrained_transformer_mismatched",
                "model_name": "cointegrated/rubert-tiny2" # Use rubert-tiny2. If you change it, don't forget to change model.embedder.model_name as well.
            }
        },
    },
    "data_loader": {
        "batch_size": 64,
        "shuffle": true
    },
    "validation_data_loader": {
        "batch_size": 64,
        "shuffle": false
    },
    "vocabulary": {
        "tokens_to_add": { # Add default OOV tokens to string-based fields.
            "lemma_rule_labels": ["@@UNKNOWN@@"],
            "pos_feats_labels": ["@@UNKNOWN@@"],
            "deprel_labels": ["@@UNKNOWN@@"],
            "semslot_labels": ["@@UNKNOWN@@"],
            "semclass_labels": ["@@UNKNOWN@@"],
        }
    },
    "model": {
        "type": "morpho_syntax_semantic_parser", # Use custom model.
        "embedder": {
            "type": "pretrained_transformer_mismatched",
            "model_name": "cointegrated/rubert-tiny2",
            "train_parameters": true
        },
        "lemma_rule_classifier": {
            "hid_dim": 512,
            "activation": "relu",
            "dropout": 0.1,
            "dictionaries": [
                {
                    "path": "dicts/ComprenoFull.txt",
                    "lemma_match_pattern": "\\d+:(.*)"
                },
                {
                    "path": "dicts/Zaliz.txt",
                    "lemma_match_pattern": "^(.*?) "
                },
                { # TODO: There should be a task-independent dictionary with pronouns.
                    "path": "data/train.conllu",
                    "lemma_match_pattern": "^\\d+\\s+.*?\\s+(.*?)\\s+"
                },
            ],
            "topk": 10,
        },
        "pos_feats_classifier": {
            "hid_dim": 256,
            "activation": "relu",
            "dropout": 0.1
        },
        "depencency_classifier": {
            "hid_dim": 128,
            "activation": "relu",
            "dropout": 0.1
        },
        "semslot_classifier": {
            "hid_dim": 1024,
            "activation": "relu",
            "dropout": 0.1
        },
        "semclass_classifier": {
            "hid_dim": 1024,
            "activation": "relu",
            "dropout": 0.1
        }
    },
    "trainer": {
        "type": "gradient_descent",
        "optimizer": {
            "type": "adam",
            "lr": 0.01, # Base (largest) learning rate.
            "parameter_groups": [
                [ # Second group of layers.
                    ["embedder"], {}
                ],
                [ # First group of layers.
                    [
                    "lemma_rule_classifier",
                    "pos_feats_classifier",
                    "dependency_classifier",
                    "semslot_classifier",
                    "semclass_classifier"
                    ], {}
                ],
            ],
        },
        "learning_rate_scheduler": {
            "type": "slanted_triangular",
            "gradual_unfreezing": true, # During first epoch the first group of layers is trained only. Starting second epoch, both groups are trained.
            "discriminative_fine_tuning": true, # Enable discriminative finetuning.
            "decay_factor": 0.01, # We want BERT to be trained with learning rate 100 times smaller than heads.
            "cut_frac": 0.0, # Increase learning rate from the smallest to the base value instantly.
            "ratio": 32, # The ratio of the smallest to the largest (base) learning rate.
        },
        "callbacks": [
            { # Enable Tensorboard logs. Can we viewed via "tensorboard --logdir serialization_dir".
                "type": "tensorboard",
                "should_log_parameter_statistics": false,
                "should_log_learning_rate": true,
            }
        ],
        "num_epochs": 30,
        "validation_metric": "+Avg", # Track average score of all scores. '+' stands for 'higher - better'.
        "grad_clipping": 5.0, # Clip gradient if too high.
        "cuda_device": 1, # GPU
    }
}
