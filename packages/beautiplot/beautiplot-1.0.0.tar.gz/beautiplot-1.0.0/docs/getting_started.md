# Getting Started

## Installation

The package can be installed via PyPI.

=== "pip"

    ``` { .shell .copy }
    pip install beautiplot
    ```

=== "uv"

    ``` { .shell .copy }
    uv add beautiplot
    ```

Alternatively, you can clone the GitHub repository and, depending on whether you want to develop it or not, run the following command(s) in the cloned directory:

=== "Application"

    ``` { .shell .copy }
    uv sync
    ```

=== "Development"

    ``` { .shell .copy }
    uv sync --all-groups
    uv run pre-commit install
    ```

## Quick example

Let's start by importing `beautiplot` and `numpy`.

``` { .python .copy }
import beautiplot.plot as bp
import numpy as np
```

Next, we generate some data — a damped oscillation in this case.

``` { .python .copy }
t = np.linspace(0, 10, 1000)
y = 5 * np.exp(-t / 2) * np.cos(2 * np.pi * t)
```

Now, we create our first figure using the [`newfig`][beautiplot.plot.newfig] function. At first, you need to estimate the margins, but you can adjust them later as needed. If you do not specify any margins, the figure will be trimmed to the axes, and tick labels or axis labels won't be visible.

``` { .python .copy }
fig, ax = bp.newfig(left=40, bottom=35)
```

We then plot the data and label the axes. You can use LaTeX syntax for labels.

``` { .python .copy }
ax.plot(t, y, label='Damped Oscillation')
ax.set_xlabel('Time $t$ / s')
ax.set_ylabel('Amplitude $A(t)$ / cm')
bp.legend(ax)
```

Finally, we save the figure. Since `pgf` is used as a backend, you cannot use `plt.show()`. Instead, you must save the figure. Here, we use `png` for visualization, but for publication-quality figures, you should use `pdf`.

``` { .python .copy }
bp.save_figure(fig, 'damped_oscillation.png')
```

![damped_oscillation.png](example_plots/damped_oscillation.png)

This simple example introduces the basic functionality, but `beautiplot` truly shines in more advanced scenarios.

For more detailed examples see the [Tutorials section](tutorials/index.md).

You can find documentation for all available functions and settings in the [API reference](reference/beautiplot/index.md).
