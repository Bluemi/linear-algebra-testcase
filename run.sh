#!/bin/bash

case "$1" in
	2)
		poetry run python3 -m linear_algebra_testcase.dim2
		;;
	3)
		poetry run python3 -m linear_algebra_testcase.dim3
		;;
	*)
		echo "invalid option"
		;;
esac
