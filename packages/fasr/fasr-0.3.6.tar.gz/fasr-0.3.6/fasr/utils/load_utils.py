from fasr.config import Config, registry


def load(save_dir: str, type: str = "component"):
    from pathlib import Path

    save_dir = Path(save_dir)
    if not save_dir.exists():
        raise FileNotFoundError(f"Directory {save_dir} does not exist")
    config_path = save_dir / "config.cfg"
    config = Config().from_disk(config_path)
    obj = registry.resolve(config)[type]
    loaded_obj = obj.load(save_dir)
    return loaded_obj
