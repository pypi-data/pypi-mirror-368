from enum import Enum
class ModelConfigKeywords(Enum):
    MODEL_CLASS = 'model_class'
    TRAINING = 'training'
    INFERENCE = 'inference'
    ARCHITECTURE = 'architecture'
    MODULE_LIST = 'module_list'
    MODULE_ORDER = 'module_order'
    CONFIG = 'config'
    WEIGHT_DECAY = 'weight_decay'

    IS_FROZEN = 'is_frozen'

    RESUME_EPOCH = 'resume_epoch'
    SKIP_LOADING = 'skip_loading'

    #TRAINING KEYWORDS
    EPOCHS = 'epochs'
    LEARNING_RATE = 'learning_rate'
    CAN_TIME_BATCH = 'can_time_batch'
    SAVE_EVERY = 'save_every'
    VALIDATE_EVERY = 'validate_every'
    VALIDATION = 'validation'
    CAN_DISPLAY_EPOCH_PROGRESS = 'can_display_epoch_progress'

    DATASET = 'dataset'
    CAN_SHUFFLE = 'can_shuffle'
    
    ####Splits
    SPLIT_TYPE = 'split_type'
    TRAIN_SPLIT = 'train_split'
    VALIDATION_SPLIT = 'validation_split'
    TEST_SPLIT = 'test_split'
    NO_SPLIT = 'full_split'



    MODEL_OUTPUT = 'model_output'
    GROUND_TRUTH = 'ground_truth'
    DATATYPE = 'datatype'
    DATA_SOURCES = 'data_sources'

    NUM_WORKERS = 'num_workers'
    BATCH_SIZE = 'batch_size'
    DATALOADER = 'dataloader'
    LOSS = 'loss'

    IS_PRELOADED = 'is_preloaded'
    #HAS_INDEX = 'has_index'

    AUTOCASTING = 'autocasting'
    CAN_AUTOCAST = 'can_autocast'
    AUTOCAST_DTYPE = 'autocast_dtype'  # e.g., 'float16', 'bfloat16'
    AUTOCAST_CACHE_ENABLED = 'autocast_cache_enabled'


    GRID_JOB = 'grid_job'
    GRID_JOB_PARAMS = 'grid_job_params'
    GRID_ACTIONS = 'grid_actions'
    GRID_JOB_STYLE = 'grid_job_style'
    GRID_SLURM_CONFIG = 'grid_slurm_config'
    GRID_DEBUG = 'grid_debug'
    GRID_JOB_JOINS = 'grid_job_joins'
    GRID_JOB_READABLE_LABELS = 'grid_job_readable_labels'

    GRID_JOB_MAIN_CONFIG = 'grid_job_origin_config'