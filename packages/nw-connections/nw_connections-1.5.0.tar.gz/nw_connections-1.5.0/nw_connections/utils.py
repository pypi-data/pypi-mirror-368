# encoding: utf-8

import requests_cache

def cache_initiated():
    """Hackish function to test if there is an existing requests_cache"""
    return bool(requests_cache.get_cache())
