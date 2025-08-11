#! /usr/bin/env python3
#
# Copyright (C) 2025 The Authors
# All rights reserved.
#
# This file is part of cps_deckenmalerei.
#
# cps_deckenmalerei is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation.
#
# cps_deckenmalerei is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with cps_deckenmalerei. If not, see http://www.gnu.org/licenses/
#
import argparse

from cps_deckenmalerei.snarf import Snarf

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("url", type=str, help="url")

    args = parser.parse_args()

    obj = Snarf(args.url)

    ##################################################################
    # Display properties
    #
    for property in obj.properties:
        print(f"{property} =", end="")
        list = obj.properties[property]
        if len(list) == 1:
            print(f" {list[0]}")
        else:
            print(f" {len(list)}")
            i = 0
            for record in obj.properties[property]:
                print(f" [{i}] {record}")
                i += 1

    ##################################################################
    # Display any photographs
    #
    print(f"PHOTOGRAPHS = {len(obj.photographs)}")
    i = 0
    for photograph in obj.photographs:
        print(f" [{i}]")
        for property in photograph:
            print(f" {property} = {photograph[property]}")
        i += 1

if __name__=="__main__":
    main()

# vim: shiftwidth=4 tabstop=4 softtabstop=4 expandtab
