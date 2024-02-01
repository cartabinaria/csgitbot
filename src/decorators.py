import multiprocessing

def run_in_separate_process(func):
    """ Run a function in a separate process, and return the result
    """
    def wrapper(*args, **kwargs):
        # Create a queue to communicate with the separate process
        queue = multiprocessing.Queue()

        # Define a function to run in a separate process
        def run_func(queue, func, args, kwargs):
            result = func(*args, **kwargs)
            queue.put(result)

        # Create and start a separate process
        process = multiprocessing.Process(target=run_func, args=(queue, func, args, kwargs))
        process.start()

        # Wait for the process to finish
        process.join()

        # Get the result from the queue
        result = queue.get()

        return result

    return wrapper
