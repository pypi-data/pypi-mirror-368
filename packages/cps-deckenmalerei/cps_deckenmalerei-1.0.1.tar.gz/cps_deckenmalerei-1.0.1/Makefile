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

cps_deckenmalerei:
	python3 -m pip install --no-dependencies .

clean:
	find -name "*~" -delete

distclean:clean
	rm -Rf dist

install:
	python3 -m pip install .
	python3 -m pip install dotenv

uninstall:
	python3 -m pip uninstall -y cps_deckenmalerei

venv:
	python3 -m venv ~/.venvs/cps_deckenmalerei

tools:
	python3 -m pip install --upgrade build
	python3 -m pip install --upgrade twine

build:distclean
	python3 -m build

upload:
	python3 -m twine upload --verbose --repository pypi dist/*

ls:
	find -type f -not -path "./.hg/*" -ls

test:	test1 test2 test3 test4 test5 test6

test1:
	wbset 1
	wbset https://www.deckenmalerei.eu/10885d10-c5b7-11e9-b6fd-d99e1ba53a95
	wbset https://www.deckenmalerei.eu/284af00a-294b-4ccf-9f49-925b86aec3dd
	wbset https://www.deckenmalerei.eu/2dcdd490-c800-11e9-8a8f-6315b3a88f02

test2:
	wbset https://www.deckenmalerei.eu/ff8a3985-b4f6-496e-ad68-a9c0d3ab1c0a

test3:
	wbset https://www.deckenmalerei.eu/00c6a927-3e65-43f1-896d-137656ee6fcb

test4:
	wbset https://www.deckenmalerei.eu/fd391f16-5096-492d-8481-042d7350c6bc

test5:
	wbset https://www.deckenmalerei.eu/0086766a-24d6-437e-ae2c-8c554335904a

test6:
	wbset https://www.deckenmalerei.eu/00d65dca-0885-4001-a130-9b4c99eb7334
	wbset https://www.deckenmalerei.eu/00e1625e-0ac7-4230-a151-c46a4718b3fd
	wbset https://www.deckenmalerei.eu/0112a993-8479-42f7-8919-be4306d63e56
	wbset https://www.deckenmalerei.eu/0182a722-f35f-42a7-8c49-a692ebeed2af
	wbset https://www.deckenmalerei.eu/021afb11-438b-4f7b-aa6f-d169b4607e22
	wbset https://www.deckenmalerei.eu/023d2508-d285-4e48-9b43-0fd41d890745
