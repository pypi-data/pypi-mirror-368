#! /usr/bin/env python3
#
# Copyright (C) 2025 The Authors
# All rights reserved.
#
# This file is part of cps_wb.
#
# cps_wb is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation.
#
# cps_wb is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with cps_wb. If not, see http://www.gnu.org/licenses/
#

def main():
    ##################################################################
    # CLASS TEST AND DEBUG
    #
    pass

class WikiLabel:
    def __init__(self, label, description, language):
        self.label = label
        self.description = description
        self.language = language

    def __str__(self):
        return f"{self.label} {self.description} {self.language}"

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
