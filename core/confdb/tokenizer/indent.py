# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# indent tokenizer
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from .line import LineTokenizer


class IndentTokenizer(LineTokenizer):
    name = "indent"

    def __init__(self, data, end_of_context=None, **kwargs):
        kwargs["keep_indent"] = True
        self.end_of_context = end_of_context
        super(IndentTokenizer, self).__init__(data, **kwargs)

    def iter_indent(self, iter):
        depths = [0]
        contexts = [tuple()]
        last = None
        for tokens in iter:
            c_depth = len(tokens[0]) if tokens[0].startswith(" ") else 0
            if c_depth:
                tokens = tokens[1:]
            if c_depth > depths[-1] and last:
                # Push context
                depths += [c_depth]
                contexts += [last]
            elif depths and c_depth < depths[-1]:
                # Pop context
                while c_depth < depths[-1]:
                    depths.pop(-1)
                    contexts.pop(-1)
            # Apply current context
            tokens = contexts[-1] + tokens
            yield tokens
            last = tokens

    def iter_indent_explicit(self, iter):
        depts = [0]
        contexts = [tuple()]
        last = None
        eoc = (self.end_of_context,)
        for tokens in iter:
            c_depth = len(tokens[0]) if tokens[0].startswith(" ") else 0
            if c_depth:
                tokens = tokens[1:]
            if c_depth > depts[-1] and last:
                # Push context
                depts += [c_depth]
                contexts += [last]
            elif tokens == eoc:
                # Pop context
                depts.pop(-1)
                contexts.pop(-1)
                continue
            # Apply current context
            tokens = contexts[-1] + tokens
            yield tokens
            last = tokens

    def __iter__(self):
        g = super(IndentTokenizer, self).__iter__()
        if self.end_of_context:
            g = self.iter_indent_explicit(g)
        else:
            g = self.iter_indent(g)
        for tokens in g:
            yield tokens
