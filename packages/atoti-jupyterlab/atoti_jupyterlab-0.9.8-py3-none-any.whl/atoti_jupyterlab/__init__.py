"""Extension to use :attr:`atoti.Session.widget` in JupyterLab."""


def _jupyter_labextension_paths() -> (  # pyright: ignore[reportUnusedFunction]
    list[dict[str, str]]
):
    return [{"src": "labextension", "dest": "@atoti/jupyterlab-extension"}]
