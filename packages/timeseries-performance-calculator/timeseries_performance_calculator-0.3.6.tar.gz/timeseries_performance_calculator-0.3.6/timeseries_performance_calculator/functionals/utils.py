from functools import partial

filter_index_prefix = lambda x: x.split(": ")[-1]
rename_index = lambda df: df.rename(index=filter_index_prefix)
rename_column_with_label = lambda label, df: df.set_axis([label], axis=1)
extract_label_from_kernel = lambda kernel: kernel.__name__.split('calculate_')[-1]
rename_column_with_kernel = lambda kernel, df: partial(rename_column_with_label, extract_label_from_kernel(kernel))(df)
validate_single_timeseries = lambda timeseries: timeseries if timeseries.shape[1] == 1 else (_ for _ in ()).throw(ValueError("DataFrame must have exactly one column"))
