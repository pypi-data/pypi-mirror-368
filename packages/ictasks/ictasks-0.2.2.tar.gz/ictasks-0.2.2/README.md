# ictasks

`ictasks` is a library to support running collections of small tasks in parallel, from a laptop through to a HPC cluster.

It is being developed to support projects and workflow standarisation at the Irish Centre for High End Computing (ICHEC).

There are many libraries like this, this one focuses on:

* being small and simple - easy for ICHEC researchers to understand all elements of it
* having low dependencies - can be installed with `pip`
* having an easy to use configuration format with `yaml`
* having verbose and structured reporting of task related metadata for analysis

# Features #

The library allows a few different ways to specify tasks.

1) As a Python package

You can create a collection of `Task` instances and launch them with the `session.run()` function. 

2) Using a `tasklist.dat` file and the command line interface (CLI):

``` shell
ictasks taskfarm --tasklist $PATH_TO_TASKLIST
```

See the `test/data/tasklist.dat` file for an example input with two small tasks.

3) Using a `yaml` config file, giving task and environment info.

``` yaml
job_id: my_job
task_distribution:
    cores_per_node: 1

tasks:
    items:
    - id: 0
      launch_cmd: "echo 'hello from task 0'"
    - id: 1
      launch_cmd: "echo 'hello from task 1'"
```

we can run this with:

``` shell
ictasks taskfarm --config my_config.yaml
```

Launching the run will launch the task in that directory and output a status file `task.json`. By default all processors on the machine (or compute node) will be assigned tasks.


# Installing #

The package can be installed from PyPI:

``` shell
pip install ictasks
```

# Contact #

Our Gitlab hosting arrangement doesn't allow us to easily accept external contributions or feedback, however they are still welcome.

In future if there is interest 


If you have any feedback on this library 

# License #

This package is Coypright of the Irish Centre for High End Computing. It can be used under the terms of the GNU Public License (GPL v3+). See the included `LICENSE.txt` file for details.

If you are an ICHEC collaborator or user of the National Service different licensing terms can be offered - please get in touch to discuss.





