import torch
from torch.utils.data import Dataset
from ml_golem.base_classes.model_base import ModuleAccessingConfigBasedClass
from ml_golem.model_loading_logic.model_config_keywords import ModelConfigKeywords
from file_golem import FileDatatypes, AbstractDatatype


class DatasetBase(ModuleAccessingConfigBasedClass,Dataset):
    DEFAULT_DATASOURCE = 'default_datasource'

    def __init__(self,args,subconfig_keys):
        super().__init__(args,subconfig_keys)

        #self.has_index = self.data_io.fetch_config_field(self.config, subconfig_keys=[ModelConfigKeywords.HAS_INDEX.value], default=False)
        self.is_preloaded = self.data_io.fetch_config_field(self.config, subconfig_keys=[ModelConfigKeywords.IS_PRELOADED.value], default=False)
        self.split_type = self.data_io.fetch_config_field(self.config, subconfig_keys=[ModelConfigKeywords.SPLIT_TYPE.value], default=ModelConfigKeywords.NO_SPLIT.value)

        # datasources= self.config.get(ModelConfigKeywords.DATA_SOURCES.value, {})
        # self.datasources = {}
        # if len(datasources) == 0:
        #     self.datasources[self.DEFAULT_DATASOURCE] = self.extract_dataset_config_and_datatype(self.config,self.DEFAULT_DATASOURCE)
        # else:
        #     for key in datasources.keys():
        #         datasource_config = datasources[key]
        #         self.datasources[key] = self.extract_dataset_config_and_datatype(datasource_config,key)
        self.db = {}

    
    def _has_index(self):
        return False




    def _load_item(self,idx):
        raise Exception('This load item method is currently deprected. Please create a custom load item')
        dataset_config = self._get_dataset_config()
        datatype = self._get_datatype()
        data_item = self.data_io.load_data(datatype,data_args={
            datatype.IDX: idx,
            datatype.CONFIG_NAME: dataset_config})
        
        if self._has_index():
            data_item[datatype.IDX] = torch.tensor(idx)
        
        return data_item
    
    def __len__(self):
        return self._get_dataset_size_by_split()



    def _get_dataset_size_by_split(self):
        dataset_split = self._get_dataset_split()
        if dataset_split == ModelConfigKeywords.NO_SPLIT.value:
            length = self._get_full_dataset_length()
        elif dataset_split == ModelConfigKeywords.TRAIN_SPLIT.value:
            length = self._get_train_set_size()
        elif dataset_split == ModelConfigKeywords.TEST_SPLIT.value:
            length =  self._get_test_set_size()
        elif dataset_split == ModelConfigKeywords.VALIDATION_SPLIT.value:
            validation_set_size = self._get_full_dataset_length() - self._get_train_set_size() - self._get_test_set_size()
            if validation_set_size < 0:
                raise Exception('Validation set size cannot be negative. Please check your dataset split configuration.')
            #self.validation_set_size = validation_set_size
            length = validation_set_size
        
        return length
    

    def _get_dataset_offset(self):
        dataset_split = self._get_dataset_split()
        if dataset_split == ModelConfigKeywords.NO_SPLIT.value:
            return 0
        elif dataset_split == ModelConfigKeywords.TRAIN_SPLIT.value:
            return 0
        elif dataset_split == ModelConfigKeywords.TEST_SPLIT.value:
            return self._get_train_set_size()
        elif dataset_split == ModelConfigKeywords.VALIDATION_SPLIT.value:
            return self._get_train_set_size() + self._get_test_set_size()
        
        raise Exception('Unknown dataset split type: {}'.format(dataset_split))
    
    def _get_train_set_size(self):
        raise Exception('This method should be implemented in the subclass. It should return the size of the training set for the current dataset split.')
    
    def _get_test_set_size(self):
        raise Exception('This method should be implemented in the subclass. It should return the size of the test set for the current dataset split.')

    def _get_dataset_split(self):
        return self.split_type

    def _get_full_dataset_length(self):
        raise Exception('This method should be implemented in the subclass. It should return the length of the full dataset, regardless of the split.')


    #def _get_dataset_length_by_split(self):
    #    raise Exception('This method should be implemented in the subclass. It should return the length of the dataset for the current split. This is useful for datasets that have different lengths for different splits, such as training, validation, and test splits.')


    def _get_custom_collate_fn(self):
        if hasattr(self,'custom_collate_fn'):
            #return self.custom_collate_fn
            def collate_fn(batch):
                collated_batch = self.custom_collate_fn(batch)

                if self._has_index():
                    indices = [item[AbstractDatatype.IDX] for item in batch]
                    collated_batch[AbstractDatatype.IDX] = indices
                return collated_batch
            return collate_fn
            #return self.custom_collate_fn
        
        datatype = self._get_datatype()
        if datatype is None or (datatype.FILE_DATATYPE != FileDatatypes.TORCH):
            return lambda x: x    
        return None


    def __getitem__(self, idx):
        #if self.dataset_split != ModelConfigKeywords.NO_SPLIT.value:
        offset_idx = idx+ self._get_dataset_offset()

        print('getting the item with idx: {}'.format(idx))
        if self.is_preloaded:
            #Dynamically load all of the items if preloading
            if len(self.db)==0:
                for i in range(len(self)):
                    preload_idx  = i + self._get_dataset_offset()
                    x = self._load_item(preload_idx)
                    self.db[i] = x

            data = self.db[idx]
        else:
            data = self._load_item(offset_idx)

        if self._has_index():
            #data[AbstractDatatype.IDX] = torch.tensor(idx)
            data[AbstractDatatype.IDX] = offset_idx

        return data
    



    
    # def _default_config(self):
    #     defaults = {
    #         self.DEFAULT_DATASOURCE: {
    #             ModelConfigKeywords.CONFIG.value: None,
    #             ModelConfigKeywords.DATATYPE.value: None
    #         }
    #     }
    #     return defaults


    # def extract_dataset_config_and_datatype(self,config,datasource_key):
    #     all_dataset_config_and_datatype = self._default_config()

    #     dataset_config = config.get(ModelConfigKeywords.CONFIG.value, None)
    #     if dataset_config is None:
    #         if datasource_key in all_dataset_config_and_datatype:
    #             dataset_config = all_dataset_config_and_datatype[datasource_key][ModelConfigKeywords.CONFIG.value]
            
    #     datatype = self.data_io.fetch_class_from_config(
    #         config_or_config_name = config,
    #         subconfig_keys=[ModelConfigKeywords.DATATYPE.value],
    #         default=None)
    #     if datatype is None:
    #         if datasource_key in all_dataset_config_and_datatype:
    #             datatype = all_dataset_config_and_datatype[datasource_key][ModelConfigKeywords.DATATYPE.value]

    #     data_dict = {
    #         ModelConfigKeywords.CONFIG.value: dataset_config,
    #         ModelConfigKeywords.DATATYPE.value: datatype
    #     }
    #     return data_dict


    # def _get_dataset_config(self,datasource=None):
    #     if len(self.datasources) == 1:
    #         return self.datasources[self.DEFAULT_DATASOURCE][ModelConfigKeywords.CONFIG.value]
    #     if datasource is not None:
    #         return self.datasources[datasource][ModelConfigKeywords.CONFIG.value]
    #     raise Exception('Multiple datasources found, please specify the datasource')
    

    # def _get_datatype(self,datasource=None):
    #     if len(self.datasources) == 1:
    #         return self.datasources[self.DEFAULT_DATASOURCE][ModelConfigKeywords.DATATYPE.value]
    #     if datasource is not None:
    #         return self.datasources[datasource][ModelConfigKeywords.DATATYPE.value]
    #     return None
    #     #raise Exception('Multiple datasources found, please specify the datasource')
