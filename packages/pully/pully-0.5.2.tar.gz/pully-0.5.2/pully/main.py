# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from .cli import parser


def main():
    args = parser.parse_args()
    return args.func(args)
