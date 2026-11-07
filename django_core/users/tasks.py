import dramatiq


@dramatiq.actor
def example_task(message: str = "Hello from Dramatiq"):
    """
    Example Dramatiq background task.
    """
    print(f"[Dramatiq] Task executed: {message}")
