#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" exception
    opyright (C) 2023 Hao HUANG
    Resume of file :
        In this file, we define the customised exceptions.
"""
############################################################################


class API_caller_Exception(Exception):
    "raise this exception when the API caller is not working properly"
    pass

class crypto_API_Exception(Exception):
    "raise this exception when the crypto API is not working properly"
    pass

class crypto_API_key_Exception(crypto_API_Exception):
    "raise this exception when the crypto API key is not valid"
    pass

# End of file