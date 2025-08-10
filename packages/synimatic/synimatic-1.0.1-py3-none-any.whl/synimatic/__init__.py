"""
Synimator - A simple and effective matplotlib animation library

A clean wrapper around matplotlib's FuncAnimation that provides:
- Easy setup for common animation patterns
- Automatic environment detection (Jupyter/terminal)
- Built-in progress tracking
- Simple save/display functionality

Usage:
    >>> def setup():
    ...     fig, ax = plt.subplots()
    ...     line, = ax.plot([], [])
    ...     return fig, ax, line
    ...
    >>> def update(frame, context):
    ...     fig, ax, line = context
    ...     # Update your plot here
    ...     line.set_data(x_data, y_data[frame])
    ...
    >>> animator = Synimator(setup)
    >>> animator.animate(update, frames=100)
    >>> animator.show()
"""

__version__ = "1.0.0"
__author__ = "Jonathan Ayalew"
__github__ = "https://github.com/jonathan-4a"
__license__ = "MIT"

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from contextlib import contextmanager
from typing import Callable, List, Any, Optional, Union, Tuple
import logging

from typing import Protocol, Sequence, runtime_checkable


@runtime_checkable
class SetupFunc(Protocol):
    def __call__(self) -> tuple[plt.Figure, plt.Axes, *tuple[Any, ...]]: ...


@runtime_checkable
class UpdateFunc(Protocol):
    def __call__(self, frame: int, context: list[Any]) -> None: ...


@runtime_checkable
class InitFunc(Protocol):
    def __call__(self, context: list[Any]) -> None: ...


# Setup logging
logger = logging.getLogger(__name__)


class SynimatorError(Exception):
    """Base exception for Synimator-related errors"""

    pass


class AnimationNotCreatedError(SynimatorError):
    """Raised when trying to show/save before creating animation"""

    pass


class InvalidSetupError(SynimatorError):
    """Raised when setup function returns invalid structure"""

    pass


def _detect_environment() -> Tuple[bool, bool]:
    """
    Detect execution environment.

    Returns:
        Tuple of (in_ipython, in_notebook)
    """
    try:
        from IPython import get_ipython

        ipython = get_ipython()

        if ipython is None:
            return False, False

        # Check for Jupyter notebook/lab environment
        in_notebook = (
            hasattr(ipython, "kernel")  # Standard check
            or ipython.__class__.__name__
            in ["ZMQInteractiveShell", "SpyderShell"]  # Fallback
            or "jupyter" in str(type(ipython)).lower()  # Additional fallback
        )

        return True, in_notebook

    except ImportError:
        return False, False


def _validate_setup_result(result: Any) -> Tuple[plt.Figure, plt.Axes, List[Any]]:
    """
    Validate and normalize setup function result.

    Args:
        result: Return value from setup function

    Returns:
        Normalized (fig, ax, artists) tuple

    Raises:
        InvalidSetupError: If setup result is invalid
    """
    if not isinstance(result, (list, tuple)) or len(result) < 2:
        raise InvalidSetupError(
            "setup() must return at least (fig, ax). "
            f"Got {type(result)} with {len(result) if hasattr(result, '__len__') else '?'} items"
        )

    fig, ax = result[0], result[1]

    if not isinstance(fig, plt.Figure):
        raise InvalidSetupError(
            f"First return value must be plt.Figure, got {type(fig)}"
        )

    if not isinstance(ax, plt.Axes):
        raise InvalidSetupError(f"Second return value must be plt.Axes, got {type(ax)}")

    # Extract artists (everything after fig, ax)
    artists = list(result[2:]) if len(result) > 2 else []

    return fig, ax, artists


