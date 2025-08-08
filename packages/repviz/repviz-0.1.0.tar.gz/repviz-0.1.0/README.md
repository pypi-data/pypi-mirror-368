# RepViz: Model Representation Visualization

RepViz is a Python package for visualizing the internal representations of machine learning models. It provides tools to hook into model execution, capture activations and gradients, and generate various plots to analyze model behavior.

## Features

*   **Model Agnostic:** Designed to work with different model architectures.
*   **Rich Visualizations:** Generate UMAP plots, heatmaps, and other visualizations to explore model representations.
*   **Extensible:** Easily register new models and plotting functions.
*   **Inference and Analysis:** Run inference with your models and analyze the results.

## Installation

To install the package in editable mode, which is recommended for development, run the following command from the root of the repository:

```bash
pip install -e .
```

This will install the package and its dependencies.

## Dependencies

The package requires Python 3.11+ and the following libraries:

*   `scikit-learn`
*   `seaborn`
*   `torch`

These will be automatically installed when you run the `pip install` command.

## Usage

The primary entry points for using RepViz are the `repviz.plots` and `repviz.inference` modules.

Here's a high-level overview of a possible workflow:

1.  **Register your model:** Use the registry in `repviz.registry` to make your model available to the visualization tools.
2.  **Run inference:** Use the functions in `repviz.inference` to run your model on your data and collect representations.
3.  **Generate plots:** Use the plotting functions in `repviz.plots` to visualize the collected representations.

For more detailed examples, please refer to the notebooks in the `notebooks/` directory.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License.