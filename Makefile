cleanpyc:
	find src -name "*\.pyc" |xargs rm -rf


cleandata:
	rm -rf parts/data/*