class Synimator:
    """
    Simple matplotlib animation wrapper with automatic environment detection.

    This class provides a clean interface for creating matplotlib animations with
    automatic progress tracking and environment-appropriate display methods.

    Args:
        setup: Function that returns (fig, ax, *artists)
        init_func: Optional initialization function called before animation starts

    Example:
        >>> def setup():
        ...     fig, ax = plt.subplots()
        ...     line, = ax.plot([], [])
        ...     ax.set_xlim(0, 10)
        ...     ax.set_ylim(-1, 1)
        ...     return fig, ax, line
        ...
        >>> def animate_func(frame, context):
        ...     fig, ax, line = context
        ...     line.set_data(range(frame), [sin(x) for x in range(frame)])
        ...
        >>> animator = Synimator(setup)
        >>> animator.animate(animate_func, frames=100)
        >>> animator.show()
    """

    def __init__(
        self,
        setup: SetupFunc,
        init_func: Optional[InitFunc] = None,
    ):
        """
        Initialize the animator.

        Args:
            setup: Function returning (fig, ax, *artists)
            init_func: Optional function called before animation starts

        Raises:
            InvalidSetupError: If setup function returns invalid structure
        """
        self.init_func = init_func or (lambda context: None)
        self._progress_bar = None
        self._animation = None
        self._content = None

        # Validate and setup the plot
        try:
            setup_result = setup()
            self.fig, self.ax, self.artists = _validate_setup_result(setup_result)
        except Exception as e:
            raise InvalidSetupError(f"Setup function failed: {e}") from e

        # Configure matplotlib with reasonable limits
        self._original_embed_limit = plt.rcParams.get("animation.embed_limit")
        plt.rcParams["animation.embed_limit"] = 50 * 1024 * 1024  # 50MB

        logger.debug(f"Initialized Synimator with {len(self.artists)} artists")

    def _init_animation(self) -> List[Any]:
        """Initialize animation - called by FuncAnimation."""
        try:
            self.init_func([self.fig, self.ax, *self.artists])
        except Exception as e:
            logger.warning(f"Init function failed: {e}")
        return self.artists

    def _update_wrapper(self, frame: int, update_func: Callable) -> List[Any]:
        """Wrapper for user update function."""
        try:
            update_func(frame, [self.fig, self.ax, *self.artists])

            if self._progress_bar is not None:
                self._progress_bar.update(1)

        except Exception as e:
            logger.warning(f"Update function failed at frame {frame}: {e}")

        return self.artists

    @contextmanager
    def _progress_context(self, frames: Union[int, List[int]]):
        """Context manager for progress bar lifecycle."""
        _, in_notebook = _detect_environment()

        if in_notebook:
            try:
                from tqdm import tqdm

                frame_count = len(frames) if hasattr(frames, "__len__") else frames
                self._progress_bar = tqdm(total=frame_count, desc="Animating", ncols=80)
            except ImportError:
                logger.info("tqdm not available, progress bar disabled")
                self._progress_bar = None

        try:
            yield
        finally:
            if self._progress_bar is not None:
                self._progress_bar.close()
                self._progress_bar = None

    def animate(
        self,
        update: UpdateFunc,
        frames: Union[int, Sequence[int]],
        blit: bool = True,
        fps: int = 16,
        embed: str = "jshtml",
        embed_limit=100,
        save_only: bool = False,
    ) -> "Synimator":
        """
        Create the animation.

        Args:
            update: Function called for each frame with signature:
                update(frame, context)
            frames: Number of frames (int) or sequence of frame values
            blit: Whether to use blitting for better performance
            fps: Frames per second
            embed: Format for Jupyter embedding ("jshtml" or "video")
            embed_limit: Maximum size for embedded content (in MB)
            save_only: If True, skip pre-rendering content. Call `save()` explicitly
                after to write animation to file.

        Returns:
            Self for method chaining

        Raises:
            ValueError: If embed format is invalid
            SynimatorError: If animation creation fails
        """

        if embed not in ("jshtml", "video"):
            raise ValueError(f"embed must be 'jshtml' or 'video', got '{embed}'")

        plt.rcParams["animation.embed_limit"] = embed_limit
        self._animation = FuncAnimation(
            self.fig,
            self._update_wrapper,
            frames=frames,
            interval=1000 / fps,
            fargs=(update,),
            init_func=self._init_animation,
            blit=blit,
        )

        if not save_only:
            try:
                with self._progress_context(frames):
                    # Pre-render for Jupyter environments
                    _, in_notebook = _detect_environment()
                    if in_notebook:
                        try:
                            if embed == "jshtml":
                                self._content = self._animation.to_jshtml()
                            else:
                                self._content = self._animation.to_html5_video()
                            plt.close(self.fig)
                            logger.debug(f"Pre-rendered animation as {embed}")
                        except Exception as e:
                            logger.warning(f"Pre-rendering failed: {e}")
                            self._content = None
                    else:
                        self._content = None

            except Exception as e:
                raise SynimatorError(f"Animation creation failed: {e}") from e
        else:
            plt.close(self.fig)

        return self

    def show(self) -> None:
        """
        Display the animation.

        In Jupyter notebooks, this will display the pre-rendered animation.
        In other environments, this will show an interactive matplotlib window.

        Raises:
            AnimationNotCreatedError: If animate() hasn't been called yet
        """
        if self._animation is None:
            raise AnimationNotCreatedError(
                "No animation created. Call animate() first."
            )

        _, in_notebook = _detect_environment()

        if in_notebook and self._content:
            try:
                from IPython.display import HTML, display

                display(HTML(self._content))
                logger.debug("Displayed pre-rendered animation in notebook")
            except ImportError:
                logger.warning("IPython not available, falling back to plt.show()")
                plt.show()
        else:
            if in_notebook:
                raise AnimationNotCreatedError(
                    "Inline display unavailable; run animate() with save_only=False."
                )
            plt.show()

    def save(self, filename: str = "animation.mp4", **kwargs) -> None:
        if self._animation is None:
            raise AnimationNotCreatedError("No animation created. Call animate() first.")

        total = (
            self._animation.save_count if hasattr(self._animation, "save_count") else None
        )
        if total is None:
            total = 100  # fallback estimate
        from tqdm import tqdm
        with tqdm(total=total, desc="Saving animation", ncols=80) as pbar:

            def progress_callback(current, total_frames):
                pbar.total = total_frames
                pbar.n = current + 1
                pbar.refresh()

            save_kwargs = {
                "dpi": 100,
                "bitrate": -1,
                "progress_callback": progress_callback,
                **kwargs,
            }

            try:
                self._animation.save(filename, **save_kwargs)
                logger.info(f"Animation saved to {filename}")
            except Exception as e:
                raise SynimatorError(f"Failed to save animation: {e}") from e

    def __del__(self):
        """Cleanup when object is destroyed."""
        try:
            if self._original_embed_limit is not None:
                plt.rcParams["animation.embed_limit"] = self._original_embed_limit
        except Exception:
            pass  # Ignore cleanup errors

    def __enter__(self) -> "Synimator":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit with cleanup."""
        if self._progress_bar is not None:
            self._progress_bar.close()


# Convenience function for one-liners
def quick_animate(
    setup: SetupFunc,
    update: UpdateFunc,
    frames: Union[int, Sequence[int]],
    **animate_kwargs,
) -> Synimator:
    """
    Create and display animation in one call.

    Args:
        setup: Setup function returning (fig, ax, *artists)
        update: Update function with signature update(frame, context)
        frames: Number of frames or frame sequence
        **animate_kwargs: Additional arguments for animate()

    Returns:
        Synimator instance (for further operations like save())

    Example:
        >>> quick_animate(my_setup, my_update, frames=50, fps=30)
    """
    animator = Synimator(setup)
    animator.animate(update, frames, **animate_kwargs)
    animator.show()
    return animator


# For backwards compatibility and convenience
__all__ = [
    "Synimator",
    "quick_animate",
    "SynimatorError",
    "AnimationNotCreatedError",
    "InvalidSetupError",
]
