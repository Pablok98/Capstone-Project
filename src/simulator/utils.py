def event(time_var):
    def event_decorator(event_func):
        def event_wrapper(self, *args, **kwargs):
            print(self)
            print(getattr(self, time_var))
            res = event_func(self, *args, **kwargs)
            return res
        return event_wrapper
    return event_decorator
