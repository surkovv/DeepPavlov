"""
Copyright 2017 Neural Networks and Deep Learning lab, MIPT

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from sklearn.model_selection import train_test_split

from deeppavlov.core.common.registry import register
from deeppavlov.core.data.dataset import Dataset


@register('classification_dataset')
class ClassificationDataset(Dataset):
    """
        Class gets data dictionary from ClassificationDatasetReader instance,
        merge fields if necessary,
        split a field if necessary
        """
    def __init__(self, data,
                 fields_to_merge=None, merged_field=None,
                 field_to_split=None, split_fields=None, split_proportions=None,
                 seed: int = None, shuffle: bool = True,
                 *args, **kwargs):
        """
        Initialize dataset using data from DatasetReader,
        merges and splits fields according to the given parameters
        Args:
            data: dictionary of data with fields "train", "valid" and "test" (or some of them)
            seed: random seed
            fields_to_merge: list of fields to merge
            merged_field: name of field to which save merged fields
            field_to_split: name of field to split
            split_fields: list of fields to which save splitted field
            split_proportions: list of corresponding proportions for splitting
            *args:
            **kwargs:
        """
        super().__init__(data, seed=seed, shuffle=shuffle)

        if fields_to_merge is not None:
            if merged_field is not None:
                print("Merging fields <<{}>> to new field <<{}>>".format(fields_to_merge,
                                                                         merged_field))
                self._merge_data(fields_to_merge=fields_to_merge,
                                 merged_field=merged_field)
            else:
                raise IOError("Given fields to merge BUT not given name of merged field")

        if field_to_split is not None:
            if split_fields is not None:
                print("Splitting field <<{}>> to new fields <<{}>>".format(field_to_split,
                                                                           split_fields))
                self._split_data(field_to_split=field_to_split,
                                 split_fields=split_fields,
                                 split_proportions=[float(s) for s in
                                                    split_proportions])
            else:
                raise IOError("Given field to split BUT not given names of split fields")

    def _split_data(self, field_to_split, split_fields, split_proportions):
        """
        Split given field of dataset to the given list of fields with corresponding proportions
        Args:
            field_to_split: field name which to split
            split_fields: list of names of fields to which split
            split_proportions: corresponding proportions

        Returns:
            None
        """
        data_to_div = self.data[field_to_split].copy()
        data_size = len(self.data[field_to_split])
        for i in range(len(split_fields) - 1):
            self.data[split_fields[i]], \
            data_to_div = train_test_split(data_to_div,
                                           test_size=
                                           len(data_to_div) - int(
                                               data_size * split_proportions[i]))
        self.data[split_fields[-1]] = data_to_div
        return True

    def _merge_data(self, fields_to_merge, merged_field):
        """
        Merge given fields of dataset
        Args:
            fields_to_merge: list of fields to merge
            merged_field: name of field to which save merged fields

        Returns:
            None
        """
        data = self.data.copy()
        data[merged_field] = []
        for name in fields_to_merge:
            data[merged_field] += self.data[name]
        self.data = data
        return True
