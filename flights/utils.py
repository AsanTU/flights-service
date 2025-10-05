def is_manager(user):
    return getattr(user, 'is_manager', False)