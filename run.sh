#!/bin/bash

case "$1" in
	2)
		python3 -m linear_algebra_testcase.dim2
		;;
	3)
		python3 -m linear_algebra_testcase.dim3
		;;
	r)
		python3 -m linear_algebra_testcase.dim3.coordinate_system
		;;
	*)
		echo "invalid option"
		;;
esac
