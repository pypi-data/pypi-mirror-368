def urljoin(*args):
    """
    Join any number of URL segments together.
    strips trailing slash from first segment and leading slash from the last segment
    strips both leading and trailing slashes from all other segments
    urljoin('/api/v1','/metric/') should turn into '/api/v1/metric/' and not strip first and last slash
    """
    results = []
    for i in range(len(args)):
        if i == 0:
            results.append(str(args[i]).rstrip('/'))
        elif i == len(args) - 1:
            results.append(str(args[i]).lstrip('/'))
        else:
            results.append(str(args[i]).strip('/'))
    return '/'.join(results)