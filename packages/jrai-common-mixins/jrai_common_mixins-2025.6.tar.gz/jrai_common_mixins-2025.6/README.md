---
title: README
author: Jan-Michael Rye
---

[insert: badges gitlab]: #

[![License](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/MIT.html) [![Pipeline Status](https://gitlab.inria.fr/jrye/jrai-common_mixins/badges/main/pipeline.svg)](https://gitlab.inria.fr/jrye/jrai-common_mixins/-/commits/main) [![PyPI](https://img.shields.io/badge/PyPI-jrai--common__mixins-006dad.svg)](https://pypi.org/project/jrai-common-mixins/) [![PyPI Downloads](https://static.pepy.tech/badge/jrai-common_mixins)](https://pepy.tech/projects/jrai-common_mixins) [![Hatch](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![Latest Release](https://gitlab.inria.fr/jrye/jrai-common_mixins/-/badges/release.svg)](https://gitlab.inria.fr/jrye/jrai-common_mixins/-/tags) [![Pylint](https://gitlab.inria.fr/jrye/jrai-common_mixins/-/jobs/artifacts/main/raw/pylint/pylint.svg?job=pylint)](https://gitlab.inria.fr/jrye/jrai-common_mixins/-/jobs/artifacts/main/raw/pylint/pylint.txt?job=pylint)

[/insert: badges gitlab]: #


# Synopsis

A collection of commonly used mixin classes to facilitate their use in other projects.

# Links

[insert: links]: #

## GitLab

* [Homepage](https://gitlab.inria.fr/jrye/jrai-common_mixins)
* [Source](https://gitlab.inria.fr/jrye/jrai-common_mixins.git)
* [Issues](https://gitlab.inria.fr/jrye/jrai-common_mixins/issues)
* [Documentation](https://jrye.gitlabpages.inria.fr/jrai-common_mixins)
* [GitLab package registry](https://gitlab.inria.fr/jrye/jrai-common_mixins/-/packages)

## Other Repositories

* [Python Package Index (PyPI)](https://pypi.org/project/jrai-common-mixins/)

[/insert: links]: #

# Usage

## Registable

The `Registable` class can be used to define custom user classes that can be tracked through common registers by name. This can be used to create extensible libraries that allow end-users to define custom subclasses that are automatically made accessible to the library's internal mechanisms.

For example, suppose that you wish to create a package that calculates distances between vectors using different metrics. The package provides a number of different metrics but the user should be able to extend the package by defining their own configurable metrics for use with the internal functionality of the package (e.g. different clustering algorithms or visualizations).

In this case, you would create a metric base class that inherits from `Registrable` and define any common methods within it. Metrics provided by the package would then be defined as subclasses of this base class and registered as shown below. These algorithsm can be selected by the end-user by the registered name through whatever configuration interface you wish to provide.

The user can then define their own metric subclasses outside of the package and register them. These names will then become available within the package and can be selected via the provided configuration interface without any modification of the package.

The following example attempts to illustrate this.

~~~python
from jrai_common_mixins.registrable import Registrable

# Define a base class for all metrics.
class Metric(Registrable):
    # Define common methods and attributes here as you would for any base class.
    # ...

# Define subclasses in your package for the metrics that you wish to provide.
class L1Metric(Metric):
    # Define L1 metric methods, e.g.
    def calculate(self, v1, v2):
        # ...


class L2Metric(Metric):
    # Define L2 metric methods, e.g.
    def calculate(self, v1, v2):
        # ...

# Register the define metrics for later use. Typically this would be done right
# after each class declaration. 
L1Metric.register(name="L1")
L2Metric.register(name="L2")

# Retrieve a metric class based on a user-defined value, such as a loaded YAML
# file with the following field:
#
#     metric: L2
#
# Suppose that this file was loaded as "config", which is a dict containing the
# object from the YAML file.

# Get the metric name.
user_metric = config["metric"]

# Get the metric subclass registered with this name.
metric_cls = Metric.get_registered(user_metric)

# Instantiate the class.
metric = metric_cls()

# Calculate a value using the given metric. Here we assume that vectors v1 and
# v2 have already been defined.
value = metric.calculate(self, v1, v2)


# Now suppose that the user wishes to define their own custom metric outside of
# your package. In a separate file, they would do the following:

# Import the Metric base class from your package.
from <your package>.<your submodule> import Metric

# Define a custom user metric as a subclass of Metric.
class TestMetric(Metric):
    # User defines custom metric subclass here.
    def calculate(self, v1, v2):
        # ...

# Register the custom metric.
TestMetric.register(name="test")

# Now the user can specify the metric "test" in the configuration file and your package will be able to load the user's metric internally.
~~~

The true utility of this approach comes from the flexibility that it provides the end user while allowing your package to remain agnostic about custom user code. For example, arbitrary parameters can be passed through to custom metrics in this example via simple YAML configuration files. Consider the following YAML file, which we will load into a dict named `config` via e.g. [PyYAML](https://pypi.org/project/PyYAML/).

~~~yaml
metric:
    name: custom
    params:
        param1: value1
        param2: value2
        # ...
~~~

With this configuration file, the user could define a custom metric as follows that accepts these parameters.

~~~python
# Example just to illustrate how arbitrary parameters could be passed through
from the configuration file.
class CustomMetric(Metric):
    def __init__(param1=5, param2=None):
        self.param1 = param1
        self.param2 = param2

    def calculate(self, v1, v2):
        result = v1 * self.param1 + v2
        if self.param2 is not None:
            result += self.param2
        return result

TestMetric.register(name="custom")

metric_name = config["metric"]["name"]
# Use the builtin dict.get method in case params is omitted from the configuration file.
metric_params = config["metric"].get("params", {})

# Get the class and then instantiate it by passing through the user parameters.
metric_cls = Metric.get_registered(metric_name)
metric = metric_cls(**metric_params)

# Calculate the value.
value = metric.calculate(v1, v2)
~~~


### Troubleshooting

#### Metaclass Conflicts

`Registrable` uses a custom metaclass to initialize internal variables. Attempting to define a subclass that also inherits from another class with a custom metaclass will lead to the following error:

~~~
TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
~~~

The solution is to create a custom metaclass that subclasses both metaclasses and use that for your own subclass, as the following example with the abstract baseclass `abc.ABC` shows.

~~~python
class CustomMetaclass(type(Registrable), type(abc.ABC)):
    """
    Custom metaclass for MySubClass that inherits from both the Registrable and
    abc.ABC metaclasses.
    """
    # The inheritance does all the work so the metaclass definition can be empty.


class MySubClass(Registrable, abc.ABC, metaclass=CustomMetaclass):
    """
    Subclass of Registrable and abc.ABC that uses the custom metaclass
    CustomMetaclass to resolve the metaclass conflict.
    """
    # Define your class as usual.
~~~

## Cachable

The `Cachable` class provides an internal caching mechanism to cache the results of property and method calls. The functionality overlaps with the caching decorators in the [functools package](https://docs.python.org/3/library/functools.html) package in the Python standard library. Here is a list of the main differences:

* `Cachable` only provides caching decorators for class properties and methods, not regular functions.
* Target classes must subclass `Cachable` which thus make this approach more invasive compared to the decorators in the functools package.
* Cached values of all properties and methods for a given instance are stored in an internal dict in the same instance.
* Methods are provided for clearing cached values by optional criteria (property or method name, creation time, access time).
* `Cachable` creates cached properties that remain true properties while functools converts them to regular attributes. The cached properties are intended to remain read-only thus no setters are currently provided.
* Caching methods can accept non-hashable arguments.
* The caching method decorator accepts user-provided functions to define equivalences of parameters on method invocation. This provides considerable flexibility at the cost of speed.
* Cached methods do not rely on the order of keyword arguments. Again, this also makes Cachable's approach slower.

### Recommendations

* For properties, use `functools.cached_property` if you do not need to occasionally clear valeus by creation or access time or if you do not need a proper read-only property.
* For methods, use `functools.cache` or `functools.lru_cache` if you need to cache multiple invocations with different parameter sets, if caching duplucate results is not an issue, or if speed is important due to high method invocation rates.
* Use `Cachable.caching_method` if method invocations are expensive and you wish to avoid redundant invocations by checking for parameter equivalence via user-defined functions. For example, pandas DataFrame arguments can be compared with `Dataframe.equals` in scenarios where equivalent data may be used and the method's computation overhead is far greater than a dataframe comparison.
* Use `Cachable.caching_method` if your method arguments are not supported by `functools.lru_cache` due to being unhashable.
* Use `Cachable` if you want to clear cached values by creation or access times, e.g. keeping only values accessed in the last hour.


### Usage

The following example dementrates how to create caching properties and methods for loading a configuration file, loading dataframes from a configured directory, and calculating expensive functions on the loaded dataframes.

~~~python
import pandas as pd
import yaml
from jrai_common_mixins.cachable import Cachable


def df_are_equal(df1, df2):
    """Return True if two dataframes are equal, else False."""
    return df1.equals(df2)


class DataframeLoader(Cachable):
    """Load pandas dataframes using data from a configuration file."""
    def __init__(self, config_path):
        """
        Args:
            config_path: The path to a YAML configuration file.
        """
        self.config_path = pathlib.Path(config_path).resolve()

    # Cached to avoid reloading the file each time we request the data.
    @Cachable.caching_property
    def config(self):
        """The loaded configuration data."""
        with self.config_path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)

    @property
    def data_dir(self):
        """The data directory specified in the configuration file."""
        # Interpret paths relative to the configuration file's parent directory.
        return self.config_path.parent.join(self.config["data_dir"])

    @Cachable.caching_method():
    def load_dataframe(self, subpath, **read_csv_kwargs):
        """
        Load dataframes from the configured data directory.

        Args:
            subpath:
                The subpath to the dataframe in the data directory.

            **read_csv_kwargs:
                Optional keyword arguments to pass through to pandas.read_csv().
        """
        path = self.data_dir / subpath
        return pd.read_csv(path, **read_csv_kwargs)
        
    # Creating a caching method that will detect calls
    @Cachable.caching_method(df_are_equal)
    def calculate_something(self, df):
        """
        Calculate some expensive function on a dataframe that should only be
        re-calculated when absolutely necessary.

        Args:
            df: A dataframe.
        """
        # Calculate value and return it.


# Intantiate the loader with a configuration file path.
df_loader = DataframeLoader(config_path)

# Load a dataframe.
df1 = df_loader.load_dataframe("test1.csv")

# Invoking it again returns the same object without reloading it from the file.
df1 = df_loader.load_dataframe("test1.csv")

# Calculate some expensive value.
value1 = df_loader.calculate_something(df1)

# Invoking it again returns the previous result without recalculating.
value1 = df_loader.calculate_something(df1)


# Clear the entire cache to force everything to be reloaded.
df_loader.clear_cache()

# Reload df1 and recalculate value1. This will also internally reload the
# configuration file.
df1 = df_loader.load_dataframe("test1.csv")
value1 = df_loader.calculate_something(df1)

# Instead of clearing the entire cache, clear only cache entreis last accessed
# more than 1 hour ago.
df_loader.clear_old_cache_entries(hours=1)
~~~

### Dalood

Cached file loading can also be provided by [Dalood](https://gitlab.inria.fr/jrye/dalood), which is another Python package created for that purpose.
