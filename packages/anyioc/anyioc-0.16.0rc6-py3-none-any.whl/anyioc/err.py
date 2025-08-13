# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

class ServiceNotFoundError(LookupError):
    '''
    raise when a service is unable to resolve.
    '''

    def __init__(self, *resolve_chain: object) -> None:
        self.resolve_chain = resolve_chain
        msg = f'unknown service: {repr(resolve_chain[-1])}'
        if len(resolve_chain) > 1:
            resolve_chain_msg = '->'.join([repr(i) for i in resolve_chain])
            msg += f'; resolve chain: {resolve_chain_msg}'
        super().__init__(msg)


__all__ = ['ServiceNotFoundError']
